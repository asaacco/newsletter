import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configDomain
import configEmail
import configTitle
import time
from datetime import datetime
from itertools import islice

TODAY = datetime.now().strftime("%Y-%m-%d")
# HTML 템플릿 파일에서 내용을 읽어오는 함수

def chunk_list(data, chunk_size):
    it = iter(data)
    while True:
        chunk = list(islice(it, chunk_size))
        if not chunk:
            break
        yield chunk

def send_email(result_html, selected_domain):
    # 도메인별 이메일 설정 가져오기
    EMAIL_CONFIG = configEmail.DOMAINS.get(selected_domain.lower())
    if not EMAIL_CONFIG:
        raise ValueError(f"Invalid domain selected: {selected_domain}")

    sender = EMAIL_CONFIG['sender']
    bcc = EMAIL_CONFIG['bcc']
    password = EMAIL_CONFIG['password']

    domain_title = configTitle.DOMAINS[selected_domain]

    BATCH_SIZE = 30  # BCC 그룹 크기 유지
    try:
        for index, chunk in enumerate(chunk_list(bcc, BATCH_SIZE)):
            try:
                # SMTP 서버 연결 (배치마다 재연결)
                with smtplib.SMTP_SSL("smtp.naver.com", 465, timeout=120) as server:
                    print(f"Connecting to SMTP server for batch {index + 1}...")
                    server.login(sender, password)

                    # 이메일 메시지 구성
                    msg = MIMEMultipart()
                    msg['From'] = sender
                    msg['To'] = "Undisclosed Recipients"
                    msg['Subject'] = f"{TODAY} {domain_title} 일일 주요 보도자료"
                    msg.attach(MIMEText(result_html, "html"))

                    # 이메일 전송
                    print(f"Sending email batch {index + 1} to: {chunk}")
                    server.sendmail(sender, chunk, msg.as_string())
                    print(f"Batch {index + 1} sent successfully!")

                # 각 배치 전송 후 대기 시간
                time.sleep(10)  # 10초 대기 (전송 간 서버 부담 최소화)

            except Exception as e:
                print(f"Failed to send email to batch {index + 1}: {e}")
                continue  # 다음 배치로 넘어감

        print("All Emails sent successfully!")

    except Exception as e:
        print(f"Failed to process email sending: {e}")

    return 0