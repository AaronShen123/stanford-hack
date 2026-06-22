import sys
import asyncio
from datetime import datetime

sys.path.append(".")

from astrology.core.time_utils import calculate_time_metrics
from astrology.calculators.scaffold_zwds import ScaffoldZWDSCalculator
from main import app, synthesize_astrology
from astrology.models import AstrologyRequest, TargetVectorEnum, GenderEnum

async def test_astral_engine():
    print("==================================================")
    print("Running ZWDS Engine Logic Validation...")
    print("Target Profile: Oct/16/2000, Si (巳)")
    print("==================================================")
    
    # 1. Compute time metrics
    metrics = calculate_time_metrics(
        birth_date="2000-10-16",
        birth_time="Si",
        longitude=120.0,
        timezone_offset=8.0
    )
    
    calc = ScaffoldZWDSCalculator()
    res = await calc.calculate_chart(
        tlt_datetime=metrics["tlt_datetime"],
        gender="M",
        latitude=22.3,
        longitude=120.0,
        jd_ut=metrics["jd_ut"]
    )
    
    print("\nCalculated Chart Stems & Branches:")
    print(f"  Year Stem-Branch: {res.get('yearly_stem_branch')}")
    print(f"  Month Branch: {res.get('monthly_branch')}")
    print(f"  Lunar Date: {res.get('lunar_date_str')}")
    print(f"  Life Master: {res.get('life_master')}")
    print(f"  Body Master: {res.get('body_master')}")
    
    # Assertions
    # Life Master == 'Finance' (Wu Qu)
    assert "Finance" in res.get("life_master"), f"Life Master expected Finance, got {res.get('life_master')}"
    
    # Body Master: check for Academic (standard ZWDS) or Intellect (requested prompt check)
    body_master = res.get("body_master", "")
    assert "Academic" in body_master or "Intellect" in body_master, f"Body Master expected Academic or Intellect, got {body_master}"
    
    print("\n✅ test_astral_engine verification completed successfully!")
    print("==================================================")

if __name__ == "__main__":
    try:
        asyncio.run(test_astral_engine())
    except AssertionError as e:
        print(f"\n❌ DIVERGENCE DETECTED: {e}")
        print("Stopping the rendering process.")
        sys.exit(1)
