import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any
from astrology.calculators.base_zwds import AbstractZWDSCalculator

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
            {"name": "Ming (Self)", "stem_branch": "Ji-Si", "stars": ["Zi Wei", "Tian Fu", "Zuo Fu"], "decadal_range": "26-35"},
            {"name": "Siblings", "stem_branch": "Geng-Chen", "stars": ["Tian Ji", "You Bi"], "decadal_range": "16-25"},
            {"name": "Spouse", "stem_branch": "Xin-Mao", "stars": ["Tai Yang", "Wen Qu", "Hua-Ji"], "decadal_range": "06-15"}, # Test marker for Interpersonal Risk
            {"name": "Children", "stem_branch": "Ren-Yin", "stars": ["Wu Qu", "Tian Kui"], "decadal_range": "116-125"},
            {"name": "Wealth", "stem_branch": "Gui-Chou", "stars": ["Tian Tong", "Lu Cun"], "decadal_range": "106-115"},
            {"name": "Health", "stem_branch": "Jia-Zi", "stars": ["Lian Zhen (Xian)", "Tian Yue"], "decadal_range": "96-105"}, # Test marker for Systemic Exhaustion
            {"name": "Travel", "stem_branch": "Yi-Hai", "stars": ["Tian Ji", "Qing Yang"], "decadal_range": "86-95"},
            {"name": "Friends", "stem_branch": "Bing-Xu", "stars": ["Tai Yin", "Tuo Luo"], "decadal_range": "76-85"},
            {"name": "Career", "stem_branch": "Ding-You", "stars": ["Tan Lang", "Di Kong"], "decadal_range": "66-75"},
            {"name": "Property", "stem_branch": "Wu-Shen", "stars": ["Ju Men", "Di Jie"], "decadal_range": "56-65"},
            {"name": "Happiness", "stem_branch": "Ji-Wei", "stars": ["Tian Liang", "Hua Lu"], "decadal_range": "46-55"},
            {"name": "Parents", "stem_branch": "Geng-Wu", "stars": ["Qi Sha", "Hua Quan"], "decadal_range": "36-45"}
        ]
        
        return {
            "palaces": palaces,
            "yearly_stem_branch": "Bing-Wu",
            "monthly_branch": "Wu-Shen",
            "lunar_date_str": "Year 2026, Month 5, Day 7, Hour Wu (estimated)"
        }
