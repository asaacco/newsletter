import json
import logging
import os
import time
import shutil
from datetime import datetime, timedelta

# 필요한 모듈 임포트 (중복 제거)
from crawler.news_crawler import fetch_news
from crawler.rss_news_crawler import crawl_esgnews_rss
from editor.preprocessor import preprocess_news
from editor.postprocessor import postprocess_news
from emailer.email_sender import send_email
from uploader.tistory_uploader import tistory_uploader
from uploader.kakao_uploader import kakao_uploader
from uploader.naver_uploader import post_to_naver_cafe

# 날짜 상수
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
ARCHIVE_THRESHOLD_DAYS = 7  # 파일 아카이브 기준

def send_email_with_file(file_path, selected_domain):
    """output.html에 저장된 내용을 사용해 이메일 전송"""
    if not os.path.exists(file_path):
        logging.error(f"Error: {file_path} 파일이 존재하지 않습니다.")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        postprocessed_news = file.read()

    logging.info(f"Sending email with content from '{file_path}'...")
    try:
        send_email(postprocessed_news, selected_domain)
        logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"이메일 전송 중 오류 발생: {e}")

def kakao_uploader_with_file(file_path, selected_domain):
    try:
        content = kakao_uploader(file_path, selected_domain)
    except Exception as e:
        logging.error(f"Kakao 업로드 중 오류 발생: {e}")
        return

    save_path = os.path.join(".", "uploader", "kakao", f"{TODAY}_kakao_letter_{selected_domain}.txt")
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(content)

    logging.info(f"파일이 {save_path}에 저장되었습니다.")
    logging.info("Kakao upload completed!")

def tistory_uploader_with_file(file_path, selected_domain):
    """output.html에 저장된 내용을 사용해 티스토리 업로드"""
    if not os.path.exists(file_path):
        logging.error(f"Error: {file_path} 파일이 존재하지 않습니다.")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        postprocessed_news = file.read()

    logging.info(f"Uploading to Tistory for domain: {selected_domain}...")
    try:
        tistory_uploader(postprocessed_news, selected_domain)
        logging.info("Tistory upload completed!")
    except Exception as e:
        logging.error(f"Tistory 업로드 중 오류 발생: {e}")

def get_newslist(selected_domain):
    """뉴스 크롤링 및 중복 제거"""
    today_filename = f"./crawler/json/{TODAY}_json_newslist_{selected_domain}.json"
    yesterday_filename = f"./crawler/json/{YESTERDAY}_json_newslist_{selected_domain}.json"

    logging.info(f"Get newslist for domain: {selected_domain}...")

    # 뉴스 크롤링
    fetched_news = fetch_news(selected_domain)

    # ESG 도메인의 경우 RSS 추가 크롤링
    if selected_domain == 'esg':
        json_data = crawl_esgnews_rss()
        esg_rss_news = json.loads(json_data)
        if "ESG_소식" not in fetched_news:
            fetched_news["ESG_소식"] = []

        valid_esg_news = [
            news for news in esg_rss_news
            if isinstance(news, dict) and "title" in news and "link" in news and news.get("date") in {TODAY, YESTERDAY}
        ]
        fetched_news["ESG_소식"] = valid_esg_news + fetched_news["ESG_소식"]

    # 어제의 뉴스 불러오기
    if os.path.exists(yesterday_filename):
        with open(yesterday_filename, "r", encoding="utf-8") as file:
            yesterday_news = json.load(file)
    else:
        yesterday_news = {}

    yesterday_titles = set()
    for key, news_list in yesterday_news.items():
        if isinstance(news_list, list):
            yesterday_titles.update(news["title"] for news in news_list if "title" in news)

    # 중복 제거
    for key, news_list in fetched_news.items():
        if isinstance(news_list, list):
            fetched_news[key] = [
                news for news in news_list
                if news.get("title") not in yesterday_titles
            ]

    logging.info("Final fetched news data structure after removing duplicates:")
    logging.info(json.dumps(fetched_news, ensure_ascii=False, indent=4))

    with open(today_filename, "w", encoding="utf-8") as file:
        json.dump(fetched_news, file, ensure_ascii=False, indent=4)
    logging.info(f"Json file saved as {today_filename}.")

def preprocess_newslist(file_path, level, selected_domain):
    """GPT를 이용한 뉴스 전처리 및 결과 저장"""
    json_file_path = os.path.join(".", "editor", "json", f"{TODAY}_json_output_{selected_domain}.json")
    
    if not os.path.exists(file_path):
        logging.error("Error: 파일이 존재하지 않습니다.")
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
                logging.error(f"어제 JSON 파일 읽기 오류: {e}")

    # 파일 확장자 확인 후 JSON 파일 읽기
    file_extension = os.path.splitext(file_path)[-1].lower()
    if file_extension == ".json":
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                fetched_news = json.load(file)
                logging.info("JSON 파일이 성공적으로 불러와졌습니다.")
            except json.JSONDecodeError as e:
                logging.error(f"JSON 파일 읽기 오류: {e}")
                return
    else:
        logging.error("지원하지 않는 파일 형식입니다. JSON 파일을 사용해주세요.")
        return

    logging.info(f"Preprocess newslist for domain: {selected_domain} in {level} mode...")
    # 전처리 함수 호출 시 mode 인자를 level 값으로 전달 (basic 또는 premium)
    response = preprocess_news(selected_domain, fetched_news, yesterday_titles, mode=level)
    
    if response:
        with open(json_file_path, "w", encoding="utf-8") as file:
            file.write(response)
        logging.info(f"Json file saved as '{json_file_path}'.")
        logging.info(f"{level.capitalize()} Preprocessing completed!")
    else:
        logging.error("전처리 중 오류가 발생했습니다.")

