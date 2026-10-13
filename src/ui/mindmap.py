"""시작 화면의 버전 마인드맵 (graphviz).

LangChain(위) → 옛 버전(한 줄) → 고른 버전의 영역(아래) 순서의 나무 모양으로 그린다.
graphviz 그림은 클릭이 안 되므로, 화면의 버전 버튼으로 고르면 그 버전이 강조되고 가지가 펼쳐진다.
색: 초록 = 최신 위치로 이사(native), 주황 = 옛 창고(classic), 회색 = 못 찾음(unresolved)
"""

from .versions import SUMMARY

INK = "#18202B"
GREEN, ORANGE, GRAY = "#1B7A43", "#B8501F", "#6B7686"
SOFT = {"root": "#2457C5", "ver": "#E4ECFB", "ver_on": "#FFE7C2", "auto": "#F1F3F6", "area": "#FFFFFF"}


def _bar(kinds: dict, width: int = 120) -> str:
    """최신 · classic · 못 찾음 비율 막대 (HTML 표 칸 너비로)."""
    total = sum(kinds.values()) or 1
    cells = []
    for key, color in (("native", GREEN), ("classic_fallback", ORANGE), ("unresolved", GRAY)):
        w = round(width * kinds.get(key, 0) / total)
        if w:
            cells.append(f'<TD BGCOLOR="{color}" WIDTH="{w}" HEIGHT="6" FIXEDSIZE="TRUE"></TD>')
    return f'<TABLE BORDER="0" CELLSPACING="0" CELLPADDING="0"><TR>{"".join(cells)}</TR></TABLE>'


def _ver_label(v: dict, on: bool) -> str:
    return (f'<<TABLE BORDER="0" CELLSPACING="3" CELLPADDING="0">'
            f'<TR><TD><FONT POINT-SIZE="22"><B>{v["version"]}</B></FONT></TD></TR>'
            f'<TR><TD><FONT POINT-SIZE="14" COLOR="{INK}">기능 {v["total"]:,}</FONT></TD></TR>'
            f'<TR><TD>{_bar(v["kinds"], 110)}</TD></TR>'
            f'</TABLE>>')


def _area_label(a: dict) -> str:
    return (f'<<TABLE BORDER="0" CELLSPACING="3" CELLPADDING="0">'
            f'<TR><TD><FONT POINT-SIZE="17"><B>{a["name"]}</B></FONT></TD></TR>'
            f'<TR><TD><FONT POINT-SIZE="14" COLOR="{INK}">{a["total"]:,}</FONT></TD></TR>'
            f'<TR><TD>{_bar(a["kinds"], 90)}</TD></TR></TABLE>>')


def dot(selected: str | None, auto: bool = False) -> str:
    """graphviz DOT 문자열. selected: 고른 옛 버전, auto: 자동 감지를 골랐는지."""
    lines = [
        "digraph G {",
        'rankdir=TB; bgcolor="transparent"; nodesep=0.22; ranksep=0.5; pad=0.35;',
        f'node [shape=box, style="rounded,filled", fontname="Malgun Gothic", color="#C9D2DD", fontcolor="{INK}", penwidth=1.2, margin="0.22,0.12"];',
        'edge [color="#9AA5B4", arrowsize=0.6, penwidth=1.3];',
        f'root [label=<<FONT POINT-SIZE="24"><B>LangChain</B></FONT><BR/><BR/><FONT POINT-SIZE="14">옛 코드</FONT>>, '
        f'fillcolor="{SOFT["root"]}", fontcolor="white", color="#2457C5", margin="0.3,0.12"];',
    ]
    if selected or auto:   # 고른 뒤에만 목표 버전 노드를 보여 준다
        lines.append(f'target [label=<<FONT POINT-SIZE="20"><B>LangChain 1.x</B></FONT><BR/><BR/><FONT POINT-SIZE="14">최신 {SUMMARY["latest"]["langchain"]}</FONT>>, '
                     f'fillcolor="{GREEN}", fontcolor="white", color="{GREEN}", margin="0.25,0.1"];')
    for v in SUMMARY["versions"]:
        on = v["version"] == selected
        nid = "v" + v["version"].replace(".", "_")
        lines.append(f'{nid} [label={_ver_label(v, on)}, fillcolor="{SOFT["ver_on"] if on else SOFT["ver"]}", '
                     f'color="{ORANGE if on else "#C9D2DD"}", penwidth={3 if on else 1.2}];')
        lines.append(f'root -> {nid} [color="{ORANGE if on else "#9AA5B4"}", penwidth={2.6 if on else 1.3}];')
        if on:
            lines.append(f'{nid} -> target [style=dashed, color="{GREEN}", penwidth=2, label=" 변환", fontname="Malgun Gothic", fontcolor="{GREEN}", fontsize=15];')
            for i, a in enumerate(v["areas"][:6]):
                aid = f"{nid}_a{i}"
                lines.append(f'{aid} [label={_area_label(a)}, fillcolor="{SOFT["area"]}"];')
                lines.append(f'{nid} -> {aid};')
    lines.append(f'auto [label=<<FONT POINT-SIZE="18"><B>모르겠어요</B></FONT><BR/><BR/><FONT POINT-SIZE="13">자동 감지</FONT>>, margin="0.3,0.15", '
                 f'fillcolor="{SOFT["ver_on"] if auto else SOFT["auto"]}", style="rounded,filled,dashed", '
                 f'color="{ORANGE if auto else "#9AA5B4"}", penwidth={3 if auto else 1.2}];')
    lines.append(f'root -> auto [style=dashed, color="{ORANGE if auto else "#9AA5B4"}"];')
    if auto:
        lines.append(f'auto -> target [style=dashed, color="{GREEN}", penwidth=2];')
    lines.append("}")
    return "\n".join(lines)
