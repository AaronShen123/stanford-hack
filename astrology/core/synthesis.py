from typing import List, Dict, Any
from astrology.models import AstrologyAspect, SynthesisFlags, WesternMatrix, ZWDSMatrix, ZWDSPattern, ZWDSPalace

BRANCHES = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]

VECTOR_TO_PALACE = {
    "wealth": "Wealth",
    "affinity": "Marriage",
    "vitality": "Health",
    "macro_evolution": "Life"
}

def find_palace_by_name(matrix: ZWDSMatrix, target_name: str) -> ZWDSPalace:
    for palace in matrix.palaces:
        if target_name.lower() in palace.name.lower():
            return palace
    return None

def find_life_palace(matrix: ZWDSMatrix) -> ZWDSPalace:
    for palace in matrix.palaces:
        name = palace.name.lower()
        if "life" in name or "命" in name or "ming" in name:
            return palace
    return None

def get_palace_branch_index(palace: ZWDSPalace) -> int:
    parts = palace.stem_branch.split("-")
    branch = parts[1] if len(parts) > 1 else parts[0]
    branch = branch.strip().title()
    if branch in BRANCHES:
        return BRANCHES.index(branch)
    return -1

def get_relational_matrix(matrix: ZWDSMatrix, target_palace_name: str) -> List[ZWDSPalace]:
    target_palace = find_palace_by_name(matrix, target_palace_name)
    if not target_palace:
        return []
    
    target_idx = get_palace_branch_index(target_palace)
    if target_idx == -1:
        return [target_palace]
        
    branch_map = {}
    for p in matrix.palaces:
        parts = p.stem_branch.split("-")
        b = parts[1] if len(parts) > 1 else parts[0]
        b_clean = b.strip().title()
        if b_clean in BRANCHES:
            branch_map[BRANCHES.index(b_clean)] = p
        
    opposite_idx = (target_idx + 6) % 12
    trine1_idx = (target_idx + 4) % 12
    trine2_idx = (target_idx + 8) % 12
    
    relational_palaces = [target_palace]
    for idx in (opposite_idx, trine1_idx, trine2_idx):
        if idx in branch_map:
            relational_palaces.append(branch_map[idx])
            
    return relational_palaces

def get_flanking_matrix(matrix: ZWDSMatrix, target_palace_name: str) -> List[ZWDSPalace]:
    target_palace = find_palace_by_name(matrix, target_palace_name)
    if not target_palace:
        return []
    
    target_idx = get_palace_branch_index(target_palace)
    if target_idx == -1:
        return []
        
    branch_map = {}
    for p in matrix.palaces:
        parts = p.stem_branch.split("-")
        b = parts[1] if len(parts) > 1 else parts[0]
        b_clean = b.strip().title()
        if b_clean in BRANCHES:
            branch_map[BRANCHES.index(b_clean)] = p
        
    flank1_idx = (target_idx - 1) % 12
    flank2_idx = (target_idx + 1) % 12
    
    flanking_palaces = []
    for idx in (flank1_idx, flank2_idx):
        if idx in branch_map:
            flanking_palaces.append(branch_map[idx])
            
    return flanking_palaces

def calculate_palace_friction_index(matrix: ZWDSMatrix, target_palace_name: str) -> float:
    relational_palaces = get_relational_matrix(matrix, target_palace_name)
    if not relational_palaces:
        return 0.0
        
    malefic_count = 0
    benefic_count = 0
    for p in relational_palaces:
        for star in p.stars_metadata:
            if star.classification == "Malefic":
                malefic_count += 1
            elif star.classification == "Benefic":
                benefic_count += 1
                
    total = malefic_count + benefic_count
    if total == 0:
        return 0.0
    return round((malefic_count / total) * 100.0, 2)

def palace_has_star(palace: ZWDSPalace, star_keywords: List[str]) -> bool:
    for star in palace.stars + [s.name for s in palace.stars_metadata]:
        s_name = star.lower()
        if any(kw in s_name for kw in star_keywords):
            return True
    return False

