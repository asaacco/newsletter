import openai
import os
import pandas as pd
from dotenv import load_dotenv
import logging
from config import PERSONA, OBJECTIVE, CONTEXT, FORMAT_RULES, DOMAIN_KNOWLEDGE, FINAL_INSTRUCTION
import configRejectKeyword
import json
from datetime import datetime, timedelta

# .env 파일 로드 및 OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 날짜 설정
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# GPT 응답 캐시를 위한 딕셔너리
_response_cache = {}

def get_chatgpt_response(persona, objective, context, format_rules, domain_knowledge, data, final_instruction):
    """
    ChatGPT API를 호출하여 응답을 받는 함수입니다.
    """
    # 캐시 키 생성
    cache_key = f"{persona}_{objective}_{hash(data)}"
    if cache_key in _response_cache:
        logging.info("Returning cached ChatGPT response.")
        return _response_cache[cache_key]

    logging.info("Generating ChatGPT request message.")
    
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
6. 최종 출력은 카테고리 이름을 key로, 그 안에 대표 기사(및 additional_source)를 담은 배열을 넣되, 포맷 규칙에 맞춰 JSON 형태로 출력하세요.(json이 아닌 다른건 절때로 포함하지 마세요 예)
"""
        },
        {
            "role": "user",
            "content": f"### Input(Json format):\n{data}"
        }
    ]

    try:
        # ChatGPT API 호출
        completion = openai.ChatCompletion.create(
            model="gpt-4o",  # GPT-4 모델
            messages=messages,
            temperature=0.7  # 답변의 창의성 조정
        )
        response = completion.choices[0].message["content"]
        logging.info("Received response from ChatGPT.")
        
        # 응답 캐시에 저장
        _response_cache[cache_key] = response
        return response

    except Exception as e:
        logging.error(f"Error calling ChatGPT API: {e}", exc_info=True)
        raise

def remove_garbage(contents_json, keywords, max_articles=50):
    """
    JSON 데이터에서 특정 키워드가 포함된 항목 제거 및 카테고리별 최대 기사 수 제한
    """
    try:
        filtered_json = {}

        for category, articles in contents_json.items():
            contents_df = pd.DataFrame(articles)

            if contents_df.empty:
                logging.warning(f"No data in category {category}. Skipping.")
                filtered_json[category] = []
                continue

            def filter_keywords(row):
                title = row.get("title", "").strip().lower()
                summary = row.get("summary", "").strip().lower()

                for keyword in keywords:
                    if keyword.lower() in title or keyword.lower() in summary:
                        return False
                return True

            filtered_df = contents_df[contents_df.apply(filter_keywords, axis=1)]
            filtered_df = filtered_df.head(max_articles)
            filtered_json[category] = filtered_df.to_dict(orient="records")

        return filtered_json

    except Exception as e:
        logging.error(f"Error in remove_garbage: {e}")
        return contents_json

def preprocess_news(selected_domain, contents_dict, yesterday_titles, mode="basic"):
    """
    뉴스 데이터를 전처리하는 함수입니다.
    """
    logging.info("Processing news with ChatGPT...")

    try:
        keywords = configRejectKeyword.DOMAINS[selected_domain]
        logging.info(f"Using keywords for domain '{selected_domain}': {keywords}")

        filtered_contents = remove_garbage(contents_dict, keywords)
        contents_json = json.dumps(filtered_contents, ensure_ascii=False, indent=4).strip()

        dynamic_context = f"""
{CONTEXT}
어제 기사 제목 목록:
{json.dumps(yesterday_titles, ensure_ascii=False)}
"""
        logging.info("Generated dynamic context for GPT request.")

        if mode == "premium":
            dynamic_context += "\n추가 분석: 프리미엄 모드에서는 8개의 주요 기사를 선정하고, 2개의 문단으로 작성하세요. 핵심 키워드나 주요 숫자를 포함하고, 자연스러운 한국어 문장으로 작성하세요.\n"
            logging.info("Premium mode activated: 추가 분석 요청 포함.")

        response = get_chatgpt_response(
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
