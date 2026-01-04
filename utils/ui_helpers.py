"""
UI 헬퍼 함수
Tkinter UI 관련 유틸리티 함수를 제공합니다.
"""

import tkinter as tk
from typing import Callable


def bind_mousewheel_to_canvas(canvas: tk.Canvas, frame: tk.Frame):
    """
    Canvas와 모든 자식 위젯에 마우스 휠 이벤트 바인딩

    Args:
        canvas: 스크롤할 Canvas 위젯
        frame: Canvas 내부의 Frame 위젯
    """
    def on_mousewheel(event):
        # Windows와 Linux 모두 지원
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            canvas.yview_scroll(1, "units")
        return "break"

    def bind_to_widget(widget):
        # Windows
        widget.bind("<MouseWheel>", on_mousewheel)
        # Linux
        widget.bind("<Button-4>", on_mousewheel)
        widget.bind("<Button-5>", on_mousewheel)
        # 모든 자식 위젯에도 재귀적으로 바인딩
        for child in widget.winfo_children():
            bind_to_widget(child)

    # Canvas와 Frame에 모두 바인딩
    canvas.bind("<MouseWheel>", on_mousewheel)
    canvas.bind("<Button-4>", on_mousewheel)
    canvas.bind("<Button-5>", on_mousewheel)
    canvas.bind("<Enter>", lambda e: canvas.focus_set())
    bind_to_widget(frame)


def center_window(window: tk.Tk, width: int = None, height: int = None):
    """
    윈도우를 화면 중앙에 배치

    Args:
        window: Tkinter 윈도우
        width: 윈도우 너비 (None이면 현재 크기 유지)
        height: 윈도우 높이 (None이면 현재 크기 유지)
    """
    window.update_idletasks()

    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


def create_scrollable_frame(parent: tk.Widget) -> tuple[tk.Canvas, tk.Frame, tk.Scrollbar]:
    """
    스크롤 가능한 프레임 생성

    Args:
        parent: 부모 위젯

    Returns:
        (canvas, frame, scrollbar) 튜플
    """
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 마우스 휠 바인딩
    bind_mousewheel_to_canvas(canvas, scrollable_frame)

    return canvas, scrollable_frame, scrollbar


def show_auto_close_dialog(parent: tk.Tk, title: str, message: str, auto_close_seconds: int = 5):
    """
    자동으로 닫히는 다이얼로그 표시

    Args:
        parent: 부모 윈도우
        title: 다이얼로그 제목
        message: 표시할 메시지
        auto_close_seconds: 자동으로 닫힐 시간 (초)
    """
    import tkinter.ttk as ttk

    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("400x150")
    dialog.transient(parent)
    dialog.grab_set()

    # 중앙에 배치
    center_window(dialog, 400, 150)

    # 메시지 표시
    msg_label = ttk.Label(
        dialog,
        text=message,
        font=("맑은 고딕", 10),
        wraplength=380,
        justify=tk.CENTER
    )
    msg_label.pack(pady=20, padx=20)

    # 남은 시간 표시
    time_label = ttk.Label(
        dialog,
        text=f"{auto_close_seconds}초 후 자동으로 닫힙니다...",
        font=("맑은 고딕", 9),
        foreground="gray"
    )
    time_label.pack(pady=5)

    # 확인 버튼
    ok_button = ttk.Button(
        dialog,
        text="확인",
        command=dialog.destroy
    )
    ok_button.pack(pady=10)

    # 자동 닫기 로직
    def countdown(remaining):
        if remaining > 0:
            time_label.config(text=f"{remaining}초 후 자동으로 닫힙니다...")
            dialog.after(1000, lambda: countdown(remaining - 1))
        else:
            dialog.destroy()

    # 카운트다운 시작
    dialog.after(1000, lambda: countdown(auto_close_seconds - 1))


