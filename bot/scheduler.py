"""
APScheduler 기반 예약 작업.

job_reset_week      : 월요일 04:30 KST  → 주차 데이터 리셋 (조용히 처리)
job_announce_penalty: 월요일 08:00 KST  → 전주 벌칙 공지 + 이번 주 테마 리마인드
"""

import logging

from telegram import Bot

from bot.config import DATA_FILE, GROUP_CHAT_ID, MAX_DAYS_PER_WEEK, PENALTY_PER_MISS, PENALTY_THRESHOLD
from bot.storage import Storage
from bot.utils import format_penalty

logger = logging.getLogger(__name__)
storage = Storage(DATA_FILE)


async def job_reset_week(bot: Bot) -> None:
    """매주 월요일 04:30 KST: 현재 주 데이터를 prev_week에 저장하고 초기화."""
    logger.info("[스케줄러] 주차 리셋 시작")
    storage.reset_week()
    logger.info("[스케줄러] 주차 리셋 완료")


async def job_announce_penalty(bot: Bot) -> None:
    """
    매주 월요일 08:00 KST: 전주 벌칙 대상자 공지 + 이번 주 테마 리마인드.
    벌칙 기준: 인증 일수 <= PENALTY_THRESHOLD (주 4일 미달)
    벌금: (4 - 인증일수) * PENALTY_PER_MISS 원
    """
    logger.info("[스케줄러] 월요일 아침 공지 시작")

    prev = storage.get_prev_week()

    # ── 지난주 벌칙 공지 ──────────────────────────────────────────────
    if not prev or not prev.get("users"):
        logger.info("[스케줄러] 이전 주 데이터 없음 → 벌칙 공지 생략")
        penalty_msg = None
        penalized: list = []
    else:
        week_start: str = prev.get("week_start", "알 수 없음")
        penalized = [
            (u["name"], u["count"], format_penalty(u["count"], MAX_DAYS_PER_WEEK, PENALTY_PER_MISS))
            for u in prev["users"].values()
            if u["count"] <= PENALTY_THRESHOLD
        ]

        if not penalized:
            penalty_msg = f"🎉 {week_start} 주차 벌칙 대상자가 없습니다!\n모두 고생하셨습니다 👏"
        else:
            penalized.sort(key=lambda x: x[1])  # 인증 일수 오름차순
            lines = [f"📢 {week_start} 주차 벌칙 안내\n"]
            for name, count, amount in penalized:
                lines.append(f"• {name}: {count}일 인증 → {amount:,}원")
            penalty_msg = "\n".join(lines)

    # ── 이번 주 테마 리마인드 ─────────────────────────────────────────
    theme = storage.get_theme()
    if theme:
        theme_msg = f"📅 이번 주 테마: {theme}\n각자 4문제(공통 1 + 자율 3) · 주 4일 인증 💪"
    else:
        theme_msg = (
            "⚠️ 이번 주 테마가 아직 없어요.\n"
            "/theme <내용> 으로 정해주세요! (예: /theme BFS/DFS 완전탐색)"
        )

    msg = "\n\n".join(m for m in (penalty_msg, theme_msg) if m)
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    logger.info("[스케줄러] 월요일 아침 공지 전송 완료 (벌칙 대상자 %d명)", len(penalized))
