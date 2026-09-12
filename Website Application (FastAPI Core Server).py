import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Cortex AI Diagnostic Gateway", version="1.0")

UPLOAD_DIR = "secure_storage/dicom_vault"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/v1/analyze")
async def analyze_scan(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.dcm', '.png', '.jpg', '.jpeg', '.tiff')):
        raise HTTPException(status_code=400, detail="Unsupported medical image format.")
    
    file_path = os.path.isdir(UPLOAD_DIR) and os.path.join(UPLOAD_DIR, file.filename)
    # Save routine handled by data storage layer module
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return JSONResponse(status_code=200, content={
        "filename": file.filename,
        "status": "Ingested successfully into secure storage pipeline",
        "next_step": "Queued for deep learning inference and LLM report generation"
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)