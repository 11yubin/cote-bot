"""
Telegram 메시지 핸들러.

handle_photo  : 사진 + 당일 날짜 캡션 → 인증 처리
handle_status : /현황 명령어 → 이번 주 인증 현황 출력
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import DATA_FILE
from bot.storage import Storage
from bot.utils import KST, contains_today, today_kst

logger = logging.getLogger(__name__)
storage = Storage(DATA_FILE)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    처리 흐름:
    1. 사진 첨부 여부 확인 (filters.PHOTO 로 이미 필터됨)
    2. 메시지 전송 날짜가 오늘(KST)인지 확인 (봇 재시작 시 밀린 업데이트 차단)
    3. 캡션에 오늘 날짜 포함 여부 확인
    4. 오늘 이미 인증했는지 중복 체크
    5. 인증 기록 → 응답 메시지 전송
    """
    message = update.message
    if not message:
        return

    # 봇이 오프라인이던 동안 쌓인 오래된 메시지 무시
    if message.date.astimezone(KST).date() != today_kst():
        return

    user = message.from_user
    caption = message.caption or ""

    if not contains_today(caption):
        await message.reply_text(
            f"⚠️ {user.first_name}님, 캡션에 오늘 날짜를 입력해 주세요!\n예) 2026-05-11"
        )
        return

    if storage.is_certified_today(user.id):
        await message.reply_text(
            f"⚠️ {user.first_name}님은 오늘 이미 인증하셨습니다!"
        )
        return

    count = storage.record_cert(user.id, user.first_name, user.username)
    await message.reply_text(f"✅ {user.first_name} {count}회 인증")


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/현황 → 이번 주 전체 인증 현황을 순위 형식으로 출력."""
    week_start = storage.get_week_start()
    users = storage.get_all_users()

    if not users:
        await update.message.reply_text("이번 주 인증 기록이 없습니다.")
        return

    sorted_users = sorted(
        users.values(),
        key=lambda u: u["weekly_count"],
        reverse=True,
    )

    lines = [f"📊 이번 주 인증 현황  (기준: {week_start})\n"]
    for i, u in enumerate(sorted_users, start=1):
        lines.append(f"{i}. {u['name']}: {u['weekly_count']}회")

    await update.message.reply_text("\n".join(lines))
