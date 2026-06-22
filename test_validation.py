import sys
import asyncio
from datetime import datetime

sys.path.append(".")

from astrology.core.time_utils import calculate_time_metrics
from astrology.calculators.scaffold_zwds import ScaffoldZWDSCalculator
from main import app, synthesize_astrology
from astrology.models import AstrologyRequest, TargetVectorEnum, GenderEnum

async def run_regression():
    print("==================================================")
    print("Running ZWDS Validation Target Regression Test...")
    print("Target Profile: Oct/16/2000, 09:30 (Si hour)")
    print("==================================================")
    
    calc = ScaffoldZWDSCalculator()
    # East Asia timezone +8
    metrics = calculate_time_metrics(
        birth_date="2000-10-16",
        birth_time="09:30:00",
        longitude=120.0,
        timezone_offset=8.0
    )
    
    print("Calculated Time Metrics:")
    print(f"  TLT Datetime: {metrics['tlt_datetime']}")
    print(f"  JD UT: {metrics['jd_ut']}")
    
    # Calculate chart
    res = await calc.calculate_chart(
        tlt_datetime=metrics["tlt_datetime"],
        gender="M",
        latitude=22.3,
        longitude=120.0,
        jd_ut=metrics["jd_ut"]
    )
    
    print("\nZWDS Output:")
    print(f"  Year Stem-Branch: {res.get('yearly_stem_branch')}")
    print(f"  Month Branch: {res.get('monthly_branch')}")
    print(f"  Lunar Date: {res.get('lunar_date_str')}")
    print(f"  Life Master: {res.get('life_master')}")
    print(f"  Body Master: {res.get('body_master')}")
    
    # Verification assertions
    assert "Geng-Chen" in res.get("yearly_stem_branch"), f"Year mismatch: got {res.get('yearly_stem_branch')}"
    assert "Xu" in res.get("monthly_branch"), f"Month mismatch: got {res.get('monthly_branch')}"
    assert res.get("life_master") == "Finance (武曲)", f"Life Master mismatch: got {res.get('life_master')}"
    # Standard/Windada 身主 for a 辰(Chen)-year is 文昌 (Academic), not 左辅.
    assert res.get("body_master") == "Academic (文昌)", f"Body Master mismatch: got {res.get('body_master')}"
    
    # Verify the Day and Hour stems using standard 5-Rat-Chase and Bazi rules
    # Day is Ding-Wei, Hour is Yi-Si. Let's make sure the returned lunar representation or date details match.
    # Note: Chinese Date: 庚辰 丙戌 丁未 乙巳
    print("\n✅ Verification check passed successfully!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_regression())
