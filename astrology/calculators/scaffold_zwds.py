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
        
        # Context-Aware Borrowing: Reduce brightness if borrowed
        if s.get("is_borrowed", False):
            if brightness == "Radiant":
                brightness = "Neutral"
        
        info = STAR_MAPPING.get(name, {"name": name, "classification": "Benefic", "archetype": ""})
        metadata.append({
            "name": name,
            "brightness_index": brightness,
            "classification": info["classification"],
            "archetype_definition": info["archetype"],
            "is_borrowed": s.get("is_borrowed", False),
            "mutagen": s.get("mutagen", None)
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


# ── Chinese -> project-alias translation tables ──────────────────────────
# Same correspondence the reference repo (Renhuai123/ziwei-doushu) relies on,
# i.e. iztro's Chinese star names mapped to this project's English aliases.
_STEM_CN2PY = {"甲": "Jia", "乙": "Yi", "丙": "Bing", "丁": "Ding", "戊": "Wu",
               "己": "Ji", "庚": "Geng", "辛": "Xin", "壬": "Ren", "癸": "Gui"}
_BRANCH_CN2PY = {"子": "Zi", "丑": "Chou", "寅": "Yin", "卯": "Mao", "辰": "Chen",
                 "巳": "Si", "午": "Wu", "未": "Wei", "申": "Shen", "酉": "You",
                 "戌": "Xu", "亥": "Hai"}
_PALACE_CN2EN = {
    "命宫": "Life Palace (命宮)", "兄弟": "Siblings Palace (兄弟)",
    "夫妻": "Marriage Palace (夫妻)", "子女": "Child Palace (子女)",
    "财帛": "Wealth Palace (財帛)", "疾厄": "Health Palace (疾厄)",
    "迁移": "Travel Palace (遷移)", "仆役": "Friends Palace (交友)",
    "官禄": "Career Palace (官祿)", "田宅": "Property Palace (田宅)",
    "福德": "Happy Palace (福德)", "父母": "Parents Palace (父母)",
}
_STAR_CN2EN = {
    "紫微": "Emperor", "天府": "Heavenly Mansion", "天机": "Advisor",
    "太阳": "Sun", "太阴": "Moon", "武曲": "Finance", "天同": "Mascot",
    "廉贞": "Justice", "贪狼": "Flirt", "巨门": "Advocate", "天梁": "Blessing",
    "七杀": "Marshal", "破军": "Pioneer", "天相": "Minister",
    "左辅": "Intellect", "右弼": "Right Assist", "文曲": "Arts",
    "文昌": "Academic", "禄存": "Wealth Star", "天魁": "Status", "天钺": "Grace",
    "擎羊": "Sternness", "陀罗": "Obstacle", "地空": "Void", "地劫": "Exhaust",
    "孤辰": "Gu Chen", "天空": "Tian Kong", "天巫": "Tian Wu",
    "火星": "Fire Star", "铃星": "Bell Star", "天马": "Tian Ma",
    "天喜": "Tian Xi", "天姚": "Tian Yao", "天刑": "Tian Xing",
    "红鸾": "Red Phoenix", "咸池": "Peach Blossom", "天才": "Genius",
    "天寿": "Longevity", "天官": "Tian Guan", "天福": "Tian Fu Aux",
    "天德": "Tian De", "月德": "Yue De", "天贵": "Tian Gui",
    "天月": "Tian Yue Aux", "天哭": "Tian Ku", "天虚": "Tian Xu",
    "龙池": "Dragon Pool", "凤阁": "Phoenix Pavilion", "台辅": "Tai Fu",
    "封诰": "Feng Gao", "三台": "San Tai", "八座": "Ba Zuo", "恩光": "En Guang",
    "天伤": "Tian Shang", "天使": "Tian Shi", "解神": "Jie Shen",
    "华盖": "Hua Gai", "截路": "Jie Lu", "蜚廉": "Fei Lian", "年解": "Nian Jie",
    "寡宿": "Gua Su", "破碎": "Po Sui", "阴煞": "Yin Sha", "旬空": "Xun Kong",
    "空亡": "Kong Wang", "天厨": "Tian Chu",
}
_BRIGHTNESS_CN2EN = {"庙": "Radiant", "旺": "Radiant", "得": "Neutral",
                     "利": "Neutral", "平": "Neutral", "不": "Dark", "陷": "Dark"}
_MUTAGEN_CN2EN = {"禄": "Hua Lu", "权": "Hua Quan", "科": "Hua Ke", "忌": "Hua Ji"}
_CHANGSHENG_CN2EN = {
    "长生": "Birth", "沐浴": "Bath", "冠带": "Youth", "临官": "Arrive",
    "帝旺": "Imperial", "衰": "Decay", "病": "Sickness", "死": "Death",
    "墓": "Grave", "绝": "Cut", "胎": "Tomb", "养": "Exhaust",
}
_BOSHI_CN2EN = {
    "博士": "Scholar", "力士": "Strength", "青龙": "Dragon", "小耗": "Small Loss",
    "将军": "General", "奏书": "Memorial", "飞廉": "Fei Lian", "喜神": "Joy",
    "病符": "Sickness God", "大耗": "Big Loss", "伏兵": "Ambush", "官府": "Officer",
}
_BUREAU_CN2EN = {"水二局": "Water 2", "木三局": "Wood 3", "金四局": "Metal 4",
                 "土五局": "Earth 5", "火六局": "Fire 6"}


def _zh(cn: str) -> str:
    """Format a Chinese star/bureau name as 'English (中文)'."""
    return f"{_STAR_CN2EN.get(cn, cn)} ({cn})"


_CN_DIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
             "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def _cn_month(m: str) -> int:
    m = m.replace("正", "一")
    if m == "十":
        return 10
    if m.startswith("十"):
        return 10 + _CN_DIGIT.get(m[1], 0)
    return _CN_DIGIT.get(m, 0)


def _cn_day(d: str) -> int:
    if d.startswith("初"):
        return _CN_DIGIT.get(d[1], 0)
    if d in ("二十",):
        return 20
    if d.startswith("廿"):
        return 20 + (_CN_DIGIT.get(d[1], 0) if len(d) > 1 else 0)
    if d in ("三十", "卅"):
        return 30
    if d == "十":
        return 10
    if d.startswith("十"):
        return 10 + _CN_DIGIT.get(d[1], 0)
    return _CN_DIGIT.get(d, 0)


def _lunar_to_english(cn_lunar: str) -> str:
    """Convert iztro's Chinese lunar date (e.g. '二〇〇〇年九月十九') to English."""
    try:
        year_part, rest = cn_lunar.split("年")
        year = int("".join(str(_CN_DIGIT[c]) for c in year_part))
        leap = "闰" in rest
        rest = rest.replace("闰", "")
        month_part, day_part = rest.split("月")
        return (f"Lunar {year}, {'leap ' if leap else ''}"
                f"Month {_cn_month(month_part)}, Day {_cn_day(day_part)}")
    except Exception:
        return cn_lunar


class ScaffoldZWDSCalculator(AbstractZWDSCalculator):
    """
    Concrete ZWDS calculator backed by ``py-iztro`` (the Python binding of the
    iztro engine — https://github.com/SylarLong/iztro).

    The reference implementation the project is validated against
    (Renhuai123/ziwei-doushu) delegates its entire chart computation to iztro,
    so this calculator does the same and then maps iztro's authoritative output
    (star positions, brightness, four transformations, masters, bureau, decadal
    limits, 长生/博士 cycles, 小限) into this project's ZWDSMatrix schema.

    No hardcoded chart datasets, per-profile overrides, or Node subprocess.
    """

    def __init__(self) -> None:
        from py_iztro import Astro  # imported lazily so import errors are clear
        self._astro = Astro()

    async def calculate_chart(
        self,
        tlt_datetime: datetime,
        gender: str = "M",
        latitude: float = 0.0,
        longitude: float = 0.0,
        **kwargs: Any
    ) -> Dict[str, Any]:
        astro = self._resolve_astro(tlt_datetime, gender, kwargs.get("time_index"))

        palaces = [self._build_palace(p) for p in astro.palaces]
        self._apply_borrowing(palaces)

        for palace in palaces:
            has_ji = (
                any(s.get("mutagen") == "Hua Ji" for s in palace["main_stars"])
                or "Hua Ji" in palace["minor_stars"]
            )
            palace["intensity"] = 0.8 if has_ji else 1.0
            palace["stars_metadata"] = build_stars_metadata(palace)

        # year / month pillars from iztro's "庚辰 丙戌 丁未 乙巳" ganzhi string.
        parts = (astro.chinese_date or "").split()

        def pillar(token: str) -> str:
            if len(token) >= 2:
                return f"{_STEM_CN2PY.get(token[0], token[0])}-{_BRANCH_CN2PY.get(token[1], token[1])}"
            return token

        return {
            "palaces": palaces,
            "yearly_stem_branch": pillar(parts[0]) if parts else "",
            "monthly_branch": pillar(parts[1]) if len(parts) > 1 else "",
            "lunar_date_str": _lunar_to_english(astro.lunar_date),
            "life_master": _zh(astro.soul),
            "body_master": _zh(astro.body),
            "bureau": f"{_BUREAU_CN2EN.get(astro.five_elements_class, astro.five_elements_class)} ({astro.five_elements_class})",
        }

    def _resolve_astro(self, tlt_datetime: datetime, gender: str, time_index=None):
        # iztro time index: 0..11 for 子..亥, 12 for late-Zi (23:00-23:59).
        # If the caller supplies an explicit branch (time_index) — e.g. the one
        # the frontend already resolved for the on-screen chart — use it so the
        # AI reads the SAME chart the user sees (single source of truth).
        if time_index is None:
            hour = tlt_datetime.hour
            time_index = 12 if hour == 23 else (hour + 1) // 2
        gender_cn = "女" if gender.upper().startswith("F") else "男"
        solar_date = tlt_datetime.strftime("%Y-%m-%d")
        return self._astro.by_solar(solar_date, time_index, gender_cn, True, "zh-CN")

    async def compute_horoscope(
        self,
        tlt_datetime: datetime,
        target_date: str,
        gender: str = "M",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Compute the 大限/流年/流月/流日 (decadal / yearly / monthly / daily)
        transits for ``target_date`` against this natal chart.

        The key signal for event reconstruction is each scope's 四化 (Si-Hua):
        the four stars that turn Lu/Quan/Ke/Ji that period and the natal palace
        they fall on. Names are translated to the project's English aliases.
        """
        astro = self._resolve_astro(tlt_datetime, gender, kwargs.get("time_index"))
        h = astro.horoscope(target_date)

        # natal branch -> natal palace name, so we can say which life domain a
        # transit 命宮 / 四化 activates.
        natal = self._build_natal_index(astro)

        def gz(scope) -> str:
            return (f"{_STEM_CN2PY.get(scope.heavenly_stem, scope.heavenly_stem)}-"
                    f"{_BRANCH_CN2PY.get(scope.earthly_branch, scope.earthly_branch)}")

        def mutagen(scope) -> Dict[str, str]:
            # iztro mutagen list is ordered [Lu, Quan, Ke, Ji].
            labels = ["Hua Lu", "Hua Quan", "Hua Ke", "Hua Ji"]
            out = {}
            for label, cn in zip(labels, list(getattr(scope, "mutagen", []) or [])):
                out[label] = _STAR_CN2EN.get(cn, cn)
            return out

        def life_palace(scope) -> str:
            branch = _BRANCH_CN2PY.get(scope.earthly_branch, scope.earthly_branch)
            return natal.get(branch, "")

        def scope_block(scope) -> Dict[str, Any]:
            if scope is None:
                return {}
            block = {
                "stem_branch": gz(scope),
                "transit_life_palace_over_natal": life_palace(scope),
                "mutagen": mutagen(scope),
            }
            rng = getattr(scope, "range", None)
            if rng:
                block["decadal_range"] = f"{rng[0]}–{rng[1]}"
            return block

        return {
            "target_date": target_date,
            "decadal": scope_block(getattr(h, "decadal", None)),
            "yearly": scope_block(getattr(h, "yearly", None)),
            "monthly": scope_block(getattr(h, "monthly", None)),
            "daily": scope_block(getattr(h, "daily", None)),
        }

    @staticmethod
    def _build_natal_index(astro: Any) -> Dict[str, str]:
        """Map each natal earthly-branch (Pinyin) to its palace English name."""
        index = {}
        for p in astro.palaces:
            branch = _BRANCH_CN2PY.get(p.earthly_branch, p.earthly_branch)
            index[branch] = _PALACE_CN2EN.get(p.name, p.name)
        return index

    # -- helpers ----------------------------------------------------------
    def _build_palace(self, p: Any) -> Dict[str, Any]:
        stem = _STEM_CN2PY.get(p.heavenly_stem, p.heavenly_stem)
        branch = _BRANCH_CN2PY.get(p.earthly_branch, p.earthly_branch)

        main_stars, minor_stars, stars = [], [], []

        for s in (p.major_stars or []):
            name = _STAR_CN2EN.get(s.name, s.name)
            status = _BRIGHTNESS_CN2EN.get(s.brightness, "Neutral")
            mutagen = _MUTAGEN_CN2EN.get(s.mutagen) if s.mutagen else None
            main_stars.append({
                "name": name, "status": status,
                "is_borrowed": False, "mutagen": mutagen,
            })
            stars.append(f"{name}({status})")
            if mutagen:
                minor_stars.append(mutagen)
                stars.append(mutagen)

        for s in list(p.minor_stars or []) + list(p.adjective_stars or []):
            name = _STAR_CN2EN.get(s.name, s.name)
            minor_stars.append(name)
            stars.append(name)
            mut = _MUTAGEN_CN2EN.get(getattr(s, "mutagen", "") or "")
            if mut:
                minor_stars.append(mut)
                stars.append(mut)

        rng = getattr(p.decadal, "range", None)
        ages = list(getattr(p, "ages", []) or [])
        return {
            "name": _PALACE_CN2EN.get(p.name, p.name),
            "stem_branch": f"{stem}-{branch}",
            "stars": stars,
            "decadal_range": f"{rng[0]}–{rng[1]}" if rng else "",
            "main_stars": main_stars,
            "minor_stars": minor_stars,
            "changsheng": _CHANGSHENG_CN2EN.get(p.changsheng12, p.changsheng12 or ""),
            "pillar_gods": [_BOSHI_CN2EN.get(p.boshi12, p.boshi12)] if p.boshi12 else [],
            "one_year_luck": ", ".join(str(a) for a in ages[:7]),
            "intensity": 1.0,
            "_branch": branch,  # transient key for borrowing; removed below
        }

    def _apply_borrowing(self, palaces: list) -> None:
        """Empty palaces (no major star) borrow the opposite axis (branch+6).
        Borrowed stars inherit the source mutagen; a borrowed Radiant star is
        reduced to Neutral. This also prevents the frontend from falling back
        to its hardcoded star list for empty palaces."""
        order = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei",
                 "Shen", "You", "Xu", "Hai"]
        by_branch_idx = {b: i for i, b in enumerate(order)}
        branch_to_palace = {p["_branch"]: p for p in palaces}

        for p in palaces:
            if p["main_stars"]:
                continue
            opp_branch = order[(by_branch_idx[p["_branch"]] + 6) % 12]
            source = branch_to_palace.get(opp_branch)
            if not source:
                continue
            for s in source["main_stars"]:
                status = "Neutral" if s["status"] == "Radiant" else s["status"]
                p["main_stars"].append({
                    "name": s["name"], "status": status,
                    "is_borrowed": True, "mutagen": s.get("mutagen"),
                })
                p["stars"].append(f"{s['name']}({status})")
                if s.get("mutagen"):
                    p["minor_stars"].append(s["mutagen"])
                    p["stars"].append(s["mutagen"])

        for p in palaces:
            p.pop("_branch", None)
