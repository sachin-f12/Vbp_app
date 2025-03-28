from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz  # PyMuPDF
from pathlib import Path
import os
from io import BytesIO
from fastapi.responses import FileResponse
from api.combined_extractor import extract_images_from_pdf
router = APIRouter()

# Define a directory to save extracted images
IMAGE_SAVE_DIR = Path("download\pdf_Images")
IMAGE_SAVE_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/extract-images")
async def extract_images(pdf_file: UploadFile = File(...)):
    """Extract images from an uploaded PDF file and return the file paths."""
    try:
        file_name = pdf_file.filename.rsplit(".", 1)[0]  # Remove .pdf extension
        save_dir = IMAGE_SAVE_DIR / file_name
        images = extract_images_from_pdf(BytesIO(await pdf_file.read()), save_dir)
        if not images:
            raise HTTPException(status_code=404, detail="No images found in the PDF.")
        return {"message": "Images extracted successfully", "images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting images: {str(e)}")

 
