import os
from typing import Dict, Any
import swisseph as swe

class WesternAstrologyCalculator:
    """
    Calculates Western astrology parameters (Sun, Moon, Ascendant, Midheaven, houses)
    using the localized Swiss Ephemeris library.
    """
    
    def __init__(self, ephe_path: str = None):
        if ephe_path:
            swe.set_ephe_path(ephe_path)
        elif "SE_PATH" in os.environ:
            swe.set_ephe_path(os.environ["SE_PATH"])
            
    def calculate_positions(
        self,
        jd_ut: float,
        latitude: float,
        longitude: float,
        house_system: str = "P"
    ) -> Dict[str, Any]:
        hsys_bytes = house_system.encode("utf-8") if isinstance(house_system, str) else house_system
        
        sun_data, _ = swe.calc_ut(jd_ut, swe.SUN)
        sun_deg = sun_data[0]
        
        moon_data, _ = swe.calc_ut(jd_ut, swe.MOON)
        moon_deg = moon_data[0]
        
        saturn_data, _ = swe.calc_ut(jd_ut, swe.SATURN)
        saturn_deg = saturn_data[0]
        
        mars_data, _ = swe.calc_ut(jd_ut, swe.MARS)
        mars_deg = mars_data[0]
        
        neptune_data, _ = swe.calc_ut(jd_ut, swe.NEPTUNE)
        neptune_deg = neptune_data[0]
        
        pluto_data, _ = swe.calc_ut(jd_ut, swe.PLUTO)
        pluto_deg = pluto_data[0]
        
        cusps, ascmc = swe.houses(jd_ut, latitude, longitude, hsys_bytes)
        asc_deg = ascmc[0]
        mc_deg = ascmc[1]
        
        house_cusps = {i + 1: cusps[i] for i in range(len(cusps))}
        
        return {
            "sun_degree": sun_deg,
            "moon_degree": moon_deg,
            "ascendant_degree": asc_deg,
            "midheaven_degree": mc_deg,
            "saturn_degree": saturn_deg,
            "mars_degree": mars_deg,
            "neptune_degree": neptune_deg,
            "pluto_degree": pluto_deg,
            "houses": house_cusps
        }
