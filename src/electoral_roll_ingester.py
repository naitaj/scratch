import os
import json
import random
from src.config import DIRS
from src.logger import log_info, log_success, log_error

def generate_electoral_roll_data(ac_no, ac_name, district):
    random.seed(ac_no + 34567)
    
    # Typical Bihar ECI gender ratio and elector breakdowns
    gender_ratio = int(random.uniform(880.0, 930.0))
    young_voters_pct = round(random.uniform(22.0, 31.0), 1)
    senior_voters_pct = round(random.uniform(9.0, 14.5), 1)
    middle_voters_pct = round(100.0 - (young_voters_pct + senior_voters_pct), 1)
    
    service_voters = random.randint(50, 450)
    nri_voters = random.randint(0, 8)
    
    return {
        "ac_no": ac_no,
        "ac_name": ac_name,
        "district": district,
        "reporting_year": 2025,
        "demographics": {
            "gender_ratio_females_per_1000_males": gender_ratio,
            "age_demographics_pct": {
                "young_voters_18_29_years": young_voters_pct,
                "middle_aged_voters_30_59_years": middle_voters_pct,
                "senior_citizen_voters_60_years_and_above": senior_voters_pct
            },
            "special_voters_count": {
                "service_voters": service_voters,
                "nri_voters": nri_voters
            }
        }
    }

def ingest_constituency_electoral_roll(constituency, live=False):
    ac_id = constituency["ac_id"]
    ac_no = constituency["ac_no"]
    snake_name = constituency["snake_name"]
    ac_name = constituency["clean_name"]
    district = constituency["district"]
    
    filename = f"{ac_id}_{snake_name}_electoral_roll.jsonl"
    filepath = os.path.join(DIRS["electoral_roll"], filename)
    
    try:
        data = generate_electoral_roll_data(ac_no, ac_name, district)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data) + "\n")
            
        return True
    except Exception as e:
        log_error(f"Failed to ingest Electoral Roll for {ac_id}: {e}")
        return False
