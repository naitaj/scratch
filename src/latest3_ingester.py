import os
import json
import random
from src.config import DIRS
from src.logger import log_info, log_success, log_error

# Define categories and sub-items
CROPS = ["paddy", "wheat", "maize", "mustard", "sugarcane", "potato", "lentils", "jute", "banana", "mango"]
LIVESTOCK = ["cow", "buffalo", "goat", "sheep", "pig", "chicken", "duck", "fish"]
INFRA = ["road", "bridge", "post_office", "bank_branch", "atm", "csc_center", "telecom_tower", "panchayat_bhawan", "community_hall", "public_toilet", "bus_stop", "market_haat", "wholesale_mandi", "waste_bin", "water_tap"]
HEALTH = ["malaria", "dengue", "cholera", "typhoid", "tuberculosis", "anemia", "stunting", "wasting", "maternal_mortality", "infant_mortality"]
MSME = ["handloom", "pottery", "blacksmith", "carpentry", "retail_grocery", "apparel_shop", "fertilizer_dealer", "brick_kiln", "agro_processing", "transport_agency"]
LAW = ["theft", "robbery", "land_encroachment", "domestic_violence", "cyber_fraud", "juvenile_crime", "liquor_smuggling", "arms_possession", "traffic_violation", "minor_disputes"]
EDUCATION = ["primary_school", "middle_school", "high_school", "senior_secondary", "general_college", "science_college", "iti_polytechnic", "coaching_center", "public_library", "sports_club"]
ENV = ["air_quality", "groundwater_salinity", "soil_erosion", "deforestation", "heatwave", "coldwave", "flood_inundation"]

DATASET_KEYS = []

# 1. Crops: 10 * 3 = 30
for crop in CROPS:
    DATASET_KEYS.extend([f"{crop}_area_share_pct", f"{crop}_yield_kg_per_hec", f"{crop}_subsidy_amount_inr"])

# 2. Livestock: 8 * 3 = 24
for anim in LIVESTOCK:
    DATASET_KEYS.extend([f"{anim}_population_count", f"{anim}_feed_centers", f"{anim}_vet_visits_annual"])

# 3. Infra: 15 * 3 = 45
for item in INFRA:
    DATASET_KEYS.extend([f"{item}_count", f"{item}_electricity_connectivity_pct", f"{item}_digital_access_status"])

# 4. Health: 10 * 3 = 30
for illness in HEALTH:
    DATASET_KEYS.extend([f"{illness}_cases_registered", f"{illness}_treatment_success_rate_pct", f"{illness}_medical_staff_ratio"])

# 5. MSME: 10 * 4 = 40
for sector in MSME:
    DATASET_KEYS.extend([f"{sector}_registered_count", f"{sector}_average_daily_turnover_inr", f"{sector}_gst_enrolled_pct", f"{sector}_credit_linked_loans"])

# 6. Law: 10 * 3 = 30
for crime in LAW:
    DATASET_KEYS.extend([f"{crime}_firs_filed", f"{crime}_disposal_rate_pct", f"{crime}_police_station_coverage_pct"])

# 7. Education: 10 * 4 = 40
for level in EDUCATION:
    DATASET_KEYS.extend([f"{level}_enrollment_count", f"{level}_girls_ratio_pct", f"{level}_pupil_teacher_ratio", f"{level}_computer_labs_pct"])

# 8. Env: 7 * 3 = 21
for factor in ENV:
    DATASET_KEYS.extend([f"{factor}_index_value", f"{factor}_annual_deviation_pct", f"{factor}_population_affected_pct"])

# Assert exactly 260 keys
assert len(DATASET_KEYS) == 260, f"Expected 260 keys, got {len(DATASET_KEYS)}"

def get_dataset_mock_data(ac_no, clean_name, district, dtype):
    random.seed(ac_no + hash(dtype) % 50000)
    
    if dtype.endswith("_pct") or dtype.endswith("_rate_pct") or dtype.endswith("_connectivity_pct") or dtype.endswith("_coverage_pct") or dtype.endswith("_labs_pct") or dtype.endswith("_ratio_pct") or dtype.endswith("_deviation_pct") or dtype.endswith("_share_pct"):
        val = round(random.uniform(5.0, 95.0), 2)
        unit = "%"
    elif dtype.endswith("_inr") or dtype.endswith("_amount_inr") or dtype.endswith("_turnover_inr"):
        val = random.randint(500, 15000000)
        unit = "INR"
    elif dtype.endswith("_kg_per_hec") or dtype.endswith("_yield_kg_per_hec"):
        val = random.randint(1200, 5500)
        unit = "kg/hectare"
    elif dtype.endswith("_status") or dtype.endswith("_access_status"):
        val = random.choice(["High Access", "Medium Access", "Low Access", "None"])
        unit = "status_index"
    elif dtype.endswith("_ratio") or dtype.endswith("_staff_ratio") or dtype.endswith("_teacher_ratio"):
        val = round(random.uniform(1.0, 65.0), 1)
        unit = "ratio"
    elif dtype.endswith("_value") or dtype.endswith("_index_value"):
        val = round(random.uniform(10.0, 500.0), 1)
        unit = "index_rating"
    else:
        val = random.randint(0, 85000)
        unit = "count"
        
    return {
        "ac_no": ac_no,
        "ac_name": clean_name,
        "district": district,
        "dataset_type": dtype,
        "value": val,
        "unit": unit,
        "last_updated": "2025-2026"
    }

def ingest_constituency_latest3(constituency):
    ac_id = constituency["ac_id"]
    ac_no = constituency["ac_no"]
    snake_name = constituency["snake_name"]
    ac_name = constituency["clean_name"]
    district = constituency["district"]
    
    latest3_dir = DIRS["latest3"]
    
    try:
        # Loop and execute all 260 generators
        for dtype in DATASET_KEYS:
            filename = f"{ac_id}_{snake_name}_{dtype}.jsonl"
            filepath = os.path.join(latest3_dir, filename)
            
            data = get_dataset_mock_data(ac_no, ac_name, district, dtype)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data) + "\n")
                
        return True
    except Exception as e:
        log_error(f"Failed to ingest latest3 datasets for {ac_id}: {e}")
        return False
