"""
코딩테스트 인증봇 진입점.

핸들러 등록 순서 (python-telegram-bot은 등록 순서대로 평가):
  1. CommandHandler("status") → handle_status
  2. CommandHandler("theme")  → handle_theme
  3. MessageHandler(PHOTO)    → handle_photo
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from zoneinfo import ZoneInfo

from bot.config import BOT_TOKEN, DATA_FILE
from bot.handlers import handle_photo, handle_status, handle_theme
from bot.scheduler import job_announce_penalty, job_reset_week
from bot.storage import Storage

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

KST = ZoneInfo("Asia/Seoul")


# ── 앱 생명주기 콜백 ───────────────────────────────────────────────────────

async def post_init(application: Application) -> None:
    """봇 시작 시: 주차 검사 → 스케줄러 시작."""
    storage = Storage(DATA_FILE)
    storage.ensure_current_week()  # 봇 재기동 시 밀린 리셋 처리

    scheduler = AsyncIOScheduler(timezone=KST)
    bot = application.bot

    # 월요일 04:30 KST: 주차 리셋
    scheduler.add_job(
        job_reset_week,
        CronTrigger(day_of_week="mon", hour=4, minute=30, timezone=KST),
        args=[bot],
        id="reset_week",
        replace_existing=True,
    )
    # 월요일 08:00 KST: 벌칙 공지 + 이번 주 테마 리마인드
    scheduler.add_job(
        job_announce_penalty,
        CronTrigger(day_of_week="mon", hour=8, minute=0, timezone=KST),
        args=[bot],
        id="announce_penalty",
        replace_existing=True,
    )

    scheduler.start()
    application.bot_data["scheduler"] = scheduler
    logger.info("스케줄러 시작 완료 (리셋: 월 04:30 / 공지: 월 08:00 KST)")


async def post_shutdown(application: Application) -> None:
    """봇 종료 시: 스케줄러 정리."""
    scheduler: AsyncIOScheduler | None = application.bot_data.get("scheduler")
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("스케줄러 종료")


# ── 앱 구성 및 실행 ───────────────────────────────────────────────────────

def main() -> None:
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # /현황 명령어
    app.add_handler(CommandHandler("status", handle_status))

    # /theme 명령어 (설정/조회)
    app.add_handler(CommandHandler("theme", handle_theme))

    # 사진이 첨부된 모든 메시지 (캡션 날짜 검사는 핸들러 내부에서 수행)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("봇 시작 중...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
