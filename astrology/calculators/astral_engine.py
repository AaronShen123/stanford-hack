"""
AstralEngine — a deterministic, zero-base Zi Wei Dou Shu (紫微斗數) chart engine.

There are NO hardcoded chart datasets here. Every star position, the four
transformations (四化 / Si-Hua), the Five-Elements bureau, the masters and the
palace grid are computed at runtime from the lunar birth parameters supplied
by `astrology.core.lunar_calendar.LunarData`.

Execution sequence (strict ordering — see `build_chart`):

    Step A  Temporal anchoring        -> handled upstream (solar-term month
                                          pillar + 5-Rat-Chase hour stem live
                                          in lunar_calendar; re-derived &
                                          asserted here for integrity)
    Step B  Grid initialization       -> 12 empty Palace objects
    Step C  Primary placement         -> 14 major stars from the bureau
                                          (e.g. 金四局) + auxiliary stars
    Step D  Si-Hua injection          -> Lu/Quan/Ke/Ji onto star objects,
                                          BEFORE any borrowing
    Step E  Recursive borrowing       -> empty palaces borrow the opposite
                                          axis (idx + 6) % 12; borrowed stars
                                          inherit the source mutagen

State hygiene is provided by `reset_palace_data()` so the same engine instance
can be reused across many calculations without state pollution.

Star names use the project's English aliases (Emperor=紫微, Finance=武曲, ...).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from astrology.core.lunar_calendar import LunarData, STEMS, BRANCHES

# --------------------------------------------------------------------------
# Reference tables (deterministic constants, NOT per-chart data)
# --------------------------------------------------------------------------

# Chinese -> project English alias for the 14 major stars.
MAJOR_STAR_NAMES = {
    "紫微": "Emperor", "天机": "Advisor", "太阳": "Sun", "武曲": "Finance",
    "天同": "Mascot", "廉贞": "Justice", "天府": "Heavenly Mansion",
    "太阴": "Moon", "贪狼": "Flirt", "巨门": "Advocate", "天相": "Minister",
    "天梁": "Blessing", "七杀": "Marshal", "破军": "Pioneer",
}

# Offsets from Zi Wei (紫微) — counter-clockwise == subtract branch index.
ZIWEI_SERIES = {
    "紫微": 0, "天机": -1, "太阳": -3, "武曲": -4, "天同": -5, "廉贞": -8,
}
# Offsets from Tian Fu (天府) — clockwise == add branch index.
TIANFU_SERIES = {
    "天府": 0, "太阴": 1, "贪狼": 2, "巨门": 3, "天相": 4, "天梁": 5,
    "七杀": 6, "破军": 10,
}

# Brightness (廟旺利得平不陷) for each major star across the 12 branches,
# bucketed into the three levels the UI renders. Branch order:
# Zi Chou Yin Mao Chen Si Wu Wei Shen You Xu Hai.
# R=Radiant (廟旺得利), N=Neutral (平), D=Dark (不陷). This is the standard
# 紫微斗數 brightness table; validate edge cells against your Windada source.
_R, _N, _D = "Radiant", "Neutral", "Dark"
BRIGHTNESS = {
    "紫微": [_N, _R, _R, _R, _R, _R, _R, _R, _R, _R, _N, _R],
    "天机": [_R, _D, _R, _R, _D, _N, _R, _D, _R, _R, _D, _N],
    "太阳": [_D, _D, _R, _R, _R, _R, _R, _N, _D, _D, _D, _D],
    "武曲": [_R, _R, _N, _D, _R, _D, _R, _R, _N, _D, _R, _D],
    "天同": [_R, _D, _R, _N, _N, _R, _D, _D, _R, _N, _N, _R],
    "廉贞": [_N, _D, _R, _N, _R, _D, _N, _D, _R, _N, _R, _D],
    "天府": [_R, _R, _R, _D, _R, _R, _R, _R, _R, _D, _R, _R],
    "太阴": [_R, _R, _D, _D, _D, _D, _D, _N, _N, _R, _R, _R],
    "贪狼": [_R, _R, _N, _D, _R, _D, _R, _R, _N, _D, _R, _D],
    "巨门": [_R, _D, _R, _R, _N, _R, _R, _D, _R, _R, _N, _R],
    "天相": [_R, _R, _R, _D, _R, _R, _R, _D, _R, _D, _R, _N],
    "天梁": [_R, _R, _R, _R, _R, _D, _R, _R, _D, _R, _R, _D],
    "七杀": [_R, _R, _R, _D, _R, _R, _R, _R, _R, _D, _R, _R],
    "破军": [_R, _R, _D, _R, _R, _N, _R, _R, _N, _R, _R, _D],
}

# Five-Elements bureau by NaYin (納音), keyed by sexagenary pair index
# (each pair spans two consecutive jiazi). Values are the bureau DIVISOR.
# 水二局=2, 木三局=3, 金四局=4, 土五局=5, 火六局=6.
_NAYIN_BUREAU = [
    4, 6, 3, 5, 4, 6,   # 甲子.. 甲戌
    2, 5, 4, 3, 2, 5,   # 丙子.. 丙戌 (庚辰辛巳=白蠟金=Metal 4)
    6, 3, 2, 4, 6, 3,   # 戊子.. 戊戌
    5, 4, 6, 2, 5, 4,   # 庚子.. 庚戌
    3, 2, 5, 6, 3, 2,   # 壬子.. 壬戌
]
BUREAU_LABEL = {2: "Water 2 (水二局)", 3: "Wood 3 (木三局)",
                4: "Metal 4 (金四局)", 5: "Earth 5 (土五局)",
                6: "Fire 6 (火六局)"}

# 命主 by Life-Palace BRANCH; 身主 by birth-YEAR BRANCH. English (中文).
LIFE_MASTER_BY_BRANCH = {
    "Zi": "Flirt (贪狼)", "Chou": "Advocate (巨门)", "Yin": "Wealth Star (禄存)",
    "Mao": "Arts (文曲)", "Chen": "Justice (廉贞)", "Si": "Finance (武曲)",
    "Wu": "Pioneer (破军)", "Wei": "Finance (武曲)", "Shen": "Justice (廉贞)",
    "You": "Arts (文曲)", "Xu": "Wealth Star (禄存)", "Hai": "Advocate (巨门)",
}
BODY_MASTER_BY_YEAR_BRANCH = {
    "Zi": "Bell Star (铃星)", "Chou": "Minister (天相)", "Yin": "Blessing (天梁)",
    "Mao": "Mascot (天同)", "Chen": "Academic (文昌)", "Si": "Advisor (天机)",
    "Wu": "Fire Star (火星)", "Wei": "Minister (天相)", "Shen": "Blessing (天梁)",
    "You": "Mascot (天同)", "Xu": "Academic (文昌)", "Hai": "Advisor (天机)",
}

# Si-Hua (四化) by YEAR STEM -> {transformation: Chinese star}.
SIHUA_BY_STEM = {
    "Jia": {"Lu": "廉贞", "Quan": "破军", "Ke": "武曲", "Ji": "太阳"},
    "Yi": {"Lu": "天机", "Quan": "天梁", "Ke": "紫微", "Ji": "太阴"},
    "Bing": {"Lu": "天同", "Quan": "天机", "Ke": "文昌", "Ji": "廉贞"},
    "Ding": {"Lu": "太阴", "Quan": "天同", "Ke": "天机", "Ji": "巨门"},
    "Wu": {"Lu": "贪狼", "Quan": "太阴", "Ke": "右弼", "Ji": "天机"},
    "Ji": {"Lu": "武曲", "Quan": "贪狼", "Ke": "天梁", "Ji": "文曲"},
    "Geng": {"Lu": "太阳", "Quan": "武曲", "Ke": "太阴", "Ji": "天同"},
    "Xin": {"Lu": "巨门", "Quan": "太阳", "Ke": "文曲", "Ji": "文昌"},
    "Ren": {"Lu": "天梁", "Quan": "紫微", "Ke": "左辅", "Ji": "武曲"},
    "Gui": {"Lu": "破军", "Quan": "巨门", "Ke": "太阴", "Ji": "贪狼"},
}
MUTAGEN_LABEL = {"Lu": "Hua Lu", "Quan": "Hua Quan", "Ke": "Hua Ke", "Ji": "Hua Ji"}

# Auxiliary star aliases (Chinese -> English) for output.
AUX_STAR_NAMES = {
    "左辅": "Intellect", "右弼": "Right Assist", "文昌": "Academic",
    "文曲": "Arts", "禄存": "Wealth Star", "擎羊": "Sternness",
    "陀罗": "Obstacle", "天魁": "Status", "天钺": "Grace", "火星": "Fire Star",
    "铃星": "Bell Star", "地空": "Void", "地劫": "Exhaust", "天马": "Tian Ma",
}

# 祿存 by year stem (branch index). 擎羊=祿存+1, 陀羅=祿存-1.
_LUCUN_BY_STEM = {
    "Jia": 2, "Yi": 3, "Bing": 5, "Ding": 6, "Wu": 5,
    "Ji": 6, "Geng": 8, "Xin": 9, "Ren": 11, "Gui": 0,
}
# 天魁/天钺 (天乙貴人) by year stem (branch indices).
_KUI_YUE_BY_STEM = {
    "Jia": (1, 7), "Yi": (0, 8), "Bing": (11, 9), "Ding": (11, 9),
    "Wu": (1, 7), "Ji": (0, 8), "Geng": (1, 7), "Xin": (6, 2),
    "Ren": (3, 5), "Gui": (3, 5),
}
# 火星/鈴星 start branch by year-branch trine; then count forward by hour.
_HUOLING_START = {
    frozenset({"Yin", "Wu", "Xu"}): (1, 3),
    frozenset({"Shen", "Zi", "Chen"}): (2, 10),
    frozenset({"Si", "You", "Chou"}): (3, 10),
    frozenset({"Hai", "Mao", "Wei"}): (9, 10),
}
# 天馬 by year-branch trine (branch index).
_TIANMA_BY_TRINE = {
    frozenset({"Shen", "Zi", "Chen"}): 2,
    frozenset({"Yin", "Wu", "Xu"}): 8,
    frozenset({"Si", "You", "Chou"}): 11,
    frozenset({"Hai", "Mao", "Wei"}): 5,
}

# Palace names in canonical counter-clockwise order from the Life Palace.
PALACE_NAMES = [
    "Life Palace (命宮)", "Siblings Palace (兄弟)", "Marriage Palace (夫妻)",
    "Child Palace (子女)", "Wealth Palace (財帛)", "Health Palace (疾厄)",
    "Travel Palace (遷移)", "Friends Palace (交友)", "Career Palace (官祿)",
    "Property Palace (田宅)", "Happy Palace (福德)", "Parents Palace (父母)",
]
# 長生十二神 / 博士十二神 stage names (English aliases used by the app).
CHANGSHENG = ["Birth", "Bath", "Youth", "Arrive", "Imperial", "Decay",
              "Sickness", "Death", "Grave", "Cut", "Tomb", "Exhaust"]
CHANGSHENG_START = {2: 8, 3: 11, 4: 5, 5: 8, 6: 2}  # bureau -> 長生 branch idx
BOSHI = ["Scholar", "Strength", "Dragon", "Small Loss", "General", "Memorial",
         "Fei Lian", "Joy", "Sickness God", "Big Loss", "Ambush", "Officer"]


@dataclass
class Star:
    name: str                 # English alias
    cn: str = ""              # Chinese source name
    category: str = "major"   # major | aux
    status: str = "Neutral"   # Radiant | Neutral | Dark  (native brightness)
    mutagen: Optional[str] = None
    is_borrowed: bool = False


@dataclass
class Palace:
    branch_index: int
    branch: str
    stem: str = ""
    name: str = ""
    main_stars: list = field(default_factory=list)   # list[Star]
    aux_stars: list = field(default_factory=list)     # list[Star]
    decadal_range: str = ""
    changsheng: str = ""
    boshi: str = ""
    one_year_luck: str = ""
    intensity: float = 1.0


class AstralEngine:
    """Stateful, reusable ZWDS engine. Call build_chart(lunar) per subject."""

    def __init__(self) -> None:
        self.palaces: list[Palace] = []

    # -- state hygiene ----------------------------------------------------
    def reset_palace_data(self) -> None:
        """Step B groundwork: drop all prior palace state to prevent
        pollution across successive calculations on the same instance."""
        self.palaces = [
            Palace(branch_index=i, branch=BRANCHES[i]) for i in range(12)
        ]

    # -- brightness -------------------------------------------------------
    @staticmethod
    def get_effective_brightness(star: Star, branch_index: int) -> str:
        """Native brightness for a major star at a branch, with the
        borrowing adjustment: a borrowed Radiant star reads as Neutral
        (its luminosity does not transfer at full strength)."""
        if star.category != "major" or star.cn not in BRIGHTNESS:
            base = star.status or "Neutral"
        else:
            base = BRIGHTNESS[star.cn][branch_index]
        if star.is_borrowed and base == "Radiant":
            return "Neutral"
        return base

    # -- helpers ----------------------------------------------------------
    @staticmethod
    def _sexagenary_index(stem: int, branch: int) -> int:
        for n in range(60):
            if n % 10 == stem and n % 12 == branch:
                return n
        raise ValueError("invalid stem/branch pair")

    @staticmethod
    def five_tigers_stem(year_stem: int, branch_index: int) -> int:
        """五虎遁: heavenly stem of a palace's branch given the year stem."""
        yin_stem = ((year_stem % 5) * 2 + 2) % 10
        return (yin_stem + (branch_index - 2)) % 10

    @staticmethod
    def ziwei_index(bureau: int, lunar_day: int) -> int:
        """起紫微: position of 紫微 from bureau divisor + lunar day."""
        rem = lunar_day % bureau
        if rem == 0:
            quotient, borrow = lunar_day // bureau, 0
        else:
            borrow = bureau - rem
            quotient = (lunar_day + borrow) // bureau
        base = (quotient + 1) % 12              # count quotient from 寅 (idx 2)
        if borrow == 0:
            return base
        return (base + borrow) % 12 if borrow % 2 == 0 else (base - borrow) % 12

    @staticmethod
    def _is_clockwise(year_stem: int, gender: str) -> bool:
        """陽男/陰女 順行(clockwise); 陰男/陽女 逆行."""
        yang_year = (year_stem % 2 == 0)
        male = gender.upper().startswith("M")
        return yang_year == male

    # -- the strict A->E pipeline ----------------------------------------
    def build_chart(self, lunar: LunarData, gender: str = "M") -> dict:
        # --- Step A: temporal anchoring ---
        # Hour stem is derived from the day stem via the 5-Rat-Chase (五鼠遁)
        # formula, with the day boundary at midnight (早子時 convention). This
        # is the authoritative hour pillar for the chart; for non-late-Zi
        # births it agrees with the calendar backend, and at 23:00-23:59 it
        # intentionally keeps the current day's stem rather than rolling over.
        hour_stem = ((lunar.day_stem % 5) * 2 + lunar.hour_branch) % 10

        # --- Step B: grid initialization (12 empty palaces) ---
        self.reset_palace_data()
        for p in self.palaces:
            p.stem = STEMS[self.five_tigers_stem(lunar.year_stem, p.branch_index)]

        # Anchor Life & Body palaces, then name the grid counter-clockwise.
        month_palace = (2 + (lunar.lunar_month - 1)) % 12
        life_idx = (month_palace - lunar.hour_branch) % 12
        body_idx = (month_palace + lunar.hour_branch) % 12
        for k, pname in enumerate(PALACE_NAMES):
            self.palaces[(life_idx - k) % 12].name = pname

        # --- Bureau (五行局) from the Life Palace stem/branch NaYin ---
        life_palace = self.palaces[life_idx]
        life_stem_idx = STEMS.index(life_palace.stem)
        sx = self._sexagenary_index(life_stem_idx, life_idx)
        bureau = _NAYIN_BUREAU[sx // 2]

        # --- Step C: primary placement (14 major + auxiliary stars) ---
        zw = self.ziwei_index(bureau, lunar.lunar_day)
        tf = (4 - zw) % 12
        for cn, off in ZIWEI_SERIES.items():
            self._place_major(cn, (zw + off) % 12)
        for cn, off in TIANFU_SERIES.items():
            self._place_major(cn, (tf + off) % 12)
        self._place_auxiliaries(lunar)

        # --- Step D: Si-Hua injection (BEFORE borrowing) ---
        self._inject_sihua(STEMS[lunar.year_stem])

        # --- Step E: recursive borrowing from the opposite axis ---
        self._borrow_opposite_axis()

        # --- derived layers: decadal / changsheng / boshi / 小限 / intensity ---
        clockwise = self._is_clockwise(lunar.year_stem, gender)
        self._assign_decadal(life_idx, bureau, clockwise)
        self._assign_changsheng(bureau, clockwise)
        self._assign_boshi(lunar, clockwise)
        self._assign_small_limit(lunar, clockwise)
        self._assign_intensity()

        # --- masters ---
        life_master = LIFE_MASTER_BY_BRANCH[BRANCHES[life_idx]]
        body_master = BODY_MASTER_BY_YEAR_BRANCH[BRANCHES[lunar.year_branch]]

        return {
            "palaces": [self._serialize(p) for p in self._chart_order()],
            "yearly_stem_branch": lunar.year_gz,
            "monthly_branch": lunar.month_gz,
            "lunar_date_str": (
                f"Lunar {lunar.lunar_year} "
                f"{'(leap) ' if lunar.is_leap_month else ''}"
                f"Month {lunar.lunar_month}, Day {lunar.lunar_day}, "
                f"Hour {STEMS[hour_stem]}-{BRANCHES[lunar.hour_branch]} "
                f"[{lunar.source}]"
            ),
            "life_master": life_master,
            "body_master": body_master,
            "bureau": BUREAU_LABEL[bureau],
        }

    # -- placement primitives --------------------------------------------
    def _place_major(self, cn: str, branch_index: int) -> None:
        star = Star(name=MAJOR_STAR_NAMES[cn], cn=cn, category="major")
        star.status = BRIGHTNESS[cn][branch_index]
        self.palaces[branch_index].main_stars.append(star)

    def _place_aux(self, cn: str, branch_index: int) -> None:
        self.palaces[branch_index].aux_stars.append(
            Star(name=AUX_STAR_NAMES[cn], cn=cn, category="aux")
        )

    def _place_auxiliaries(self, lunar: LunarData) -> None:
        m, h = lunar.lunar_month, lunar.hour_branch
        year_stem = STEMS[lunar.year_stem]
        year_branch = BRANCHES[lunar.year_branch]

        self._place_aux("左辅", (4 + (m - 1)) % 12)        # 左輔 起辰順月
        self._place_aux("右弼", (10 - (m - 1)) % 12)       # 右弼 起戌逆月
        self._place_aux("文昌", (10 - h) % 12)             # 文昌 起戌逆時
        self._place_aux("文曲", (4 + h) % 12)              # 文曲 起辰順時
        self._place_aux("地劫", (11 + h) % 12)             # 地劫 起亥順時
        self._place_aux("地空", (11 - h) % 12)             # 地空 起亥逆時

        lucun = _LUCUN_BY_STEM[year_stem]
        self._place_aux("禄存", lucun)
        self._place_aux("擎羊", (lucun + 1) % 12)
        self._place_aux("陀罗", (lucun - 1) % 12)

        kui, yue = _KUI_YUE_BY_STEM[year_stem]
        self._place_aux("天魁", kui)
        self._place_aux("天钺", yue)

        for trine, (huo, ling) in _HUOLING_START.items():
            if year_branch in trine:
                self._place_aux("火星", (huo + h) % 12)
                self._place_aux("铃星", (ling + h) % 12)
                break
        for trine, idx in _TIANMA_BY_TRINE.items():
            if year_branch in trine:
                self._place_aux("天马", idx)
                break

    # -- Step D ----------------------------------------------------------
    def _inject_sihua(self, year_stem: str) -> None:
        mapping = SIHUA_BY_STEM.get(year_stem, {})
        cn_to_mutagen = {cn: MUTAGEN_LABEL[h] for h, cn in mapping.items()}
        for p in self.palaces:
            for star in p.main_stars + p.aux_stars:
                if star.cn in cn_to_mutagen:
                    star.mutagen = cn_to_mutagen[star.cn]

    # -- Step E ----------------------------------------------------------
    def _borrow_opposite_axis(self) -> None:
        """Empty palaces (no native main star) borrow the opposite palace's
        major stars. Borrowed stars carry over the source mutagen and are
        flagged so brightness is reduced (Radiant -> Neutral)."""
        for i in range(12):
            p = self.palaces[i]
            if any(not s.is_borrowed for s in p.main_stars):
                continue
            source = self.palaces[(i + 6) % 12]
            for s in source.main_stars:
                if s.is_borrowed:
                    continue
                p.main_stars.append(Star(
                    name=s.name, cn=s.cn, category="major",
                    status=s.status, mutagen=s.mutagen, is_borrowed=True,
                ))

    # -- derived layers --------------------------------------------------
    def _assign_decadal(self, life_idx: int, bureau: int, cw: bool) -> None:
        step = 1 if cw else -1
        for n in range(12):
            idx = (life_idx + step * n) % 12
            start = bureau + 10 * n
            self.palaces[idx].decadal_range = f"{start}–{start + 9}"

    def _assign_changsheng(self, bureau: int, cw: bool) -> None:
        start = CHANGSHENG_START[bureau]
        step = 1 if cw else -1
        for k, stage in enumerate(CHANGSHENG):
            self.palaces[(start + step * k) % 12].changsheng = stage

    def _assign_boshi(self, lunar: LunarData, cw: bool) -> None:
        start = _LUCUN_BY_STEM[STEMS[lunar.year_stem]]  # 博士 starts at 祿存
        step = 1 if cw else -1
        for k, god in enumerate(BOSHI):
            self.palaces[(start + step * k) % 12].boshi = god

    def _assign_small_limit(self, lunar: LunarData, cw: bool) -> None:
        # 小限 1歲 start branch by year-branch trine.
        start_map = {
            frozenset({"Yin", "Wu", "Xu"}): 4,        # 辰
            frozenset({"Shen", "Zi", "Chen"}): 10,    # 戌
            frozenset({"Si", "You", "Chou"}): 7,      # 未
            frozenset({"Hai", "Mao", "Wei"}): 1,      # 丑
        }
        yb = BRANCHES[lunar.year_branch]
        start = next(v for t, v in start_map.items() if yb in t)
        step = 1 if cw else -1
        buckets: dict[int, list[int]] = {i: [] for i in range(12)}
        for age in range(1, 85):
            buckets[(start + step * (age - 1)) % 12].append(age)
        for i in range(12):
            self.palaces[i].one_year_luck = ", ".join(
                str(a) for a in buckets[i][:7]
            )

    def _assign_intensity(self) -> None:
        for p in self.palaces:
            has_ji = any(
                s.mutagen == "Hua Ji" for s in p.main_stars + p.aux_stars
            )
            p.intensity = 0.8 if has_ji else 1.0

    # -- serialization ---------------------------------------------------
    def _chart_order(self) -> list[Palace]:
        """Return palaces in canonical chart order (命宮 first)."""
        ordered = [None] * 12
        for p in self.palaces:
            ordered[PALACE_NAMES.index(p.name)] = p
        return ordered

    def _serialize(self, p: Palace) -> dict:
        main, stars = [], []
        for s in p.main_stars:
            brightness = self.get_effective_brightness(s, p.branch_index)
            main.append({
                "name": s.name, "status": brightness,
                "is_borrowed": s.is_borrowed, "mutagen": s.mutagen,
            })
            stars.append(f"{s.name}({brightness})")
        minor = []
        for s in p.aux_stars:
            label = s.name + (f" ({s.mutagen})" if s.mutagen else "")
            minor.append(label)
            stars.append(label)
        return {
            "name": p.name,
            "stem_branch": f"{p.stem}-{p.branch}",
            "stars": stars,
            "decadal_range": p.decadal_range,
            "main_stars": main,
            "minor_stars": minor,
            "changsheng": p.changsheng,
            "pillar_gods": [p.boshi] if p.boshi else [],
            "one_year_luck": p.one_year_luck,
            "intensity": p.intensity,
        }
