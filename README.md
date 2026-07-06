# 코테봇 (cote-bot)

코딩테스트 스터디 그룹용 Telegram 인증 봇.  
사진을 전송하면 인증을 기록하고, 매주 미달 인원에게 벌금을 공지합니다.  
스터디 7월 개정판(4+1+2 시스템) 기준: **주 4일 인증**이 목표입니다.

## 기능

- **인증** : 그룹 채팅에 사진을 전송하면 당일 1회 인증 처리 (중복 방지)
- **/theme** : 이번 주 테마 설정/조회 (매주 직접 지정)
  - `/theme BFS/DFS 완전탐색` → 이번 주 테마 설정
  - `/theme` → 현재 테마 조회
- **/status** : 이번 주 테마 + 인증 현황 순위 출력
- **주차 리셋** : 매주 월요일 04:30 KST 자동 초기화 (테마도 함께 초기화)
- **월요일 아침 공지** : 매주 월요일 08:00 KST — 지난주 벌금 공지 + 이번 주 테마 리마인드

## 시작하기

### 환경 변수 설정

```bash
cp .env.example .env
# .env 파일에서 BOT_TOKEN, GROUP_CHAT_ID 입력
```

| 변수 | 설명 |
|------|------|
| `BOT_TOKEN` | BotFather에서 발급받은 토큰 |
| `GROUP_CHAT_ID` | 인증 메시지를 받을 그룹 채팅 ID (음수) |
| `DATA_FILE` | 데이터 파일 경로 (기본값: `data/store.json`) |

### 로컬 실행 테스트

```bash
pip install -r requirements.txt
python main.py
```

### Docker 실행

```bash
docker compose up -d
```

## 벌칙 기준

| 항목 | 값 |
|------|----|
| 주 목표 인증 | 4일 |
| 벌칙 기준 | 주 3일 이하 (4일 미달) |
| 미달 1일당 벌금 | 5,000원 |

> 예) 3일 인증 → 5,000원 · 0일 인증 → 20,000원 · 4일 이상 → 벌금 없음
>
> 코드 리뷰 벌금(설명 미흡·복붙 시 1회 10,000원)은 대면 처리 대상으로 봇에서 자동화하지 않습니다.

## 기술 스택

- Python 3.11+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 21
- APScheduler 3
- Docker
