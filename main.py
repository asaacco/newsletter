from crawler.news_crawler import fetch_news
from editor.preprocessor import preprocess_news
from editor.postprocessor import postprocess_news
from emailer.email_sender import send_email
from uploader.tistory_uploader import tistory_uploader
from uploader.kakao_uploader import kakao_uploader
from crawler.rss_news_crawler import crawl_esgnews_rss

from editor.preprocessor import preprocess_news
from crawler.news_crawler import fetch_news

from uploader.naver_uploader import post_to_naver_cafe
import json
import logging
import pandas as pd
from datetime import datetime, timedelta
import os
import time

TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def send_email_with_file(file_path, selected_domain):
    """output.html에 저장된 내용을 사용해 이메일 전송"""
    if not os.path.exists(file_path):
        print("Error: {file_path} 파일이 존재하지 않습니다.")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        postprocessed_news = file.read()

    print("Sending email with content from '{file_path}'...")
    # 이메일 전송 로직 추가
    send_email(postprocessed_news, selected_domain)
    print("Email sent successfully!")


def kakao_uploader_with_file(file_path, selected_domain):
    content = kakao_uploader(file_path, selected_domain)

    save_path = os.path.join(
    ".", "uploader", "kakao", f"{TODAY}_kakao_letter_{selected_domain}.txt"
    )
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"파일이 {save_path}에 저장되었습니다.")
    print("Kakao upload completed!")


def tistory_uploader_with_file(file_path, selected_domain):
    """output.html에 저장된 내용을 사용해 티스토리 업로드"""
    if not os.path.exists(file_path):
        print("Error: {file_path} 파일이 존재하지 않습니다.")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        postprocessed_news = file.read()

    print(f"Uploading to Tistory for domain: {selected_domain}...")
    # 티스토리 업로드 로직 추가
    tistory_uploader(postprocessed_news, selected_domain)
    print("Tistory upload completed!")

def full_code_run(selected_domain):
    """전체 코드 실행"""
    print("need update")

def get_newslist(selected_domain):
    """뉴스 크롤링"""
    today_filename = f"./crawler/json/{TODAY}_json_newslist_{selected_domain}.json"
    yesterday_filename = f"./crawler/json/{YESTERDAY}_json_newslist_{selected_domain}.json"

    print(f"Get newlist for domain: {selected_domain}...")

    # Initial fetched news
    fetched_news = fetch_news(selected_domain)

    # Ensure "ESG_소식" key is safely updated
    if selected_domain == 'esg':
        json_data = crawl_esgnews_rss()
        esg_rss_news = json.loads(json_data)  # 다시 Python 객체로 변환

        if "ESG_소식" not in fetched_news:
            fetched_news["ESG_소식"] = []

        # Filter valid ESG news with date filter
        valid_esg_news = [
            news for news in esg_rss_news
            if isinstance(news, dict) 
            and "title" in news 
            and "link" in news 
            and news.get("date") in {TODAY, YESTERDAY}
        ]

        # Add valid ESG news to the beginning of "ESG_소식"
        fetched_news["ESG_소식"] = valid_esg_news + fetched_news["ESG_소식"]
    # Check if yesterday's file exists
    if os.path.exists(yesterday_filename):
        with open(yesterday_filename, "r", encoding="utf-8") as file:
            yesterday_news = json.load(file)
    else:
        yesterday_news = {}

    # Collect yesterday's titles for comparison
    yesterday_titles = set()
    for key, news_list in yesterday_news.items():
        if isinstance(news_list, list):
            yesterday_titles.update(news["title"] for news in news_list if "title" in news)

    # Remove duplicates from fetched_news
    for key, news_list in fetched_news.items():
        if isinstance(news_list, list):
            fetched_news[key] = [
                news for news in news_list
                if news.get("title") not in yesterday_titles
            ]

    # Debugging: Print the fetched_news structure before saving
    print("Final fetched news data structure after removing duplicates:")
    print(json.dumps(fetched_news, ensure_ascii=False, indent=4))

    # Save the updated news list to a JSON file
    with open(today_filename, "w", encoding="utf-8") as file:
        json.dump(fetched_news, file, ensure_ascii=False, indent=4)  # JSON 파일 저장
    print(f"Json file saved as {today_filename}.")

