from datetime import datetime, timedelta  # 날짜와 시간 처리를 위한 모듈 가져오기
import os
from dotenv import load_dotenv
from crawler.contact_update import esg_get_email_list


# 이메일 설정 (보안상 비밀번호는 환경변수 또는 보안 모듈 사용 권장)
SEMICONDUCTOR_EMAIL = {
    'sender': os.getenv('EMAIL_SENDER'),
    'receivers': ['asaac.corp@gmail.com'],
    'bcc': ['stephencho820@gmail.com', 'jxli917@naver.com', 'kehdgnsdl77@naver.com'],
    'password': os.getenv('EMAIL_PASSWORD')  # 환경변수로부터 비밀번호를 가져옴
}

INTERIOR_EMAIL = {
    'sender': os.getenv('EMAIL_SENDER'),
    'receivers': ['asaac.corp@gmail.com'],
    'bcc': ['stephencho820@gmail.com', 'glaubeaj@naver.com'],
    'password': os.getenv('EMAIL_PASSWORD')  # 환경변수로부터 비밀번호를 가져옴
}

ESG_EMAIL = {
    'sender': os.getenv('EMAIL_SENDER'),
    'receivers': ['asaac.corp@gmail.com', 'asaacco@naver.com'],
    'bcc': esg_get_email_list(),
    #'bcc': ['junheon.lee@kakao.com', 'asaac.corp@gmail.com', 'asaacco@naver.com'],
    'password': os.getenv('EMAIL_PASSWORD')  # 환경변수로부터 비밀번호를 가져옴
}

STOCK_EMAIL = {
    'sender': os.getenv('EMAIL_SENDER'),
    'receivers': ['asaac.corp@gmail.com'],
    'bcc': ['stephencho820@gmail.com', 'jeihyuck@naver.com','infynylg@gmail.com'],
    'password': os.getenv('EMAIL_PASSWORD')  # 환경변수로부터 비밀번호를 가져옴
}

AI_EMAIL = {
    'sender': os.getenv('EMAIL_SENDER'),
    'receivers': ['asaac.corp@gmail.com'],
    'bcc': ['junheon.lee@kakao.com', 'asaac.corp@gmail.com'],
    #'bcc': ['asaac.corp@gmail.com', 'asaacco@naver.com'],
    'password': os.getenv('EMAIL_PASSWORD')  # 환경변수로부터 비밀번호를 가져옴
}

DOMAINS = {
    "semiconductor": SEMICONDUCTOR_EMAIL,
    "interior": INTERIOR_EMAIL,
    "esg": ESG_EMAIL,
    "ai": AI_EMAIL
}
