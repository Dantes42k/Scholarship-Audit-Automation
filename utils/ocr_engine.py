import pdfplumber
import fitz  # PyMuPDF
import cv2
import numpy as np
import re

def get_text_from_file(file_path, reader):
    """ 파일 유형별 텍스트 추출 통합 인터페이스  """
    full_text = ""
    filename = os.path.basename(file_path).lower()
    
    if filename.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages: full_text += page.extract_text() or ""
        # 텍스트가 너무 적으면 스캔된 PDF로 간주하고 OCR 실행 
        if len(re.sub(r'\s+', '', full_text)) < 50:
            full_text = ocr_from_pdf_to_text(file_path, reader)
            
    elif filename.endswith(('.png', '.jpg', '.jpeg')):
        img = cv2.imread(file_path)
        if img is not None:
            full_text = " ".join(reader.readtext(img, detail=0))
            
    return full_text

def ocr_from_pdf_to_text(file_path, reader):
    """ PDF 페이지를 이미지로 변환하여 OCR 수행  """
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        img = cv2.imdecode(np.frombuffer(pix.tobytes("png"), np.uint8), cv2.IMREAD_COLOR)
        text += " ".join(reader.readtext(img, detail=0))
    return text
