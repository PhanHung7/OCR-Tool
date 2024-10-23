from fastapi import FastAPI, HTTPException, Query, Path, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import pandas as pd
from typing import Optional
import shutil
import KL_OCR
from enum import Enum
import zipfile
from spire.doc import *
from spire.doc.common import *


from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

app = FastAPI()

config = Cfg.load_config_from_file(r"D:\\OCR\\OCR\\vietocr\\base.yml")

config['cnn']['pretrained']=False
config['device'] = 'cpu'

vietocr = Predictor(config)

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"Đã xóa file: {file_path}")
    except FileNotFoundError:
        print(f"File không tìm thấy: {file_path}")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

def check_pdf(file_path):
    if file_path.endswith('.pdf'): return True
    return False

UPLOAD_FOLDER = "API_Files"
img = False
pdf_file = False
count = 0

try:
    lis_lang = pd.read_json('lang.json')
except:
    lis_lang = {"Announcement": "Some error occurred"}

class Option(str, Enum):
    option1 = "Vietnamese"
    option2 = "English"
    option3 = "Japanese"
    option4 = "Korean"
    option5 = "Arabic"
    option6 = "Chinese"

@app.get("/")
async def Check():
    return {"Check": "OK"}

@app.get("/user_{name}")
async def User(name: str):
    return {"Hello": f"{name}"}

@app.get("/List_Language")
async def list_model():
    return {"List_Language": lis_lang}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global UPLOAD_FOLDER
    
    if file.filename.split('.')[-1] not in ["jpg", "png", "pdf"]:
        return {"Error": f"Your file is {file.filename} not an image or pdf file please check it"}

    # Ensure the upload directory exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Create the full path where the file will be saved
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save the file
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"info": f"File '{file.filename}' saved at '{file_location}'"}

@app.get("/Convert_image_to_docx")
async def Convert(lang: Option):
    global pdf_file, UPLOAD_FOLDER, count, vietocr
    
    error_img_lis = []
    
    save_folder = ''
    Word_file = f"Word_file_{count}.docx"
    zip_filename = f"Files_{count}.zip"
    
    lis_file_excel = []
    lis_excel_path = []
    
    output_file = f'output_file_{count}'
    
    if not os.path.exists(output_file):
        os.makedirs(output_file)
    
    for file in os.listdir(UPLOAD_FOLDER): 
        error_img_lis, save_folder = KL_OCR.OCR(os.path.join(UPLOAD_FOLDER, file), vietocr, lang.lower(), check_pdf(file), count)
        
        compression = zipfile.ZIP_DEFLATED

        zf = zipfile.ZipFile(os.path.join(output_file, zip_filename), mode="w")
        
        for i in os.listdir(save_folder):
            if i.endswith('.docx'): 
                continue
            count_file = 0
            directory = os.path.join(save_folder, i)
            for filename in os.listdir(directory):
                if filename.endswith('.xlsx'):
                    new_name = f"page_{i}_{count_file}.xlsx"
                    os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))
                    count_file+=1
                    zf.write(os.path.join(directory, new_name), new_name, compress_type=compression)
        
        doc = Document()
        first = True
        
        for i in os.listdir(save_folder):
            if i.endswith('.docx'):
                if first: 
                    doc.LoadFromFile(os.path.join(save_folder, i))
                    first = False
                else:
                    file_name = os.path.join(save_folder, i)
                    doc.InsertTextFromFile(file_name, FileFormat.Auto)
        
        doc.SaveToFile(os.path.join(output_file,Word_file))
        
        zf.write(os.path.join(output_file,Word_file), Word_file, compress_type=compression)
        
        zf.close()
        doc.Close()
        
        delete_file(os.path.join(UPLOAD_FOLDER, file)) 
        count+=1
        return FileResponse(os.path.join(output_file, zip_filename), media_type='application/zip', filename=zip_filename) 
    return {"Error":"No Files found in data"}