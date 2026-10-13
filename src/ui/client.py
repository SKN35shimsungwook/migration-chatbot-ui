"""화면이 챗봇을 부르는 단 한 곳.

지금은 가짜 결과(mock.py)를 돌려준다. 1번 그래프가 준비되면 이 파일의 run() 만
진짜 그래프 호출로 바꾸면 화면은 그대로 동작한다. (부르는 함수 이름과 결과 모양은 1번 · 3번과 정함)
"""

from .mock import run_mock

TARGET_VERSIONS = ["1.x"]


def mode() -> str:
    """화면 위쪽 배지에 보여 줄 연결 상태."""
    try:
        import src.rag.retrieval.import_lookup  # noqa: F401  2번 검색기가 있으면 근거는 실제
        return "mock+real_evidence"
    except ImportError:
        return "mock"


def run(code: str, target_version: str = TARGET_VERSIONS[0]) -> dict:
    """옛 코드를 넣으면 결과(dict)를 돌려준다. 모양은 docs/화면_결과_모양.md."""
    # TODO(1번 그래프 연결 후): from src.graph.supervisor import ... 로 진짜 결과 받기
    return run_mock(code, target_version)
