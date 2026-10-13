"""LangChain 마이그레이션 챗봇 화면 (4번 화면 · 평가).

실행 (프로젝트 루트에서):
    uv add streamlit          # 팀 저장소에서는 1번과 상의 후
    uv run streamlit run app.py

구성: 왼쪽 채팅(옛 코드 넣기) + 오른쪽 결과 패널(전후 비교 · 근거 · 진행 과정).
챗봇 호출은 src/ui/client.py 한 곳에서만 한다. 지금은 가짜 결과, 근거는 2번 대응표가 있으면 실제.
"""

import difflib
import time

import streamlit as st

from src.ui.client import TARGET_VERSIONS, mode, run

st.set_page_config(page_title="LangChain 마이그레이션 챗봇", page_icon=":material/sync_alt:", layout="wide")

EXAMPLES = {
    "쉬움 · import 경로": (
        "from langchain.chat_models import ChatOpenAI\n"
        "from langchain.prompts import PromptTemplate\n\n"
        "llm = ChatOpenAI(temperature=0)\n"
        "prompt = PromptTemplate.from_template(\"{topic}을 한 줄로 설명해줘\")"
    ),
    "중간 · LLMChain": (
        "from langchain.chat_models import ChatOpenAI\n"
        "from langchain.chains import LLMChain\n"
        "from langchain.prompts import PromptTemplate\n\n"
        "llm = ChatOpenAI(temperature=0)\n"
        "prompt = PromptTemplate.from_template(\"{product}을 만드는 회사 이름을 지어줘\")\n"
        "chain = LLMChain(llm=llm, prompt=prompt)\n"
        "print(chain.run(product=\"양말\"))"
    ),
    "어려움 · 에이전트 · 메모리": (
        "from langchain.chat_models import ChatOpenAI\n"
        "from langchain.agents import initialize_agent\n"
        "from langchain.memory import ConversationBufferMemory\n\n"
        "llm = ChatOpenAI(temperature=0)\n"
        "memory = ConversationBufferMemory()\n"
        "agent = initialize_agent([], llm, memory=memory)"
    ),
}
KIND_LABEL = {"native": "최신 위치", "classic_fallback": "옛 창고(classic)", "unresolved": "못 찾음"}
MODE_BADGE = {
    "mock": ("가짜 결과 · 예시 근거", "gray"),
    "mock+real_evidence": ("가짜 결과 · 근거는 2번 대응표", "blue"),
    "graph": ("팀 챗봇 연결됨", "green"),
}

st.session_state.setdefault("messages", [])
st.session_state.setdefault("results", [])

# ---------------------------------------------------------------- 사이드바
with st.sidebar:
    st.title("마이그레이션 챗봇")
    st.caption("옛 LangChain 코드를 최신 버전으로 고치고, 근거와 검증 결과를 함께 보여 줍니다.")
    target = st.selectbox("목표 버전", [f"LangChain {v}" for v in TARGET_VERSIONS]).removeprefix("LangChain ")
    label, color = MODE_BADGE[mode()]
    st.badge(label, icon=":material/lan:", color=color)
    st.subheader("예제로 해 보기", divider="gray")
    for name, code in EXAMPLES.items():
        if st.button(name, width="stretch"):
            st.session_state["pending"] = code
    if st.button("대화 지우기", icon=":material/delete:", width="stretch"):
        st.session_state["messages"], st.session_state["results"] = [], []
        st.rerun()

convert_tab, compare_tab, about_tab = st.tabs(
    [":material/forum: 변환하기", ":material/bar_chart: 비교 (준비 중)", ":material/info: 프로젝트 소개"])


def summary(result: dict) -> str:
    v = result["verification"]
    if not v["success"]:
        return v["message"]
    changes = result["changes"]
    classic = [c for c in changes if c["kind"] == "classic_fallback"]
    lcel = [c for c in classic if "StrOutputParser" in c["new"]]
    extra = ""
    if lcel:
        extra += f" 1.x에서 없어진 기능 {len(lcel)}개는 최신 방식(LCEL)으로 바꿨어요."
    if len(classic) > len(lcel):
        extra += f" {len(classic) - len(lcel)}개는 옛 창고(classic) 위치와 대안을 같이 안내해요."
    return (f"import {len(changes)}줄을 찾아 고쳤어요.{extra} 검증은 {v['attempts']}회 만에 통과했어요. "
            "오른쪽에서 자세히 보세요.")