def detect_zwds_patterns(matrix: ZWDSMatrix) -> List[ZWDSPattern]:
    patterns = []
    
    life_palace = find_life_palace(matrix)
    if not life_palace:
        return [
            ZWDSPattern(name="【文星拱命格】", is_triggered=False, description="Life Palace or trines contain both Wen Chang & Wen Qu."),
            ZWDSPattern(name="【空劫夾命格】", is_triggered=False, description="Life Palace is flanked by Di Jie & Di Kong in adjacent palaces.")
        ]
        
    life_idx = get_palace_branch_index(life_palace)
    if life_idx == -1:
        return [
            ZWDSPattern(name="【文星拱命格】", is_triggered=False, description="Life Palace or trines contain both Wen Chang & Wen Qu."),
            ZWDSPattern(name="【空劫夾命格】", is_triggered=False, description="Life Palace is flanked by Di Jie & Di Kong in adjacent palaces.")
        ]
    
    branch_map = {}
    for p in matrix.palaces:
        parts = p.stem_branch.split("-")
        b = parts[1] if len(parts) > 1 else parts[0]
        b_clean = b.strip().title()
        if b_clean in BRANCHES:
            branch_map[BRANCHES.index(b_clean)] = p
        
    # Pattern 1: 【文星拱命格】
    trine1_idx = (life_idx + 4) % 12
    trine2_idx = (life_idx + 8) % 12
    trine1 = branch_map.get(trine1_idx)
    trine2 = branch_map.get(trine2_idx)
    
    has_wen_chang = False
    has_wen_qu = False
    for p in [life_palace, trine1, trine2]:
        if p:
            if palace_has_star(p, ["wen chang", "academic"]):
                has_wen_chang = True
            if palace_has_star(p, ["wen qu", "arts"]):
                has_wen_qu = True
                
    wen_star_triggered = has_wen_chang and has_wen_qu
    patterns.append(ZWDSPattern(
        name="【文星拱命格】",
        is_triggered=wen_star_triggered,
        description="Life Palace or trines contain both Wen Chang (Academic) and Wen Qu (Arts) stars, indicating literary talent and intellect."
    ))
    
    # Pattern 2: 【空劫夾命格】
    flanking = get_flanking_matrix(matrix, life_palace.name)
    kong_jie_triggered = False
    if len(flanking) == 2:
        f1, f2 = flanking[0], flanking[1]
        has_jie1 = palace_has_star(f1, ["di jie", "exhaust"])
        has_kong1 = palace_has_star(f1, ["di kong", "void"])
        has_jie2 = palace_has_star(f2, ["di jie", "exhaust"])
        has_kong2 = palace_has_star(f2, ["di kong", "void"])
        kong_jie_triggered = (has_jie1 and has_kong2) or (has_kong1 and has_jie2)
        
    patterns.append(ZWDSPattern(
        name="【空劫夾命格】",
        is_triggered=kong_jie_triggered,
        description="Life Palace is flanked by Di Jie (Exhaust) and Di Kong (Void) in adjacent palaces, indicating sudden setbacks and fluctuations."
    ))
    
    return patterns

def get_planet_house(longitude: float, cusps: Dict[int, float]) -> int:
    """
    Determines which house (1 to 12) a planet's longitude falls into,
    correctly handling boundary crossovers.
    """
    for h in range(1, 12):
        c_start = cusps[h]
        c_end = cusps[h + 1]
        if c_start < c_end:
            if c_start <= longitude < c_end:
                return h
        else:  # Handle 360/0 degree crossover
            if longitude >= c_start or longitude < c_end:
                return h
                
    # Check House 12
    c_start = cusps[12]
    c_end = cusps[1]
    if c_start < c_end:
        if c_start <= longitude < c_end:
            return 12
    else:
        if longitude >= c_start or longitude < c_end:
            return 12
            
    return 1

