from typing import List, Dict
from astrology.models import AstrologyAspect, ZWDSPalace

# A localized reference database of astrological definitions and interpretations
ASTRO_KNOWLEDGE_BASE = {
    "aspects": {
        "Saturn-square-Midheaven": (
            "Saturn square Midheaven indicates significant career obstacles, structural bottlenecks, "
            "and friction with authority figures. Success requires systematic discipline, persistence, "
            "and overcoming deep-seated professional resistance."
        ),
        "Sun-square-Ascendant": (
            "Sun square Ascendant creates a tension between the inner identity and the outer persona. "
            "The native may face friction in social environments and must learn to align their core power "
            "with how they project themselves to the world."
        ),
        "Ascendant-square-Midheaven": (
            "Ascendant square Midheaven indicates alignment issues between personal desires and public "
            "reputation/career path. It creates structural pressure, forcing the native to continually "
            "adjust their style of action to fit professional realities."
        ),
        "Mars-opposition-Pluto": (
            "Mars opposition Pluto represents a highly explosive power dynamic, power struggles, and relational "
            "volatility. When triggered inside relational boundaries, it presents a risk of intense conflict, "
            "betrayal, or legal disputes."
        ),
        "Moon-square-Neptune": (
            "Moon square Neptune creates emotional sensitivity, escapist tendencies, and difficulty seeing "
            "situations clearly. When active, it raises the risk of psychosomatic exhaustion or lack of boundaries."
        ),
        "Moon-opposition-Neptune": (
            "Moon opposition Neptune signals high emotional sensitivity, susceptibility to deception, and boundary "
            "dissolution. When triggered, it indicates a risk of systemic energy drainage or chronic fatigue."
        ),
        "Moon-conjunction-Neptune": (
            "Moon conjunct Neptune amplifies psychic sensitivity, emotional vulnerability, and artistic imagination. "
            "Without proper grounding, it can lead to emotional confusion and physical vitality exhaustion."
        ),
        "Sun-conjunction-Midheaven": (
            "Sun conjunct Midheaven points to a powerful career drive and public visibility. The native's identity "
            "is heavily bound to their public achievement and professional success."
        ),
        "Sun-trine-Moon": (
            "Sun trine Moon creates a harmonious baseline between conscious will and emotional needs. It supports "
            "vitality, internal balance, and ease of flow in life pursuits."
        ),
    },
    "zwds": {
        "Spouse-Hua-Ji": (
            "Hua-Ji (化忌) in the Spouse Palace signifies relational karma, attachment complications, or "
            "friction in marriages. Communication bottlenecks, high expectations, or relational blocks are active."
        ),
        "Wealth-Hua-Ji": (
            "Hua-Ji in the Wealth Palace indicates financial volatility, initial cash-flow blockages, and "
            "recurrent obstacles in acquiring material wealth. Requires cautious investment strategies."
        ),
        "Career-Hua-Ji": (
            "Hua-Ji in the Career Palace causes professional setbacks, career path changes, and obstacles "
            "with projects or colleagues. Relates to hard work with delayed returns."
        ),
        "Friends-Hua-Ji": (
            "Hua-Ji in the Friends Palace indicates betrayal by companions, friction in partnerships, and "
            "relational blockages with peers."
        ),
        "Health-Xian": (
            "Main stars in the Health Palace dropping to Xian (陷/Dim) brightness suggests compromised physical "
            "vitality, susceptibility to systemic exhaustion, and vulnerable somatic sectors."
        ),
    }
}

def retrieve_astrological_context(
    aspects: List[AstrologyAspect],
    palaces: List[ZWDSPalace],
    target_vector: str
) -> List[str]:
    """
    RAG Component: Performs semantic keyword matching against the localized astrological 
    reference database to retrieve context chunks relevant to the calculated birth chart.
    """
    retrieved_chunks = []
    
    # 1. Search aspects
    for aspect in aspects:
        # Check standard and reverse matches (e.g. Saturn-square-Midheaven or Midheaven-square-Saturn)
        key1 = f"{aspect.planet1}-{aspect.aspect_type}-{aspect.planet2}"
        key2 = f"{aspect.planet2}-{aspect.aspect_type}-{aspect.planet1}"
        
        if key1 in ASTRO_KNOWLEDGE_BASE["aspects"]:
            retrieved_chunks.append(f"[Aspect] {ASTRO_KNOWLEDGE_BASE['aspects'][key1]}")
        elif key2 in ASTRO_KNOWLEDGE_BASE["aspects"]:
            retrieved_chunks.append(f"[Aspect] {ASTRO_KNOWLEDGE_BASE['aspects'][key2]}")
            
    # 2. Search ZWDS Palaces
    for palace in palaces:
        palace_name = palace.name.lower()
        
        # Check Hua-Ji
        if "hua-ji" in [star.lower() for star in palace.stars]:
            for key in ASTRO_KNOWLEDGE_BASE["zwds"]:
                if key.endswith("Hua-Ji") and key.split("-")[0].lower() in palace_name:
                    retrieved_chunks.append(f"[ZWDS] {ASTRO_KNOWLEDGE_BASE['zwds'][key]}")
                    
        # Check Xian/Dim in Health
        if "health" in palace_name:
            has_xian = any("xian" in star.lower() or "dim" in star.lower() for star in palace.stars)
            if has_xian:
                retrieved_chunks.append(f"[ZWDS] {ASTRO_KNOWLEDGE_BASE['zwds']['Health-Xian']}")
                
    # 3. Sort/Prioritize based on the target vector
    def relevance_score(chunk: str) -> int:
        score = 0
        chunk_lower = chunk.lower()
        if target_vector == "wealth":
            if any(w in chunk_lower for w in ("wealth", "career", "saturn", "midheaven", "finance")):
                score += 10
        elif target_vector == "affinity":
            if any(w in chunk_lower for w in ("spouse", "friends", "relation", "mars", "pluto", "conflict")):
                score += 10
        elif target_vector == "vitality":
            if any(w in chunk_lower for w in ("health", "vitality", "moon", "neptune", "exhaustion", "somatic")):
                score += 10
        elif target_vector == "macro_evolution":
            if any(w in chunk_lower for w in ("evolution", "path", "destiny", "identity", "sun")):
                score += 10
        return score
        
    retrieved_chunks.sort(key=relevance_score, reverse=True)
    return retrieved_chunks
