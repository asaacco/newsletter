# ESG 관련 키워드 설정
ESG_KEYWORD = {
    "ESG_소식": ["ESG | 공급망실사 | 탄소중립 | 재생에너지 | CSRD"],
    "AI_소식": ["AI | 인공지능 | 자동화 | 클라우드 | 로보틱스 | 자율주행"]
}

# AI, 인공지능, DX 관련 키워드 설정
AI_KEYWORD = {
    "AI_소식": ["AI | 인공지능 | 자동화 | 클라우드 | 로보틱스 | 자율주행"],
#    "메타버스_소식": ["메타버스 | 확장현실 | 가상현실 | 증강현실 | AR | XR"],
#    "로봇_소식": ["테슬라봇 | 로봇 | 보스톤다이나믹스 | 모빌리티 | 자율주행 | 무인 | 로보틱스"]
}

# 반도체, 배터리, AI/로봇 관련 키워드 설정
SEMICONDUCTOR_KEYWORD = {
    "반도체_소식": ["HBM | 반도체 | 삼성전자 | SK하이닉스 | 양자컴퓨터"],
    "배터리_소식": ["배터리 | 2차전지 | 삼성SDI | LG화학 "],
    "DX_소식": ["디지털전환 | DigitalTransformation"]
}

# 인테리어 관련 키워드 설정
INTERIOR_KEYWORD = {
    "가구_인테리어": ["가구용", "특판가구", "인테리어", "주거공간", "건자재"],
    "업체동향": ["한샘", "리바트", "넵스", "에넥스", "LX지인", "LX하우시스"],
    "재건축_분양소식": ["분양", "재개발", "재건축"]
}

DOMAINS = {
    "semiconductor": SEMICONDUCTOR_KEYWORD,
    "interior": INTERIOR_KEYWORD,
    "esg": ESG_KEYWORD,
    "ai": AI_KEYWORD
}