class ActEpisodeTreeView:
    """
    막(Act) > 에피소드(Episode) 계층 구조를 표시하는 트리뷰 위젯

    범용적으로 사용 가능하며, 선택 시 콜백을 호출합니다.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_select_callback: Callable = None,
        on_select_all_callback: Callable = None,
        width: int = 240,
        show_all_button: bool = True,
        all_button_text: str = "전체 보기"
    ):
        """
        Args:
            parent: 부모 위젯
            on_select_callback: 에피소드 선택 시 콜백 (act_name, episode_data)
            on_select_all_callback: 전체 보기 선택 시 콜백 (act_name or None)
            width: 트리뷰 너비
            show_all_button: 전체 보기 버튼 표시 여부
            all_button_text: 전체 보기 버튼 텍스트
        """
        import tkinter.ttk as ttk

        self.parent = parent
        self.on_select_callback = on_select_callback
        self.on_select_all_callback = on_select_all_callback
        self.episodes_by_act = {}
        self.current_act = ""
        self.current_episode_num = 0

        # 메인 프레임
        self.frame = ttk.Frame(parent)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 상단: 전체 보기 버튼 (트리뷰 위에 배치)
        if show_all_button:
            self.all_btn = ttk.Button(
                self.frame,
                text=all_button_text,
                command=self._on_select_all
            )
            self.all_btn.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # 트리뷰 컨테이너 (트리뷰 + 스크롤바)
        tree_container = ttk.Frame(self.frame)
        tree_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 트리뷰 스타일 설정
        style = ttk.Style()
        style.configure("ActTree.Treeview", font=("맑은 고딕", 10), rowheight=26)
        style.configure("ActTree.Treeview.Heading", font=("맑은 고딕", 10, "bold"))

        # 트리뷰
        self.tree = ttk.Treeview(
            tree_container,
            style="ActTree.Treeview",
            selectmode="browse",
            show="tree"
        )
        self.tree.column("#0", width=width, minwidth=200)

        # 스크롤바
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 배치
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 이벤트 바인딩
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # 막 항목 클릭 시 펼침/접힘 (화살표 외 영역 클릭도 지원)
        self.tree.bind("<Button-1>", self._on_single_click)

    def load_data(self, episodes_by_act: dict):
        """
        데이터 로드 및 트리뷰 갱신

        Args:
            episodes_by_act: {act_name: [episode_data, ...]} 형태의 딕셔너리
        """
        import re

        self.episodes_by_act = episodes_by_act

        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not episodes_by_act:
            self.tree.insert("", tk.END, iid="__empty__", text="(데이터 없음)")
            return

        # 막 이름 정렬
        def act_sort_key(act_name: str) -> tuple:
            match = re.search(r'Act(\d+)(?:-(\d+))?', act_name)
            if match:
                main_num = int(match.group(1))
                sub_num = int(match.group(2)) if match.group(2) else 0
                return (main_num, sub_num)
            return (999, 0)

        sorted_acts = sorted(episodes_by_act.keys(), key=act_sort_key)

        # 트리 구성
        for act_name in sorted_acts:
            episodes = episodes_by_act.get(act_name, [])

            # 막 표시 이름 생성
            display_name = self._get_act_display_name(act_name)
            ep_count = len(episodes)

            # 막 노드 추가
            act_id = f"act_{act_name}"
            self.tree.insert(
                "",
                tk.END,
                iid=act_id,
                text=f"{display_name} ({ep_count})",
                open=False,
                tags=("act",)
            )

            # 에피소드 노드 추가
            for ep in episodes:
                ep_num = ep.get("episode_num", 0) or ep.get("chapter_number", 0)
                ep_title = ep.get("title", "")

                # 제목이 너무 길면 축약
                if len(ep_title) > 12:
                    ep_title = ep_title[:12] + ".."

                ep_id = f"ep_{act_name}_{ep_num}"
                self.tree.insert(
                    act_id,
                    tk.END,
                    iid=ep_id,
                    text=f"EP{ep_num:02d} {ep_title}",
                    tags=("episode",)
                )

        # 첫 번째 막 펼치기
        if sorted_acts:
            first_act_id = f"act_{sorted_acts[0]}"
            self.tree.item(first_act_id, open=True)

    def _get_act_display_name(self, act_name: str) -> str:
        """막 이름을 표시용 텍스트로 변환"""
        import re

        # Act1_지옥의시작 -> 1막: 지옥의시작
        match = re.match(r'Act(\d+)(?:-(\d+))?_(.+)', act_name)
        if match:
            main_num = match.group(1)
            sub_num = match.group(2)
            title = match.group(3)
            if sub_num:
                return f"{main_num}-{sub_num}막: {title}"
            else:
                return f"{main_num}막: {title}"
        return act_name

    def _on_tree_select(self, event):
        """트리 항목 선택 이벤트"""
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]

        # 빈 항목 무시
        if item_id == "__empty__":
            return

        # 막 선택 시 (펼침/접힘만)
        if item_id.startswith("act_"):
            act_name = item_id[4:]  # "act_" 제거
            self.current_act = act_name
            # 막 전체 보기 콜백
            if self.on_select_all_callback:
                self.on_select_all_callback(act_name)

        # 에피소드 선택 시
        elif item_id.startswith("ep_"):
            parts = item_id[3:].rsplit("_", 1)  # "ep_" 제거 후 분리
            if len(parts) == 2:
                act_name = parts[0]
                try:
                    ep_num = int(parts[1])
                except ValueError:
                    return

                self.current_act = act_name
                self.current_episode_num = ep_num

                # 에피소드 데이터 찾기
                episodes = self.episodes_by_act.get(act_name, [])
                ep_data = None
                for ep in episodes:
                    if (ep.get("episode_num") == ep_num or
                        ep.get("chapter_number") == ep_num):
                        ep_data = ep
                        break

                if ep_data and self.on_select_callback:
                    self.on_select_callback(act_name, ep_data)

    def _on_single_click(self, event):
        """싱글 클릭으로 막 펼침/접힘 토글 (화살표 외 영역도 지원)"""
        # 클릭한 위치의 항목 확인
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        # 클릭한 영역 확인 (tree: 텍스트/아이콘 영역)
        region = self.tree.identify_region(event.x, event.y)

        # 막 항목 클릭 시 펼침/접힘 토글
        if item_id.startswith("act_") and region in ("tree", "cell"):
            is_open = self.tree.item(item_id, "open")
            self.tree.item(item_id, open=not is_open)

    def _on_double_click(self, event):
        """더블클릭으로 막 펼침/접힘 토글"""
        item_id = self.tree.identify_row(event.y)
        if item_id and item_id.startswith("act_"):
            is_open = self.tree.item(item_id, "open")
            self.tree.item(item_id, open=not is_open)
            return "break"  # 이벤트 전파 중단

    def _on_select_all(self):
        """전체 대본 보기"""
        if self.on_select_all_callback:
            self.on_select_all_callback(None)

    def select_episode(self, act_name: str, episode_num: int):
        """프로그래밍 방식으로 에피소드 선택"""
        # 막 펼치기
        act_id = f"act_{act_name}"
        if self.tree.exists(act_id):
            self.tree.item(act_id, open=True)

        # 에피소드 선택
        ep_id = f"ep_{act_name}_{episode_num}"
        if self.tree.exists(ep_id):
            self.tree.selection_set(ep_id)
            self.tree.see(ep_id)

    def get_frame(self) -> tk.Frame:
        """프레임 위젯 반환"""
        return self.frame
