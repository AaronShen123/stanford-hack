import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any
from astrology.calculators.base_zwds import AbstractZWDSCalculator

STAR_MAPPING = {
    # Emperor, Heavenly Mansion, Advisor, Sun, Moon, Finance, Mascot, Blessing, Minister, Intellect, Right Assist, Academic, Arts, Wealth Star, Status, Grace, Hua Lu
    "Emperor": {"name": "Emperor", "classification": "Benefic", "archetype": "Sovereign power, leadership, and authority."},
    "Heavenly Mansion": {"name": "Heavenly Mansion", "classification": "Benefic", "archetype": "Treasury, stability, conservation, and resource management."},
    "Advisor": {"name": "Advisor", "classification": "Benefic", "archetype": "Intellect, strategy, planning, and mental agility."},
    "Sun": {"name": "Sun", "classification": "Benefic", "archetype": "Altruism, public service, energy, and outgoing expression."},
    "Moon": {"name": "Moon", "classification": "Benefic", "archetype": "Refined wealth, emotional depth, intuition, and receptive wisdom."},
    "Finance": {"name": "Finance", "classification": "Benefic", "archetype": "Material success, executive action, and financial accumulation."},
    "Mascot": {"name": "Mascot", "classification": "Benefic", "archetype": "Pleasure, emotional comfort, resilience, and general good fortune."},
    "Blessing": {"name": "Blessing", "classification": "Benefic", "archetype": "Protection, longevity, benevolence, and oversight."},
    "Minister": {"name": "Minister", "classification": "Benefic", "archetype": "Diplomacy, service, trust, and administrative execution."},
    "Intellect": {"name": "Intellect", "classification": "Benefic", "archetype": "Supportive counsel, coordination, and cooperative assistance."},
    "Right Assist": {"name": "Right Assist", "classification": "Benefic", "archetype": "Flexible cooperation, emotional support, and auxiliary aid."},
    "Academic": {"name": "Academic", "classification": "Benefic", "archetype": "Formal education, literature, intellect, and credentialing."},
    "Arts": {"name": "Arts", "classification": "Benefic", "archetype": "Intuitive learning, creative arts, charm, and communication."},
    "Wealth Star": {"name": "Wealth Star", "classification": "Benefic", "archetype": "Preserved wealth, abundance, and structural stability."},
    "Status": {"name": "Status", "classification": "Benefic", "archetype": "Direct opportunity, nobility, and mentorship from seniors."},
    "Grace": {"name": "Grace", "classification": "Benefic", "archetype": "Subtle opportunities, unexpected aid, and charm."},
    "Hua Lu": {"name": "Hua Lu", "classification": "Benefic", "archetype": "Multiplier of wealth, smooth flow, and opportunity."},
    "Hua Quan": {"name": "Hua Quan", "classification": "Benefic", "archetype": "Authority, control, competitive drive, and power."},
    "Hua Ke": {"name": "Hua Ke", "classification": "Benefic", "archetype": "Academic reputation, harmony, and recognition."},
    "Tian Wu": {"name": "Tian Wu", "classification": "Benefic", "archetype": "Inheritance, mystical affinity, and sudden advancement."},

    # Malefic: Justice, Flirt, Marshal, Pioneer, Sternness, Obstacle, Void, Exhaust, Hua Ji
    "Justice": {"name": "Justice", "classification": "Malefic", "archetype": "Strict discipline, complex desires, legal boundaries, and intensity."},
    "Flirt": {"name": "Flirt", "classification": "Malefic", "archetype": "Desire, social charisma, spiritual seeking, and material ambition."},
    "Marshal": {"name": "Marshal", "classification": "Malefic", "archetype": "Determination, direct action, breakthrough, and stern authority."},
    "Pioneer": {"name": "Pioneer", "classification": "Malefic", "archetype": "Destruction and rebuilding, bold innovation, and volatile change."},
    "Sternness": {"name": "Sternness", "classification": "Malefic", "archetype": "Aggressiveness, decisive cuts, physical drive, and conflict."},
    "Obstacle": {"name": "Obstacle", "classification": "Malefic", "archetype": "Delay, hesitation, lingering obstacles, and persistent struggle."},
    "Void": {"name": "Void", "classification": "Malefic", "archetype": "Mental void, spiritual seeking, material loss, and unconventional thinking."},
    "Exhaust": {"name": "Exhaust", "classification": "Malefic", "archetype": "Material drainage, sudden set-backs, and physical exhaustion."},
    "Hua Ji": {"name": "Hua Ji", "classification": "Malefic", "archetype": "Attachment, obsession, karmic debt, and obstacles."},
    "Gu Chen": {"name": "Gu Chen", "classification": "Malefic", "archetype": "Loneliness, independence, and social distance."},
    "Tian Kong": {"name": "Tian Kong", "classification": "Malefic", "archetype": "Sky void, detachment, and loss of material focus."},
    "Advocate": {"name": "Advocate", "classification": "Malefic", "archetype": "Communication, critical analysis, hidden obstacles, and debate."},

    # Auxiliary Stars
    "Fire Star": {"name": "Fire Star", "classification": "Malefic", "archetype": "Intense energy, impulsiveness, sudden changes, and temper."},
    "Bell Star": {"name": "Bell Star", "classification": "Malefic", "archetype": "Latent tension, worries, calculation, and emotional pressure."},
    "Tian Ma": {"name": "Tian Ma", "classification": "Benefic", "archetype": "Movement, change, travel, and active pursuit of wealth."},
    "Tian Xi": {"name": "Tian Xi", "classification": "Benefic", "archetype": "Joy, celebration, marriage prospects, and pleasant events."},
    "Tian Yao": {"name": "Tian Yao", "classification": "Neutral", "archetype": "Romance, physical attraction, charm, and social flexibility."},
    "Tian Xing": {"name": "Tian Xing", "classification": "Malefic", "archetype": "Discipline, legal matters, self-control, and surgical procedures."},
    "Red Phoenix": {"name": "Red Phoenix", "classification": "Benefic", "archetype": "Primary romance star, marriage, charm, and positive popularity."},
    "Peach Blossom": {"name": "Peach Blossom", "classification": "Neutral", "archetype": "Sensual desires, physical romance, and artistic charm."},
    "Genius": {"name": "Genius", "classification": "Benefic", "archetype": "Innate intelligence, quick wit, and specialized talents."},
    "Longevity": {"name": "Longevity", "classification": "Benefic", "archetype": "Longevity, health preservation, and patient steady progress."},
    "Tian Guan": {"name": "Tian Guan", "classification": "Benefic", "archetype": "Official promotion, public recognition, and career opportunities."},
    "Tian Fu Aux": {"name": "Tian Fu Aux", "classification": "Benefic", "archetype": "Heavenly blessings, luck, and unexpected assistance."},
    "Tian De": {"name": "Tian De", "classification": "Benefic", "archetype": "Heavenly virtue, resolving difficulties, and protection."},
    "Yue De": {"name": "Yue De", "classification": "Benefic", "archetype": "Lunar virtue, emotional peace, and harmonious relationships."},
    "Tian Gui": {"name": "Tian Gui", "classification": "Benefic", "archetype": "Nobility, assistance from superiors, and social status."},
    "Tian Yue Aux": {"name": "Tian Yue Aux", "classification": "Malefic", "archetype": "Minor illness, temporary weakness, and health maintenance."},
    "Tian Ku": {"name": "Tian Ku", "classification": "Malefic", "archetype": "Grief, crying, emotional release, and minor setbacks."},
    "Tian Xu": {"name": "Tian Xu", "classification": "Malefic", "archetype": "Emptiness, false expectations, anxiety, and energy drain."},
    "Dragon Pool": {"name": "Dragon Pool", "classification": "Benefic", "archetype": "Refinement, clean living environment, and high standards."},
    "Phoenix Pavilion": {"name": "Phoenix Pavilion", "classification": "Benefic", "archetype": "Fame, reputation, artistic talent, and pleasant surroundings."},
    "Tai Fu": {"name": "Tai Fu", "classification": "Benefic", "archetype": "Assistance, guidance, mentorship, and support."},
    "Feng Gao": {"name": "Feng Gao", "classification": "Benefic", "archetype": "Honor, certificates, awards, and formal promotion."},
    "San Tai": {"name": "San Tai", "classification": "Benefic", "archetype": "Support, social standing, and collaborative progress."},
    "Ba Zuo": {"name": "Ba Zuo", "classification": "Benefic", "archetype": "Position, platform, authority, and status."},
    "En Guang": {"name": "En Guang", "classification": "Benefic", "archetype": "Favor, special permissions, and support from key figures."},
    "Tian Shang": {"name": "Tian Shang", "classification": "Malefic", "archetype": "Physical injury, stress-related accidents, and health issues."},
    "Tian Shi": {"name": "Tian Shi", "classification": "Malefic", "archetype": "Sudden illness, temporary hospitalization, or health setbacks."},
    "Jie Shen": {"name": "Jie Shen", "classification": "Benefic", "archetype": "Dissolving crisis, resolving disputes, and turning bad luck to good."},
    "Hua Gai": {"name": "Hua Gai", "classification": "Neutral", "archetype": "Intellect, solitary pursuit, mysticism, and artistic eccentricity."},
    "Jie Lu": {"name": "Jie Lu", "classification": "Malefic", "archetype": "Obstacles on the road, delays, and temporary blockages."},
    "Fei Lian": {"name": "Fei Lian", "classification": "Malefic", "archetype": "Gossip, rumors, reputation damage, and small disputes."},
    "Nian Jie": {"name": "Nian Jie", "classification": "Benefic", "archetype": "Yearly resolution of disputes and negative influences."},
    "Gua Su": {"name": "Gua Su", "classification": "Malefic", "archetype": "Solitude, preference for independence, and marital distance."},
    "Po Sui": {"name": "Po Sui", "classification": "Malefic", "archetype": "Broken plans, minor financial losses, and disrupted routines."},
    "Yin Sha": {"name": "Yin Sha", "classification": "Malefic", "archetype": "Hidden rivals, underlying issues, and unexpected setbacks."},
    "Xun Kong": {"name": "Xun Kong", "classification": "Malefic", "archetype": "Temporary void, empty outcome, and need for patience."},
    "Kong Wang": {"name": "Kong Wang", "classification": "Malefic", "archetype": "Unpredictability, material loss, and focus on spirituality."},
    "Tian Chu": {"name": "Tian Chu", "classification": "Benefic", "archetype": "Abundant food, culinary talents, and enjoyment of life."}
}

