import os
import json
import random
from src.config import DIRS
from src.logger import log_info, log_success, log_error

def generate_economic_data(ac_no, ac_name, district):
    random.seed(ac_no + 45678)
    
    # Establish district profiles: Patna is highly developed, others are developing
    is_patna = (district.lower() == "patna")
    
    if is_patna:
        gddp_lakhs = random.randint(1200000, 1800000)
        per_capita_inr = random.randint(110000, 150000)
        cd_ratio_pct = round(random.uniform(48.0, 58.0), 2)
        branches_per_100k = round(random.uniform(12.0, 18.0), 1)
    else:
        gddp_lakhs = random.randint(150000, 450000)
        per_capita_inr = random.randint(22000, 45000)
        cd_ratio_pct = round(random.uniform(32.0, 45.0), 2)
        branches_per_100k = round(random.uniform(3.5, 8.5), 1)
        
    return {
        "ac_no": ac_no,
        "ac_name": ac_name,
        "district": district,
        "reporting_period": "2024-2025",
        "financial_indicators": {
            "gross_district_domestic_product_gddp_lakhs_inr": gddp_lakhs,
            "district_per_capita_income_inr": per_capita_inr,
            "credit_deposit_cd_ratio_pct": cd_ratio_pct,
            "commercial_bank_branches_per_100k_population": branches_per_100k
        }
    }

def ingest_constituency_economics(constituency, live=False):
    ac_id = constituency["ac_id"]
    ac_no = constituency["ac_no"]
    snake_name = constituency["snake_name"]
    ac_name = constituency["clean_name"]
    district = constituency["district"]
    
    filename = f"{ac_id}_{snake_name}_economics.jsonl"
    filepath = os.path.join(DIRS["economic_indicators"], filename)
    
    try:
        data = generate_economic_data(ac_no, ac_name, district)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data) + "\n")
            
        return True
    except Exception as e:
        log_error(f"Failed to ingest Economics for {ac_id}: {e}")
        return False
