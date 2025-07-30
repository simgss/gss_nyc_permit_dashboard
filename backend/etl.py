import os
import requests
import uuid
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add backend directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

from emailer import send_confirmation_email
from db import supabase


# Load environment variables
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)


GEOCLIENT_API_KEY = os.getenv("GEOCLIENT_API_KEY")



# --- NYC Geoclient ---
def geocode_address(house_number, street, borough):
    if not (house_number and street and borough):
        return None, None
    try:
        url = "https://api.nyc.gov/geoclient/v2/address.json"
        params = {
            "houseNumber": house_number,
            "street": street,
            "borough": borough,
            "subscription-key": GEOCLIENT_API_KEY
        }
        resp = requests.get(url, params=params)
        data = resp.json().get("address", {})
        return data.get("latitude"), data.get("longitude")
    except Exception as e:
        print(f" Geocoding failed: {e}")
        return None, None

# --- Main ETL Function ---
def fetch_and_store_permits(permit_type, start_date, end_date, user_email, city, zip_code, property_type=None, work_category=None):

    print(f"Starting ETL for {permit_type} from {start_date} to {end_date} for {user_email}")
    print(f" City: {city} | ZIP: {zip_code if zip_code else 'N/A'}")

    try:
        # NYC Open Data (only if city is NYC)
        if city != "New York City":
            return f" Currently only NYC is supported. You selected: {city}"

        url = "https://data.cityofnewyork.us/resource/rbx6-tga4.json"
        filters = f"work_type = '{permit_type}' AND issued_date BETWEEN '{start_date}T00:00:00' AND '{end_date}T23:59:59'"
        if zip_code:
            filters += f" AND owner_zip_code = '{zip_code}'"

        params = {"$limit": 100, "$where": filters}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return " No permits found for the selected filters."

        print(f" Found {len(data)} permits.")
        inserted_count = 0

        for permit in data:
            lat, lon = geocode_address(
                permit.get("house_no"),
                permit.get("street_name"),
                permit.get("borough")
            )

            record = {
                "id": str(uuid.uuid4()),
                "user_email": user_email,
                "city": city,
                "property_type": property_type,
                "work_category": work_category,
                "zip_code": zip_code,
                "permit_type": permit_type,
                "start_date": start_date,
                "end_date": end_date,
                "data": permit,
                "applicant_business_address": permit.get("applicant_business_address"),
                "applicant_business_name": permit.get("applicant_business_name"),
                "applicant_first_name": permit.get("applicant_first_name"),
                "applicant_last_name": permit.get("applicant_last_name"),
                "applicant_middle_name": permit.get("applicant_middle_name"),
                "filing_representative_first_name": permit.get("filing_representative_first_name"),
                "filing_representative_last_name": permit.get("filing_representative_last_name"),
                "filing_representative_middle_initial": permit.get("filing_representative_middle_initial"),
                "filing_representative_business_name": permit.get("filing_representative_business_name"),
                "filing_reason": permit.get("filing_reason"),
                "house_no": permit.get("house_no"),
                "street_name": permit.get("street_name"),
                "borough": permit.get("borough"),
                "c_b_no": permit.get("c_b_no"),
                "work_on_floor": permit.get("work_on_floor"),
                "work_type": permit.get("work_type"),
                "permittee_s_license_type": permit.get("permittee_s_license_type"),
                "applicant_license": permit.get("applicant_license"),
                "work_permit": permit.get("work_permit"),
                "approved_date": permit.get("approved_date"),
                "issued_date": permit.get("issued_date"),
                "expired_date": permit.get("expired_date"),
                "job_description": permit.get("job_description"),
                "estimated_job_costs": permit.get("estimated_job_costs"),
                "owner_business_name": permit.get("owner_business_name"),
                "owner_name": permit.get("owner_name"),
                "lot": permit.get("lot"),
                "bin": permit.get("bin"),
                "block": permit.get("block"),
                "job_filing_number": permit.get("job_filing_number"),
                "house_number": permit.get("house_no"),
                "zipcode": permit.get("owner_zip_code"),
                "permit_status": permit.get("permit_status"),
                "permit_issuance_date": permit.get("issued_date"),
                "description": permit.get("description"),
                "latitude": lat,
                "longitude": lon,
                "owner_zip_code": permit.get("owner_zip_code"),
                "city": city,
            }

            supabase.table("permits").insert(record).execute()
            inserted_count += 1
            print(f" Inserted permit {permit.get('job_filing_number')}")

        #  Send confirmation
        send_confirmation_email(user_email, inserted_count)

        return f" Inserted {inserted_count} permits."
    
    except Exception as e:
        print(f" Unexpected error: {e}")
        return f" Error: {e}"

if __name__ == "__main__":
    result = fetch_and_store_permits(
        permit_type="General Construction",  # try just "GC"
        start_date="2024-01-01",
        end_date="2025-07-28",
        user_email="bpushparathna@gmail.com",
        city="New York City",
        zip_code=None  # <== REMOVE ZIP to get more results
    )
    print(result)


