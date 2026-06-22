import uuid
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from astrology.models import AstrologyRequest, AstrologyResponse, TimeMetricsModel, WesternMatrix, ZWDSMatrix, AstrologyCompletionResponse
from astrology.core.time_utils import calculate_time_metrics
from astrology.calculators.western import WesternAstrologyCalculator
from astrology.calculators.scaffold_zwds import ScaffoldZWDSCalculator
from astrology.core.synthesis import generate_synthesis_flags
from astrology.core.rag import retrieve_astrological_context
from astrology.core.prompt_compiler import compile_prompt, generate_completion

app = FastAPI(
    title="Astrology Synthesis Engine API",
    version="1.0.0",
    description="Engine merging Western Ephemeris with Chinese ZWDS matrices"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom RFC 7807 Exception Handler for Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_id = str(uuid.uuid4().hex[:8])
    errors = exc.errors()
    
    formatted_details = []
    for err in errors:
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        formatted_details.append(f"{loc}: {msg}")
    
    detail_str = "; ".join(formatted_details)
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "type": "/errors/validation-failed",
            "title": "Request Validation Failed",
            "status": status.HTTP_400_BAD_REQUEST,
            "detail": detail_str,
            "instance": f"{request.url.path}/err_{error_id}"
        }
    )

# Custom RFC 7807 Exception Handler for General Server Errors
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4().hex[:8])
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "/errors/internal-server-error",
            "title": "Internal Server Error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": str(exc),
            "instance": f"{request.url.path}/err_{error_id}"
        }
    )

# Initialize calculators once at startup
# Isolate time standard: western_calc receives pure UTC via jd_ut, zwds_calc receives LAT tlt_datetime
western_calc = WesternAstrologyCalculator()
zwds_calc = ScaffoldZWDSCalculator()

@app.post(
    "/api/v1/astrology/synthesis",
    response_model=AstrologyResponse,
    status_code=status.HTTP_200_OK,
    summary="Synthesize Western and ZWDS Astrology Matrices",
    description="Ingests birth coordinates to calculate TLT, query planetary ephemerides, and synthesize structural matrices."
)
async def synthesize_astrology(payload: AstrologyRequest):
    # 1. Compute time metrics (UTC, LMT, TLT, Julian Days, and Earthly Branch boundary check)
    metrics = calculate_time_metrics(
        birth_date=payload.birth_date,
        birth_time=payload.birth_time,
        longitude=payload.longitude,
        timezone_offset=payload.timezone_offset
    )
    
    # 2. Compute Western positions using Swiss Ephemeris (uses pure UTC-based jd_ut)
    west_pos = western_calc.calculate_positions(
        jd_ut=metrics["jd_ut"],
        latitude=payload.latitude,
        longitude=payload.longitude
    )
    
    western_matrix = WesternMatrix(
        sun_degree=west_pos["sun_degree"],
        moon_degree=west_pos["moon_degree"],
        ascendant_degree=west_pos["ascendant_degree"],
        midheaven_degree=west_pos["midheaven_degree"],
        saturn_degree=west_pos["saturn_degree"],
        mars_degree=west_pos["mars_degree"],
        neptune_degree=west_pos["neptune_degree"],
        pluto_degree=west_pos["pluto_degree"],
        houses=west_pos["houses"]
    )
    
    # 3. Compute Chinese ZWDS using raw Local Datetime to align with standard ZWDS rules
    zwds_pos = await zwds_calc.calculate_chart(
        tlt_datetime=metrics["local_datetime"],
        gender=payload.gender.value,
        latitude=payload.latitude,
        longitude=payload.longitude
    )
    
    zwds_matrix = ZWDSMatrix(**zwds_pos)
    
    # 4. Generate Synthesis Matrix aspects and unified risk fusions
    synthesis_flags = generate_synthesis_flags(
        western=western_matrix,
        zwds=zwds_matrix,
        target_vector=payload.target_vector.value
    )
    
    # Enforce earthly branch boundaries: flag as dual-matrix if within 60 seconds
    synthesis_flags.dual_matrix_indicator = metrics["branch_boundary_anomaly"]
    
    # 5. Format birth time metrics for output
    time_metrics_response = TimeMetricsModel(
        local_datetime=metrics["local_datetime"].isoformat(),
        utc_datetime=metrics["utc_datetime"].isoformat(),
        lmt_datetime=metrics["lmt_datetime"].isoformat(),
        tlt_datetime=metrics["tlt_datetime"].isoformat(),
        timezone_offset=metrics["timezone_offset"],
        jd_ut=metrics["jd_ut"],
        jd_et=metrics["jd_et"],
        eot_seconds=metrics["eot_seconds"],
        branch_boundary_anomaly=metrics["branch_boundary_anomaly"]
    )
    
    # 6. Return response
    return AstrologyResponse(
        birth_time_metrics=time_metrics_response,
        western_matrix=western_matrix,
        zwds_matrix=zwds_matrix,
        synthesis_flags=synthesis_flags
    )


@app.post(
    "/api/v1/astrology/completion",
    response_model=AstrologyCompletionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Astrology Completion and Reading via LLM",
    description="Calculates matrices, performs RAG context retrieval, compiles prompt, and invokes Gemini for the final reading."
)
async def generate_astrology_completion(payload: AstrologyRequest):
    # 1. Calculate the base AstrologyResponse
    synthesis = await synthesize_astrology(payload)
    
    # 2. Retrieve astrological context from the RAG library
    context_chunks = retrieve_astrological_context(
        aspects=synthesis.synthesis_flags.aspects,
        palaces=synthesis.zwds_matrix.palaces,
        target_vector=payload.target_vector.value
    )
    
    # 3. Compile the prompt context
    compiled_prompt = compile_prompt(
        astrology_data=synthesis.model_dump(),
        context_chunks=context_chunks,
        target_vector=payload.target_vector.value
    )
    
    # 4. Invoke Gemini API (raises Exception on missing API key, caught and formatted by RFC 7807 handler)
    try:
        reading = await generate_completion(compiled_prompt)
    except ValueError as val_err:
        raise Exception(f"Configuration Error: {str(val_err)}")
        
    return AstrologyCompletionResponse(
        synthesis=synthesis,
        compiled_prompt=compiled_prompt,
        reading=reading
    )
