import os
import requests
from datetime import date

# LinkedIn API 설정
ACCESS_TOKEN = "your_access_token"
API_URL = "https://api.linkedin.com/v2/ugcPosts"

# 오늘 날짜와 파일 경로 설정
TODAY = date.today().strftime("%Y-%m-%d")
selected_domain = "example"  # 도메인 이름 설정
file_path = os.path.join(".", "uploader", "kakao", f"{TODAY}_kakao_letter_{selected_domain}.txt")

# 파일 읽기
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# LinkedIn 포스팅 데이터 준비
payload = {
    "author": f"urn:li:person:{your_linkedin_id}",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": content},
            "shareMediaCategory": "NONE",
        }
    },
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
}

# 헤더 설정
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# LinkedIn에 포스팅
response = requests.post(API_URL, headers=headers, json=payload)

# 결과 출력
if response.status_code == 201:
    print("포스팅 성공!")
else:
    print(f"포스팅 실패: {response.status_code}, {response.text}")
