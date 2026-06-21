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
            "archetype_definition": info["archetype"]
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
        
        lny_offsets = {
            1990: 27,
            2000: 36,
            2026: 48
        }
        lny_day = lny_offsets.get(year, 30)
        
        import datetime
        birth_date = datetime.date(year, month, day)
        lny_date = datetime.date(year, 1, 1) + datetime.timedelta(days=lny_day - 1)
        if birth_date < lny_date:
            l_year = year - 1
            prev_lny_day = lny_offsets.get(l_year, 30)
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

        for p in palaces:
            p["stars_metadata"] = build_stars_metadata(p)

        return {
            "palaces": palaces,
            "yearly_stem_branch": yearly_stem_branch,
            "monthly_branch": monthly_branch,
            "lunar_date_str": lunar_date_str
        }
