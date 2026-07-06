import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID: int = int(os.environ["GROUP_CHAT_ID"])
DATA_FILE: str = os.getenv("DATA_FILE", "data/store.json")

# 벌칙 기준 (7월 개정판: 주 4일 인증)
PENALTY_THRESHOLD: int = 3       # 이 일수 이하면 벌칙 (4일 미달)
MAX_DAYS_PER_WEEK: int = 4       # 주 목표 인증 일수
PENALTY_PER_MISS: int = 5_000    # 미달 1일당 벌금 (원)