def calculate_aspects(western: WesternMatrix) -> List[AstrologyAspect]:
    """
    Computes major aspects between Sun, Moon, Ascendant, Midheaven, Saturn, Mars, Neptune, and Pluto.
    Supported aspects: conjunction (0°), sextile (60°), square (90°), trine (120°), opposition (180°).
    """
    bodies = {
        "Sun": western.sun_degree,
        "Moon": western.moon_degree,
        "Ascendant": western.ascendant_degree,
        "Midheaven": western.midheaven_degree,
        "Saturn": western.saturn_degree,
        "Mars": western.mars_degree,
        "Neptune": western.neptune_degree,
        "Pluto": western.pluto_degree
    }
    
    aspect_definitions = [
        {"name": "conjunction", "angle": 0.0, "orb": 8.0},
        {"name": "sextile", "angle": 60.0, "orb": 6.0},
        {"name": "square", "angle": 90.0, "orb": 8.0},
        {"name": "trine", "angle": 120.0, "orb": 8.0},
        {"name": "opposition", "angle": 180.0, "orb": 8.0}
    ]
    
    detected_aspects = []
    body_names = list(bodies.keys())
    
    for i in range(len(body_names)):
        for j in range(i + 1, len(body_names)):
            name1 = body_names[i]
            name2 = body_names[j]
            deg1 = bodies[name1]
            deg2 = bodies[name2]
            
            diff = abs(deg1 - deg2)
            diff = min(diff, 360.0 - diff)
            
            for aspect in aspect_definitions:
                target = aspect["angle"]
                max_orb = aspect["orb"]
                actual_orb = abs(diff - target)
                
                if actual_orb <= max_orb:
                    detected_aspects.append(AstrologyAspect(
                        planet1=name1,
                        planet2=name2,
                        aspect_type=aspect["name"],
                        degree_difference=diff,
                        orb=actual_orb
                    ))
                    break
                    
    return detected_aspects

