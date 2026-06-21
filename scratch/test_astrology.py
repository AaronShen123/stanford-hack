import sys
from datetime import datetime, timedelta
import asyncio

sys.path.append(".")

from astrology.core.time_utils import calculate_time_metrics, check_branch_boundary_anomaly
from astrology.calculators.western import WesternAstrologyCalculator
from astrology.calculators.scaffold_zwds import ScaffoldZWDSCalculator
from astrology.core.synthesis import generate_synthesis_flags, get_planet_house
from astrology.models import AstrologyRequest, AstrologyResponse, WesternMatrix, ZWDSMatrix, ZWDSPalace, TargetVectorEnum, GenderEnum, AstrologyCompletionResponse
from main import synthesize_astrology, app, generate_astrology_completion

# Mock generate_completion if ANTHROPIC_API_KEY is not set
import os
from dotenv import load_dotenv
from unittest.mock import AsyncMock

load_dotenv()

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("⚠️ ANTHROPIC_API_KEY is not set. Mocking Anthropic Claude LLM API call for testing.")
    import main
    import astrology.core.prompt_compiler
    mocked_reading = "[Mocked Claude Reading] This is a mock reading for testing because ANTHROPIC_API_KEY was not provided."
    main.generate_completion = AsyncMock(return_value=mocked_reading)
    astrology.core.prompt_compiler.generate_completion = AsyncMock(return_value=mocked_reading)


def test_time_calculations():
    print("Running Time Calculations Test...")
    birth_date = "1990-05-15"
    birth_time = "12:00:00"
    longitude = -122.4194
    
    metrics = calculate_time_metrics(birth_date, birth_time, longitude)
    
    assert metrics["timezone_offset"] == -8.0
    assert metrics["utc_datetime"].hour == 20
    assert metrics["lmt_datetime"].hour == 11
    assert metrics["lmt_datetime"].minute == 50
    assert not metrics["branch_boundary_anomaly"]
    
    print("✅ Time calculations test passed.")
    return metrics

def test_boundary_anomaly():
    print("Running Earthly Branch Boundary Anomaly Test...")
    # Si hour starts at 09:00, Wu hour starts at 11:00.
    # 11:00:15 True Local Time is within 60s of the 11:00 Wu boundary.
    tlt_dt_near = datetime(2026, 6, 20, 11, 0, 15)
    tlt_dt_far = datetime(2026, 6, 20, 11, 10, 0)
    
    assert check_branch_boundary_anomaly(tlt_dt_near) is True, "Expected boundary anomaly for 11:00:15"
    assert check_branch_boundary_anomaly(tlt_dt_far) is False, "Expected no anomaly for 11:10:00"
    
    print("✅ Earthly Branch boundary anomaly test passed.")

def test_western_calculator(jd_ut):
    print("Running Western Calculator Test...")
    calc = WesternAstrologyCalculator()
    positions = calc.calculate_positions(
        jd_ut=jd_ut,
        latitude=37.7749,
        longitude=-122.4194
    )
    
    assert "sun_degree" in positions
    assert "saturn_degree" in positions
    assert "mars_degree" in positions
    assert "neptune_degree" in positions
    assert "pluto_degree" in positions
    assert len(positions["houses"]) == 12
    
    # Test house calculation
    house_placements = {
        "Sun": get_planet_house(positions["sun_degree"], positions["houses"]),
        "Saturn": get_planet_house(positions["saturn_degree"], positions["houses"]),
    }
    print(f"  Sun falls in House: {house_placements['Sun']}")
    print(f"  Saturn falls in House: {house_placements['Saturn']}")
    
    print("✅ Western calculator (with Saturn, Mars, Neptune, Pluto) test passed.")
    return positions

