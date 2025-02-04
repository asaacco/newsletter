# NAVER에 자동 업로드 하는 모듈

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


# 사용 예시
URL = "https://cafe.naver.com/asaacco"  # 네이버 카페 주소
USER_ID = "asaacco@naver.com"  # 네이버 아이디
USER_PW = "qhdks!23"  # 네이버 비밀번호


def post_to_naver_cafe(title, content, tags):
    # Selenium WebDriver 설정
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)

    try:
        # 네이버 로그인 페이지로 이동
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(2)

        # 아이디 입력
        driver.find_element(By.ID, "id").send_keys(USER_ID)
        time.sleep(1)

        # 비밀번호 입력
        driver.find_element(By.ID, "pw").send_keys(USER_PW)
        time.sleep(1)

        # 로그인 버튼 클릭
        driver.find_element(By.ID, "log.login").click()
        time.sleep(3)

        # 카페 이동
        driver.get(URL)
        time.sleep(3)

        # 글쓰기 버튼 클릭 (카페별로 버튼 위치가 다를 수 있음)
        write_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".button-writing")))
        write_button.click()
        time.sleep(3)

        # 카테고리 선택 (카테고리 이름이 "일일 브리핑"일 경우)
        category_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "menuCategoryId")))
        category_dropdown.click()
        time.sleep(1)
        category_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[text()='일일 브리핑']")))
        category_option.click()
        time.sleep(1)
        
        # 제목 입력
        title_box = wait.until(EC.presence_of_element_located((By.ID, "subject")))
        title_box.send_keys(title)
        time.sleep(1)

        # 본문 입력 (HTML 지원)
        content_box = driver.find_element(By.ID, "content")
        content_box.send_keys(content)
        time.sleep(1)

        # 태그 입력
        tags_box = wait.until(EC.presence_of_element_located((By.ID, "tags")))
        tags_box.send_keys(", ".join(tags))  # 태그를 쉼표로 구분하여 입력
        time.sleep(1)

        # 등록 버튼 클릭
        submit_button = driver.find_element(By.ID, "btn-submit")
        submit_button.click()
        time.sleep(3)

        print("게시글이 성공적으로 등록되었습니다!")

    except Exception as e:
        print(f"에러 발생: {e}")

    finally:
        driver.quit()
