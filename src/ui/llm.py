"""LLM 보조 기능: 연상 질문 만들기, 코드 없는 질문에 짧게 답하기.

OpenAI 키: .streamlit/secrets.toml 의 OPENAI_API_KEY 또는 환경 변수 OPENAI_API_KEY.
키가 없으면 연상 질문은 비어 있고, 화면이 "키를 설정하면 나온다"고 안내한다.
"""

import json
import os

MODEL = os.environ.get("MIGRATION_UI_MODEL", "gpt-4o-mini")

FOLLOWUP_PROMPT = """너는 LangChain 버전 마이그레이션 코드 어시스턴트다.
사용자가 방금 옛 LangChain 코드를 1.x로 바꿨다. 이 사용자가 실무에서 이어서 궁금해할 질문 3개를 만든다.

규칙
- 한국어, 한 질문은 40자 이내, 사용자가 직접 묻는 말투 ("~하려면?", "~는 왜 바뀌었어?")
- 방금 결과와 직접 이어지는 질문만 (바뀐 기능, 옛 창고(classic)로 남은 기능, 검증 실패 이유, 설치할 패키지, 다음 단계 코드)
- 서로 다른 관점 3개 (원리 1개, 실무 적용 1개, 다음 코드 1개)
- JSON 으로만 답한다: {"questions": ["...", "...", "..."]}"""

ANSWER_PROMPT = """너는 LangChain 버전 마이그레이션 코드 어시스턴트다. LangChain 1.x 기준으로 한국어로 짧게(8줄 이내) 답한다.
코드가 필요하면 1.x 코드로 보여 준다. 확실하지 않은 API 는 지어내지 말고 "공식 문서 확인 필요"라고 말한다.
옛 코드를 통째로 바꾸고 싶다면 코드를 붙여 넣으라고 안내한다."""


def api_key() -> str | None:
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        key = None
    return key or os.environ.get("OPENAI_API_KEY")


def _client():
    from openai import OpenAI
    return OpenAI(api_key=api_key())


def _context(result: dict) -> str:
    changes = [{k: c.get(k) for k in ("old", "new", "kind", "alternative")} for c in result.get("changes", [])]
    return json.dumps({"target_version": result.get("target_version"), "changes": changes,
                       "verification": result.get("verification"), "unresolved": result.get("unresolved", [])},
                      ensure_ascii=False)[:4000]


def followups(user_text: str, result: dict | None) -> list[str]:
    """방금 대화를 보고 연상 질문 3개. 키가 없거나 실패하면 빈 목록."""
    if not api_key():
        return []
    try:
        resp = _client().chat.completions.create(
            model=MODEL, temperature=0.4, response_format={"type": "json_object"},
            messages=[{"role": "system", "content": FOLLOWUP_PROMPT},
                      {"role": "user", "content": f"사용자 입력:\n{user_text[:3000]}\n\n결과:\n{_context(result or {})}"}])
        qs = json.loads(resp.choices[0].message.content).get("questions", [])
        return [q.strip() for q in qs if isinstance(q, str) and q.strip()][:3]
    except Exception:
        return []


def answer(question: str, history: list[dict]) -> str:
    """코드 없는 질문(연상 질문 등)에 짧게 답한다."""
    if not api_key():
        return ("코드가 없는 질문은 OpenAI 키를 설정하면 답할 수 있어요. "
                "옛 코드를 붙여 넣으면 바로 1.x로 바꿔 드려요.")
    msgs = [{"role": "system", "content": ANSWER_PROMPT}]
    for m in history[-6:]:
        msgs.append({"role": m["role"], "content": m["content"][:2000]})
    msgs.append({"role": "user", "content": question})
    try:
        resp = _client().chat.completions.create(model=MODEL, temperature=0.2, messages=msgs)
        return resp.choices[0].message.content
    except Exception as e:
        return f"답변을 만들지 못했어요 ({type(e).__name__}). 잠시 뒤 다시 시도해 주세요."
