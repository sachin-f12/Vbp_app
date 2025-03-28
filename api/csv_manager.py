from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
import os
from pathlib import Path
from fastapi.responses import FileResponse

router = APIRouter()

UPLOAD_FOLDER = Path("uploaded_files")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """Sanitizes the filename to remove invalid characters."""
    return "".join(c for c in filename if c.isalnum() or c in (".", "_", "-", " ")).rstrip()

@router.post("/upload/")
async def upload_and_convert_to_csv(file: UploadFile = File(...), csv_name: str = Form(...)):
    """Uploads a file and converts it to CSV."""
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
        # Save uploaded file temporarily
        temp_file_path = UPLOAD_FOLDER / file.filename
        with open(temp_file_path, "wb") as f:
            f.write(contents)
        
        # Determine file type (case-insensitive)
        ext = file.filename.lower().split('.')[-1]

        # Read data using pandas
        if ext == "xlsx":
            df = pd.read_excel(temp_file_path)
        elif ext == "csv":
            df = pd.read_csv(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Only .csv and .xlsx allowed.")
        
        # Check if DataFrame is empty
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file contains no data.")

        # Convert to CSV
        sanitized_csv_name = sanitize_filename(csv_name) + ".csv"
        csv_file_path = UPLOAD_FOLDER / sanitized_csv_name
        df.to_csv(csv_file_path, index=False)
        
        return {"message": "File converted successfully", "csv_filename": sanitized_csv_name}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/list/")
async def list_csv_files():
    """Lists all available CSV files."""
    try:
        files = [f.name for f in UPLOAD_FOLDER.glob("*.csv")]
        return {"csv_files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.get("/download/{csv_filename}")
async def download_csv(csv_filename: str):
    """Allows downloading a CSV file."""
    file_path = UPLOAD_FOLDER / csv_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=csv_filename, media_type="text/csv")

@router.delete("/delete/{csv_filename}")
async def delete_csv(csv_filename: str):
    """Deletes a CSV file."""
    file_path = UPLOAD_FOLDER / csv_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"message": f"File {csv_filename} deleted successfully"}

@router.post("/create/")
async def create_csv(csv_name: str = Form(...)):
    """Creates an empty CSV file."""
    try:
        sanitized_csv_name = sanitize_filename(csv_name) + ".csv"
        csv_file_path = UPLOAD_FOLDER / sanitized_csv_name
        with open(csv_file_path, "w") as f:
            pass  # Create empty file
        return {"message": f"CSV file '{sanitized_csv_name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating CSV file: {str(e)}")
