"""
대본 탭
에피소드 MD 파일을 막(Act) > 에피소드 구조로 표시합니다.
사이드바 트리뷰 구조로 깔끔하게 표시합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import re
from typing import Optional, Dict, List, Any
from .base_tab import BaseTab
from utils.ui_helpers import ActEpisodeTreeView


class ScriptsTab(BaseTab):
    """대본 탭 클래스 - 사이드바 트리뷰 구조"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        # 데이터
        self.episodes_by_act: Dict[str, List[Dict[str, Any]]] = {}
        self.current_act: str = ""
        self.current_episode_num: int = 0

        # UI 요소
        self.tree_view: Optional[ActEpisodeTreeView] = None
        self.script_viewer: Optional[scrolledtext.ScrolledText] = None
        self.info_label: Optional[ttk.Label] = None

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "대본"

    def create_ui(self):
        """UI 생성 - 사이드바 트리뷰 + 콘텐츠 영역"""
        self.frame.columnconfigure(0, weight=0)  # 사이드바
        self.frame.columnconfigure(1, weight=1)  # 콘텐츠
        self.frame.rowconfigure(0, weight=1)

        # ===== 왼쪽: 사이드바 트리뷰 =====
        sidebar_frame = ttk.Frame(self.frame, padding=(5, 5, 0, 5))
        sidebar_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))

        self.tree_view = ActEpisodeTreeView(
            parent=sidebar_frame,
            on_select_callback=self._on_episode_select,
            on_select_all_callback=self._on_show_all,
            width=240,
            all_button_text="전체 대본"
        )

        # ===== 오른쪽: 콘텐츠 영역 =====
        content_frame = ttk.Frame(self.frame, padding=5)
        content_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        # 상단: 정보 표시 + 복사 버튼
        header_frame = ttk.Frame(content_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        header_frame.columnconfigure(0, weight=1)

        self.info_label = ttk.Label(
            header_frame,
            text="에피소드를 선택하세요",
            font=("맑은 고딕", 11, "bold"),
            foreground="#333"
        )
        self.info_label.grid(row=0, column=0, sticky=tk.W)

        # 복사 버튼
        ttk.Button(
            header_frame,
            text="대본 복사",
            command=self._copy_to_clipboard
        ).grid(row=0, column=1, sticky=tk.E)

        # 대본 뷰어
        viewer_frame = ttk.LabelFrame(content_frame, text="대본 내용", padding=8)
        viewer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        self.script_viewer = scrolledtext.ScrolledText(
            viewer_frame,
            wrap=tk.WORD,
            font=("맑은 고딕", 11),
            state=tk.DISABLED,
            borderwidth=0,
            highlightthickness=0
        )
        self.script_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def update_display(self):
        """화면 업데이트 - MD 파일 로드"""
        # 에피소드 스크립트 로드
        self.episodes_by_act = self.file_service.load_episode_scripts()

        if not self.episodes_by_act:
            self._show_no_data_message()
            return

        # 트리뷰에 데이터 로드
        if self.tree_view:
            self.tree_view.load_data(self.episodes_by_act)

        # 첫 에피소드 자동 선택
        if self.episodes_by_act:
            first_act = list(self.episodes_by_act.keys())[0]
            episodes = self.episodes_by_act.get(first_act, [])
            if episodes:
                self._on_episode_select(first_act, episodes[0])

    def _show_no_data_message(self):
        """데이터 없음 메시지"""
        if self.tree_view:
            self.tree_view.load_data({})

        if self.info_label:
            self.info_label.config(text="대본 파일 없음")

        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0,
                "대본 파일이 없습니다.\n\n"
                "프로젝트 폴더 내에 '*_episodes' 폴더를 확인해주세요.\n"
                "예: 프로젝트명_episodes/Act1_제목/EP01_에피소드제목.md"
            )
            self.script_viewer.config(state=tk.DISABLED)

    def _on_episode_select(self, act_name: str, episode_data: Dict[str, Any]):
        """에피소드 선택 시 콜백"""
        self.current_act = act_name
        self.current_episode_num = episode_data.get("episode_num", 0)

        # 정보 표시
        ep_title = episode_data.get("title", "")
        char_count = episode_data.get("char_count", 0)
        act_display = self._get_act_display_short(act_name)

        if self.info_label:
            self.info_label.config(
                text=f"{act_display} > EP{self.current_episode_num:02d}: {ep_title}  ({char_count:,}자)"
            )

        # 대본 내용 표시
        content = episode_data.get("content", "")
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0, content)
            self.script_viewer.config(state=tk.DISABLED)
            self.script_viewer.see("1.0")

    def _on_show_all(self, act_name: Optional[str]):
        """
        전체 보기 콜백
        act_name이 None이면 전체 대본, 아니면 해당 막 전체
        """
        if act_name is None:
            self._show_all_scripts()
        else:
            self._show_act_scripts(act_name)

    def _show_act_scripts(self, act_name: str):
        """특정 막의 모든 에피소드 표시"""
        episodes = self.episodes_by_act.get(act_name, [])
        if not episodes:
            return

        self.current_act = act_name
        self.current_episode_num = 0

        # 전체 내용 생성
        lines = []
        total_chars = 0
        act_display = self._get_act_display_short(act_name)

        lines.append("=" * 70)
        lines.append(f"  {act_display} 전체 대본")
        lines.append("=" * 70)
        lines.append("")

        for ep in episodes:
            ep_num = ep.get("episode_num", 0)
            ep_title = ep.get("title", "")
            content = ep.get("content", "")
            char_count = len(content)
            total_chars += char_count

            lines.append("-" * 50)
            lines.append(f"  EP{ep_num:02d}: {ep_title} ({char_count:,}자)")
            lines.append("-" * 50)
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("")

        lines.append("=" * 70)
        lines.append(f"  총 {len(episodes)}개 에피소드, {total_chars:,}자")
        lines.append("=" * 70)

        full_text = "\n".join(lines)

        # 정보 표시
        if self.info_label:
            self.info_label.config(
                text=f"{act_display} 전체  ({len(episodes)}개 에피소드, {total_chars:,}자)"
            )

        # 대본 표시
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0, full_text)
            self.script_viewer.config(state=tk.DISABLED)
            self.script_viewer.see("1.0")

    def _show_all_scripts(self):
        """전체 대본 표시"""
        if not self.episodes_by_act:
            return

        self.current_act = ""
        self.current_episode_num = 0

        # 전체 내용 생성
        lines = []
        total_chars = 0
        total_episodes = 0

        lines.append("=" * 70)
        lines.append("  전체 대본")
        lines.append("=" * 70)
        lines.append("")

        # 막 정렬
        sorted_acts = sorted(
            self.episodes_by_act.keys(),
            key=lambda x: self._act_sort_key(x)
        )

        for act_name in sorted_acts:
            episodes = self.episodes_by_act.get(act_name, [])
            act_display = self._get_act_display_short(act_name)

            lines.append("=" * 70)
            lines.append(f"  {act_display}")
            lines.append("=" * 70)
            lines.append("")

            for ep in episodes:
                ep_num = ep.get("episode_num", 0)
                ep_title = ep.get("title", "")
                content = ep.get("content", "")
                char_count = len(content)
                total_chars += char_count
                total_episodes += 1

                lines.append("-" * 50)
                lines.append(f"  EP{ep_num:02d}: {ep_title} ({char_count:,}자)")
                lines.append("-" * 50)
                lines.append("")
                lines.append(content)
                lines.append("")
                lines.append("")

        lines.append("=" * 70)
        lines.append(f"  전체 {len(sorted_acts)}막, {total_episodes}개 에피소드, {total_chars:,}자")
        lines.append("=" * 70)

        full_text = "\n".join(lines)

        # 정보 표시
        if self.info_label:
            self.info_label.config(
                text=f"전체 대본  ({len(sorted_acts)}막 {total_episodes}개 에피소드, {total_chars:,}자)"
            )

        # 대본 표시
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0, full_text)
            self.script_viewer.config(state=tk.DISABLED)
            self.script_viewer.see("1.0")

    def _get_act_display_short(self, act_name: str) -> str:
        """막 이름을 짧은 표시용 텍스트로 변환"""
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

    def _act_sort_key(self, act_name: str) -> tuple:
        """막 이름 정렬 키"""
        match = re.search(r'Act(\d+)(?:-(\d+))?', act_name)
        if match:
            main_num = int(match.group(1))
            sub_num = int(match.group(2)) if match.group(2) else 0
            return (main_num, sub_num)
        return (999, 0)

    def _copy_to_clipboard(self):
        """대본 내용을 클립보드에 복사"""
        if not self.script_viewer:
            return

        # 텍스트 가져오기
        content = self.script_viewer.get(1.0, tk.END).strip()

        if not content:
            return

        # 클립보드에 복사
        self.frame.clipboard_clear()
        self.frame.clipboard_append(content)

        # 복사 완료 알림 (info_label에 임시 표시)
        original_text = self.info_label.cget("text")
        self.info_label.config(text="복사 완료!", foreground="green")

        # 2초 후 원래 텍스트로 복원
        self.frame.after(2000, lambda: self.info_label.config(text=original_text, foreground="#333"))

    def save(self) -> bool:
        """데이터 저장 (대본 탭은 읽기 전용이므로 항상 True)"""
        return True
