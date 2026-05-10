import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")


def now_kst() -> datetime:
    return datetime.now(KST)


def today_kst() -> date:
    return now_kst().date()


def today_str() -> str:
    return today_kst().isoformat()


def this_monday() -> date:
    today = today_kst()
    return today - timedelta(days=today.weekday())


def contains_today(text: str) -> bool:
    """
    캡션 텍스트에 오늘 날짜(KST)가 포함되어 있는지 확인합니다.
    지원 형식:
      - 2026-05-08 / 2026/05/08 / 2026.05.08
      - 05-08 / 05/08 / 05.08
      - 5-8 / 5/8 / 5.8
      - 5월 8일 / 05월 08일
    """
    d = today_kst()
    y, m, day = d.year, d.month, d.day

    patterns = [
        # 전체 날짜: 2026-05-08
        rf"{y}[-/.]{m:02d}[-/.]{day:02d}",
        rf"{y}[-/.]{m}[-/.]{day}(?!\d)",
        # 월/일만: 05-08, 5/8, 5.8  (앞뒤 숫자 없어야 함)
        rf"(?<!\d){m:02d}[-/.]{day:02d}(?!\d)",
        rf"(?<!\d){m}[-/.]{day}(?!\d)",
        # 한국어: 5월 8일
        rf"{m}월\s*{day}일",
    ]

    return any(re.search(p, text) for p in patterns)


def format_penalty(count: int, max_days: int, penalty_per_miss: int) -> int:
    """미달 횟수 * 벌금 단가 반환 (0이면 벌칙 없음)."""
    miss = max_days - count
    return miss * penalty_per_miss if miss > 0 else 0
