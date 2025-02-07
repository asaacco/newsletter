import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import logging
from config import DATE_YESTERDAY, DATE_TODAY
import configDomain
import configChannel 

def convert_relative_date(relative_date):
    if "일 전" in relative_date:
        days_ago = int(relative_date.split("일 전")[0].strip())
        return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    elif "시간 전" in relative_date:
        hours_ago = int(relative_date.split("시간 전")[0].strip())
        return (datetime.now() - timedelta(hours=hours_ago)).strftime('%Y-%m-%d')
    # 필요하다면 분, 주 등 추가 처리
    return datetime.now().strftime('%Y-%m-%d')

def crawl_news(query, yesterday, today, selected_domain):
    all_news_list = []  # 모든 매체의 결과를 저장할 리스트

    # 선택된 도메인에서 미디어 번호 가져오기
    if selected_domain not in configChannel.DOMAINS:
        logging.error("Invalid domain selected.")
        return []

    media_numbers = configChannel.DOMAINS[selected_domain] + configChannel.DOMAINS['global']
    print(f"오늘의 미디어 {configChannel.DOMAINS[selected_domain]} | {configChannel.DOMAINS['global']}")
    if not media_numbers:
        logging.warning("No media numbers configured for this domain.")
        return []

    # 각 매체 번호에 대해 개별적으로 검색
    for media_number in media_numbers:
        news_list = []
        page = 1  # 각 매체에 대해 페이지를 1로 초기화

        print(f"\nSearching for media: {media_number}")
        while True:
            # 매체별 URL 생성
            url = (f"https://search.naver.com/search.naver?where=news&query={query}"
                   f"&sm=tab_pge&sort=0&photo=0&field=1&pd=3&ds={yesterday}&de={today}"
                   f"&docid=&related=0&mynews=1&office_type=2&office_section_code=8"
                   f"&news_office_checked={media_number}&nso=so:r,p:from{yesterday.replace('.', '')}to{today.replace('.', '')}"
                   f"&start={page}")

            logging.debug(f"Fetching URL: {url}")
            print(f"Fetching URL: {url}")
            response = requests.get(url)
            if response.status_code != 200:
                logging.error(f"Failed to fetch URL for media {media_number}")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select(".news_wrap")

            if not items:
                logging.info(f"No more news articles found for media {media_number}.")
                break

            for item in items:
                title = item.select_one(".news_tit").text
                link = item.select_one(".news_tit")["href"]
                summary = item.select_one(".news_dsc").text if item.select_one(".news_dsc") else "No summary"
                date_element = item.select_one(".info_group .info")
                date = convert_relative_date(date_element.text.strip()) if date_element else "날짜 없음"
                media_name = item.select_one(".info_group .press").text.strip()

                news_list.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "date": date,
                    "media_name": media_name
                })

            # 다음 페이지로 넘어가기
            page += 10
            time.sleep(2)  # 서버 과부하 방지를 위해 잠시 대기
            if page >= 40:  # 최대 페이지 제한
                break

        # 매체별 결과를 전체 리스트에 추가
        all_news_list.extend(news_list)
        print(f"Finished fetching for media: {media_number}")

    return all_news_list


def fetch_news(selected_domain):
    # 도메인별 키워드 가져오기
    domain_keywords = configDomain.DOMAINS.get(selected_domain.lower())
    if not domain_keywords:
        raise ValueError(f"Invalid domain selected: {selected_domain}")
    
    fetched_news_dict = {}
    for section, keywords in domain_keywords.items():
        all_news = []
        for keyword in keywords:
            logging.debug(f"Crawling news for keyword: {keyword}")  # 키워드에 대한 크롤링 상태 확인
            news_list = crawl_news(keyword, DATE_YESTERDAY, DATE_TODAY, selected_domain)

            # 크롤링 결과 디버깅
            if news_list:
                logging.debug(f"News found for {keyword}: {len(news_list)} articles")  # 뉴스 개수 출력
            else:
                logging.debug(f"No news found for {keyword}")  # 뉴스가 없을 경우 디버깅 정보 출력

            all_news.extend(news_list)
        fetched_news_dict[section] = all_news
        print(fetched_news_dict)
        print(type(fetched_news_dict))
        
    return fetched_news_dict
