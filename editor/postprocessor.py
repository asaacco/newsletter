# GPT와 연동하여 Usecase 별로 추가 가공하는 단계
import openai
import pandas as pd
import json
import re
import configDomain
import configTitle
import configSubtitle
import configHtml
import time
import datetime
import re
import requests
from bs4 import BeautifulSoup
from html import escape

TODAY_YEAR = datetime.datetime.now().strftime("%Y")

def shorten_url(original_url):
    """TinyURL API를 사용해 URL 단축"""
    api_url = f"https://tinyurl.com/api-create.php?url={original_url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"URL 단축 실패: {original_url}")
        return original_url

def load_template(selected_domain):
    # 템플릿 파일 경로 생성
    template_path = f"templates/{selected_domain}_email_template.html"

    # 템플릿 파일 열기
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            template = file.read()
        return template
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found: {template_path}")

def generate_section(news_list):
    # 입력 데이터가 리스트인지 확인
    if not isinstance(news_list, list) or not news_list:
        return "<div>No news available.</div>"

    # 뉴스 항목을 HTML로 변환
    section_html = "<div class='news-section'>\n"
    print(news_list)

    for article in news_list:
        section_html += f'''
        <div class="news-item"><br>
        <div style="border-top: 1px solid #ddd; margin: 0 30px 25px;"></div>
        <span style="font-size: 16px; line-height: 2; font-weight: bold;">
            <a href="{escape(article['link'])}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: #003366;">{escape(article["title"])}
            </a>
        </span>
        <span style="font-size: 14px; line-height: 2;">
            | [{escape(article["media_name"])}] ({escape(article["date"])})
        </span>
        <div style="border-top: 0px solid #ddd; margin: 20px 0;"></div>
        <p style="font-size: 14px; line-height: 2;">{article["new_summary_with_insight"]}</p>
        '''
#           <p>* 해당 기사: <a href="{article["link"]}">{article["link"]}</a></p>

        # 키 존재 여부를 확인하여 안전하게 처리
#        if article.get("additional_source"):
#            section_html += f'<p>* 다른 기사: {article["additional_source"]}</p>'
#        section_html += '</div><br>'
    section_html += '</div>'
    return section_html

def json_to_html(news_by_section, selected_domain):

    # HTML 템플릿을 불러옴
    template = load_template(selected_domain)

    # 선택된 도메인에 따라 섹션 키워드 가져오기
    if selected_domain not in configDomain.DOMAINS:
        raise ValueError(f"Invalid domain selected: {selected_domain}")
    
    domain_keywords = configDomain.DOMAINS[selected_domain]

    # 섹션별로 뉴스 HTML 생성
    section_html_map = {}
    for section, keyword in domain_keywords.items():
        section_html_map[section] = generate_section(news_by_section.get(section, []))

    # 템플릿에서 변수를 실제 뉴스 내용으로 치환
    body = template
    for section, html_content in section_html_map.items():
        body = body.replace(f"{{{{ {section} }}}}", html_content)
        
    return body

def json_to_string(selected_domain, json_file_path: str) -> str:
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON 파일 파싱 오류: {e}")
        return ""

    # 최종 결과를 누적할 리스트
    lines = []
    title = configTitle.DOMAINS.get(selected_domain)
    subtitle = configSubtitle.DOMAINS.get(selected_domain)
    html_title = configHtml.DOMAINS.get(selected_domain)

    # 헤더 부분
    lines.append(f"ASAAC 일일 뉴스 브리핑 ({title})\n\n")
    lines.append("\"아침 사과 같은 ASAAC한 소식을 전합니다.\"\n")

    for idx, html_title_item in enumerate(html_title):  # 리스트를 순회하며 인덱스와 값 가져오기
        lines.append(f"\n# {subtitle[idx]} 동향 \n\n")  # subtitle의 해당 인덱스 사용
        news_list = data.get(html_title_item, [])  # 리스트 항목을 키로 사용해 데이터 가져오기

        # 뉴스 처리 로직 추가
        if not news_list:
            lines.append("관련 뉴스가 없습니다.\n")
        else:
            for i, news_item in enumerate(news_list, start=1):
                article_title = news_item.get("title", "제목 없음")
                media_name = news_item.get("media_name", "미디어 정보 없음")
                date = news_item.get("date", "날짜 정보 없음")
                summary = news_item.get("new_summary_with_insight", "").strip()
                link = news_item.get("link", "")
                additional_source = news_item.get("additional_source", None)  # 추가 기사 데이터 가져오기

                # 기사 번호/제목/매체/날짜
                lines.append(f"{i}/ {article_title} [{media_name}] ({date})\n")
                # 기사 요약
                if summary:
                    lines.append(f"{summary}\n")
                # 기사 링크
                if link:
                    lines.append(f"* 해당 기사: {link}\n")

                # 추가 기사 처리
                if additional_source:
                    lines.append(f"* 다른 기사: {additional_source}\n")

                lines.append("\n")  # 각 기사를 구분하기 위한 줄바꿈

    lines.append(f"ASAAC Co.\n")
    lines.append(f"* 더 자세한 {title} 관련 뉴스 기사 및 인사이트\n")
    lines.append(f"* 홈페이지: https://asaac.co.kr\n")
    lines.append(f"* 구독신청: https://forms.gle/rMzrDcKLTFHTid7LA\n")
    lines.append(f"* 오픈채팅: https://open.kakao.com/o/grtDi31g\n")
    lines.append(f" © {TODAY_YEAR}. ASAAC Co.\n")

    # 모든 라인을 하나의 문자열로 합치기
    result_string = "".join(lines)
    print(result_string)
    return result_string

def process_html(html_content):
    """HTML 문서에서 본문 텍스트의 URL을 추출하고 단축 URL로 대체"""
    soup = BeautifulSoup(html_content, 'lxml')

    # 모든 텍스트 노드에서 URL을 찾아 단축 URL로 대체
    for element in soup.find_all(text=True):  # 텍스트 노드 검색
        urls = re.findall(r'(https?://\S+)', element)  # 텍스트에서 URL 추출
        if urls:
            for url in urls:
                print(f"원본 URL: {url}")
                shortened_url = shorten_url(url)
                print(f"단축 URL: {shortened_url}\n")
                element.replace_with(element.replace(url, shortened_url))  # URL 대체

    return str(soup)

def postprocess_news(contents, selected_domain):
    try:
        # contents가 dict인지 확인
        if isinstance(contents, dict):
            contents_json = contents
            print("Input is already in JSON format")
        else:
            contents_json = json.loads(contents)
            print("Successfully changed to JSON format")
    except json.JSONDecodeError as e:
        print(f"Failed to change to JSON format: {e}")
        return None  # 변환 실패 시 None 반환 또는 예외 처리

    # 변환된 JSON을 확인 (디버깅용)
    # print(json.dumps(contents_json, indent=4))

    html_contents = json_to_html(contents_json, selected_domain)
    # HTML 처리
    updated_html = process_html(html_contents)

    return updated_html
