
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.routers import intent, patients, doctors, hospitals, records, insurance, pharmacy, auth, email, monitoring

app = FastAPI(title="Intent Healthcare Platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(intent.router, prefix="/v1/intent")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(doctors.router, prefix="/api/v1")
app.include_router(hospitals.router, prefix="/api/v1")
app.include_router(records.router, prefix="/api/v1")
app.include_router(insurance.router, prefix="/api/v1")
app.include_router(pharmacy.router, prefix="/api/v1")
app.include_router(email.router, prefix="/api/v1/email")
app.include_router(monitoring.router, prefix="/api/v1")

@app.websocket("/ws/er")
async def er(ws: WebSocket):
    await ws.accept()
    # Send real-time bed availability data
    from app.services.real_data_service import get_all_bed_availability
    bed_data = get_all_bed_availability()
    
    # Calculate summary stats
    total_beds = sum(bed["total_beds"] for bed in bed_data)
    available_beds = sum(bed["available_beds"] for bed in bed_data)
    total_icu = sum(bed["icu_beds"] for bed in bed_data)
    available_icu = sum(bed["available_icu"] for bed in bed_data)
    
    await ws.send_json({
        "beds": available_beds,
        "icu": available_icu,
        "total_beds": total_beds,
        "total_icu": total_icu,
        "occupancy_rate": round(((total_beds - available_beds) / total_beds) * 100, 1) if total_beds > 0 else 0,
        "hospitals_count": len(bed_data),
        "critical_hospitals": len([bed for bed in bed_data if bed["status"] == "Critical"]),
        "timestamp": bed_data[0]["last_updated"] if bed_data else None
    })
