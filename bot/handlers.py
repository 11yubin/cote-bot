"""
Telegram 메시지 핸들러.

handle_photo  : 사진 + 당일 날짜 캡션 → 인증 처리
handle_theme  : /theme 명령어 → 이번 주 테마 설정/조회
handle_status : /status 명령어 → 이번 주 테마 + 인증 현황 출력
handle_guide  : /guide 명령어 → 봇 사용법 안내
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import DATA_FILE, MAX_DAYS_PER_WEEK, PENALTY_PER_MISS
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


async def handle_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/guide → 봇 사용법 안내."""
    text = (
        "🤖 코테봇 사용법\n"
        "\n"
        "📸 인증\n"
        "  · 그룹 채팅에 사진 전송 + 캡션에 오늘 날짜 입력\n"
        "  · 예) 사진 + \"2026-07-06\"\n"
        "  · 하루 1회만 인정 (중복 방지)\n"
        "\n"
        "📅 테마\n"
        "  · /theme <내용>  → 이번 주 테마 설정 (예: /theme BFS/DFS)\n"
        "  · /theme         → 이번 주 테마 조회\n"
        "\n"
        "📊 현황\n"
        "  · /status  → 이번 주 테마 + 인증 순위\n"
        "  · /guide   → 이 사용법 다시 보기\n"
        "\n"
        f"⚖️ 규칙 (주 {MAX_DAYS_PER_WEEK}일 인증)\n"
        f"  · {MAX_DAYS_PER_WEEK}일 미달 시 1일당 {PENALTY_PER_MISS:,}원 벌금\n"
        "  · 각자 4문제 (공통 1 + 자율 3)\n"
        "\n"
        "⏰ 자동 공지\n"
        "  · 월요일 04:30 주차 리셋 (조용히)\n"
        "  · 월요일 08:00 지난주 벌금 + 이번 주 테마 리마인드"
    )
    await update.message.reply_text(text)
