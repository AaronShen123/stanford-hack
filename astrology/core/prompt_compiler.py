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

async def generate_completion(compiled_prompt: str, model_name: str = "claude-opus-4-8") -> str:
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


# ──────────────────────────────────────────────────────────────────────────
# Interactive ZWDS master — grounded, multi-turn chat
# ──────────────────────────────────────────────────────────────────────────

MASTER_SYSTEM_PROMPT = """You are a master practitioner of Zi Wei Dou Shu (紫微斗數, Purple Star Astrology) with decades of experience — the kind of reader people travel to consult. You speak in clear, fluent English while preserving the Chinese term in parentheses on first use (e.g. "Life Palace (命宮)", "Wealth (武曲)").

Your job is to give readings as precise and specific as a seasoned human 命理師 — never generic horoscope filler. Every claim you make must be traceable to the chart data provided in the context block. If the data does not support a conclusion, say so plainly rather than inventing.

METHODOLOGY you reason with (silently — show conclusions, not lectures):
- The natal chart (本命盤): the 12 palaces, the 14 major stars and their brightness, the auxiliary stars, the birth-year four transformations (生年四化 Lu/Quan/Ke/Ji), the Life Master (命主) and Body Master (身主), and the Five-Elements Bureau (五行局).
- The three-and-four alignment (三方四正): a palace is judged together with its opposite and its two trine palaces.
- Borrowed stars (借星): an empty palace borrows the opposite palace's major stars at reduced strength.
- Timing via transits: the decade (大限), the year (流年), the month (流月), and the day (流日). The single most important timing signal is the FOUR TRANSFORMATIONS of that period (流年/流月/流日四化): the star that turns 化忌 (Hua Ji) marks friction, loss, fixation, or a difficult person/event in the palace it lands on; 化祿 (Hua Lu) marks opportunity, money, smooth flow; 化權 (Hua Quan) marks power, control, advancement; 化科 (Hua Ke) marks reputation, study, recognition. Read which natal life-domain (palace) each transformation activates.

WHEN THE USER GIVES YOU A PAST DATE OR YEAR and asks what happened:
- Use the transit context provided (大限/流年/流月/流日 with their 四化 and which natal palace each activates).
- Reconstruct concretely: which life area was active (career, wealth, marriage, health, relationships, study, travel, family), the FLAVOR of events (gain vs loss, conflict vs harmony, advancement vs setback), and the KIND of people likely encountered (e.g. a benefactor/mentor 貴人 when 化祿/天魁天鉞 are active in the Friends/Career palace; a romantic interest when 紅鸾/天喜/廉貞貪狼 or 化祿 activate the Marriage/Travel palace; a rival or someone causing trouble when 化忌 hits the Friends/Marriage palace).
- Be specific and confident about the THEME and the type of person, while honest that astrology gives patterns and probabilities, not guaranteed facts. Frame as "the chart strongly indicates…", "this is a year where…", "you likely encountered someone who…".
- Then ask one sharp follow-up question to confirm or refine (a real 命理師 reads the client's reaction).

STYLE:
- Lead with the answer the user asked for. Be vivid and human, not clinical.
- Use short paragraphs and the occasional bolded key term. Tables are welcome for palace/timing breakdowns.
- Never refuse a sincere astrology question, but do not give medical, legal, or financial directives — give astrological insight and let the user decide.
- Stay grounded in THIS chart. Do not recite generic star meanings unless tying them to this person's palaces.
"""


def _fmt_stars(palace: dict) -> str:
    parts = []
    for s in palace.get("main_stars", []):
        tag = s.get("name", "")
        if s.get("status"):
            tag += f"·{s['status']}"
        if s.get("mutagen"):
            tag += f"·{s['mutagen']}"
        if s.get("is_borrowed"):
            tag += "(borrowed)"
        parts.append(tag)
    minors = [m for m in palace.get("minor_stars", []) if m]
    if minors:
        parts.append("aux: " + ", ".join(minors))
    return "; ".join(parts) if parts else "(empty)"


def format_chart_context(synthesis: dict, horoscope: dict | None = None) -> str:
    """Render the natal chart (+ optional transit) as a compact grounding block."""
    z = synthesis.get("zwds_matrix", {})
    lines = ["# NATAL CHART (本命盤)"]
    lines.append(f"Year pillar: {z.get('yearly_stem_branch')} | Month pillar: {z.get('monthly_branch')}")
    lines.append(f"Bureau (五行局): {z.get('bureau', 'n/a')}")
    lines.append(f"Life Master (命主): {z.get('life_master')} | Body Master (身主): {z.get('body_master')}")
    lines.append(f"Lunar: {z.get('lunar_date_str')}")
    lines.append("\n## Twelve Palaces")
    for p in z.get("palaces", []):
        flags = []
        if p.get("intensity", 1.0) < 1.0:
            flags.append("⚠Hua-Ji palace")
        lines.append(
            f"- {p.get('name')} [{p.get('stem_branch')}] "
            f"(decade {p.get('decadal_range','?')}): {_fmt_stars(p)}"
            + (f"  {' '.join(flags)}" if flags else "")
        )

    if horoscope:
        lines.append(f"\n# TRANSITS for {horoscope.get('target_date')} (run-time 流盤)")
        for scope, label in [("decadal", "Decade 大限"), ("yearly", "Year 流年"),
                             ("monthly", "Month 流月"), ("daily", "Day 流日")]:
            blk = horoscope.get(scope) or {}
            if not blk:
                continue
            muta = blk.get("mutagen", {})
            muta_str = ", ".join(f"{k}→{v}" for k, v in muta.items()) or "n/a"
            lp = blk.get("transit_life_palace_over_natal", "")
            extra = f" | decade ages {blk['decadal_range']}" if blk.get("decadal_range") else ""
            lines.append(
                f"- {label}: pillar {blk.get('stem_branch')}"
                f" | transit Life Palace sits over natal [{lp}]{extra}"
                f"\n    四化 (transformations this period): {muta_str}"
            )
        lines.append(
            "\nInterpret the transit 四化 against the natal palaces above to reconstruct the period's events and the people involved."
        )
    return "\n".join(lines)


async def chat_with_master(
    chart_context: str,
    history: list,
    question: str,
    model_name: str = "claude-opus-4-8",
) -> str:
    """Multi-turn grounded reading. ``history`` is a list of {role, content}."""
    client = get_anthropic_client()

    # Stable system block (persona + this subject's chart) → cacheable prefix.
    system = [
        {"type": "text", "text": MASTER_SYSTEM_PROMPT},
        {"type": "text", "text": chart_context,
         "cache_control": {"type": "ephemeral"}},
    ]

    messages = []
    for turn in (history or []):
        role = turn.get("role")
        content = turn.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": question})

    # Stream so long, thoughtful readings don't hit the request timeout.
    async with client.messages.stream(
        model=model_name,
        max_tokens=4096,
        system=system,
        thinking={"type": "adaptive"},
        messages=messages,
    ) as stream:
        final = await stream.get_final_message()

    return "".join(b.text for b in final.content if b.type == "text")
