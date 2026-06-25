import os
import json
import random
from src.config import DIRS
from src.logger import log_info, log_success, log_error

def generate_infrastructure_data(ac_no, ac_name, district):
    random.seed(ac_no + 56789)
    
    road_connectivity = round(random.uniform(78.0, 94.5), 1)
    unconnected_habitations = random.randint(5, 45)
    secondary_school_access = round(random.uniform(62.0, 88.0), 1)
    phc_coverage_ratio_pct = round(random.uniform(70.0, 92.5), 1)
    
    return {
        "ac_no": ac_no,
        "ac_name": ac_name,
        "district": district,
        "reporting_period": "2024-2025",
        "infrastructure_stats": {
            "rural_road_connectivity_rate_pmgsy_pct": road_connectivity,
            "unconnected_habitations_count": unconnected_habitations,
            "villages_with_secondary_school_access_pct": secondary_school_access,
            "primary_health_center_phc_coverage_ratio_pct": phc_coverage_ratio_pct
        }
    }

def ingest_constituency_infrastructure(constituency, live=False):
    ac_id = constituency["ac_id"]
    ac_no = constituency["ac_no"]
    snake_name = constituency["snake_name"]
    ac_name = constituency["clean_name"]
    district = constituency["district"]
    
    filename = f"{ac_id}_{snake_name}_infrastructure.jsonl"
    filepath = os.path.join(DIRS["infrastructure"], filename)
    
    try:
        data = generate_infrastructure_data(ac_no, ac_name, district)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data) + "\n")
            
        return True
    except Exception as e:
        log_error(f"Failed to ingest Infrastructure for {ac_id}: {e}")
        return False
