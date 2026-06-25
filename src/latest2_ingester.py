import os
import json
import random
from src.config import DIRS
from src.logger import log_info, log_success, log_error

DATASET_KEYS = [
    # 1. Agricultural Geography & Hydrology
    "irrigation_coverage", "groundwater_depth", "pesticide_usage", "organic_farming", "tubewell_density",
    "cold_storage_capacity", "major_crop_yield", "tractor_penetration", "soil_salinity", "horticulture_share",
    
    # 2. Digital Access & Telecom Quality
    "average_internet_speed", "public_wifi_zones", "mobile_signal_blackspots", "csc_transaction_volume", "optical_fiber_panchayats",
    "smartphone_ownership", "news_whatsapp_subscribers", "upi_retail_adoption", "school_smart_classes", "digital_literacy_trained",
    
    # 3. Health Access & Private Health Sector
    "private_clinic_density", "pharmacy_density", "ambulance_response_time", "distance_tertiary_care", "ayushman_card_saturation",
    "malnutrition_treatment_centers", "generic_medicine_sales", "ashray_grih_beds", "tb_cure_rate", "maternity_benefit_coverage",
    
    # 4. Financial Services & Inclusion
    "mudra_loans_disbursed", "atm_density", "microfinance_borrowers", "kcc_farmers", "insurance_pension_subscribers",
    "cooperative_bank_branches", "loan_recovery_rate", "pan_card_holders", "post_bank_accounts", "digital_banking_frauds",
    
    # 5. Urbanization, Trade & Small Business
    "urbanization_rate", "registered_msmes", "commercial_power_connections", "weekly_haat_vendors", "gst_registrations",
    "industrial_area_footprint", "property_transactions", "slum_population_share", "unorganized_sector_workers", "street_vendor_loans"
]

def get_dataset_mock_data(ac_no, clean_name, district, dtype):
    random.seed(ac_no + hash(dtype) % 30000)
    
    if dtype in ["irrigation_coverage", "soil_salinity", "horticulture_share", "optical_fiber_panchayats", "smartphone_ownership", "upi_retail_adoption", "school_smart_classes", "ayushman_card_saturation", "tb_cure_rate", "loan_recovery_rate", "pan_card_holders", "urbanization_rate", "slum_population_share", "mobile_signal_blackspots"]:
        val = round(random.uniform(5.0, 95.0), 2)
        unit = "%"
    elif dtype in ["groundwater_depth", "distance_tertiary_care"]:
        val = round(random.uniform(2.0, 45.0), 1)
        unit = "meters" if dtype == "groundwater_depth" else "km"
    elif dtype in ["pesticide_usage"]:
        val = round(random.uniform(0.5, 4.5), 2)
        unit = "kg/hectare"
    elif dtype in ["organic_farming"]:
        val = random.randint(10, 1500)
        unit = "acres"
    elif dtype in ["tubewell_density", "private_clinic_density", "pharmacy_density", "atm_density"]:
        val = random.randint(1, 150)
        unit = "count / density"
    elif dtype in ["cold_storage_capacity"]:
        val = random.randint(500, 15000)
        unit = "Metric Tons"
    elif dtype in ["major_crop_yield"]:
        val = random.randint(1500, 4500)
        unit = "kg/hectare"
    elif dtype in ["tractor_penetration"]:
        val = round(random.uniform(5.0, 85.0), 1)
        unit = "per 1000 landholders"
    elif dtype in ["average_internet_speed"]:
        val = round(random.uniform(10.0, 150.0), 1)
        unit = "Mbps"
    elif dtype in ["csc_transaction_volume"]:
        val = random.randint(100, 5000)
        unit = "transactions/month"
    elif dtype in ["ambulance_response_time"]:
        val = random.randint(15, 90)
        unit = "minutes"
    elif dtype in ["mudra_loans_disbursed", "generic_medicine_sales"]:
        val = random.randint(50, 8500)
        unit = "Lakhs INR" if dtype == "mudra_loans_disbursed" else "% share"
    elif dtype in ["news_whatsapp_subscribers", "digital_literacy_trained", "malnutrition_treatment_centers", "ashray_grih_beds", "maternity_benefit_coverage", "microfinance_borrowers", "kcc_farmers", "insurance_pension_subscribers", "post_bank_accounts", "registered_msmes", "commercial_power_connections", "weekly_haat_vendors", "gst_registrations", "property_transactions", "unorganized_sector_workers", "street_vendor_loans"]:
        val = random.randint(50, 125000)
        unit = "count"
    elif dtype in ["cooperative_bank_branches"]:
        val = random.randint(1, 12)
        unit = "branches"
    else:
        val = random.randint(0, 100)
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

def ingest_constituency_latest2(constituency):
    ac_id = constituency["ac_id"]
    ac_no = constituency["ac_no"]
    snake_name = constituency["snake_name"]
    ac_name = constituency["clean_name"]
    district = constituency["district"]
    
    latest2_dir = DIRS["latest2"]
    
    try:
        # Loop and execute all 50 generators
        for dtype in DATASET_KEYS:
            filename = f"{ac_id}_{snake_name}_{dtype}.jsonl"
            filepath = os.path.join(latest2_dir, filename)
            
            data = get_dataset_mock_data(ac_no, ac_name, district, dtype)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data) + "\n")
                
        return True
    except Exception as e:
        log_error(f"Failed to ingest latest2 datasets for {ac_id}: {e}")
        return False
