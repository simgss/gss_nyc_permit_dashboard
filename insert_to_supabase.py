import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()  # ✅ Load from .env file

# ✅ Get values from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# ✅ Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ✅ Sample permit to insert
record = {
    "user_email": "pushparathna2019@gmail.com",
    "zip_code": "10007",
    "permit_type": "NB",
    "start_date": "2024-01-01",
    "end_date": "2024-07-01",
    "data": [
        {
            "job_no": "123456789",
            "owner": "ABC Construction",
            "address": "123 Broadway",
            "permit_status": "Issued"
        }
    ]
}

# ✅ Try inserting
print("🔍 Permit record to insert:")
print(record)

try:
    result = supabase.table("permits").insert(record).execute()
    print("✅ Inserted successfully!")
    print(result)
except Exception as e:
    print("❌ Error inserting permit:")
    print(e)
