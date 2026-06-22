from datetime import datetime, timedelta
import swisseph as swe

def calculate_time_metrics(
    birth_date: str,
    birth_time: str,
    longitude: float,
    timezone_offset: float = None
) -> dict:
    """
    Calculates LMT (Local Mean Time), TLT (True Local Time / Local Apparent Time),
    UTC datetime, and astronomical Julian Days (UT and ET).
    
    If timezone_offset is not provided, it is approximated from the longitude.
    """
    branch_time_map = {
        "Zi": "00:00:00",
        "Chou": "02:00:00",
        "Yin": "04:00:00",
        "Mao": "06:00:00",
        "Chen": "08:00:00",
        "Si": "10:00:00",
        "Wu": "12:00:00",
        "Wei": "14:00:00",
        "Shen": "16:00:00",
        "You": "18:00:00",
        "Xu": "20:00:00",
        "Hai": "22:00:00",
    }
    resolved_time = branch_time_map.get(birth_time, birth_time)
    local_dt = datetime.strptime(f"{birth_date} {resolved_time}", "%Y-%m-%d %H:%M:%S")
    
    if timezone_offset is None:
        timezone_offset = float(round(longitude / 15.0))
        
    utc_dt = local_dt - timedelta(hours=timezone_offset)
    
    utc_hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd_ut = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_hour_decimal
    )
    
    lmt_offset_seconds = longitude * 240.0
    lmt_dt = utc_dt + timedelta(seconds=lmt_offset_seconds)
    
    eot_days = swe.time_equ(jd_ut)
    eot_seconds = eot_days * 86400.0
    
    tlt_dt = lmt_dt + timedelta(seconds=eot_seconds)
    
    delta_t = swe.deltat(jd_ut)
    jd_et = jd_ut + delta_t
    
    # Check if the birth time is within 60 seconds of a branch boundary (odd hours)
    branch_boundary_anomaly = check_branch_boundary_anomaly(tlt_dt)
    
    return {
        "local_datetime": local_dt,
        "utc_datetime": utc_dt,
        "lmt_datetime": lmt_dt,
        "tlt_datetime": tlt_dt,
        "timezone_offset": timezone_offset,
        "jd_ut": jd_ut,
        "jd_et": jd_et,
        "eot_seconds": eot_seconds,
        "branch_boundary_anomaly": branch_boundary_anomaly
    }

def check_branch_boundary_anomaly(tlt_dt: datetime) -> bool:
    """
    Checks if the True Local Time (TLT) falls within a 60-second window
    of any Earthly Branch boundary (odd hours: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23).
    """
    tlt_seconds = tlt_dt.hour * 3600 + tlt_dt.minute * 60 + tlt_dt.second + tlt_dt.microsecond / 1_000_000.0
    for boundary_hour in range(1, 24, 2):
        boundary_seconds = boundary_hour * 3600
        if abs(tlt_seconds - boundary_seconds) <= 60.0:
            return True
    return False
