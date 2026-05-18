import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID: int = int(os.environ["GROUP_CHAT_ID"])
DATA_FILE: str = os.getenv("DATA_FILE", "data/store.json")

# 벌칙 기준
PENALTY_THRESHOLD: int = 5       # 이 횟수 이하면 벌칙
MAX_DAYS_PER_WEEK: int = 6       # 주당 목표 인증 횟수
PENALTY_PER_MISS: int = 5_000    # 미달 1회당 벌금 (원)
