import os
import json
import random
from src.config import DIRS
from src.logger import log_info, log_success, log_error

# High flood risk districts in Bihar: Supaul, Saharsa, Madhepura, Khagaria, Darbhanga, Madhubani, West Champaran, East Champaran
HIGH_RISK_DISTRICTS = [
    "supaul", "saharsa", "madhepura", "khagaria", "darbhanga", "madhubani", 
    "west champaran", "east champaran", "samastipur", "muzaffarpur", "gopalganj"
]

RIVER_BASINS = {
    "west champaran": "Gandak",
    "east champaran": "Burhi Gandak",
    "gopalganj": "Gandak",
    "supaul": "Kosi",
    "saharsa": "Kosi",
    "madhepura": "Kosi",
    "darbhanga": "Bagmati",
    "madhubani": "Kamala Balan",
    "khagaria": "Kosi / Ganges",
    "patna": "Ganges / Sone / Punpun",
    "bhojpur": "Sone",
    "rohtas": "Sone",
    "buxar": "Ganges",
    "bhagalpur": "Ganges"
}

def generate_flood_data(ac_no, ac_name, district):
    random.seed(ac_no + 67890)
    
    dist_lower = district.lower()
    river_basin = RIVER_BASINS.get(dist_lower, "Ganges" if random.choice([True, False]) else "None")
    
    if dist_lower in HIGH_RISK_DISTRICTS:
        risk_level = "High"
        inundation_pct = round(random.uniform(45.0, 85.0), 1)
    elif river_basin != "None":
        risk_level = "Medium"
        inundation_pct = round(random.uniform(15.0, 44.5), 1)
    else:
        risk_level = "Low"
        inundation_pct = round(random.uniform(0.5, 14.5), 1)
        
    return {
        "ac_no": ac_no,
        "ac_name": ac_name,
        "district": district,
        "assessment_year": 2025,
        "flood_vulnerability": {
            "risk_classification": risk_level,
            "associated_river_basin": river_basin,
            "estimated_inundation_prone_area_pct": inundation_pct
        }
    }

def ingest_constituency_flood(constituency, live=False):
    ac_id = constituency["ac_id"]
    ac_no = constituency["ac_no"]
    snake_name = constituency["snake_name"]
    ac_name = constituency["clean_name"]
    district = constituency["district"]
    
    filename = f"{ac_id}_{snake_name}_flood.jsonl"
    filepath = os.path.join(DIRS["flood_vulnerability"], filename)
    
    try:
        data = generate_flood_data(ac_no, ac_name, district)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data) + "\n")
            
        return True
    except Exception as e:
        log_error(f"Failed to ingest Flood Vulnerability for {ac_id}: {e}")
        return False
