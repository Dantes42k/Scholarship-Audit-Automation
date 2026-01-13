import time
import json
import re

def ask_gemini_batch(file_data_list, criteria):
    if not file_data_list: return []
    
    # 1. Pre-filtering (빈 파일 제외)
    valid_files = []
    dummy_results = {}
    
    for idx, f in enumerate(file_data_list):
        content = f['text'].strip()
        if len(re.sub(r'\s', '', content)) < 10:
            dummy_results[idx] = {
                "verdict": "Reject", 
                "reason_codes": ["REV-00"], 
                "ai_comment": "내용 식별 불가",
                "file_type": "기타",
                "score": ""
            }
        else:
            valid_files.append((idx, f, sanitize_text(content)))
    
    if not valid_files and dummy_results:
        return [dummy_results[i] for i in range(len(file_data_list))]

    # 2. Prompt Construction
    prompt_items = []
    for idx, f, txt in valid_files:
        prompt_items.append(f"[파일ID:{idx}] {f['name']}\n{txt[:6000]}")
    
    joined_context = "\n----------------\n".join(prompt_items)
    
    prompt = f"""
    **Role:** 장학금 감사관(Auditor).
    **Target:**
    - 신청자: {criteria['name']}
    - 검증금액(총액): {criteria['amount']}원
    - 유형: {criteria.get('type', 'Unknown')}
    
    **Step 1: 문서 유형 분류 (file_type)**
    다음 중 하나로 분류:
    - "영수증": 카드전표, 매출전표, 이체확인증, 결제증빙
    - "응시결과": 성적표, 점수표, 시험결과
    - "수강증": 수강확인증, 교육이수증
    - "출석확인증": 출석부, 출석확인서
    - "응시확인서": 시험 접수확인서, 응시확인증
    - "기타": 위 항목에 해당하지 않는 문서
    
    **Step 2: 점수/합격여부 추출 (score) - 응시결과인 경우만**
    - 숫자 점수가 있으면 그대로 기록 (예: "750", "850", "IH", "AL")
    - "합격" 또는 "Pass" 키워드가 있으면 "합격"
    - "불합격" 또는 "Fail" 키워드가 있으면 "불합격"
    - 점수나 합격여부가 없으면 빈 문자열 ""
    
    **Step 3: 검증 규칙**
    1. **금액/승인:** 영수증 금액이 '{criteria['amount']}'원과 일치하고 승인번호(주문번호)가 있는가?
    2. **명의:** 승인번호가 없으면(이체증), 보낸사람/예금주가 '{criteria['name']}'여야 함. 다르면 [VAL-04].
    3. **예외:** 'TOEIC'/'YBM'은 수험번호가 있으면 금액 차이 허용(Pass).
    
    **Output JSON List:**
    [ {{ "file_id": Int, "file_type": "문서유형", "score": "점수/합격여부", "verdict": "Pass/Reject", "reason_codes": ["CODE"], "ai_comment": "Summary" }}, ... ]
    
    **Content:**
    {joined_context}
    """
    
    ai_final_results = {}
    for _ in range(2):
        try:
            resp = model.generate_content(prompt)
            clean = re.sub(r'|```', '', resp.text).strip()
            parsed = json.loads(clean)
            if isinstance(parsed, list):
                for item in parsed:
                    ai_final_results[item['file_id']] = item
            break
        except Exception as e:
            print(f"       ⚠️ AI 호출 오류: {e}")
            time.sleep(1)
    
    # Merge Results
    final_output = []
    for i in range(len(file_data_list)):
        if i in dummy_results:
            final_output.append(dummy_results[i])
        elif i in ai_final_results:
            final_output.append(ai_final_results[i])
        else:
            final_output.append({
                "verdict": "Reject", 
                "reason_codes": ["REV-00"], 
                "ai_comment": "AI Error",
                "file_type": "기타",
                "score": ""
            })
            
    return final_output

def process_ai_result_to_text(ai_res):
    codes = ai_res.get("reason_codes", [])
    if isinstance(codes, str): codes = [codes]
    verdict = ai_res.get("verdict", "Reject")
    comment = ai_res.get("ai_comment", "")
    file_type = ai_res.get("file_type", "기타")
    score = ai_res.get("score", "")
    
    if verdict == "Pass": 
        return "적합", "-", "-", "", comment, file_type, score
        
    # REASON_MAP에서 메시지 가져오기 (코드가 없으면 빈 문자열)
    msgs = []
    for c in codes:
        if c and c in REASON_MAP:
            msg = REASON_MAP[c]
            if msg:  # 빈 문자열이 아닌 경우만 추가 (REV-00 제외)
                msgs.append(msg)
        elif c:  # REASON_MAP에 없는 코드인 경우 코드 그대로 추가
            msgs.append(f"[알수없음] {c}")
    
    flag = "⚠️확인필요" if "REV-00" in codes else ""
    return "부적합", " / ".join(msgs) if msgs else "-", ", ".join(codes), flag, comment, file_type, score
    pass
