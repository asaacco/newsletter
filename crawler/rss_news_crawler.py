import xml.etree.ElementTree as ET
import re
from datetime import datetime
import requests
import json

# def crawl_esgtoday_rss():
#     # URL에서 XML 데이터 가져오기
#     url = "https://www.esgtoday.com/feed/"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     }
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         xml_data = response.text
#     else:
#         raise Exception(f"Failed to fetch data from {url}. Status code: {response.status_code}")

#     # XML 데이터를 파싱
#     root = ET.fromstring(xml_data)

#     # HTML 태그 제거 함수
#     def remove_html_tags(text):
#         clean = re.sub(r'<.*?>', '', text)
#         return clean

#     # 문장 분리 함수
#     def split_into_sentences(text):
#         # 구두점을 기준으로 문장 분리
#         sentences = re.split(r'(?<=[.!?])\s+', text)
#         # 불완전한 텍스트도 포함해 최소한의 출력 보장
#         return [s.strip() for s in sentences if s.strip()]

#     # 추출한 데이터를 저장할 리스트
#     articles = []

#     # XML 데이터에서 필요한 정보 추출
#     for item in root.findall(".//item"):
#         title = item.find("title").text if item.find("title") is not None else ""
#         link = item.find("link").text if item.find("link") is not None else ""
#         description = item.find("description").text if item.find("description") is not None else ""
#         content_encoded = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
#         content = content_encoded.text if content_encoded is not None else ""
#         pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""

#         # HTML 태그 제거 및 상위 5문장만 추출
#         combined_content = remove_html_tags(description + " " + content)
#         if combined_content:
#             sentences = split_into_sentences(combined_content)
#             summary = ' '.join(sentences[:5])  # 최대 5개의 문장 포함
#         else:
#             summary = "No description available."

#         # 날짜 변환
#         try:
#             date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
#             formatted_date = date_obj.strftime('%Y-%m-%d')
#         except ValueError:
#             formatted_date = ""

#         # JSON 형식으로 저장
#         articles.append({
#             "title": title,
#             "link": link,
#             "summary": summary,
#             "date": formatted_date,
#             "media_name": "ESG Today"
#         })

#     # 결과 반환
#     return json.dumps(articles, indent=4, ensure_ascii=False)



# def crawl_esgnews_rss():
#     # URL에서 XML 데이터 가져오기
#     url = "https://esgnews.com/feed/"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     }
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         xml_data = response.text
#     else:
#         raise Exception(f"Failed to fetch data from {url}. Status code: {response.status_code}")

#     # XML 데이터를 파싱
#     root = ET.fromstring(xml_data)

#     # HTML 태그 제거 함수
#     def remove_html_tags(text):
#         clean = re.sub(r'<.*?>', '', text)
#         return clean

#     # 문장 분리 함수
#     def split_into_sentences(text):
#         # 구두점을 기준으로 문장 분리
#         sentences = re.split(r'(?<=[.!?])\s+', text)
#         # 불완전한 텍스트도 포함해 최소한의 출력 보장
#         return [s.strip() for s in sentences if s.strip()]

#     # 추출한 데이터를 저장할 리스트
#     articles = []

#     # XML 데이터에서 필요한 정보 추출
#     for item in root.findall(".//item"):
#         title = item.find("title").text if item.find("title") is not None else ""
#         link = item.find("link").text if item.find("link") is not None else ""
#         description = item.find("description").text if item.find("description") is not None else ""
#         content_encoded = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
#         content = content_encoded.text if content_encoded is not None else ""
#         pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""

#         # HTML 태그 제거 및 상위 5문장만 추출
#         combined_content = remove_html_tags(description + " " + content)
#         if combined_content:
#             sentences = split_into_sentences(combined_content)
#             summary = ' '.join(sentences[:5])  # 최대 5개의 문장 포함
#         else:
#             summary = "No description available."

#         # 날짜 변환
#         try:
#             date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
#             formatted_date = date_obj.strftime('%Y-%m-%d')
#         except ValueError:
#             formatted_date = ""

#         # JSON 형식으로 저장
#         articles.append({
#             "title": title,
#             "link": link,
#             "summary": summary,
#             "date": formatted_date,
#             "media_name": "ESG News"
#         })

#     # 결과 반환
#     return json.dumps(articles, indent=4, ensure_ascii=False)


def fetch_rss_data(url, media_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        xml_data = response.text
    else:
        raise Exception(f"Failed to fetch data from {url}. Status code: {response.status_code}")

    # XML 데이터를 파싱
    root = ET.fromstring(xml_data)

    # HTML 태그 제거 함수
    def remove_html_tags(text):
        clean = re.sub(r'<.*?>', '', text)
        return clean

    # 문장 분리 함수
    def split_into_sentences(text):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    # 추출한 데이터를 저장할 리스트
    articles = []

    # XML 데이터에서 필요한 정보 추출
    for item in root.findall(".//item"):
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        description = item.find("description").text if item.find("description") is not None else ""
        content_encoded = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
        content = content_encoded.text if content_encoded is not None else ""
        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""

        # HTML 태그 제거 및 상위 5문장만 추출
        combined_content = remove_html_tags(description + " " + content)
        if combined_content:
            sentences = split_into_sentences(combined_content)
            summary = ' '.join(sentences[:5])
        else:
            summary = "No description available."

        # 날짜 변환
        try:
            date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
            formatted_date = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            formatted_date = ""

        # JSON 형식으로 저장
        articles.append({
            "title": f"[외신] {title}",
            "link": link,
            "summary": summary,
            "date": formatted_date,
            "media_name": media_name
        })

    return articles

def crawl_esgnews_rss():
    # ESG Today RSS URL
    esg_today_url = "https://www.esgtoday.com/feed/"
    esg_today_articles = fetch_rss_data(esg_today_url, "ESG Today")

    # ESG News RSS URL
    esg_news_url = "https://esgnews.com/feed/"
    esg_news_articles = fetch_rss_data(esg_news_url, "ESG News")

    # 두 데이터를 병합
    all_articles = esg_today_articles + esg_news_articles

    # 결과를 JSON으로 반환
    return json.dumps(all_articles, indent=4, ensure_ascii=False)