def preprocess_newslist(file_path, level, selected_domain):
    """gpt로 요약/인사이트 생성"""
    json_file_path = os.path.join(
        ".", "editor", "json", f"{TODAY}_json_output_{selected_domain}.json"
    )
    if not os.path.exists(file_path):
        print("Error: 파일이 존재하지 않습니다.")
        return

    # 어제 파일에서 title 리스트 가져오기
    yesterday_file_path = f"./editor/json/{YESTERDAY}_json_output_{selected_domain}.json"
    yesterday_titles = []

    if os.path.exists(yesterday_file_path):
        with open(yesterday_file_path, "r", encoding="utf-8") as file:
            try:
                yesterday_news = json.load(file)
                for key, news_list in yesterday_news.items():
                    if isinstance(news_list, list):
                        yesterday_titles.extend(news["title"] for news in news_list if "title" in news)
            except json.JSONDecodeError as e:
                print(f"어제 JSON 파일 읽기 오류: {e}")

    # 파일 확장자에 따라 JSON 파일 읽기
    file_extension = os.path.splitext(file_path)[-1].lower()
    
    if file_extension == ".json":
        # JSON 파일 읽기
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                fetched_news = json.load(file)  # JSON 파싱
                print("JSON 파일이 성공적으로 불러와졌습니다.")
            except json.JSONDecodeError as e:
                print(f"JSON 파일 읽기 오류: {e}")
                return
    else:
        print("지원하지 않는 파일 형식입니다. JSON 파일을 사용해주세요.")
        return

    print(f"Preprocess newslist for domain: {selected_domain}...")


    if level in ["basic"]:
        print("entered basic mode")
        print("yesterday's file")
        print(yesterday_titles)
        preprocessed_news = preprocess_news(selected_domain, fetched_news, yesterday_titles)

        with open(json_file_path, "w", encoding="utf-8") as file:
            file.write(preprocessed_news)
        print(f"Json file saved as '{json_file_path}'.")

        print(f"{level.capitalize()} Preprocessing completed!")
    elif level in ["premium"]:
        print("entered premium mode")
        #준헌이가 개발 분요한 부분

        
        
def postprocess_newslist(file_path, selected_domain):

    html_file_path = os.path.join(
        ".", "editor", "html", f"{TODAY}_html_output_{selected_domain}.html"
    )
        # 파일 확장자에 따라 JSON 파일 읽기
    file_extension = os.path.splitext(file_path)[-1].lower()
    
    if file_extension == ".json":
        # JSON 파일 읽기
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                fetched_news = json.load(file)  # JSON 파싱
                print("JSON 파일이 성공적으로 불러와졌습니다.")
            except json.JSONDecodeError as e:
                print(f"JSON 파일 읽기 오류: {e}")
                return
    else:
        print("지원하지 않는 파일 형식입니다. JSON 파일을 사용해주세요.")
        return

    print(f"Preprocess newslist for domain: {selected_domain}...")

    print(fetched_news)

    postprocessed_news = postprocess_news(fetched_news, selected_domain)

    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(postprocessed_news)

    print(f"HTML file saved as '{html_file_path}'.")


def main():
    """사용자 선택에 따라 기능 실행"""

    while True:
        print("\nSelect a domain:")
        print("1. AI")
        print("2. ESG")
        print("3. Interior")
        print("4. Semiconductor")
        print("0. Exit")

        choice = input("Enter your choice (0-4): ") 

        if choice == "1":
            select_domain = "ai"
            break
        elif choice == "2":
            select_domain = "esg"
            break
        elif choice == "3":
            select_domain = "interior"
            break
        elif choice == "4":
            select_domain = "semiconductor"
            break
        elif choice == "0":
            break
        else:
            print("Invalid input. Please try again.")

    html_file_path = os.path.join(
        ".", "editor", "html", f"{TODAY}_html_output_{select_domain}.html"
    )

    json_file_path_raw =  os.path.join(
        ".", "crawler", "json", f"{TODAY}_json_newslist_{select_domain}.json"
    )

    json_file_path_preprocessed =  os.path.join(
        ".", "editor", "json", f"{TODAY}_json_output_{select_domain}.json"
    )
    if choice == "0":
        print("Exiting the application...")
    else:
        while True:            
            print("\nSelect an option:")
            
            print("1. Full Code Run")
            print("2. Run Crawler")
            print(f"3. Run Preprocessor(Basic, from {json_file_path_raw})")
            print(f"4. Run Preprocessor(Premium, from {json_file_path_raw})")
            print(f"5. Run Postprocessor")
            print(f"6. Run Emailer (from {html_file_path})")
            print(f"7. Run Uploader (Tistory, from {html_file_path})")
            print(f"8. Run Uploader (Kakao, from {json_file_path_preprocessed})")
            print("0. Exit")

            choice = input("Enter your choice (0-8): ")

            if choice == "1":
                full_code_run(select_domain)
            elif choice == "2":
                get_newslist(select_domain)    
            elif choice == "3":
                preprocess_newslist(json_file_path_raw, "basic", select_domain)  
            elif choice == "4":
                preprocess_newslist(json_file_path_raw, "premium", select_domain)  
            elif choice == "5":
                postprocess_newslist(json_file_path_preprocessed, select_domain)
            elif choice == "6":
                send_email_with_file(html_file_path, select_domain)
            elif choice == "7":
                tistory_uploader_with_file(html_file_path, select_domain)  # 도메인은 ai로 설정
            elif choice == "8":
                kakao_uploader_with_file(json_file_path_preprocessed, select_domain)
            elif choice == "0":
                print("Exiting the application...")
                break
            else:
                print("Invalid input. Please try again.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
