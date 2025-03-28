# from fastapi import APIRouter, UploadFile, File, HTTPException
# from pdf2image import convert_from_bytes
# import fitz  # PyMuPDF
# from io import BytesIO, StringIO
# import base64
# import httpx
# import csv
# import os
# import asyncio
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv(override=True)
# api_key = os.getenv("OPENAI_API_KEY")
# POPPLER_PATH = r"C:\\Program Files\\poppler-24.08.0\\Library\\bin"

# if not api_key:
#     raise RuntimeError("Missing OpenAI API key. Ensure it is set in the environment variables.")

# router = APIRouter()
# BASE_FOLDER = os.path.join("download", "combined_extreactions")  # Ensure it's inside "download"
# os.makedirs(BASE_FOLDER, exist_ok=True)

# def encode_image(image_bytes):
#     """Encodes image bytes to Base64 format."""
#     return base64.b64encode(image_bytes).decode("utf-8")

# async def extract_tables_from_image(image_bytes):
#     """Extracts tables from an image using OpenAI's GPT-4o-mini."""
#     base64_image = encode_image(image_bytes)

#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {api_key}"
#     }

#     content_text = (
#         "Extract all tables from the provided image. If no tables are found, return 'no table found'. "
#         "If multiple tables exist, separate them properly."
#     )

#     payload = {
#         "model": "gpt-4o-mini",
#         "messages": [
#             {"role": "user", "content": [
#                 {"type": "text", "text": content_text},
#                 {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
#             ]}
#         ],
#         "max_tokens": 800
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail="Error processing image with OpenAI API.")

#     return response.json()['choices'][0]['message']['content']

# async def extract_images_from_pdf(pdf_file: BytesIO, save_dir: str):
#     """Extract images from a PDF file and save in the correct folder."""
#     doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
#     os.makedirs(save_dir, exist_ok=True)

#     for page_num in range(len(doc)):
#         page = doc[page_num]
#         image_list = page.get_images(full=True)
#         for img_index, img in enumerate(image_list, start=1):
#             xref = img[0]
#             base_image = doc.extract_image(xref)
#             img_bytes = base_image["image"]
#             img_ext = base_image["ext"]
#             img_name = f"image_page_{page_num + 1}_{img_index}.{img_ext}"
#             img_path = os.path.join(save_dir, img_name)

#             with open(img_path, "wb") as f:
#                 f.write(img_bytes)

# async def extract_tables_from_pdf(pdf_bytes, save_dir: str):
#     """Extract tables from a PDF and save as CSV files in the correct folder."""
#     images = await asyncio.to_thread(convert_from_bytes, pdf_bytes, poppler_path=POPPLER_PATH)
    
#     os.makedirs(save_dir, exist_ok=True)
#     tasks = []
    
#     for i, image in enumerate(images):
#         img_bytes = BytesIO()
#         image.save(img_bytes, format="JPEG")
#         tasks.append(extract_tables_from_image(img_bytes.getvalue()))

#     extracted_texts = await asyncio.gather(*tasks)

#     for i, extracted_text in enumerate(extracted_texts):
#         if extracted_text and "no table found" not in extracted_text.lower():
#             csv_filename = os.path.join(save_dir, f"table_page_{i + 1}.csv")
#             with open(csv_filename, "w", newline="") as f:
#                 csv_writer = csv.writer(f)
#                 for line in extracted_text.split("\n"):
#                     columns = [cell.strip() for cell in line.split("|") if cell.strip()]
#                     if columns:
#                         csv_writer.writerow(columns)

# @router.post("/extract-combined/")
# async def extract_combined(pdf_file: UploadFile = File(...)):
#     """Extract images and tables from a PDF and save them inside the correct subfolder within 'download'."""
#     try:
#         pdf_bytes = await pdf_file.read()
#         pdf_name = pdf_file.filename.rsplit(".", 1)[0]
#         save_folder = os.path.join(BASE_FOLDER, pdf_name)  # Ensure correct folder inside 'download/extracted_content'

#         await asyncio.gather(
#             extract_images_from_pdf(BytesIO(pdf_bytes), save_folder),
#             extract_tables_from_pdf(pdf_bytes, save_folder)
#         )

#         return {"message": f"Extraction completed. Files saved in: {save_folder}"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")
from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
from pathlib import Path
from io import BytesIO, StringIO
import base64
import requests
import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"

if not api_key:
    raise RuntimeError("Missing OpenAI API key. Ensure it is set in the environment variables.")

router = APIRouter()
BASE_FOLDER = Path("download/combined_extractions")
BASE_FOLDER.mkdir(parents=True, exist_ok=True)

def encode_image(image_bytes):
    """Encodes image bytes to Base64 format."""
    return base64.b64encode(image_bytes).decode("utf-8")

def extract_tables_from_image(image_bytes):
    """Extracts tables from an image using OpenAI's GPT-4o-mini."""
    base64_image = encode_image(image_bytes)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    print("working on imanges tables")
    content_text = (
        "Extract all tables from the provided image. If no tables are found, return 'no table found'. "
        "If multiple tables exist, separate them properly."
    )
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": content_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        "max_tokens": 800
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error processing image with OpenAI API.")
    
    return response.json()['choices'][0]['message']['content']

def extract_images_from_pdf(pdf_file: BytesIO, save_dir: Path):
    """Extract images from a PDF file and save them to a directory."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    save_dir.mkdir(parents=True, exist_ok=True)
    print("working on imanges")
    extracted_images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_ext = base_image["ext"]
            img_name = f"image_{page_num + 1}_{img_index}.{img_ext}"
            img_path = save_dir / img_name

            with open(img_path, "wb") as f:
                f.write(img_bytes)

            extracted_images.append(str(img_path))
    
    return extracted_images

def extract_tables_from_pdf(pdf_bytes: bytes, save_dir: Path):
    """Extract tables from a PDF and store as CSV files in a folder."""
    images = convert_from_bytes(pdf_bytes, poppler_path=POPPLER_PATH)
    extracted_tables = []

    for i, image in enumerate(images):
        img_bytes = BytesIO()
        image.save(img_bytes, format="JPEG")
        extracted_text = extract_tables_from_image(img_bytes.getvalue())

        if extracted_text and "no table found" not in extracted_text.lower():
            csv_filename = save_dir / f"table_page_{i + 1}.csv"
            
            with open(csv_filename, "w", newline="") as f:
                csv_writer = csv.writer(f)
                for line in extracted_text.split("\n"):
                    columns = [cell.strip() for cell in line.split("|") if cell.strip()]
                    if columns:
                        csv_writer.writerow(columns)

            extracted_tables.append(str(csv_filename))
    
    return extracted_tables

@router.post("/extract-combined/")
async def extract_combined(pdf_file: UploadFile = File(...)):
    """Extract images and tables from a PDF and save in a dedicated folder."""
    try:
        pdf_bytes = await pdf_file.read()
        pdf_name = pdf_file.filename.rsplit(".", 1)[0]  # Get filename without extension
        save_folder = BASE_FOLDER / pdf_name

        save_folder.mkdir(parents=True, exist_ok=True)

        extracted_images = extract_images_from_pdf(BytesIO(pdf_bytes), save_folder)
        extracted_tables = extract_tables_from_pdf(pdf_bytes, save_folder)

        if not extracted_images and not extracted_tables:
            raise HTTPException(status_code=400, detail="No tables or images found in the PDF.")

        return {
            "message": f"Extraction completed. Files saved in: {save_folder}",
            "image_files": extracted_images,
            "table_files": extracted_tables
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")

