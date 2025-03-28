from fastapi import APIRouter, UploadFile, File, HTTPException
from pdf2image import convert_from_bytes
from io import BytesIO, StringIO
import base64
import requests
import csv
import os
from dotenv import load_dotenv
from api.combined_extractor import extract_tables_from_image,encode_image
# Load environment variables
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"

if not api_key:
    raise RuntimeError("Missing OpenAI API key. Ensure it is set in the environment variables.")

router = APIRouter()
BASE_FOLDER = "download/extracted_tables"
os.makedirs(BASE_FOLDER, exist_ok=True)


@router.post("/extract-tables/")
async def extract_tables_from_pdf(pdf_file: UploadFile = File(...)):
    """Extracts tables from a PDF file and saves CSV files inside a folder named after the PDF."""
    try:
        pdf_bytes = await pdf_file.read()
        pdf_name = pdf_file.filename.rsplit(".", 1)[0]  # Get filename without extension
        save_folder = os.path.join(BASE_FOLDER, pdf_name)  # Ensure correct folder

        os.makedirs(save_folder, exist_ok=True)  # Create folder if not exists

        images = convert_from_bytes(pdf_bytes, poppler_path=POPPLER_PATH)
        extracted_tables = []
        
        for i, image in enumerate(images):
            img_bytes = BytesIO()
            image.save(img_bytes, format="JPEG")
            extracted_text = extract_tables_from_image(img_bytes.getvalue())

            if extracted_text and "no table found" not in extracted_text.lower():
                csv_filename = os.path.join(save_folder, f"table_page_{i + 1}.csv")
                
                with open(csv_filename, "w", newline="") as f:
                    csv_writer = csv.writer(f)
                    for line in extracted_text.split("\n"):
                        columns = [cell.strip() for cell in line.split("|") if cell.strip()]
                        if columns:
                            csv_writer.writerow(columns)

                extracted_tables.append(csv_filename)
        
        if not extracted_tables:
            raise HTTPException(status_code=400, detail="No tables found in the PDF.")

        return {"message": f"Extraction completed. Tables saved in: {save_folder}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting tables: {str(e)}")
