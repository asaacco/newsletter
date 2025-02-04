import os
import platform
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoAlertPresentException, TimeoutException

import pyperclip
import pyautogui
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager

import configTitle
import configTag

# 가상 디스플레이 설정 (Windows 환경에서는 비활성화)
if platform.system() != "Windows":
    from pyvirtualdisplay import Display
    os.environ["DISPLAY"] = ":99.0"
    os.environ["XAUTHORITY"] = "/dev/null"
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    print("가상 디스플레이가 설정되었습니다.")
else:
    print("Windows 환경이므로 가상 디스플레이를 사용하지 않습니다.")

# 환경 변수 로드
load_dotenv()
TODAY = datetime.now().strftime("%Y-%m-%d")

def tistory_uploader(content, selected_domain):
    """
    Tistory 블로그에 자동으로 글을 업로드하는 함수
    :param content: 업로드할 HTML 내용
    :param selected_domain: 선택된 카테고리 도메인 (예: 'esg', 'ai')
    """
    # 로그인 및 글쓰기 URL
    TISTORY_URL = "https://asaacco.tistory.com/manage/newpost"
    LOGIN_URL = "https://accounts.kakao.com/login/?continue=https%3A%2F%2Fwww.tistory.com"

    # 계정 정보 로드
    TISTORY_USER_ID = os.getenv("TISTORY_USER_ID")
    TISTORY_USER_PW = os.getenv("TISTORY_USER_PW")
    secure = 'blank'  # 보안을 위해 비밀번호 입력 후 클립보드 초기화

    # 카테고리 및 태그 설정
    TITLE = configTitle.DOMAINS.get(selected_domain, "")
    TAGS = configTag.DOMAINS.get(selected_domain, [])

    # Selenium 크롬 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUI 없이 실행
    chrome_options.add_argument("--no-sandbox")  # 권한 문제 해결
    chrome_options.add_argument("--disable-gpu")  # GPU 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 문제 해결
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # 웹드라이버 실행
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)
    driver.implicitly_wait(5)
    driver.maximize_window()

    # 카카오 로그인
    driver.get(LOGIN_URL)
    id_field = driver.find_element(By.CSS_SELECTOR, "#loginId")
    id_field.click()
    pyperclip.copy(TISTORY_USER_ID)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)

    pw_field = driver.find_element(By.CSS_SELECTOR, "#password")
    pw_field.click()
    pyperclip.copy(TISTORY_USER_PW)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyperclip.copy(secure)

    driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div/form/div[4]/button[1]').click()
    time.sleep(2)

    # 글쓰기 페이지 이동
    driver.get(TISTORY_URL)
    time.sleep(2)

    # HTML 모드로 변경
    try:
        dropdown_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#editor-mode-layer-btn-open")))
        dropdown_button.click()
        dropdown_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="editor-mode-html"]')))
        dropdown_option.click()
    except TimeoutException:
        print("HTML 모드 전환 실패. 스크린샷을 저장합니다.")
        driver.save_screenshot("error_screenshot.png")
        driver.quit()
        return -1

    # 제목 입력
    title_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#post-title-inp")))
    title_field.clear()
    title_field.send_keys(f"{TODAY} {TITLE} 일일 주요 보도자료")

    # 본문 입력 (HTML 에디터 사용)
    driver.execute_script("""
        var editor = document.querySelector('.CodeMirror').CodeMirror;
        editor.setValue(arguments[0]);  
        editor.focus();
        editor.getInputField().dispatchEvent(new Event('input', { bubbles: true }));
        editor.getInputField().dispatchEvent(new Event('change', { bubbles: true }));
    """, content)
    time.sleep(2)

    # 태그 입력
    tag_input = driver.find_element(By.CSS_SELECTOR, "#tagText")
    for tag in TAGS:
        tag_input.send_keys(tag)
        tag_input.send_keys(Keys.ENTER)
        time.sleep(0.5)

    print("모든 태그가 입력되었습니다.")

    # 등록 버튼 클릭
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#publish-layer-btn")))
    submit_button.click()
    final_submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#publish-btn")))
    final_submit_button.click()

    print("게시글이 성공적으로 등록되었습니다!")
    driver.quit()
    return 0
