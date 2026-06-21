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

def compile_prompt(
    astrology_data: dict,
    context_chunks: list,
    target_vector: str
) -> str:
    """
    Assembles a structured prompt containing the calculated JSON matrix and RAG context chunks.
    """
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
{json.dumps(astrology_data, indent=2)}

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
