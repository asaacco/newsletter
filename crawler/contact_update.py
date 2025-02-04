from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Google Sheets API 인증 및 설정
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # 인증 파일 경로

# 시트 정보
SPREADSHEET_ID = '1dlw-fFLB2L9bm0u-brV1mQeyPI0BWtypyUMM8yDPMw0'  # Google Sheet ID

SHEET_NAME = 'Form Responses 2'  # 가져올 시트 이름
RANGE_C = f'{SHEET_NAME}!C2:C'  # C열 (구독 해지 여부)
RANGE_D = f'{SHEET_NAME}!D2:D'  # D열 (이메일 리스트)
OUTPUT_FILE = 'email_list.txt'  # 저장할 파일명

def get_filtered_email_list():
    """Google Sheets에서 구독 상태 확인 후 이메일 리스트 필터링"""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # C열과 D열 데이터 가져오기
    sheet = service.spreadsheets()
    result_c = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_C).execute()
    result_d = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_D).execute()

    values_c = result_c.get('values', [])
    values_d = result_d.get('values', [])

    # 이메일과 구독 상태 매핑
    subscription_data = [(values_c[i][0] if i < len(values_c) else "", values_d[i][0] if i < len(values_d) else "") for i in range(max(len(values_c), len(values_d)))]

    # "구독 해지"된 이메일 주소를 수집
    unsubscribed_emails = {email for status, email in subscription_data if status == "구독 해지" and email}

    # "구독 해지"된 이메일을 수신자 리스트에서 제외
    filtered_email_list = [
        email for status, email in subscription_data if email and email not in unsubscribed_emails
    ]

    # 중복 제거
    unique_email_list = list(set(filtered_email_list))
    return unique_email_list, list(unsubscribed_emails)

def save_to_txt_file(email_list):
    """이메일 리스트를 파일로 저장"""
    # 리스트를 쉼표로 구분된 문자열로 변환
    email_string = ", ".join(email_list)

    # 파일에 저장
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
        file.write(email_string)
    print(f"Email list has been saved to '{OUTPUT_FILE}'")

def print_summary(email_list, unsubscribed_emails):
    """요약 정보 출력"""
    total_emails = len(email_list)
    unsubscribed_count = len(unsubscribed_emails)

    print(f"오늘 뉴스레터 수신자는 총 {total_emails}명입니다.")
    if unsubscribed_count > 0:
        unsubscribed_list = ", ".join(unsubscribed_emails)
        print(f"구독 해지는 총 {unsubscribed_count}명입니다: {unsubscribed_list}")
    else:
        print("구독 해지된 이메일이 없습니다.")



def esg_get_email_list():
    filtered_email_list, unsubscribed_emails = get_filtered_email_list()
    save_to_txt_file(filtered_email_list)
    print_summary(filtered_email_list, unsubscribed_emails)
    return filtered_email_list