def show_result(result: dict) -> None:
    v = result["verification"]
    with st.container(horizontal=True):
        if v["success"]:
            st.badge(f"검증 통과 · {v['attempts']}회", icon=":material/check_circle:", color="green")
        else:
            st.badge("변환 못 함", icon=":material/error:", color="red")
        st.badge(f"목표 LangChain {result['target_version']}", icon=":material/flag:", color="gray")
        if result["changes"]:
            real = all(c["real_evidence"] for c in result["changes"])
            st.badge("근거: 2번 대응표" if real else "근거: 예시", icon=":material/menu_book:",
                     color="blue" if real else "gray")
    if not v["success"]:
        st.warning(v["message"])
        return
    before, after, steps = st.tabs(["전후 비교", "변경표 · 근거", "진행 과정"])
    with before:
        left, right = st.columns(2)
        left.caption("변경 전")
        left.code(result["original_code"], language="python", wrap_lines=True)
        right.caption("변경 후")
        right.code(result["migrated_code"], language="python", wrap_lines=True)
        diff = difflib.unified_diff(result["original_code"].splitlines(), result["migrated_code"].splitlines(),
                                    "변경 전", "변경 후", lineterm="")
        with st.expander("바뀐 줄만 보기"):
            st.code("\n".join(diff), language="diff")
    with after:
        rows = [{"옛 줄": c["old"], "새 줄": c["new"], "종류": KIND_LABEL.get(c["kind"], c["kind"]),
                 "대안": c["alternative"] or "", "근거 ID": c["evidence_id"]} for c in result["changes"]]
        st.table(rows)
        st.caption("옛 창고(classic)는 1.x에서 없어져 langchain_classic에만 남은 기능입니다. 대안이 있으면 최신 방식으로 바꿉니다.")
    with steps:
        for s in result["steps"]:
            st.markdown(f"**{s['name']}** · {s['detail']}")


# ---------------------------------------------------------------- 변환하기
with convert_tab:
    chat_col, result_col = st.columns([1, 1.25], gap="large")
    with chat_col:
        box = st.container(height=520)
        with box:
            if not st.session_state["messages"]:
                with st.chat_message("assistant"):
                    st.write("옛 LangChain 코드를 붙여 넣어 주세요. 왼쪽 예제 버튼으로 바로 해 볼 수도 있어요.")
            for m in st.session_state["messages"]:
                with st.chat_message(m["role"]):
                    if m["role"] == "user":
                        st.code(m["content"], language="python", wrap_lines=True)
                    else:
                        st.write(m["content"])
        typed = st.chat_input("옛 코드를 붙여 넣으세요 (여러 줄은 Shift+Enter)")
        code = typed or st.session_state.pop("pending", None)
        if code:
            st.session_state["messages"].append({"role": "user", "content": code})
            with box:
                with st.chat_message("user"):
                    st.code(code, language="python", wrap_lines=True)
                with st.chat_message("assistant"):
                    with st.status("변환하는 중...", expanded=True) as status:
                        result = run(code, target)
                        for s in result["steps"]:
                            st.write(f"{s['name']} · {s['detail']}")
                            time.sleep(0.25)
                        status.update(label="완료", state="complete" if result["verification"]["success"] else "error",
                                      expanded=False)
                    st.write(summary(result))
            st.session_state["messages"].append({"role": "assistant", "content": summary(result)})
            st.session_state["results"].append(result)
    with result_col:
        st.subheader("결과", divider="blue")
        if st.session_state["results"]:
            show_result(st.session_state["results"][-1])
        else:
            st.info("코드를 넣으면 여기에 전후 비교, 바뀐 줄과 근거, 진행 과정이 나옵니다.", icon=":material/arrow_back:")

# ---------------------------------------------------------------- 비교 (평가)
with compare_tab:
    st.info("일반 AI와 우리 챗봇의 비교 결과가 들어갈 자리입니다. 챗봇이 완성되면 같은 문제로 실험해서 채웁니다.",
            icon=":material/hourglass_empty:")
    cols = st.columns(3)
    for col, (name, desc) in zip(cols, [("성공률", "일반 AI vs 우리 챗봇"),
                                         ("난이도별", "쉬움 · 중간 · 어려움"),
                                         ("다시 고치기 효과", "1회차 → 최종")]):
        with col.container(border=True):
            st.markdown(f"**{name}**")
            st.caption(desc)
            st.metric("결과", "–")

# ---------------------------------------------------------------- 프로젝트 소개
with about_tab:
    st.subheader("옛 LangChain 코드를 최신으로, 근거와 검증까지", divider="gray")
    st.write("일반 AI는 옛 버전을 기억해서 틀린 코드를 주고, 틀린 줄도 모릅니다. "
             "이 챗봇은 최신 문서와 이사 목록에서 근거를 찾아 고치고, 실제로 실행해서 확인합니다.")
    st.markdown(
        "| 단계 | 하는 일 | 담당 |\n|---|---|---|\n"
        "| ① analyzer | 코드에서 import 경로 뽑기 | 3번 |\n"
        "| ② retriever | 이사 목록 · 문서에서 근거 찾기 | 2번 |\n"
        "| ③ rewriter | 근거를 보고 코드 다시 쓰기 | 3번 |\n"
        "| ④ verifier | 실행해서 확인, 실패하면 ②로 | 3번 |\n"
        "| ⑤ report | 결과 정리 | 미정 |\n"
        "| 연결 | 단계 잇기, 다시 할지 판단 | 1번 |\n"
        "| 화면 · 평가 | 보여 주기, 일반 AI와 비교 | 4번 |")
