from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.etl import fetch_and_store_permits

app = FastAPI()

# Allow all CORS origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.post("/run-etl")
async def run_etl(request: Request):
    data = await request.json()

    permit_type = data.get("permit_type")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    email = data.get("email")
    city = data.get("city")
    zip_code = data.get("zip_code", "")

    try:
        result = fetch_and_store_permits(
            permit_type, start_date, end_date, email, city, zip_code
        )
        return {"message": result}
    except Exception as e:
        return {"error": str(e)}

