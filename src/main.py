import os
import json
import openpyxl
import google.generativeai as genai
import easyocr
from playwright.sync_api import sync_playwright

# [모듈 임포트]
from config.settings import GEMINI_API_KEY, REPORT_FILE, DOWNLOAD_DIR
from utils.file_utils import (
    fix_jsp_extension, clean_name, mask_id, mask_name, 
    mask_filename, sanitize_text_enhanced
)
from utils.ocr_engine import get_text_from_file
from utils.ai_handler import ask_gemini_batch, process_ai_result_to_text

def run_automation():
    # 1. 시스템 초기화
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp', generation_config={"response_mime_type": "application/json"})
    reader = easyocr.Reader(['ko', 'en'], gpu=True)
    
    # 2. 코드북 로드 (docs/codebook.json)
    codebook_path = os.path.join("docs", "codebook.json")
    with open(codebook_path, "r", encoding="utf-8") as f:
        REASON_MAP = json.load(f)

    # 3. 엑셀 파일 준비
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Type", "ID", "Name", "EduName", "Amount(Total)", "Date", "File", "FileType", "Verdict", "Score", "MsgForUser", "RejectCode", "ReviewFlag", "Comment"])

    # 4. 브라우저 제어 (Playwright)
    with sync_playwright() as p:
        # 이 부분은 실제 접속 대상 사이트의 로그인 및 그리드 로직에 맞게 구현됩니다.
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        frame = page.frame(name="right")
        
        # [예시 루프: 그리드 데이터 순회]
        # AUIGrid 등에서 가져온 student_list를 순회한다고 가정
        student_list = [] # 실제로는 AUIGrid.getGridData()로 가져옴
        
        for item in student_list:
            s_id = item.get('rs_hakbun')    # 원본 ID
            s_name = item.get('rs_cc01name') # 원본 이름
            
            # --- [AI 분석 단계: 원본 데이터 사용] ---
            # 1. 파일 다운로드 및 텍스트 추출 (원본)
            # tasks 로직 생략 (기존 다운로드 로직 수행)
            file_paths = [] # 다운로드된 파일 경로들
            file_data_for_ai = []
            
            for fp in file_paths:
                raw_text = get_text_from_file(fp, reader)
                file_data_for_ai.append({"name": os.path.basename(fp), "text": raw_text})
            
            # 2. AI에게 원본 정보 전달 (정확한 매칭을 위함)
            criteria = {"name": s_name, "amount": 0, "type": "응시"} # 실데이터 반영
            ai_raw_results = ask_gemini_batch(model, file_data_for_ai, criteria)
            
            # --- [보고서 작성 단계: 비식별화 적용] ---
            masked_s_id = mask_id(s_id)
            masked_s_name = mask_name(s_name)
            
            for i, f_data in enumerate(file_data_for_ai):
                res = ai_raw_results[i]
                
                # 1. 결과 텍스트 가공
                verdict, msg, code, flag, comment, f_type, score = process_ai_result_to_text(res, REASON_MAP)
                
                # 2. 개인정보 마스킹 처리
                masked_fname = mask_filename(f_data['name'], s_id, s_name)
                safe_comment = sanitize_text_enhanced(comment)
                # 코멘트 내 원본 이름이 있다면 마스킹된 이름으로 대체
                safe_comment = safe_comment.replace(s_name, masked_s_name)
                
                # 3. 엑셀 기재 (마스킹된 정보 사용)
                ws.append([
                    "신청", masked_s_id, masked_s_name, "교육명", 0, "2026.01.13",
                    masked_fname, f_type, verdict, score, msg, code, flag, safe_comment
                ])

    # 5. 결과 저장
    wb.save(REPORT_FILE)
    print(f"✅ 분석 및 비식별화 보고서 작성 완료! \n📂 위치: {REPORT_FILE}")

if __name__ == "__main__":
    run_automation()
