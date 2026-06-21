import os
import json
from dotenv import load_dotenv
import anthropic

# Load environment variables from .env if present
load_dotenv()

def get_anthropic_client():
    """
    Configures and returns the AsyncAnthropic client.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please set it or add it to a .env file.")
    return anthropic.AsyncAnthropic(api_key=api_key)

STAR_LOCALIZATION_DICTIONARY = {
    "Zi Wei": "Emperor",
    "Tian Fu": "Heavenly Mansion",
    "Zuo Fu": "Intellect",
    "You Bi": "Right Assist",
    "Tian Ji": "Advisor",
    "Tai Yang": "Sun",
    "Tai Yin": "Moon",
    "Wu Qu": "Finance",
    "Tian Tong": "Mascot",
    "Lian Zhen": "Justice",
    "Tan Lang": "Flirt",
    "Ju Men": "Advocate",
    "Tian Liang": "Blessing",
    "Qi Sha": "Marshal",
    "Po Jun": "Pioneer",
    "Tian Xiang": "Minister",
    "Wen Qu": "Arts",
    "Wen Chang": "Academic",
    "Lu Cun": "Wealth Star",
    "Tian Kui": "Status",
    "Tian Yue": "Grace",
    "Qing Yang": "Sternness",
    "Tuo Luo": "Obstacle",
    "Di Kong": "Void",
    "Di Jie": "Exhaust"
}
def compress_astrology_payload(astrology_data: dict) -> dict:
    """
    Compresses the raw response payload by stripping redundant keys,
    aspect degrees details, and verbose definitions.
    """
    compressed = {}
    
    # 1. Compress birth_time_metrics
    metrics = astrology_data.get("birth_time_metrics", {})
    compressed["birth_time_metrics"] = {
        "local_datetime": metrics.get("local_datetime"),
        "lmt_datetime": metrics.get("lmt_datetime"),
        "tlt_datetime": metrics.get("tlt_datetime"),
        "timezone_offset": metrics.get("timezone_offset"),
        "branch_boundary_anomaly": metrics.get("branch_boundary_anomaly", False)
    }
    
    # 2. Keep western_matrix (simple dict)
    compressed["western_matrix"] = astrology_data.get("western_matrix", {})
    
    # 3. Compress zwds_matrix
    zwds = astrology_data.get("zwds_matrix", {})
    compressed_palaces = []
    for p in zwds.get("palaces", []):
        compact_stars = []
        for s in p.get("stars_metadata", []):
            b_idx = s.get("brightness_index", "Neutral")
            cls_ = s.get("classification", "Benefic")
            compact_stars.append({
                "name": s.get("name"),
                "brightness": b_idx,
                "type": cls_
            })
        
        compressed_palaces.append({
            "name": p.get("name"),
            "stem_branch": p.get("stem_branch"),
            "decadal_range": p.get("decadal_range"),
            "changsheng": p.get("changsheng"),
            "stars": compact_stars,
            "pillar_gods": p.get("pillar_gods"),
            "one_year_luck": p.get("one_year_luck")
        })
        
    compressed["zwds_matrix"] = {
        "palaces": compressed_palaces,
        "yearly_stem_branch": zwds.get("yearly_stem_branch"),
        "monthly_branch": zwds.get("monthly_branch"),
        "lunar_date_str": zwds.get("lunar_date_str")
    }
    
    # 4. Compress synthesis_flags
    flags = astrology_data.get("synthesis_flags", {})
    compressed["synthesis_flags"] = {
        "friction_index": flags.get("friction_index"),
        "friction_points": flags.get("friction_points"),
        "critical_bottleneck": flags.get("critical_bottleneck"),
        "interpersonal_risk": flags.get("interpersonal_risk"),
        "systemic_exhaustion": flags.get("systemic_exhaustion"),
        "palace_friction_index": flags.get("palace_friction_index"),
        "detected_patterns": [
            {"name": pat.get("name") if isinstance(pat, dict) else pat.name,
             "triggered": pat.get("is_triggered") if isinstance(pat, dict) else pat.is_triggered}
            for pat in flags.get("detected_patterns", [])
        ]
    }
    
    return compressed

def compile_prompt(
    astrology_data: dict,
    context_chunks: list,
    target_vector: str
) -> str:
    """
    Assembles a structured prompt containing the calculated JSON matrix and RAG context chunks.
    """
    compressed_data = compress_astrology_payload(astrology_data)
    context_text = "\n".join(f"- {chunk}" for chunk in context_chunks)
    
    prompt = f"""You are a Lead Backend Engineer, AI Systems Architect, and expert astrologer.
We have parsed raw birth data into a hybrid deterministic matrix containing:
1. Western Ephemeris degrees and Placidus houses.
2. Chinese Zi Wei Dou Shu (ZWDS) palace locations.
3. Aspect calculations and cross-system overlap risk triggers.

Here is the central Star Localization Dictionary used on the frontend UI:
{json.dumps(STAR_LOCALIZATION_DICTIONARY, indent=2)}

IMPORTANT LOCALIZATION RULE:
Please ensure that in your analysis and output report, you reference stars using both their English UI labels and Pinyin (e.g., "Finance (Wu Qu)", "Mascot (Tian Tong)", "Wealth Star (Lu Cun)", "Flirt (Tan Lang)", "Void (Di Kong)", "Exhaust (Di Jie)") so that the generated report text matches the exact UI labels rendered on the frontend interface.

Here is the parsed JSON astrology data payload:
{json.dumps(compressed_data, indent=2)}

Here are relevant retrieved astrological interpretation context chunks (RAG context):
{context_text}

Target analysis vector: {target_vector.upper()}

Please provide a highly synthesized, deterministic, and expert astrological analysis based on this data.
Your output must focus on identifying structural constraints, friction points, and opportunities.
Ensure your response is professional, clear, and structured in Markdown. Avoid generic fluff.
"""
    return prompt

async def generate_completion(compiled_prompt: str, model_name: str = "claude-opus-4-7") -> str:
    """
    Calls Anthropic Claude API asynchronously to generate context completion.
    """
    client = get_anthropic_client()
    response = await client.messages.create(
        model=model_name,
        max_tokens=4096,
        messages=[
            {"role": "user", "content": compiled_prompt}
        ]
    )
    return response.content[0].text
