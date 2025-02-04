import openai
import os
import pandas as pd
from dotenv import load_dotenv
import logging
from config import PERSONA, OBJECTIVE, CONTEXT, FORMAT_RULES, DOMAIN_KNOWLEDGE, FINAL_INSTRUCTION
import configRejectKeyword
# .env 파일 로드 및 OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
import json
import pandas as pd
import logging
from openai import OpenAI
from datetime import datetime, timedelta 
import time
# 날짜 설정
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def get_chatgpt4o_response_newsletter(persona, objective, context, format_rules, domain_knowledge, data, final_instruction):

    client = OpenAI()

    logging.info("Generated message for ChatGPT.")
    
    # ChatGPT 요청 메시지 생성
    messages = [
        {
            "role": "system",
            "content": f"""{persona}

    ### 목표 및 작업 설명
    {objective}

    ### Input 데이터의 설명
    {context}

    ### 결과물의 규칙
    {format_rules}

    ### 특별히 지켜야 하는 규칙
    {domain_knowledge}

    ### 최종 지시
    {final_instruction}

    # ===========================
    #  추가 지침 (카테고리별 처리)
    # ===========================
    1. 입력 JSON에는 여러 최상위 카테고리(예: "메타버스_소식", "로봇_소식" 등)가 있을 수 있음.
    2. 각 카테고리를 '독립적으로' 분석하여, 카테고리 내부에서만 중복 여부를 판단하고 대표 기사를 선정합니다.
    3. 카테고리가 다르면 절대 중복으로 묶지 않습니다.
    4. 모든 카테고리에 대해 결과(JSON)를 생성하며, 어떤 카테고리도 누락시키면 안 됩니다.
    5. 중복이 아니면 기사들을 절대 제거하지 않고 모두 결과에 포함해야 합니다.
    6. 최종 출력은 카테고리 이름을 key로, 그 안에 대표 기사(및 additional_source)를 담은 배열을 넣되, 포맷 규칙에 맞춰 JSON 형태로 출력하세요.
    
    """
        },
        {
            "role": "user",
            "content": f"### Input(Json format):\n{data}"
        }
    ]

    try:
        # ChatGPT API 호출
        completion = client.chat.completions.create(
        model="gpt-4o",  # GPT-4 모델
        messages=messages,
        response_format = {'type':"json_object"},
        temperature=0.7  # 답변의 창의성 조정
        )
        response = completion.choices[0].message.content
        logging.info("Received response from ChatGPT.")
        return response

    except Exception as e:
        logging.error(f"Error calling ChatGPT API: {e}", exc_info=True)
        raise
# 특정 키워드가 포함된 항목을 제거하는 함수
def remove_garbage(contents_json, keywords, max_articles=50):
    """JSON 데이터에서 특정 키워드가 포함된 항목 제거 및 카테고리별 최대 기사 수 제한"""
    try:
        # 결과를 저장할 딕셔너리 초기화
        filtered_json = {}

        # 각 카테고리(예: ESG_소식, AI_소식)에 대해 처리
        for category, articles in contents_json.items():
            # 카테고리 내 기사 데이터를 DataFrame으로 변환
            contents_df = pd.DataFrame(articles)

            if contents_df.empty:
                logging.warning(f"No data in category {category}. Skipping.")
                filtered_json[category] = []
                continue

            # 키워드가 title 또는 summary에 포함된 경우 해당 항목 제거
            def filter_keywords(row):
                # title과 summary 값 확인
                title = row.get("title", "").strip().lower()
                summary = row.get("summary", "").strip().lower()

                # 디버깅: 각 row의 title, summary 출력
                print(f"Checking article: title='{title}', summary='{summary}'")

                for keyword in keywords:
                    if keyword.lower() in title or keyword.lower() in summary:
                        print(f"Filtered out: title='{title}', keyword='{keyword}'")
                        return False  # 해당 기사 제거
                return True  # 유지

            # 필터링된 DataFrame 생성
            filtered_df = contents_df[contents_df.apply(filter_keywords, axis=1)]

            # 디버깅: 필터링 후 남은 기사 수
            print(f"Category: {category}, Articles Remaining: {len(filtered_df)}")

            # 카테고리별로 최대 max_articles개 기사만 유지
            filtered_df = filtered_df.head(max_articles)

            # 필터링 결과를 딕셔너리에 추가
            filtered_json[category] = filtered_df.to_dict(orient="records")

        return filtered_json

    except Exception as e:
        logging.error(f"Error in remove_garbage: {e}")
        return contents_json

#준헌이가 개발 분요한 부분(basic, premium preprocessing 버젼 만들기)
def preprocess_news(selected_domain, contents_dict, yesterday_titles):
    """ChatGPT로 뉴스 처리"""
    logging.info("Processing news with ChatGPT...")
    print("Start processing news...")

    try:
        # 키워드 목록
        keywords = configRejectKeyword.DOMAINS[selected_domain]

        # 입력 데이터에서 특정 키워드를 포함하는 항목 제거 및 카테고리별 처리
        filtered_contents = remove_garbage(contents_dict, keywords)
        print(f"Filtered contents: {json.dumps(filtered_contents, ensure_ascii=False, indent=2)}")
        #print(filtered_contents)
        #time.sleep(10000)

        # DataFrame을 JSON 형식으로 변환
        contents_json = json.dumps(filtered_contents, ensure_ascii=False)

        # 어제 기사 제목을 포함한 CONTEXT 생성
        dynamic_context = f"""
        {CONTEXT}
        어제 기사 제목 목록:
        {json.dumps(yesterday_titles, ensure_ascii=False)}
        """
        print("Generated dynamic context for GPT request.")

        # ChatGPT API에 데이터 전달
        response = get_chatgpt4o_response_newsletter(
            persona=PERSONA,
            objective=OBJECTIVE,
            context=dynamic_context,
            format_rules=FORMAT_RULES,
            domain_knowledge=DOMAIN_KNOWLEDGE,
            final_instruction=FINAL_INSTRUCTION,
            data=contents_json
        )

        return response

    except Exception as e:
        logging.error(f"Error in preprocess_news: {e}")
        return None

