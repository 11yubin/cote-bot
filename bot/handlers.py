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
from bot.utils import KST, contains_today, logical_date, today_kst

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
    if logical_date(message.date.astimezone(KST)) != today_kst():
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


async def handle_theme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /theme            → 이번 주 테마 조회
    /theme <내용>     → 이번 주 테마 설정 (두 사람이 매주 직접 지정)
    """
    message = update.message
    if not message:
        return

    theme = " ".join(context.args).strip()

    # 인자 없음 → 조회
    if not theme:
        current = storage.get_theme()
        if current:
            await message.reply_text(f"📅 이번 주 테마: {current}")
        else:
            await message.reply_text(
                "⚠️ 이번 주 테마가 아직 없어요.\n"
                "예) /theme BFS/DFS 완전탐색"
            )
        return

    # 인자 있음 → 설정
    storage.set_theme(theme)
    await message.reply_text(
        f"📌 이번 주 테마가 \"{theme}\"(으)로 설정됐어요.\n"
        "각자 4문제(공통 1 + 자율 3) · 주 4일 인증 💪"
    )


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/현황 → 이번 주 테마 + 전체 인증 현황을 순위 형식으로 출력."""
    week_start = storage.get_week_start()
    theme = storage.get_theme()
    users = storage.get_all_users()

    theme_line = f"📅 이번 주 테마: {theme}" if theme else "📅 이번 주 테마: 미설정"

    if not users:
        await update.message.reply_text(f"{theme_line}\n\n이번 주 인증 기록이 없습니다.")
        return

    sorted_users = sorted(
        users.values(),
        key=lambda u: u["weekly_count"],
        reverse=True,
    )

    lines = [theme_line, f"\n📊 이번 주 인증 현황  (기준: {week_start})\n"]
    for i, u in enumerate(sorted_users, start=1):
        lines.append(f"{i}. {u['name']}: {u['weekly_count']}회")

    await update.message.reply_text("\n".join(lines))
