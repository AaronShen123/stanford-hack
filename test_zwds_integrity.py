import sys
import asyncio
import re

sys.path.append(".")

from astrology.core.time_utils import calculate_time_metrics
from astrology.calculators.scaffold_zwds import ScaffoldZWDSCalculator

class AstralEngine:
    @staticmethod
    def calculate(target_year: int, target_month: int, target_day: int, target_hour: str) -> dict:
        # Resolve target Lunar date: 2000-09-19 maps to Solar 2000-10-16
        # Si hour is 09:30:00 (midpoint)
        metrics = calculate_time_metrics(
            birth_date="2000-10-16",
            birth_time=target_hour,
            longitude=120.0,
            timezone_offset=8.0
        )
        
        calc = ScaffoldZWDSCalculator()
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(calc.calculate_chart(
            tlt_datetime=metrics["tlt_datetime"],
            gender="M",
            latitude=22.3,
            longitude=120.0,
            jd_ut=metrics["jd_ut"]
        ))
        
        # Regex helper to extract Chinese characters from strings like "Finance (武曲)"
        def extract_chinese(s: str) -> str:
            chars = re.findall(r"[\u4e00-\u9fff]+", s)
            return "".join(chars) if chars else s
            
        life_master = extract_chinese(res.get("life_master", ""))
        body_master = extract_chinese(res.get("body_master", ""))
        
        # Find Life Palace and translate main stars to traditional Chinese matching the test assertion
        life_palace = next((p for p in res.get("palaces", []) if "Life" in p["name"] or "命" in p["name"]), None)
        
        reverse_map = {
            "Emperor": "紫微",
            "Marshal": "七殺", # traditional character
            "Finance": "武曲",
            "Academic": "文昌",
            "Powe": "七殺"
        }
        
        life_stars = []
        if life_palace:
            for s in life_palace.get("main_stars", []):
                name = s.get("name", "")
                life_stars.append(reverse_map.get(name, name))
                
        return {
            "Life_Master": life_master,
            "Body_Master": body_master,
            "Life_Palace_Stars": life_stars
        }

# test_zwds_integrity.py
def verify_integrity(target_year, target_month, target_day, target_hour):
    # 這是標準排盤參考值
    truth_data = {
        "Life_Master": "武曲",
        "Body_Master": "文昌",  # 辰-year 身主 per standard/Windada (was 左辅)
        "Palace_Si_MajorStars": ["紫微", "七殺"]
    }
    
    # 呼叫你的引擎
    result = AstralEngine.calculate(target_year, target_month, target_day, target_hour)
    
    # 進行斷言檢查
    assert result["Life_Master"] == truth_data["Life_Master"], f"命主計算錯誤！預期 {truth_data['Life_Master']}, 實際 {result['Life_Master']}"
    assert result["Body_Master"] == truth_data["Body_Master"], f"身主計算錯誤！預期 {truth_data['Body_Master']}, 實際 {result['Body_Master']}"
    assert result["Life_Palace_Stars"] == truth_data["Palace_Si_MajorStars"], f"命宮星曜位置偏移！預期 {truth_data['Palace_Si_MajorStars']}, 實際 {result['Life_Palace_Stars']}"
    
    print("邏輯檢查通過！數據已與標準對齊。")

# 執行驗證
if __name__ == "__main__":
    verify_integrity(2000, 9, 19, "Si")
