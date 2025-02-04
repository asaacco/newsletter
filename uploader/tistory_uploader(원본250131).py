# Tistory에 자동 업로드 하는 모듈
# 준헌이가 개발 분요한 부분

from pyvirtualdisplay import Display
import os

# 가상 디스플레이 시작
os.environ["DISPLAY"] = ":99.0"
os.environ["XAUTHORITY"] = "/dev/null"

display = Display(visible=0, size=(1920, 1080))
display.start()

import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

import configTitle
import configTag
from dotenv import load_dotenv

# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime

# 환경 변수 설정
load_dotenv()

import pyautogui

print("가상 디스플레이가 설정되었습니다.")

TODAY = datetime.now().strftime("%Y-%m-%d")

def tistory_uploader(content, selected_domain):

    TISTORY_URL = "https://asaacco.tistory.com/manage/newpost"
    LOGIN_URL = "https://accounts.kakao.com/login/?continue=https%3A%2F%2Fkauth.kakao.com%2Foauth%2Fauthorize%3Fis_popup%3Dfalse%26ka%3Dsdk%252F2.7.3%2520os%252Fjavascript%2520sdk_type%252Fjavascript%2520lang%252Fko-KR%2520device%252FWin32%2520origin%252Fhttps%25253A%25252F%25252Fwww.tistory.com%26auth_tran_id%3DgQNeDDVOqs5dQlpPKIv3OOUj~Y5GeRz0zmKidzpLmxRBHUBuiSEsf-M.85.X%26response_type%3Dcode%26state%3DaHR0cHM6Ly93d3cudGlzdG9yeS5jb20v%26redirect_uri%3Dhttps%253A%252F%252Fwww.tistory.com%252Fauth%252Fkakao%252Fredirect%26client_id%3D3e6ddd834b023f24221217e370daed18%26through_account%3Dtrue&talk_login=hidden#login"  # 네이버 카페 주소

    load_dotenv()
    TISTORY_USER_ID = os.getenv("TISTORY_USER_ID")
    TISTORY_USER_PW = os.getenv("TISTORY_USER_PW")

    secure='blank'
    # ESG 도메인에서 'ESG_소식'과 'DX_소식'의 리스트 값 가져오기
    TITLE = configTitle.DOMAINS[selected_domain]
    TAGS = configTag.DOMAINS.get(selected_domain, [])

    # 브라우저 꺼짐 방지
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUI 없이 실행
    chrome_options.add_argument("--no-sandbox")  # 권한 문제 해결
    chrome_options.add_argument("--disable-gpu")  # GPU 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 문제 해결
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("detach", True)

    # 불필요한 에러메세지 없애기
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)
    # 웹페이지 해당 주소 이름
    driver.implicitly_wait(5)  # 웹페이지가 로딩될 때까지 5초 기다림
    driver.maximize_window()  # 화면 최대화
    driver.get(LOGIN_URL)
    # 아이디 입력창
    id = driver.find_element(By.CSS_SELECTOR, "#mainContent > div > div > form > div.item_form.fst > div")
    id.click()
    pyperclip.copy(TISTORY_USER_ID)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(2)

    # 비밀번호 입력창
    pw = driver.find_element(By.CSS_SELECTOR, "#password--2")
    pw.click()
    pyperclip.copy(TISTORY_USER_PW)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(2)
    pyperclip.copy(secure)  #비밀번호 보안을 위해 클립보드에 blank 저장
            

    # 로그인 버튼
    driver.find_element(By.XPATH,'//*[@id="mainContent"]/div/div/form/div[4]/button[1]').click()
    time.sleep(2)

    # 글쓰기 버튼 클릭 
    driver.get(TISTORY_URL)
    ##CSS selector : cafe-info-data > div.cafe-write-btn > a
    # element = driver.find_element(By.CSS_SELECTOR, "#container > main > aside > div.box-profile > div > div.profile-btn-group.member > button.btn-g.btn-primary.btn-write")
    # element.click()  # 클릭 이벤트 수행 (필요시)
    # time.sleep(3)
    time.sleep(2)

    try:
        # 모달창(Alert)으로 전환 시도
        alert = driver.switch_to.alert
        print("모달창이 있습니다. 확인 버튼을 클릭합니다.")
        alert.dismiss()  # 취소 버튼 클릭
    except NoAlertPresentException:
        print("모달창이 존재하지 않습니다. 다음 단계로 넘어갑니다.")

    # # 새로운 창으로 전환
    # WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)  # 새 창 열리기를 대기
    # new_window = driver.window_handles[-1]  # 새 창 핸들 (맨 마지막 창)
    # driver.switch_to.window(new_window)  # 새 창으로 전환
    time.sleep(2)

    # 드롭다운 버튼 클릭
    print("드롭다운 클릭")
    dropdown_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#editor-mode-layer-btn-open"))
    )
    try:
        dropdown_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#editor-mode-layer-btn-open"))
        )
        dropdown_button.click()
    except TimeoutException:
        print("드롭다운 버튼을 찾을 수 없습니다. 페이지 상태를 확인하세요.")
        driver.save_screenshot("error_screenshot.png")
        print("스크린샷이 저장되었습니다: error_screenshot.png")
        raise
    
    dropdown_button.click()
    print("html 선택")
    # 'html' 옵션 선택
    dropdown_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="editor-mode-html"]'))
    )
    dropdown_option.click()

    # 모달창(브라우저 Alert)으로 전환
    alert = driver.switch_to.alert

    # 확인 버튼 클릭
    alert.accept()

    # 드롭다운 버튼 클릭
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#category-btn"))
    )
    dropdown_button.click()

    # '일일 브리핑' 옵션 선택
    if selected_domain == 'esg':
        dropdown_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="category-item-749422"]'))
        )
        dropdown_option.click()

    elif selected_domain == 'ai':
        dropdown_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="category-item-749419"]'))
        )
        dropdown_option.click()
    # 제목 입력

    title_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#post-title-inp"))
    )
    title_field.clear()  # 기존 내용 삭제
    title_field.send_keys(f"{TODAY} {TITLE} 일일 주요 보도자료")

    # # CodeMirror의 textarea 요소를 찾아 값 입력
    # textarea = driver.find_element(By.CSS_SELECTOR, ".CodeMirror textarea")

    # # textarea 클릭 및 값 입력
    # textarea.click()
    # textarea.clear()

    # # 키보드 입력으로 내용 입력 (줄바꿈 포함)
    # for line in content.split("\n"):
    #     textarea.send_keys(line)
    #     textarea.send_keys(Keys.SHIFT, Keys.ENTER)  # 줄바꿈 입력
    driver.execute_script("""
        var editor = document.querySelector('.CodeMirror').CodeMirror;

        // 에디터에 HTML 내용 설정
        editor.setValue(arguments[0]);  
        editor.focus();

        // 입력 및 변경 이벤트 트리거
        var inputEvent = new Event('input', { bubbles: true });
        var changeEvent = new Event('change', { bubbles: true });

        // 실제 입력 필드에 이벤트 발생
        editor.getInputField().dispatchEvent(inputEvent);
        editor.getInputField().dispatchEvent(changeEvent);

        // 임의의 문자 입력 후 삭제
        editor.replaceSelection(" ");  // 공백 한 칸 입력
        editor.replaceSelection("");   // 공백 삭제

        // 최종 입력 및 변경 이벤트 트리거
        editor.getInputField().dispatchEvent(inputEvent);
        editor.getInputField().dispatchEvent(changeEvent);

        // 에디터 포커스 이동
        editor.getInputField().dispatchEvent(new Event('blur', { bubbles: true }));
    """, content)
    time.sleep(5)
    # 테그 입력
    tag_input = driver.find_element(By.CSS_SELECTOR, "#tagText")
        # TAG 리스트를 순회하며 입력
    for tag in TAGS:
        tag_input.send_keys(tag)  # 태그 입력
        tag_input.send_keys(Keys.ENTER)  # 엔터 키 입력
        time.sleep(0.5)  # 입력 후 약간의 딜레이 (필요 시 조정)
        
    print("모든 태그가 입력되었습니다.")


    
    # 등록 버튼 클릭
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#publish-layer-btn"))
    )
    submit_button.click()  # 등록 버튼 클릭

    final_submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#publish-btn"))
    )
    final_submit_button.click()  # 등록 버튼 클릭


    print("게시글이 성공적으로 등록되었습니다!")

    driver.quit()

    return 0




