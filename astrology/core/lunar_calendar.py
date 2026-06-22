"""
Deterministic Chinese-calendar provider for the ZWDS engine.

This module is the ONLY place that converts a Gregorian/True-Local-Time
moment into the lunar + sexagenary data that Zi Wei Dou Shu needs. It does
NOT contain any chart logic — it purely answers "what is the lunar date and
the four ganzhi pillars for this instant?".

Accuracy strategy ("do all"): we try multiple authoritative backends in
priority order and use the first that is installed:

    1. sxtwl        -- 寿星天文历, astronomical solar-term + lunar conversion
    2. lunar_python -- pure-python port of the Lunar library

Both produce true solar-term month pillars (Step A: "do not use calendar
months") and correct lunar day (needed for exact Zi Wei placement). If
neither is importable we raise — we deliberately do NOT fall back to the old
29.53-day approximation, because an approximate lunar day silently corrupts
the entire chart.

Convention notes:
  * ZWDS changes the YEAR pillar at Lunar New Year (正月初一), not 立春. We
    therefore derive the year ganzhi from the *lunar year integer*, not from
    a solar-term-based year pillar.
  * The MONTH pillar is solar-term based (used for BaZi display); the lunar
    month *number* (used to anchor the Life/Body palaces) is separate and
    also returned.
  * Late-Zi (晚子時, 23:00-23:59) maps to branch 子 (index 0); day-pillar
    roll-over is delegated to the backend's hour handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
BRANCHES = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei",
            "Shen", "You", "Xu", "Hai"]

_GAN_CN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
_ZHI_CN = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


@dataclass
class LunarData:
    """Normalized calendar inputs consumed by AstralEngine."""
    lunar_year: int
    lunar_month: int          # 1..12, anchors Life/Body palace (Step B)
    lunar_day: int            # 1..30, drives Zi Wei placement (Step C)
    is_leap_month: bool

    year_stem: int            # index into STEMS / BRANCHES
    year_branch: int
    month_stem: int           # solar-term based (Step A)
    month_branch: int
    day_stem: int             # drives 5-Rat-Chase hour stem
    day_branch: int
    hour_stem: int
    hour_branch: int

    source: str

    @property
    def year_gz(self) -> str:
        return f"{STEMS[self.year_stem]}-{BRANCHES[self.year_branch]}"

    @property
    def month_gz(self) -> str:
        return f"{STEMS[self.month_stem]}-{BRANCHES[self.month_branch]}"

    @property
    def day_gz(self) -> str:
        return f"{STEMS[self.day_stem]}-{BRANCHES[self.day_branch]}"

    @property
    def hour_gz(self) -> str:
        return f"{STEMS[self.hour_stem]}-{BRANCHES[self.hour_branch]}"


def hour_to_branch_index(hour: int) -> int:
    """子=0 covers 23:00-00:59. ((hour + 1) // 2) % 12."""
    return ((hour + 1) // 2) % 12


def _from_sxtwl(dt: datetime) -> LunarData:
    import sxtwl
    day = sxtwl.fromSolar(dt.year, dt.month, dt.day)

    yg, mg, dg = day.getYearGZ(), day.getMonthGZ(), day.getDayGZ()
    hg = day.getHourGZ(dt.hour)

    lunar_year = day.getLunarYear()
    # ZWDS year boundary = Lunar New Year, so derive year ganzhi from the
    # lunar year integer rather than sxtwl's 立春-based getYearGZ.
    year_stem = (lunar_year - 4) % 10
    year_branch = (lunar_year - 4) % 12

    return LunarData(
        lunar_year=lunar_year,
        lunar_month=day.getLunarMonth(),
        lunar_day=day.getLunarDay(),
        is_leap_month=bool(day.isLunarLeap()),
        year_stem=year_stem,
        year_branch=year_branch,
        month_stem=mg.tg,
        month_branch=mg.dz,
        day_stem=dg.tg,
        day_branch=dg.dz,
        hour_stem=hg.tg,
        hour_branch=hg.dz,
        source="sxtwl",
    )


def _from_lunar_python(dt: datetime) -> LunarData:
    from lunar_python import Solar
    lunar = Solar.fromYmdHms(
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
    ).getLunar()

    lunar_year = lunar.getYear()
    year_stem = (lunar_year - 4) % 10
    year_branch = (lunar_year - 4) % 12

    def gz(gan_cn: str, zhi_cn: str) -> tuple[int, int]:
        return _GAN_CN.index(gan_cn), _ZHI_CN.index(zhi_cn)

    m_stem, m_branch = gz(lunar.getMonthGan(), lunar.getMonthZhi())
    d_stem, d_branch = gz(lunar.getDayGan(), lunar.getDayZhi())
    h_stem, h_branch = gz(lunar.getTimeGan(), lunar.getTimeZhi())

    month_raw = lunar.getMonth()  # negative => leap month
    return LunarData(
        lunar_year=lunar_year,
        lunar_month=abs(month_raw),
        lunar_day=lunar.getDay(),
        is_leap_month=month_raw < 0,
        year_stem=year_stem,
        year_branch=year_branch,
        month_stem=m_stem,
        month_branch=m_branch,
        day_stem=d_stem,
        day_branch=d_branch,
        hour_stem=h_stem,
        hour_branch=h_branch,
        source="lunar_python",
    )


_BACKENDS = (_from_sxtwl, _from_lunar_python)


def resolve_lunar_data(dt: datetime) -> LunarData:
    """Return LunarData for an instant using the first available backend."""
    errors = []
    for backend in _BACKENDS:
        try:
            return backend(dt)
        except ImportError as exc:
            errors.append(f"{backend.__name__}: not installed ({exc})")
        except Exception as exc:  # backend present but failed on this date
            errors.append(f"{backend.__name__}: {exc!r}")
    raise RuntimeError(
        "No Chinese-calendar backend available. Install one of: sxtwl, "
        "lunar_python. Details:\n  " + "\n  ".join(errors)
    )