def test_synthesis_decay_and_matrix_triggers():
    print("Running Synthesis Continuous Decay & Risk Triggers Test...")
    
    # Create a mock WesternMatrix with Mars-Pluto Opposition near 7th house
    # Cusps: House 7 is between 328.25 and 351.87
    houses = {
        1: 148.25, 2: 171.87, 3: 200.35, 4: 233.25, 5: 267.61, 6: 299.74,
        7: 328.25, 8: 351.87, 9: 20.35, 10: 53.25, 11: 87.61, 12: 119.74
    }
    
    # Mars in 7th house (e.g. 335.0), Pluto in 1st house (e.g. 156.0) -> Angle diff = 179.0 (~180 deg opposition)
    western_matrix = WesternMatrix(
        sun_degree=54.7,
        moon_degree=301.2,
        ascendant_degree=148.25,
        midheaven_degree=53.25,
        saturn_degree=55.0, # Saturn conjunct Midheaven (53.25), which is Square Ascendant (148.25)
        mars_degree=335.0,  # In 7th House (328.25 to 351.87)
        neptune_degree=125.0, # In 12th House (119.74 to 148.25)
        pluto_degree=156.0,  # In 1st House, in opposition to Mars
        houses=houses
    )
    
    # ZWDS matrix with:
    # 1. Hua-Ji in Spouse Palace (to trigger Interpersonal Risk)
    # 2. Main star in Health Palace with Xian (to trigger Systemic Exhaustion)
    palaces = [
        ZWDSPalace(name="Ming (Self)", stem_branch="Ji-Si", stars=["Zi Wei"]),
        ZWDSPalace(name="Spouse", stem_branch="Xin-Wei", stars=["Tai Yang", "Hua-Ji"]), # Interpersonal ZWDS trigger
        ZWDSPalace(name="Health", stem_branch="Jia-Xu", stars=["Lian Zhen (Xian)", "Tian Yue"]), # Health ZWDS trigger
        ZWDSPalace(name="Wealth", stem_branch="Gui-You", stars=["Tian Tong", "Lu Cun"]),
        ZWDSPalace(name="Career", stem_branch="Ding-Chou", stars=["Tan Lang", "Di Kong"])
    ]
    # Fill remaining palaces to make it valid
    while len(palaces) < 12:
        palaces.append(ZWDSPalace(name=f"Palace-{len(palaces)}", stem_branch="X-Y", stars=[]))
        
    zwds_matrix = ZWDSMatrix(
        palaces=palaces,
        yearly_stem_branch="Bing-Wu",
        monthly_branch="Wu-Shen",
        lunar_date_str="Mock Date"
    )
    
    # Test Affinity Vector: Interpersonal Risk should trigger
    flags_affinity = generate_synthesis_flags(western_matrix, zwds_matrix, "affinity")
    assert flags_affinity.interpersonal_risk is True, "Expected interpersonal_risk to be True"
    print(f"  Friction Index (Decay Curve applied): {flags_affinity.friction_index}")
    
    # Test Vitality Vector: Systemic Exhaustion should trigger
    # Moon is at 301.2 (in 6th house: 299.74 to 328.25), Neptune is at 125.0 (in 12th house: 119.74 to 148.25).
    # Moon and Neptune are in opposition: 301.2 - 125.0 = 176.2 -> Opposition aspect with ~3.8 orb.
    # Moon/Neptune hard aspect inside 6th/12th house met! Health ZWDS trigger (Lian Zhen Xian) met!
    flags_vitality = generate_synthesis_flags(western_matrix, zwds_matrix, "vitality")
    assert flags_vitality.systemic_exhaustion is True, "Expected systemic_exhaustion to be True"
    
    print("✅ Synthesis decay and risk triggers test passed.")

async def test_endpoint():
    print("Running FastAPI Endpoint Controller Test...")
    request_payload = AstrologyRequest(
        birth_date="1990-05-15",
        birth_time="12:00:00",
        latitude=37.7749,
        longitude=-122.4194,
        target_vector=TargetVectorEnum.WEALTH,
        gender=GenderEnum.M
    )
    
    response = await synthesize_astrology(request_payload)
    assert isinstance(response, AstrologyResponse)
    
    # Verify extra planets are in the serialized output
    assert response.western_matrix.saturn_degree > 0
    assert response.western_matrix.mars_degree > 0
    assert response.western_matrix.neptune_degree > 0
    assert response.western_matrix.pluto_degree > 0
    
    # Check that ZWDS palaces are mapped
    assert len(response.zwds_matrix.palaces) == 12
    assert response.synthesis_flags.friction_index >= 0
    
    print("✅ FastAPI Endpoint test passed.")
    print("Output Response payload:")
    print(response.model_dump_json(indent=2))

async def test_completion_endpoint():
    print("Running FastAPI Completion Endpoint Test...")
    request_payload = AstrologyRequest(
        birth_date="1990-05-15",
        birth_time="12:00:00",
        latitude=37.7749,
        longitude=-122.4194,
        target_vector=TargetVectorEnum.WEALTH,
        gender=GenderEnum.M
    )
    
    response = await generate_astrology_completion(request_payload)
    assert isinstance(response, AstrologyCompletionResponse)
    assert response.reading != ""
    assert "wealth" in response.compiled_prompt.lower()
    
    print("✅ FastAPI Completion Endpoint test passed.")
    print("Completion Reading Output:")
    print(response.reading)

if __name__ == "__main__":
    print("Starting Hardened Astrology Synthesis Engine Verification...")
    metrics = test_time_calculations()
    test_boundary_anomaly()
    west_pos = test_western_calculator(metrics["jd_ut"])
    test_synthesis_decay_and_matrix_triggers()
    asyncio.run(test_endpoint())
    asyncio.run(test_completion_endpoint())
    print("All tests completed successfully!")
