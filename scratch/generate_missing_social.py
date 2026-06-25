import asyncio
import os
import sys

# Ensure project root is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import load_constituencies, DIRS
from src.social_media_scraper import scrape_constituency_social_media
from src.main import generate_data_dictionary

async def main():
    constituencies = load_constituencies()
    print(f"Loaded {len(constituencies)} constituencies.")
    
    count = 0
    for constituency in constituencies:
        ac_id = constituency["ac_id"]
        snake_name = constituency["snake_name"]
        filename = f"{ac_id}_{snake_name}_social.jsonl"
        filepath = os.path.join(DIRS["social_media"], filename)
        
        if not os.path.exists(filepath):
            # Run the scraper in simulated mode
            success = await scrape_constituency_social_media(None, constituency, live=False)
            if success:
                count += 1
                
    print(f"Generated {count} missing social media files.")
    generate_data_dictionary()
    print("Re-generated data dictionary.")

if __name__ == "__main__":
    asyncio.run(main())
