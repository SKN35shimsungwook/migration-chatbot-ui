# 실무형 질문 30개 (4번 · 평가)

`questions.json`: 실제 사용자가 보낼 법한 **자연어 요청 + 옛 LangChain 코드** 30개. 화면의 예시 질문으로도 쓰고, 일반 AI와 우리 챗봇을 비교할 때 시험지로도 씁니다.

| 필드 | 뜻 |
|---|---|
| `id` · `type` · `difficulty` | q01~q30, 유형(10가지), 쉬움 · 중간 · 어려움 |
| `source_version` | 이 코드가 쓰였을 법한 옛 버전 |
| `request` | 사용자 요청 문장 (에러 메시지를 붙인 요청, 일부만 바꿔 달라는 요청 등) |
| `code` | 옛 코드 |
| `expected_imports` | 좋은 답이면 들어 있어야 할 1.x import (LangChain 1.4.4에서 실제로 import 확인) |
| `checks` | 사람이 볼 점검 항목 (예: `.run( 없음 → invoke`, 대화 기억 유지) |

| 유형 (각 3개) | |
|---|---|
| import 경로 · 문서 로더 · 분할기 · 임베딩 · 벡터스토어 | 경로만 바뀐 경우부터 패키지 설치 안내까지 |
| LLMChain → LCEL · 체인 조합 · RAG | 없어진 체인을 `|`로 다시 짜기 |
| 메모리 · 에이전트 · 도구 | 체크포인터, `create_agent`로 구조 바꾸기 |
| 출력 파서 · 실무 상황 | 구조화 출력, 에러 메시지 설명, 전역 설정, 못 바꾸는 부분 안내 |

난이도: 쉬움 7 · 중간 15 · 어려움 8

## 만들기 · 검사

```powershell
python eval/build_questions.py
```

```powershell
python eval/check_questions.py --py <LangChain 1.x python> --map data/processed/import_map.jsonl --symbols data/raw/symbols
```

검사 항목: 옛 코드가 1.x에서 실제로 깨지는가, 기대 import가 1.x에서 되는가(패키지가 없으면 2번 도구 목록으로 확인), 옛 경로가 2번 대응표에 있는가. 2026-10-14 결과 **30/30 통과**.
