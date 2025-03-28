# from utils.api_caller import ApiCaller
# from utils.display_helpers import display_surgical_device_result, display_diagnostic_result
# from fastapi import  APIRouter,FastAPI, File, UploadFile, Form, Depends
# from typing import Optional
# import shutil
# import os

# router = APIRouter()

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# api_caller = ApiCaller()

# @router.post("/upload/")
# async def upload_file(file: UploadFile = File(...)):
#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     return {"message": "File uploaded successfully", "file_path": file_path}

# @router.post("/analyze/surgical-device/")
# async def analyze_surgical_device(
#     file_path: str = Form(...),
#     device_name: str = Form(...),
#     technique: str = Form(...)
# ):
#     result = api_caller.analyze_surgical_device(file_path, device_name, technique)
#     return result

# @router.post("/analyze/diagnostic/")
# async def analyze_diagnostic(
#     file_path: str = Form(...),
#     test_name: str = Form(...),
#     technique: str = Form(...),
#     sample_type: str = Form(...),
#     diagnostic_type: str = Form(...)
# ):
#     result = api_caller.analyze_diagnostic(file_path, test_name, technique, sample_type, diagnostic_type)
#     return result

from utils.api_caller import ApiCaller
from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

api_caller = ApiCaller()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "File uploaded successfully", "file_path": file_path}

@router.post("/analyze/surgical-device/")
async def analyze_surgical_device(
    file_path: str = Form(...),
    device_name: str = Form(...),
    technique: str = Form(...)
):
    result = api_caller.analyze_surgical_device(file_path, device_name, technique)
    return {"status": "success", "analysis_result": result}

@router.post("/analyze/diagnostic/")
async def analyze_diagnostic(
    file_path: str = Form(...),
    test_name: str = Form(...),
    technique: str = Form(...),
    sample_type: str = Form(...),
    diagnostic_type: str = Form(...)
):
    result = api_caller.analyze_diagnostic(file_path, test_name, technique, sample_type, diagnostic_type)
    return {"status": "success", "analysis_result": result}
