import os
import json
import random
from src.config import DIRS
from src.logger import log_info, log_success, log_error

DATASET_KEYS = [
    # 1. Economy, Employment & Livelihoods
    "unemployment_rate", "female_labor_participation", "agri_labor_wage", "construction_labor_wage",
    "bank_accounts_density", "cooperative_societies", "artisan_weavers", "brick_kilns", "skill_enrollment", "registered_startups",
    
    # 2. Infrastructure & Transportation
    "national_highways", "state_highways", "rail_stations", "panchayat_bhawans", "phc_ownership",
    "water_treatment_plants", "telecom_towers", "post_offices", "petrol_pumps", "common_service_centers",
    
    # 3. Education Infrastructure & Outcomes
    "high_school_ptr", "school_playgrounds", "female_dropout_rate", "science_colleges", "anganwadi_centers",
    "asha_workers", "school_girls_toilets", "school_electricity", "school_computer_labs", "adult_literacy_centers",
    
    # 4. Health & Nutrition Indicators
    "maternal_mortality", "infant_mortality", "anemia_prevalence", "tb_cases", "child_immunization",
    "child_malnutrition", "institutional_deliveries", "mobile_medical_units", "cancer_referrals", "hospital_bed_capacity",
    
    # 5. Social Welfare & Pension Schemes
    "old_age_pensioners", "widow_pensioners", "disability_pensioners", "bicycle_beneficiaries",
    "scholarship_beneficiaries", "ration_shops", "jan_aushadhi_kendras", "family_benefit_schemes",
    "kanya_utthan_beneficiaries", "icds_budget_share",
    
    # 6. Local Governance & Panchayat Audits
    "panchayat_audits", "rtps_compliance", "panchayat_turnout", "women_mukhiyas", "gram_sabha_meetings",
    "panchayat_fund_utilization", "gram_kutchery_resolutions", "panchayat_tax_revenues", "digitized_panchayats", "dpro_ratings",
    
    # 7. Environment & Natural Risks
    "aqi_average", "forest_cover_area", "groundwater_salinity", "arsenic_villages", "fluoride_villages",
    "earthquake_zone", "weather_casualty_risk", "soil_carbon", "rainfall_deviation", "soil_erosion_risk",
    
    # 8. Law, Order & Security
    "caste_disputes", "sc_protection_cases", "land_dispute_cases", "arms_act_violations", "police_station_density",
    "liquor_ban_cases", "cybercrime_cases", "juvenile_cases", "border_disputes", "women_helpdesk_cases",
    
    # 9. Social Media & Digital Footprint
    "whatsapp_group_count", "avg_youtube_views", "fb_post_frequency", "local_hashtags_count",
    "digital_ad_spend", "meme_pages_count", "social_positivity_ratio", "instagram_growth_rate",
    "whatsapp_channels_count", "misinformation_flags",
    
    # 10. Financial Payouts & Subsidies
    "pm_kisan_beneficiaries", "diesel_subsidies", "fertilizer_subsidies", "student_credit_cards",
    "jeevika_bank_loans", "electricity_subsidies", "minority_startup_loans", "lpg_subsidy_transactions",
    "crop_insurance_payouts", "artisan_loans"
]

def get_dataset_mock_data(ac_no, clean_name, district, dtype):
    random.seed(ac_no + hash(dtype) % 20000)
    
    # Heuristics based on name/dtype
    if dtype in ["unemployment_rate", "female_labor_participation", "female_dropout_rate", "child_immunization", "child_malnutrition", "institutional_deliveries", "anemia_prevalence", "rtps_compliance", "panchayat_turnout", "panchayat_fund_utilization", "forest_cover_area", "soil_carbon", "social_positivity_ratio", "instagram_growth_rate"]:
        val = round(random.uniform(10.0, 92.0), 2)
        unit = "%"
    elif dtype in ["agri_labor_wage", "construction_labor_wage"]:
        val = random.randint(250, 750)
        unit = "INR/day"
    elif dtype in ["bank_accounts_density", "police_station_density"]:
        val = random.randint(200, 1200)
        unit = "per 100,000 population"
    elif dtype in ["national_highways", "state_highways"]:
        val = round(random.uniform(5.0, 65.0), 2)
        unit = "km"
    elif dtype in ["aqi_average"]:
        val = random.randint(60, 240)
        unit = "AQI"
    elif dtype in ["maternal_mortality", "infant_mortality"]:
        val = round(random.uniform(15.0, 180.0), 1)
        unit = "ratio"
    elif dtype in ["pm_kisan_beneficiaries", "old_age_pensioners", "widow_pensioners", "disability_pensioners", "bicycle_beneficiaries", "scholarship_beneficiaries", "kanya_utthan_beneficiaries", "jeevika_bank_loans", "electricity_subsidies", "lpg_subsidy_transactions", "crop_insurance_payouts", "diesel_subsidies", "fertilizer_subsidies", "student_credit_cards", "minority_startup_loans", "artisan_loans"]:
        val = random.randint(1200, 185000)
        unit = "count / INR"
    elif dtype in ["panchayat_audits", "earthquake_zone", "phc_ownership", "dpro_ratings", "digitized_panchayats"]:
        val = random.choice(["Satisfactory", "Pending", "Critical", "Clean", "High Risk", "Moderate Risk", "Government-owned", "Rented"])
        unit = "status"
    else:
        val = random.randint(2, 450)
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

def ingest_constituency_latest1(constituency):
    ac_id = constituency["ac_id"]
    ac_no = constituency["ac_no"]
    snake_name = constituency["snake_name"]
    ac_name = constituency["clean_name"]
    district = constituency["district"]
    
    latest1_dir = DIRS["latest1"]
    
    try:
        # Loop and execute all 100 generators
        for dtype in DATASET_KEYS:
            filename = f"{ac_id}_{snake_name}_{dtype}.jsonl"
            filepath = os.path.join(latest1_dir, filename)
            
            data = get_dataset_mock_data(ac_no, ac_name, district, dtype)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data) + "\n")
                
        return True
    except Exception as e:
        log_error(f"Failed to ingest latest1 datasets for {ac_id}: {e}")
        return False
