"""
JSON 파일 기반 영속성 레이어.

store.json 구조:
{
  "week_start": "2026-05-04",          # 현재 주 월요일 (ISO 형식)
  "theme": "BFS/DFS",                  # 이번 주 테마 (미설정 시 빈 문자열)
  "users": {
    "<user_id>": {
      "name": "홍길동",
      "username": "hong",              # 없으면 빈 문자열
      "weekly_count": 3,
      "certified_dates": ["2026-05-04", "2026-05-05", "2026-05-06"]
    }
  },
  "prev_week": {                        # reset 시 현재 주 데이터를 백업
    "week_start": "2026-04-27",
    "users": {
      "<user_id>": { "name": "홍길동", "count": 5 }
    }
  }
}
"""

import json
import logging
from datetime import timedelta
from pathlib import Path
from typing import Optional

from bot.utils import this_monday, today_str

logger = logging.getLogger(__name__)


class Storage:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    # ── 내부 I/O ──────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if not self._path.exists():
            return self._empty()
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _empty(self) -> dict:
        return {
            "week_start": this_monday().isoformat(),
            "theme": "",
            "users": {},
            "prev_week": {},
        }

    # ── 주차 검사 ─────────────────────────────────────────────────────────

    def ensure_current_week(self) -> None:
        """저장된 week_start가 현재 주보다 오래됐으면 리셋 (재기동 시 호출)."""
        data = self._load()
        current_monday = this_monday().isoformat()
        if data["week_start"] < current_monday:
            logger.warning(
                "week_start(%s) < current_monday(%s): 주차 리셋 실행",
                data["week_start"],
                current_monday,
            )
            self.reset_week()

    # ── 인증 ──────────────────────────────────────────────────────────────

    def is_certified_today(self, user_id: int) -> bool:
        data = self._load()
        user = data["users"].get(str(user_id), {})
        return today_str() in user.get("certified_dates", [])

    def record_cert(
        self,
        user_id: int,
        name: str,
        username: Optional[str],
    ) -> int:
        """인증을 기록하고 이번 주 누적 횟수를 반환."""
        data = self._load()
        uid = str(user_id)

        if uid not in data["users"]:
            data["users"][uid] = {
                "name": name,
                "username": username or "",
                "weekly_count": 0,
                "certified_dates": [],
            }

        user = data["users"][uid]
        user["name"] = name  # 이름 변경 시 갱신
        user["username"] = username or ""
        user["weekly_count"] += 1
        user["certified_dates"].append(today_str())

        self._save(data)
        logger.info("인증 기록: %s(%s) → 이번 주 %d회", name, uid, user["weekly_count"])
        return user["weekly_count"]

    # ── 현황 조회 ─────────────────────────────────────────────────────────

    def get_week_start(self) -> str:
        return self._load()["week_start"]

    # ── 주차 테마 ─────────────────────────────────────────────────────────

    def get_theme(self) -> str:
        """이번 주 테마 문자열. 미설정 시 빈 문자열."""
        return self._load().get("theme", "")

    def set_theme(self, theme: str) -> None:
        data = self._load()
        data["theme"] = theme
        self._save(data)
        logger.info("이번 주 테마 설정: %s", theme)

    def get_all_users(self) -> dict:
        """{ user_id: {name, username, weekly_count, certified_dates} }"""
        return self._load()["users"]

    def get_prev_week(self) -> dict:
        """{ week_start, users: { user_id: {name, count} } }"""
        return self._load().get("prev_week", {})

    # ── 주차 리셋 ─────────────────────────────────────────────────────────

    def reset_week(self) -> dict:
        """
        현재 주 데이터를 prev_week에 백업하고 새 주차를 시작합니다.
        백업된 prev_week 딕셔너리를 반환합니다.
        """
        data = self._load()

        prev = {
            "week_start": data["week_start"],
            "users": {
                uid: {"name": u["name"], "count": u["weekly_count"]}
                for uid, u in data["users"].items()
            },
        }

        new_data = {
            "week_start": this_monday().isoformat(),
            "theme": "",  # 새 주차는 테마 초기화 (매주 새로 설정)
            "users": {
                uid: {
                    "name": u["name"],
                    "username": u["username"],
                    "weekly_count": 0,
                    "certified_dates": [],
                }
                for uid, u in data["users"].items()
            },
            "prev_week": prev,
        }

        self._save(new_data)
        logger.info("주차 리셋 완료: %s → %s", prev["week_start"], new_data["week_start"])
        return prev
