# 마이그레이션 챗봇 화면 (4번 · 화면)

**배포 주소**: [https://migration-chatbot-ui-47wunvzaww7qc27nmwufvh.streamlit.app/](https://migration-chatbot-ui-47wunvzaww7qc27nmwufvh.streamlit.app/)

> 팀 프로젝트 **LangChain 버전 마이그레이션 챗봇**의 화면을 먼저 만들어 보는 4번 작업 저장소입니다.
> 팀 저장소와 **같은 폴더 구조**로 만들어서, 완성되면 4번이 직접 팀 저장소의 4번 브랜치로 옮겨 PR합니다.
> 1 · 2 · 3번의 코드는 이 저장소에 넣지 않았습니다 (`src/agents`, `src/graph`, `src/rag`, `data`는 빈 자리).

## 화면 구성

| 위치 | 내용 |
|---|---|
| 로그인 | username (중복 금지) → TiDB `users` 테이블 (`user_id`) |
| 사이드바 | ChatGPT처럼 새 대화 · **예시 질문(35개 중 골라 보내기)** · 내 대화 목록 · 로그아웃 (대화 기록은 TiDB에 저장) |
| 위쪽 | 지금 코드 버전(자동 감지) · 변환할 버전(0.0.300 ~ 1.x 아무 방향, 옛 버전으로 되돌리기 포함) |
| 왼쪽 채팅 | 옛 코드나 질문, 답변 아래 이어서 물어보기([선택 기능] LLM 연상 질문) |
| 오른쪽 결과 | 검증 배지 · 버전 · 근거, 탭: 전후 비교 / 변경표 · 근거 |

실행 · 설정은 [docs/화면_실행방법.md](docs/화면_실행방법.md), 질문 35개는 [eval/README.md](eval/README.md), DB 는 [docs/DB_설계.md](docs/DB_설계.md) (ERD), 머지할 때 가져갈 기능 · 뺄 기능은 [docs/머지_가이드.md](docs/머지_가이드.md).

## 무엇이 실제이고 무엇이 틀인가

| 부분 | 이 저장소에서만 실행 | 팀 저장소(2번 데이터 있음)에서 실행 |
|---|---|---|
| 옛 버전 목록 | 실제 (2번 대응표의 버전) | 실제 |
| 근거 ID | 예시 (`sample-…`) | **실제** (`imap-…`) |
| 대화 기록 | SQLite(로컬) 또는 secrets 의 TiDB | 같음 |
| 연상 질문 | OpenAI 키가 있으면 LLM | 같음 |
| 옛 버전 자동 감지 | 예시 (일부 기능만) | **실제** (대응표 9,155줄) |
| 코드 변환 결과 | **가짜** (흉내) | **가짜** (3번 rewriter가 나오면 교체) |
| 벡터 DB(Chroma) 문서 검색 | 안 씀 | 안 씀 (API 키 필요, 1번 그래프 연결 후) |

## 자동 점검 봇

```bash
python tools/bot_check.py
```

가입 · 중복 금지 · 로그인 → 세션(질문 여러 개 → 대화 1개) → 지금 코드 버전 13가지 → 버전 오가기 · 같은 버전 안내 → 질문 35개 전부 실행 → 예시 질문 → 대화 저장 · 다시 열기 → 사용자 분리까지 29가지를 임시 SQLite로 점검합니다.
2026-10-14 결과: 팀 저장소 구조 + 2번 데이터에서 **29/29 통과**. 이 저장소에서만 돌리면 예시 대응표라 자동 감지 5건은 범위를 좁히지 못합니다.

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

비밀 값(OpenAI 키, TiDB)은 `.streamlit/secrets.toml.example`을 복사해 채웁니다. 자세한 방법은 [docs/화면_실행방법.md](docs/화면_실행방법.md).

## 폴더 (팀 저장소와 같은 구조)

```text
├── app.py              ← 화면 (팀 저장소의 Hello World 자리)
├── src/
│   ├── ui/
│   │   ├── client.py   ← 챗봇을 부르는 단 한 곳 (지금은 가짜 결과)
│   │   ├── mock.py     ← 가짜 결과 + 2번 대응표 근거 찾기
│   │   ├── db.py       ← 사용자 · 대화 기록 (TiDB, 없으면 SQLite)
│   │   ├── versions.py ← 화면의 버전 목록
│   │   ├── optional.py ← 선택 기능 불러오기
│   │   └── extras/     ← [선택 기능 · 4번 영역 아님] 폴더째 빼도 화면 동작
│   │       ├── followups.py      연상 질문 · 코드 없는 질문 답변
│   │       ├── version_detect.py 지금 코드 버전 자동 감지
│   │       └── version_map.py    버전 ↔ 버전 변환 (되돌리기)
│   │   └── version_summary.json ← 2번 대응표의 버전 · 영역별 숫자 요약
│   ├── agents/  graph/  prompt/  rag/   (빈 자리: 1 · 2 · 3번 몫)
├── data/               (빈 자리: 2번 몫)
└── docs/
    └── 화면_결과_모양.md  ← 화면이 받고 싶은 결과 모양 (1 · 3번과 상의할 초안)
```

## 팀 저장소로 옮길 때

1. 1번에게 `app.py` 자리와 `streamlit` 추가를 확인받기
2. 팀 저장소 4번 브랜치에 `app.py`, `src/ui/`, `docs/화면_결과_모양.md`만 복사 (빈 자리 폴더는 복사하지 않음)
3. 화면을 켜서 근거 배지가 **"근거: 2번 대응표"**로 바뀌는지 확인 → PR