def generate_synthesis_flags(
    western: WesternMatrix,
    zwds: ZWDSMatrix,
    target_vector: str
) -> SynthesisFlags:
    """
    Computes structural friction using continuous decay curves and cross-references 
    Western ephemeris with ZWDS palaces to identify unified system action triggers.
    """
    aspects = calculate_aspects(western)
    
    # 1. Compute continuous orb friction decay
    friction_index = 0.0
    friction_points = []
    
    for aspect in aspects:
        if aspect.aspect_type in ("square", "opposition"):
            weight = 3.0 if aspect.aspect_type == "opposition" else 2.0
            # Continuous linear decay: W_friction = 1.0 - (theta_actual / theta_max)
            w_friction = 1.0 - (aspect.orb / 8.0)
            aspect_friction = weight * w_friction
            friction_index += aspect_friction
            friction_points.append(
                f"{aspect.planet1} {aspect.aspect_type} {aspect.planet2} (orb {aspect.orb:.2f}°)"
            )
            
    # 2. Determine planet house positions
    saturn_house = get_planet_house(western.saturn_degree, western.houses)
    mars_house = get_planet_house(western.mars_degree, western.houses)
    pluto_house = get_planet_house(western.pluto_degree, western.houses)
    moon_house = get_planet_house(western.moon_degree, western.houses)
    neptune_house = get_planet_house(western.neptune_degree, western.houses)
    
    # Helper to check ZWDS stars in specific palaces
    def find_palace(name_query: str) -> Dict[str, Any]:
        for palace in zwds.palaces:
            if name_query.lower() in palace.name.lower():
                return palace.model_dump()
        return {"name": "", "stem_branch": "", "stars": []}
        
    wealth_palace = find_palace("Wealth")
    career_palace = find_palace("Career")
    spouse_palace = find_palace("Spouse")
    friends_palace = find_palace("Friends")
    health_palace = find_palace("Health")
    
    # 3. Cross-System Risk Matrix Evaluation
    
    # Risk 1: Wealth Bottleneck
    # Western: Saturn in 2nd/10th house OR Saturn square Midheaven
    saturn_sq_mc = any(
        (a.planet1 in ("Saturn", "Midheaven") and a.planet2 in ("Saturn", "Midheaven") and a.aspect_type == "square")
        for a in aspects
    )
    west_wealth_trigger = (saturn_house in (2, 10)) or saturn_sq_mc
    # ZWDS: Hua-Ji in Wealth or Career palace
    zwds_wealth_trigger = ("Hua-Ji" in wealth_palace["stars"]) or ("Hua-Ji" in career_palace["stars"])
    
    critical_bottleneck = False
    if west_wealth_trigger and zwds_wealth_trigger:
        critical_bottleneck = True
        # Hard-code friction_index to >= 0.90 if trigger is met
        friction_index = max(friction_index, 0.90)
        
    # Risk 2: Interpersonal Risk
    # Western: Mars/Pluto Opposition and one inside the 7th house
    mars_opp_pluto = any(
        (a.planet1 in ("Mars", "Pluto") and a.planet2 in ("Mars", "Pluto") and a.aspect_type == "opposition")
        for a in aspects
    )
    west_interpersonal_trigger = mars_opp_pluto and (7 in (mars_house, pluto_house))
    # ZWDS: Hua-Ji in Spouse or Friends palace
    zwds_interpersonal_trigger = ("Hua-Ji" in spouse_palace["stars"]) or ("Hua-Ji" in friends_palace["stars"])
    
    interpersonal_risk = False
    if west_interpersonal_trigger and zwds_interpersonal_trigger:
        interpersonal_risk = True
        
    # Risk 3: Systemic Exhaustion
    # Western: Moon/Neptune hard aspect (conjunction, square, opposition) inside 6th/12th house
    moon_neptune_hard = any(
        (a.planet1 in ("Moon", "Neptune") and a.planet2 in ("Moon", "Neptune") and a.aspect_type in ("conjunction", "square", "opposition"))
        for a in aspects
    )
    west_exhaustion_trigger = moon_neptune_hard and any(h in (6, 12) for h in (moon_house, neptune_house))
    # ZWDS: Main star in Health Palace contains "Xian" or "Dim"
    zwds_exhaustion_trigger = any(
        ("xian" in star.lower() or "dim" in star.lower())
        for star in health_palace["stars"]
    )
    
    systemic_exhaustion = False
    if west_exhaustion_trigger and zwds_exhaustion_trigger:
        systemic_exhaustion = True

    # 4. Generate Synthesis Notes & Metadata
    synthesis_notes = []
    
    if target_vector == "wealth":
        synthesis_notes.append("Analyzing wealth flow. Cross-referencing Saturn position with ZWDS Wealth & Career Palaces.")
        if critical_bottleneck:
            synthesis_notes.append("CRITICAL WEALTH BOTTLENECK: Saturn blocking houses + ZWDS Hua-Ji active. Action required.")
    elif target_vector == "affinity":
        synthesis_notes.append("Evaluating relational affinity. Scanning Mars/Pluto opposition and Spouse/Friends ZWDS configuration.")
        if interpersonal_risk:
            synthesis_notes.append("INTERPERSONAL RISK DETECTED: routing query through legal/betrayal diagnostic vector.")
    elif target_vector == "vitality":
        synthesis_notes.append("Assessing core vitality matrix. Scanned Moon/Neptune hard aspects and Health Palace stars.")
        if systemic_exhaustion:
            synthesis_notes.append("SYSTEMIC EXHAUSTION TRIGGERED: Appending structural warning flags to downstream prompt.")
    elif target_vector == "macro_evolution":
        synthesis_notes.append("Analyzing long-term evolutionary path. Midheaven and Sun placements are prioritized.")
        
    if critical_bottleneck:
        synthesis_notes.append("[Flag: critical_bottleneck=True]")
    if interpersonal_risk:
        synthesis_notes.append("[Flag: interpersonal_risk=True]")
    if systemic_exhaustion:
        synthesis_notes.append("[Flag: systemic_exhaustion=True]")

    if not friction_points:
        friction_points.append("No major friction aspects (squares or oppositions) detected.")
        if not synthesis_notes:
            synthesis_notes.append("Harmonious baseline configurations.")
            
    # Check if the coordinates or parameters are near branch boundary
    # We set dual_matrix_indicator if branch boundary anomaly is detected (handled at main level)
    
    target_palace_name = VECTOR_TO_PALACE.get(target_vector, "Life")
    palace_friction = calculate_palace_friction_index(zwds, target_palace_name)
    detected_pats = detect_zwds_patterns(zwds)

    return SynthesisFlags(
        friction_index=round(friction_index, 2),
        friction_points=friction_points,
        aspects=aspects,
        synthesis_notes=synthesis_notes,
        dual_matrix_indicator=False, # Set downstream in main.py
        critical_bottleneck=critical_bottleneck,
        interpersonal_risk=interpersonal_risk,
        systemic_exhaustion=systemic_exhaustion,
        palace_friction_index=palace_friction,
        detected_patterns=detected_pats
    )
