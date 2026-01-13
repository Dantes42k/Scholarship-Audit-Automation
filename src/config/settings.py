import os
from dotenv import load_dotenv
from datetime import datetime

# .env 파일 활성화
load_dotenv()

# 보안 정보
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 경로 설정
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
BASE_TARGET_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "장학금정리")
REPORT_FILE = os.path.join(BASE_TARGET_DIR, f"통합검증보고서_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")

# 폴더 자동 생성
if not os.path.exists(BASE_TARGET_DIR):
    os.makedirs(BASE_TARGET_DIR)
