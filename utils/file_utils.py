import os
import re
import shutil
import time

def clean_name(text):
    """ 파일명으로 쓸 수 없는 특수문자 제거 """
    if not text: return "Unknown"
    return re.sub(r'[\\/:*?"<>|\r\n]', '_', text).strip()

def clean_currency(text):
    """ '84,000원' -> 84000 정수 변환 """
    if not text: return 0
    clean = re.sub(r'[^0-9]', '', str(text))
    return int(clean) if clean else 0

def fix_jsp_extension(file_path):
    """ JSP 등 잘못된 확장자를 실제 바이너리 헤더를 읽어 복원  """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
        
        new_ext = ""
        if header.startswith(b'%PDF'): new_ext = '.pdf'
        elif header.startswith(b'\x89PNG'): new_ext = '.png'
        elif header.startswith(b'\xff\xd8'): new_ext = '.jpg'
        
        if new_ext:
            base = os.path.splitext(file_path)[0]
            new_path = base + new_ext
            os.rename(file_path, new_path)
            return new_path
    except: pass
    return file_path

def mask_id(id_str):
    """학번 마지막 4자리 비식별화 (예: 1234567 -> 123****)"""
    id_str = str(id_str)
    if len(id_str) > 4:
        return id_str[:-4] + "****"
    return "****"

def mask_name(name):
    """이름 가운데 글자 비식별화 (예: 홍길동 -> 홍*동)"""
    if not name: return ""
    name_len = len(name)
    if name_len <= 2:
        return name[0] + "*"
    else:
        # 가운데 글자들을 마스킹 (3글자면 1개, 4글자면 2개)
        mid = name_len // 2
        return name[:mid] + "*" + name[mid+1:]

def mask_filename(filename, original_id, original_name):
    """파일명 내 학번과 이름 포함 시 마스킹"""
    masked = filename
    if original_id in masked:
        masked = masked.replace(original_id, "********")
    if original_name in masked:
        masked = masked.replace(original_name, "***")
    return masked

def sanitize_text_enhanced(text):
    """주민번호, 승인번호 등 개인정보 마스킹 강화"""
    if not text: return ""
    # 1. 주민등록번호 (기존 로직 유지)
    text = re.sub(r'\d{6}[- ]?[1-4]\d{6}', '[ID_MASKED]', text)
    # 2. 8자리 승인번호 (예: 30011017 -> [AUTH_MASKED])
    text = re.sub(r'\b\d{8}\b', '[AUTH_MASKED]', text)
    # 3. 카드번호 패턴 (예: 4673-09**-****-2042)
    text = re.sub(r'\d{4}-\d{2}\*\*-\*\*\*\*-\d{4}', '[CARD_MASKED]', text)
    return text
