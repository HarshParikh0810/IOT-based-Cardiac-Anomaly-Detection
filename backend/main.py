from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time
from datetime import datetime

app = FastAPI(title="IoT ECG Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store each ESP32's data separately
device_data = {}  # { esp_id: { 'latest': {...}, 'ready': bool, 'last_update': timestamp } }

# Data model for type validation
class ECGData(BaseModel):
    hr: float
    spo2: float
    ecg: List[float]
    rest_ecg: Optional[int] = 0
    timestamp: Optional[str] = None

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "IoT ECG Backend API",
        "active_devices": len(device_data),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/start/{esp_id}")
def start_measurement(esp_id: str, esp_ip: Optional[str] = None):
    """Called by frontend to signal ESP32 to start collecting"""
    device_data[esp_id] = {
        "latest": {},
        "ready": False,
        "last_update": time.time(),
        "status": "collecting",
        "collecting": True  # ✅ NEW: Flag to indicate ESP should collect
    }
    print(f"🚀 Start signal sent for {esp_id} - ESP32 should detect this on next poll")
    print(f"   Device data: {device_data[esp_id]}")
    
    return {
        "status": "collecting",
        "esp_id": esp_id,
        "message": f"Measurement started for {esp_id}"
    }

@app.post("/data/{esp_id}")
async def receive_data(esp_id: str, payload: dict):
    """ESP32 posts data after measurement"""
    try:
        # Validate data
        ecg_data = ECGData(**payload)
        
        # ✅ UPDATED: Mark as ready and stop collecting
        device_data[esp_id] = {
            "latest": payload,
            "ready": True,
            "last_update": time.time(),
            "status": "ready",
            "collecting": False  # ✅ Stop collecting after data received
        }
        
        print(f"✅ Received data from ESP32 {esp_id}")
        print(f"   HR: {ecg_data.hr:.2f} bpm, SpO2: {ecg_data.spo2:.2f}%, ECG points: {len(ecg_data.ecg)}")
        
        return {
            "status": "ok",
            "message": "Data received successfully",
            "esp_id": esp_id
        }
    except Exception as e:
        print(f"❌ Error receiving data from {esp_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")

@app.get("/latest/{esp_id}")
def get_latest(esp_id: str):
    """
    ✅ UPDATED: ESP32 polls this to check if it should collect
    Frontend polls this to get data
    """
    if esp_id not in device_data:
        print(f"⚠️ Unknown device ID: {esp_id} - Initializing...")
        # ✅ NEW: Initialize device on first contact
        device_data[esp_id] = {
            "latest": {},
            "ready": False,
            "last_update": time.time(),
            "status": "idle",
            "collecting": False
        }
        return {"status": "idle", "message": "Device initialized, waiting for start signal"}
    
    info = device_data[esp_id]
    
    # Check if data is stale (older than 5 minutes)
    time_since_update = time.time() - info["last_update"]
    if time_since_update > 300 and info["ready"]:
        print(f"⚠️ Stale data for {esp_id} (last update: {time_since_update:.0f}s ago)")
        return {
            "status": "stale",
            "message": "Data is too old, please start new measurement"
        }
    
    # ✅ NEW: If collecting flag is set, tell ESP to collect
    if info.get("collecting", False):
        print(f"📡 ESP32 {esp_id} polling - sending collect signal")
        return {
            "status": "collecting",
            "message": "Start data collection now"
        }
    
    # ✅ UPDATED: If not ready and not collecting, return idle
    if not info["ready"] and not info.get("collecting", False):
        print(f"📡 ESP32 {esp_id} polling - status: idle")
        return {
            "status": "idle",
            "message": "Waiting for start signal..."
        }
    
    # ✅ If ready, return the actual data
    if info["ready"]:
        print(f"📤 Sending data to frontend for {esp_id}")
        response = info["latest"].copy()
        response["status"] = "ready"
        return response
    
    # Default idle response
    return {
        "status": "idle",
        "message": "Waiting..."
    }

@app.get("/devices")
def list_devices():
    """List all connected devices and their status"""
    devices = []
    current_time = time.time()
    
    for esp_id, info in device_data.items():
        devices.append({
            "esp_id": esp_id,
            "status": info.get("status", "unknown"),
            "ready": info["ready"],
            "collecting": info.get("collecting", False),
            "last_update": datetime.fromtimestamp(info["last_update"]).isoformat(),
            "seconds_ago": f"{current_time - info['last_update']:.1f}s",
            "has_data": bool(info.get("latest"))
        })
    
    return {
        "total_devices": len(devices),
        "devices": devices
    }

@app.delete("/device/{esp_id}")
def clear_device(esp_id: str):
    """Clear data for a specific device"""
    if esp_id in device_data:
        del device_data[esp_id]
        print(f"🗑️ Cleared data for {esp_id}")
        return {"status": "cleared", "esp_id": esp_id}
    return {"status": "not_found", "esp_id": esp_id}

@app.delete("/devices/clear")
def clear_all_devices():
    """Clear all device data"""
    count = len(device_data)
    device_data.clear()
    print(f"🗑️ Cleared all device data ({count} devices)")
    return {"status": "cleared", "count": count}

@app.get("/debug/{esp_id}")
def debug_device(esp_id: str):
    """Get detailed debug info for a device"""
    if esp_id not in device_data:
        return {"error": "Device not found"}
    
    info = device_data[esp_id]
    current_time = time.time()
    
    return {
        "esp_id": esp_id,
        "ready": info["ready"],
        "status": info.get("status", "unknown"),
        "collecting": info.get("collecting", False),
        "last_update": datetime.fromtimestamp(info["last_update"]).isoformat(),
        "seconds_since_update": current_time - info["last_update"],
        "has_latest_data": bool(info.get("latest")),
        "latest_data_keys": list(info.get("latest", {}).keys()),
        "data": info.get("latest", {})
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server...")
    print("📡 Listening on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)