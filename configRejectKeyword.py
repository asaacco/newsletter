# 반도체, 배터리, AI/로봇 관련 키워드 설정

SEMICONDUCTOR_REJECT_KEYWORD = []

INTERIOR_REJECT_KEYWORD = []

ESG_REJECT_KEYWORD = [
            "특징주", "발간", "채용", "선정", "개최", "수상", "개설", "획득", "경기도", "기부", 
            "사진", "포토", "향상", "달성", "CES", "신간", "학교", "과목", "선생님", 
            "▼", "▲", "병원", "교육", "장중", "마감", "봉사", 
            "농어촌", "가족친화기업", "급등주",
#            "문화 마케팅", "장터", "전통시장", "복지", "금리", "성장", "지원", "캠페인", 
#            "공헌", "브랜드", "상장", "평가", "신용", "실천", "컨설팅", "공단", "증권", "플랫폼", "친환경",
#            "acquire", "invest", "fund", "million"
        ]

AI_REJECT_KEYWORD = [
            "특징주", "발간", "채용", "선정", "개최", "수상", "개설", "획득",
            "지자체", "공모", "사진", "포토", "향상", "달성", "CES", "신간", "학교",
            "과목", "선생님", "▼", "▲", "병원", "교육", "달성", "장중", "마감", "유튜버", 
            "컨설팅", "대출", "상장", "출간", "서학", "스타트업", "처벌",
        ]

DOMAINS = {
    "semiconductor": SEMICONDUCTOR_REJECT_KEYWORD,
    "interior": INTERIOR_REJECT_KEYWORD,
    "esg": ESG_REJECT_KEYWORD,
    "ai": AI_REJECT_KEYWORD
}