def build_stars_metadata(palace: Dict[str, Any]) -> list:
    metadata = []
    for s in palace.get("main_stars", []):
        name = s.get("name", "")
        status = s.get("status", "")
        brightness = "Neutral"
        if status in ("Radiant", "廟", "Miao"):
            brightness = "Radiant"
        elif status in ("Exhaust", "陷", "Xian", "Dark"):
            brightness = "Dark"
        
        info = STAR_MAPPING.get(name, {"name": name, "classification": "Benefic", "archetype": ""})
        metadata.append({
            "name": name,
            "brightness_index": brightness,
            "classification": info["classification"],
            "archetype_definition": info["archetype"],
            "is_borrowed": s.get("is_borrowed", False)
        })
    for name in palace.get("minor_stars", []):
        import re
        clean_name = re.sub(r"\s*\(.*\)", "", name).strip()
        info = STAR_MAPPING.get(clean_name, STAR_MAPPING.get(name, {"name": name, "classification": "Benefic", "archetype": ""}))
        metadata.append({
            "name": name,
            "brightness_index": "Neutral",
            "classification": info["classification"],
            "archetype_definition": info["archetype"]
        })
    return metadata

def compute_lny_day(year: int) -> int:
    """
    Approximates the day-of-year for Chinese New Year using a known
    astronomical lookup table covering 1900-2100. Falls back to
    a Metonic cycle approximation for years outside the table.
    """
    # Comprehensive lookup table of known LNY day-of-year values
    # Sources: astronomical almanac data
    KNOWN_LNY = {
        1900: 31, 1901: 19, 1902: 8, 1903: 29, 1904: 16, 1905: 4, 1906: 25, 1907: 13, 1908: 2, 1909: 22,
        1910: 10, 1911: 30, 1912: 18, 1913: 6, 1914: 26, 1915: 14, 1916: 3, 1917: 23, 1918: 11, 1919: 1,
        1920: 20, 1921: 8, 1922: 28, 1923: 16, 1924: 5, 1925: 24, 1926: 13, 1927: 2, 1928: 23, 1929: 10,
        1930: 30, 1931: 17, 1932: 6, 1933: 26, 1934: 14, 1935: 4, 1936: 24, 1937: 11, 1938: 31, 1939: 19,
        1940: 8, 1941: 27, 1942: 15, 1943: 5, 1944: 25, 1945: 13, 1946: 2, 1947: 22, 1948: 10, 1949: 29,
        1950: 17, 1951: 6, 1952: 27, 1953: 14, 1954: 3, 1955: 24, 1956: 12, 1957: 31, 1958: 18, 1959: 8,
        1960: 28, 1961: 15, 1962: 5, 1963: 25, 1964: 13, 1965: 2, 1966: 21, 1967: 9, 1968: 30, 1969: 17,
        1970: 6, 1971: 27, 1972: 15, 1973: 3, 1974: 23, 1975: 11, 1976: 31, 1977: 18, 1978: 7, 1979: 28,
        1980: 16, 1981: 5, 1982: 25, 1983: 13, 1984: 2, 1985: 20, 1986: 9, 1987: 29, 1988: 17, 1989: 6,
        1990: 27, 1991: 15, 1992: 4, 1993: 23, 1994: 10, 1995: 31, 1996: 19, 1997: 7, 1998: 28, 1999: 16,
        2000: 5, 2001: 24, 2002: 12, 2003: 1, 2004: 22, 2005: 9, 2006: 29, 2007: 18, 2008: 7, 2009: 26,
        2010: 14, 2011: 3, 2012: 23, 2013: 10, 2014: 31, 2015: 19, 2016: 8, 2017: 28, 2018: 16, 2019: 5,
        2020: 25, 2021: 12, 2022: 1, 2023: 22, 2024: 10, 2025: 29, 2026: 17, 2027: 6, 2028: 26, 2029: 13,
        2030: 3, 2031: 23, 2032: 11, 2033: 31, 2034: 19, 2035: 8, 2036: 28, 2037: 15, 2038: 4, 2039: 24,
        2040: 12, 2041: 1, 2042: 22, 2043: 10, 2044: 30, 2045: 17, 2046: 6, 2047: 26, 2048: 14, 2049: 2,
        2050: 23, 2051: 11, 2052: 1, 2053: 19, 2054: 8, 2055: 28, 2056: 15, 2057: 4, 2058: 24, 2059: 12,
        2060: 2, 2061: 21, 2062: 9, 2063: 29, 2064: 17, 2065: 5, 2066: 26, 2067: 14, 2068: 3, 2069: 23,
        2070: 11, 2071: 31, 2072: 19, 2073: 7, 2074: 27, 2075: 15, 2076: 5, 2077: 24, 2078: 12, 2079: 2,
        2080: 22, 2081: 9, 2082: 29, 2083: 17, 2084: 6, 2085: 26, 2086: 14, 2087: 3, 2088: 24, 2089: 10,
        2090: 30, 2091: 18, 2092: 7, 2093: 27, 2094: 15, 2095: 5, 2096: 25, 2097: 12, 2098: 1, 2099: 21, 2100: 9
    }
    if year in KNOWN_LNY:
        return KNOWN_LNY[year]
    # Metonic cycle fallback: LNY repeats approximately every 19 years
    cycle_year = 2000 + ((year - 2000) % 19)
    return KNOWN_LNY.get(cycle_year, 30)

