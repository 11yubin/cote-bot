# 코테봇 (cote-bot)

코딩테스트 스터디 그룹용 Telegram 인증 봇.  
사진을 전송하면 인증을 기록하고, 매주 미달 인원에게 벌금을 공지합니다.

## 기능

- **인증** : 그룹 채팅에 사진을 전송하면 당일 1회 인증 처리 (중복 방지)
- **/status** : 이번 주 인증 현황 순위 출력
- **주차 리셋** : 매주 월요일 04:30 KST 자동 초기화
- **벌칙 공지** : 매주 월요일 10:00 KST — 주당 5회 이하 인증 시 미달 1회당 5,000원 벌금 공지

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
| 주당 최대 인증 | 7회 |
| 벌칙 기준 | 주 5회 이하 |
| 미달 1회당 벌금 | 5,000원 |

## 기술 스택

- Python 3.11+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 21
- APScheduler 3
- Docker