def postprocess_newslist(file_path, selected_domain):
    """JSON 전처리 결과를 HTML 파일로 후처리"""
    html_file_path = os.path.join(".", "editor", "html", f"{TODAY}_html_output_{selected_domain}.html")
    file_extension = os.path.splitext(file_path)[-1].lower()
    if file_extension == ".json":
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                fetched_news = json.load(file)
                logging.info("JSON 파일이 성공적으로 불러와졌습니다.")
            except json.JSONDecodeError as e:
                logging.error(f"JSON 파일 읽기 오류: {e}")
                return
    else:
        logging.error("지원하지 않는 파일 형식입니다. JSON 파일을 사용해주세요.")
        return

    logging.info(f"Postprocess newslist for domain: {selected_domain}...")
    postprocessed_news = postprocess_news(fetched_news, selected_domain)
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(postprocessed_news)
    logging.info(f"HTML file saved as '{html_file_path}'.")

def full_code_run(selected_domain):
    """전체 파이프라인 실행: 크롤링 -> 전처리 -> 후처리 -> 이메일 및 업로드"""
    try:
        get_newslist(selected_domain)
    except Exception as e:
        logging.error(f"뉴스 크롤링 중 오류 발생: {e}")
        return

    json_file_path_raw = f"./crawler/json/{TODAY}_json_newslist_{selected_domain}.json"
    json_file_path_preprocessed = f"./editor/json/{TODAY}_json_output_{selected_domain}.json"
    html_file_path = f"./editor/html/{TODAY}_html_output_{selected_domain}.html"

    try:
        # premium 모드로 전처리 호출 (혹은 필요에 따라 basic 모드를 선택)
        preprocess_newslist(json_file_path_raw, "premium", selected_domain)
    except Exception as e:
        logging.error(f"전처리 중 오류 발생: {e}")
        return

    try:
        postprocess_newslist(json_file_path_preprocessed, selected_domain)
    except Exception as e:
        logging.error(f"후처리 중 오류 발생: {e}")
        return

    try:
        send_email_with_file(html_file_path, selected_domain)
    except Exception as e:
        logging.error(f"이메일 전송 중 오류 발생: {e}")

    try:
        tistory_uploader_with_file(html_file_path, selected_domain)
    except Exception as e:
        logging.error(f"Tistory 업로드 중 오류 발생: {e}")

    try:
        kakao_uploader_with_file(json_file_path_preprocessed, selected_domain)
    except Exception as e:
        logging.error(f"Kakao 업로드 중 오류 발생: {e}")

def archive_old_files(directory, days_threshold=ARCHIVE_THRESHOLD_DAYS):
    """
    지정한 디렉토리 내의 파일 중 수정일자가 지정된 기간(days_threshold)보다 오래된 파일을
    ./archive/<디렉토리명>/ 로 이동합니다.
    """
    archive_dir = os.path.join(".", "archive", os.path.basename(directory))
    os.makedirs(archive_dir, exist_ok=True)
    now = time.time()
    threshold = days_threshold * 86400  # days to seconds

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > threshold:
                try:
                    shutil.move(file_path, os.path.join(archive_dir, filename))
                    logging.info(f"Archived {file_path} to {archive_dir}")
                except Exception as e:
                    logging.error(f"파일 이동 실패: {file_path} 에러: {e}")

def main():
    """사용자 선택에 따라 기능 실행"""
    while True:
        print("\nSelect a domain:")
        print("1. AI")
        print("2. ESG")
        print("3. Interior")
        print("4. Semiconductor")
        print("0. Exit")

        choice = input("Enter your choice (0-4): ").strip()
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
            logging.info("Exiting the application...")
            return
        else:
            print("Invalid input. Please try again.")

    html_file_path = os.path.join(".", "editor", "html", f"{TODAY}_html_output_{select_domain}.html")
    json_file_path_raw = os.path.join(".", "crawler", "json", f"{TODAY}_json_newslist_{select_domain}.json")
    json_file_path_preprocessed = os.path.join(".", "editor", "json", f"{TODAY}_json_output_{select_domain}.json")

    while True:
        print("\nSelect an option:")
        print("1. Full Code Run (전체 파이프라인 실행)")
        print("2. Run Crawler")
        print(f"3. Run Preprocessor (Basic, from {json_file_path_raw})")
        print(f"4. Run Preprocessor (Premium, from {json_file_path_raw})")
        print(f"5. Run Postprocessor")
        print(f"6. Run Emailer (from {html_file_path})")
        print(f"7. Run Uploader (Tistory, from {html_file_path})")
        print(f"8. Run Uploader (Kakao, from {json_file_path_preprocessed})")
        print("9. Archive old files (파일 아카이브)")
        print("0. Exit")

        option = input("Enter your choice (0-9): ").strip()

        if option == "1":
            full_code_run(select_domain)
        elif option == "2":
            get_newslist(select_domain)
        elif option == "3":
            preprocess_newslist(json_file_path_raw, "basic", select_domain)
        elif option == "4":
            preprocess_newslist(json_file_path_raw, "premium", select_domain)
        elif option == "5":
            postprocess_newslist(json_file_path_preprocessed, select_domain)
        elif option == "6":
            send_email_with_file(html_file_path, select_domain)
        elif option == "7":
            tistory_uploader_with_file(html_file_path, select_domain)
        elif option == "8":
            kakao_uploader_with_file(json_file_path_preprocessed, select_domain)
        elif option == "9":
            archive_old_files("./crawler/json")
            archive_old_files("./editor/html")
            archive_old_files("./editor/json")
        elif option == "0":
            logging.info("Exiting the application...")
            break
        else:
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