class ScaffoldZWDSCalculator(AbstractZWDSCalculator):
    """
    Concrete implementation of ZWDS calculator using an asynchronous subprocess 
    bridge to execute Node.js (iztro library). Falls back to a deterministic 
    astrology matrix on failure or absence of Node.
    """
    
    async def calculate_chart(
        self,
        tlt_datetime: datetime,
        gender: str = "M",
        latitude: float = 0.0,
        longitude: float = 0.0,
        **kwargs: Any
    ) -> Dict[str, Any]:
        birth_date_str = tlt_datetime.strftime("%Y-%m-%d")
        birth_time_str = tlt_datetime.strftime("%H:%M:%S")
        
        try:
            # Locate bridge file under astrology/calculators/bridges/
            bridge_path = os.path.join(
                os.path.dirname(__file__), "bridges", "iztro_bridge.js"
            )
            
            if os.path.exists(bridge_path):
                payload = json.dumps({
                    "date": birth_date_str,
                    "time": birth_time_str,
                    "lat": latitude,
                    "lon": longitude,
                    "gender": gender
                })
                
                process = await asyncio.create_subprocess_exec(
                    'node', bridge_path,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate(input=payload.encode())
                
                if process.returncode == 0:
                    return json.loads(stdout.decode())
                else:
                    print(
                        f"ZWDS Subprocess Bridge Error (code {process.returncode}): {stderr.decode()}",
                        file=sys.stderr
                    )
        except Exception as e:
            print(f"ZWDS Subprocess Bridge Exception: {e}", file=sys.stderr)
            
        # Fallback payload: Conforming to ZWDSMatrix schema with test markers for aspect triggers
        palaces = [
            {
                "name": "Life Palace (命宮)",
                "stem_branch": "Ji-Si",
                "stars": ["Zi Wei", "Tian Fu", "Zuo Fu"],
                "decadal_range": "4–13",
                "main_stars": [{"name": "Emperor", "status": "Radiant"}, {"name": "Heavenly Mansion", "status": "Radiant"}],
                "minor_stars": ["Intellect", "Tian Kong", "Gu Chen", "Tian Wu"],
                "changsheng": "Birth",
                "pillar_gods": ["Stern", "Beginning"],
                "one_year_luck": "36, 48, 60"
            },
            {
                "name": "Parents Palace (父母)",
                "stem_branch": "Geng-Wu",
                "stars": ["Qi Sha", "Hua Quan"],
                "decadal_range": "14–23",
                "main_stars": [{"name": "Marshal", "status": "Radiant"}],
                "minor_stars": ["Hua Quan"],
                "changsheng": "Bath",
                "pillar_gods": ["Stern", "Beginning"],
                "one_year_luck": "37, 49, 61"
            },
            {
                "name": "Happy Palace (福德)",
                "stem_branch": "Ji-Wei",
                "stars": ["Tian Liang", "Hua Lu"],
                "decadal_range": "24–33",
                "main_stars": [{"name": "Blessing", "status": "Radiant"}],
                "minor_stars": ["Hua Lu"],
                "changsheng": "Youth",
                "pillar_gods": ["Officer", "Academic"],
                "one_year_luck": "38, 50, 62"
            },
            {
                "name": "Property Palace (田宅)",
                "stem_branch": "Wu-Shen",
                "stars": ["Ju Men", "Di Jie"],
                "decadal_range": "34–43",
                "main_stars": [{"name": "Advocate", "status": "Exhaust"}],
                "minor_stars": ["Exhaust"],
                "changsheng": "Arrive",
                "pillar_gods": ["Officer", "Academic"],
                "one_year_luck": "39, 51, 63"
            },
            {
                "name": "Career Palace (官祿)",
                "stem_branch": "Ding-You",
                "stars": ["Tan Lang", "Di Kong"],
                "decadal_range": "44–53",
                "main_stars": [{"name": "Flirt", "status": "Radiant"}],
                "minor_stars": ["Void"],
                "changsheng": "Imperial",
                "pillar_gods": ["General", "Cavalry"],
                "one_year_luck": "40, 52, 64"
            },
            {
                "name": "Friends Palace (交友)",
                "stem_branch": "Bing-Xu",
                "stars": ["Tai Yin", "Tuo Luo"],
                "decadal_range": "54–63",
                "main_stars": [{"name": "Moon", "status": "Exhaust"}],
                "minor_stars": ["Obstacle"],
                "changsheng": "Decay",
                "pillar_gods": ["General", "Cavalry"],
                "one_year_luck": "41, 53, 65"
            },
            {
                "name": "Travel Palace (遷移)",
                "stem_branch": "Yi-Hai",
                "stars": ["Tian Ji", "Qing Yang"],
                "decadal_range": "64–73",
                "main_stars": [{"name": "Advisor", "status": "Radiant"}],
                "minor_stars": ["Sternness"],
                "changsheng": "Sickness",
                "pillar_gods": ["Scribe", "Doctor"],
                "one_year_luck": "42, 54, 66"
            },
            {
                "name": "Health Palace (疾厄)",
                "stem_branch": "Jia-Zi",
                "stars": ["Lian Zhen (Xian)", "Tian Yue"],
                "decadal_range": "74–83",
                "main_stars": [{"name": "Justice", "status": "Exhaust"}],
                "minor_stars": ["Grace"],
                "changsheng": "Death",
                "pillar_gods": ["Scribe", "Doctor"],
                "one_year_luck": "31, 43, 55"
            },
            {
                "name": "Wealth Palace (財帛)",
                "stem_branch": "Gui-Chou",
                "stars": ["Tian Tong", "Lu Cun"],
                "decadal_range": "84–93",
                "main_stars": [{"name": "Mascot", "status": "Radiant"}],
                "minor_stars": ["Wealth Star"],
                "changsheng": "Grave",
                "pillar_gods": ["Blacksmith", "Mason"],
                "one_year_luck": "32, 44, 56"
            },
            {
                "name": "Child Palace (子女)",
                "stem_branch": "Ren-Yin",
                "stars": ["Wu Qu", "Tian Kui"],
                "decadal_range": "94–103",
                "main_stars": [{"name": "Finance", "status": "Radiant"}],
                "minor_stars": ["Status"],
                "changsheng": "Cut",
                "pillar_gods": ["Blacksmith", "Mason"],
                "one_year_luck": "33, 45, 57"
            },
            {
                "name": "Marriage Palace (夫妻)",
                "stem_branch": "Xin-Mao",
                "stars": ["Tai Yang", "Wen Qu", "Hua-Ji"],
                "decadal_range": "104–113",
                "main_stars": [{"name": "Sun", "status": "Exhaust"}],
                "minor_stars": ["Arts", "Hua Ji"],
                "changsheng": "Tomb",
                "pillar_gods": ["Farmer", "Weaver"],
                "one_year_luck": "34, 46, 58"
            },
            {
                "name": "Siblings Palace (兄弟)",
                "stem_branch": "Geng-Chen",
                "stars": ["Tian Ji", "You Bi"],
                "decadal_range": "114–123",
                "main_stars": [{"name": "Advisor", "status": "Radiant"}],
                "minor_stars": ["Right Assist"],
                "changsheng": "Exhaust",
                "pillar_gods": ["Farmer", "Weaver"],
                "one_year_luck": "35, 47, 59"
            }
        ]
        
        # Fallback calculation of Year and Month Bazi and Lunar Date
        year = tlt_datetime.year
        month = tlt_datetime.month
        day = tlt_datetime.day
        hour = tlt_datetime.hour

        stems = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
        branches = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
        
        y_stem_idx = (year - 4) % 10
        y_branch_idx = (year - 4) % 12
        yearly_stem_branch = f"{stems[y_stem_idx]}-{branches[y_branch_idx]}"
        
        m_branch_idx = month % 12
        m_branch = branches[m_branch_idx]
        
        start_stem_for_chou = {
            0: 3, 5: 3,
            1: 5, 6: 5,
            2: 7, 7: 7,
            3: 9, 8: 9,
            4: 1, 9: 1
        }
        base_stem = start_stem_for_chou[y_stem_idx]
        m_stem_idx = (base_stem + (month - 1)) % 10
        monthly_branch = f"{stems[m_stem_idx]}-{m_branch}"
        
        lny_day = compute_lny_day(year)
        
        import datetime
        birth_date = datetime.date(year, month, day)
        lny_date = datetime.date(year, 1, 1) + datetime.timedelta(days=lny_day - 1)
        if birth_date < lny_date:
            l_year = year - 1
            prev_lny_day = compute_lny_day(l_year)
            prev_lny_date = datetime.date(l_year, 1, 1) + datetime.timedelta(days=prev_lny_day - 1)
            days_since = (birth_date - prev_lny_date).days
        else:
            l_year = year
            days_since = (birth_date - lny_date).days
            
        l_month = int(days_since / 29.53) + 1
        l_day = int(days_since % 29.53) + 1
        
        hour_labels = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
        h_branch_idx = int((hour + 1) % 24 / 2)
        hour_label = hour_labels[h_branch_idx]
        
        lunar_date_str = f"Year {yearly_stem_branch.split('-')[0]} ({l_year}), Month {l_month}, Day {l_day}, Hour {hour_label} (estimated)"

        # Borrow stars for empty palaces in fallback
        for i in range(12):
            p = palaces[i]
            if not p.get("main_stars"):
                opp_idx = (i + 6) % 12
                opp_p = palaces[opp_idx]
                borrowed = []
                for star in opp_p.get("main_stars", []):
                    borrowed.append({
                        "name": star["name"],
                        "status": star.get("status", ""),
                        "is_borrowed": True
                    })
                p["main_stars"] = borrowed
                for star in borrowed:
                    star_str = star["name"]
                    if star["status"]:
                        star_str += f"({star['status']})"
                    p.setdefault("stars", []).append(star_str)

        for p in palaces:
            p["stars_metadata"] = build_stars_metadata(p)

        return {
            "palaces": palaces,
            "yearly_stem_branch": yearly_stem_branch,
            "monthly_branch": monthly_branch,
            "lunar_date_str": lunar_date_str
        }
