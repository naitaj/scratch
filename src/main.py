import os
import sys
import json
import argparse
import asyncio
from playwright.async_api import async_playwright

from src.config import ensure_directories, load_constituencies, DIRS
from src.logger import log_info, log_success, log_warn, log_error

# Import Harvester Modules
from src.eci_harvester import harvest_constituency_eci
from src.affidavits_scraper import harvest_affidavits_for_constituency
from src.census_ingester import ingest_constituency_census
from src.scheme_tracker import track_constituency_schemes
from src.news_aggregator import aggregate_constituency_news
from src.spatial_downloader import download_constituency_spatial

CHECKPOINT_PATH = r"c:\scratch\logs\checkpoint.json"

def load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_warn(f"Failed to load checkpoint file ({e}). Starting fresh.")
    return {"completed_ac_nos": []}

def save_checkpoint(checkpoint_data):
    try:
        with open(CHECKPOINT_PATH, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=4)
    except Exception as e:
        log_error(f"Failed to save checkpoint file: {e}")

def count_file_records(filepath):
    """
    Utility to count lines/records in JSON Lines files or GeoJSON files.
    """
    if not os.path.exists(filepath):
        return 0
    if filepath.endswith('.geojson'):
        return 1 # Single geometry feature is 1 record
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def generate_data_dictionary():
    """
    AC4: Builds a preliminary draft structure for data_dictionary.md,
    tracing file system paths and total record metrics to meet Phase 1 closure criteria.
    """
    log_info("Generating raw data dictionary (data/raw/data_dictionary.md)...")
    dict_path = os.path.join(DIRS["eci_2025"], "..", "data_dictionary.md")
    dict_path = os.path.abspath(dict_path)
    
    sections = {
        "eci_2025": {"desc": "ECI Bihar 2025 Legislative Assembly results per constituency", "format": "JSON Lines (.jsonl)"},
        "eci_2020": {"desc": "ECI Bihar 2020 Legislative Assembly results per constituency", "format": "JSON Lines (.jsonl)"},
        "candidate_affidavits": {"desc": "Form 26 affidavit candidate metadata and physical PDF files", "format": "JSON Lines (.jsonl) & PDF (.pdf)"},
        "census": {"desc": "Primary Census Abstract demographic splits mapped to assembly bounds", "format": "JSON Lines (.jsonl)"},
        "schemes": {"desc": "MGNREGA, PMAY and Ujjwala welfare allocations", "format": "JSON Lines (.jsonl)"},
        "news": {"desc": "Pre-election media mention snippets and urls", "format": "JSON Lines (.jsonl)"},
        "spatial": {"desc": "Boundary polygons represented in GeoJSON formats", "format": "GeoJSON (.geojson)"}
    }
    
    md_content = []
    md_content.append("# ConstituencyIQ Phase 1 Raw Data Dictionary\n")
    md_content.append("This document catalogs the data components acquired during Phase 1: Raw Data Acquisition.\n")
    md_content.append("| Directory Name | File Format | Description | File Count | Total Records |")
    md_content.append("| :--- | :--- | :--- | :--- | :--- |")
    
    for key, info in sections.items():
        folder_path = DIRS[key]
        if not os.path.exists(folder_path):
            md_content.append(f"| `data/raw/{key}/` | {info['format']} | {info['desc']} | 0 | 0 |")
            continue
            
        files = os.listdir(folder_path)
        # Filter for data files
        data_files = [f for f in files if f.endswith('.jsonl') or f.endswith('.geojson')]
        pdf_files = [f for f in files if f.endswith('.pdf')]
        
        file_count = len(data_files) + len(pdf_files)
        total_records = 0
        
        for f in data_files:
            total_records += count_file_records(os.path.join(folder_path, f))
            
        md_content.append(f"| `data/raw/{key}/` | {info['format']} | {info['desc']} | {file_count} | {total_records} |")
        
    md_content.append("\n## Schema Definitions\n")
    
    # Write a quick sample schema for each folder
    for key, info in sections.items():
        md_content.append(f"### `data/raw/{key}/` Schema")
        md_content.append(f"*   **Description**: {info['desc']}")
        md_content.append(f"*   **Format**: {info['format']}")
        
        # Pull a sample file if exists
        folder_path = DIRS[key]
        sample_printed = False
        if os.path.exists(folder_path):
            data_files = [f for f in os.listdir(folder_path) if f.endswith('.jsonl') or f.endswith('.geojson')]
            if data_files:
                sample_file = os.path.join(folder_path, data_files[0])
                try:
                    with open(sample_file, 'r', encoding='utf-8') as f:
                        if sample_file.endswith('.geojson'):
                            js_sample = json.load(f)
                            # Truncate coordinates for readability
                            if "geometry" in js_sample and "coordinates" in js_sample["geometry"]:
                                js_sample["geometry"]["coordinates"] = "[[... truncated coordinates ...]]"
                            sample_str = json.dumps(js_sample, indent=2)
                        else:
                            first_line = f.readline()
                            sample_str = json.dumps(json.loads(first_line), indent=2)
                        md_content.append("\n**Sample Record**:")
                        md_content.append("```json")
                        md_content.append(sample_str)
                        md_content.append("```\n")
                        sample_printed = True
                except Exception as e:
                    pass
        if not sample_printed:
            md_content.append("\n*(No sample data generated yet)*\n")
            
    with open(dict_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
        
    log_success(f"Raw data dictionary successfully written to {dict_path}")

async def run_pipeline(limit=None, live=False):
    log_info("Initializing Anti-Gravity Ingestion Pipeline...")
    ensure_directories()
    
    constituencies = load_constituencies()
    log_info(f"Loaded {len(constituencies)} constituencies from master lookup.")
    
    checkpoint = load_checkpoint()
    completed_nos = checkpoint["completed_ac_nos"]
    log_info(f"Loaded checkpoint. {len(completed_nos)} constituencies already processed.")
    
    target_constituencies = []
    for c in constituencies:
        if c["ac_no"] not in completed_nos:
            target_constituencies.append(c)
            
    if limit:
        target_constituencies = target_constituencies[:limit]
        log_info(f"Limit applied: Processing next {len(target_constituencies)} constituencies.")
        
    if not target_constituencies:
        log_success("All constituencies already processed or no targets remaining.")
        generate_data_dictionary()
        return
        
    log_info(f"Starting acquisition for {len(target_constituencies)} constituencies...")
    
    # Initialize Playwright browser context if running live
    playwright_context = None
    browser = None
    page = None
    
    if live:
        log_info("Starting Playwright headless Chromium for live scraping...")
        try:
            playwright_context = await async_playwright().start()
            browser = await playwright_context.chromium.launch(headless=True)
            page = await browser.new_page()
            # Set user agent to avoid blocking (NFR1)
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
        except Exception as e:
            log_error(f"Failed to initialize Playwright: {e}. Defaulting to simulated fallback mode.")
            live = False
            
    try:
        for idx, constituency in enumerate(target_constituencies):
            ac_no = constituency["ac_no"]
            ac_id = constituency["ac_id"]
            name = constituency["clean_name"]
            
            log_info(f"[{idx+1}/{len(target_constituencies)}] Starting processing for {ac_id} - {name}")
            
            # Module 1: ECI 2025 results
            ok = await harvest_constituency_eci(page, constituency, 2025, live=live)
            if not ok:
                log_error(f"ECI 2025 harvesting failed for {ac_id}. Skipping constituency.")
                continue
                
            # Module 1 (historical): ECI 2020 results
            ok = await harvest_constituency_eci(page, constituency, 2020, live=live)
            if not ok:
                log_error(f"ECI 2020 harvesting failed for {ac_id}. Skipping.")
                continue
                
            # Retrieve candidates for affidavit scraping (we read them from the ECI 2025 outputs we just saved)
            # Load candidate list from saved JSON Lines file
            saved_eci_file = os.path.join(DIRS["eci_2025"], f"{ac_id}_{constituency['snake_name']}_eci2025.jsonl")
            with open(saved_eci_file, 'r', encoding='utf-8') as f:
                eci_data = json.loads(f.readline())
            candidates = eci_data["candidates"]
            
            # Module 2: Candidate Affidavits Scraper
            ok = harvest_affidavits_for_constituency(constituency, candidates, live=live)
            if not ok:
                log_error(f"Affidavits harvesting failed for {ac_id}. Skipping.")
                continue
                
            # Module 3: Census Demographic Ingester
            ok = ingest_constituency_census(constituency, live=live)
            if not ok:
                log_error(f"Census ingestion failed for {ac_id}. Skipping.")
                continue
                
            # Module 4: Welfare Scheme Allocation Tracker
            ok = track_constituency_schemes(constituency, live=live)
            if not ok:
                log_error(f"Scheme tracking failed for {ac_id}. Skipping.")
                continue
                
            # Module 5: News Aggregator
            ok = aggregate_constituency_news(constituency, live=live)
            if not ok:
                log_error(f"News aggregation failed for {ac_id}. Skipping.")
                continue
                
            # Module 6: Spatial Downloader
            ok = download_constituency_spatial(constituency, live=live)
            if not ok:
                log_error(f"Spatial boundary download failed for {ac_id}. Skipping.")
                continue
                
            # Record completed AC
            completed_nos.append(ac_no)
            save_checkpoint({"completed_ac_nos": completed_nos})
            log_success(f"Finished processing all modules successfully for {ac_id} - {name}\n")
            
    finally:
        if browser:
            await browser.close()
        if playwright_context:
            await playwright_context.stop()
            
    # Output final summary data dictionary
    generate_data_dictionary()
    log_success("Pipeline execution run finished successfully.")

def main():
    parser = argparse.ArgumentParser(description="Anti-Gravity Automated Ingestion Pipeline Orchestrator")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of constituencies to process (smoke test)")
    parser.add_argument("--live", action="store_true", help="Enable live scraping mode using Playwright and live API connections")
    
    args = parser.parse_args()
    
    asyncio.run(run_pipeline(limit=args.limit, live=args.live))

if __name__ == "__main__":
    main()
