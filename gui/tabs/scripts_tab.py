"""
대본 탭
에피소드 MD 파일을 막(Act) > 에피소드 구조로 표시합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from typing import Optional, Dict, List, Any
from .base_tab import BaseTab


class ScriptsTab(BaseTab):
    """대본 탭 클래스 - 막 > 에피소드 구조"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        # 막/에피소드 데이터
        self.episodes_by_act: Dict[str, List[Dict[str, Any]]] = {}
        self.act_names: List[str] = []
        self.current_act: str = ""
        self.current_episode_num: int = 0

        # UI 요소
        self.act_buttons_frame = None
        self.act_buttons: Dict[str, ttk.Button] = {}
        self.episode_buttons_frame = None
        self.episode_buttons: Dict[int, ttk.Button] = {}
        self.script_viewer = None
        self.script_char_count_label = None

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "대본"

    def create_ui(self):
        """UI 생성 - 막 > 에피소드 계층 구조"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)  # 콘텐츠 영역

        # ===== 상단: 막(Act) 선택 버튼 =====
        act_row = ttk.Frame(self.frame)
        act_row.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=(10, 5))

        ttk.Label(
            act_row,
            text="막 선택:",
            font=("맑은 고딕", 11, "bold")
        ).pack(side=tk.LEFT, padx=(5, 10))

        self.act_buttons_frame = ttk.Frame(act_row)
        self.act_buttons_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ===== 중단: 에피소드 선택 버튼 =====
        episode_row = ttk.Frame(self.frame)
        episode_row.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(
            episode_row,
            text="에피소드:",
            font=("맑은 고딕", 10)
        ).pack(side=tk.LEFT, padx=(5, 10))

        self.episode_buttons_frame = ttk.Frame(episode_row)
        self.episode_buttons_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 글자 수 표시
        self.script_char_count_label = ttk.Label(
            episode_row,
            text="",
            font=("맑은 고딕", 10),
            foreground="gray"
        )
        self.script_char_count_label.pack(side=tk.RIGHT, padx=10)

        # ===== 하단: 대본 뷰어 =====
        content_frame = ttk.LabelFrame(self.frame, text="대본 내용", padding=10)
        content_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        self.script_viewer = scrolledtext.ScrolledText(
            content_frame,
            width=100,
            height=30,
            wrap=tk.WORD,
            font=("맑은 고딕", 11),
            state=tk.DISABLED
        )
        self.script_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def update_display(self):
        """화면 업데이트 - MD 파일 로드"""
        # 에피소드 스크립트 로드
        self.episodes_by_act = self.file_service.load_episode_scripts()

        if not self.episodes_by_act:
            self._show_no_episodes_message()
            return

        # 막 이름 정렬 (Act1, Act2-1, Act2-2, Act3 순서)
        self.act_names = sorted(
            self.episodes_by_act.keys(),
            key=lambda x: self._act_sort_key(x)
        )

        # 막 버튼 생성
        self._create_act_buttons()

        # 첫 번째 막 자동 선택
        if self.act_names and not self.current_act:
            self._select_act(self.act_names[0])

    def _act_sort_key(self, act_name: str) -> tuple:
        """막 이름 정렬 키 (Act1, Act2-1, Act2-2, Act3 순서)"""
        match = re.search(r'Act(\d+)(?:-(\d+))?', act_name)
        if match:
            main_num = int(match.group(1))
            sub_num = int(match.group(2)) if match.group(2) else 0
            return (main_num, sub_num)
        return (999, 0)

    def _show_no_episodes_message(self):
        """에피소드가 없을 때 메시지 표시"""
        # 막 버튼 영역 비우기
        if self.act_buttons_frame:
            for widget in self.act_buttons_frame.winfo_children():
                widget.destroy()
            ttk.Label(
                self.act_buttons_frame,
                text="(대본 없음)",
                font=("맑은 고딕", 9),
                foreground="gray"
            ).pack(side=tk.LEFT)

        # 에피소드 버튼 영역 비우기
        if self.episode_buttons_frame:
            for widget in self.episode_buttons_frame.winfo_children():
                widget.destroy()

        # 뷰어에 안내 메시지
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0,
                "대본 파일이 없습니다.\n\n"
                "프로젝트 폴더 내에 '*_episodes' 폴더를 확인해주세요.\n"
                "예: 프로젝트명_episodes/Act1_제목/EP01_에피소드제목.md"
            )
            self.script_viewer.config(state=tk.DISABLED)

        # 글자 수 초기화
        if self.script_char_count_label:
            self.script_char_count_label.config(text="")

    def _create_act_buttons(self):
        """막(Act) 선택 버튼 생성"""
        if not self.act_buttons_frame:
            return

        # 기존 버튼 제거
        for widget in self.act_buttons_frame.winfo_children():
            widget.destroy()
        self.act_buttons.clear()

        if not self.act_names:
            ttk.Label(
                self.act_buttons_frame,
                text="(대본 없음)",
                font=("맑은 고딕", 9),
                foreground="gray"
            ).pack(side=tk.LEFT)
            return

        # 각 막별 버튼 생성
        for act_name in self.act_names:
            # 막 이름에서 표시용 텍스트 추출
            display_name = self._get_act_display_name(act_name)
            episode_count = len(self.episodes_by_act.get(act_name, []))

            btn = ttk.Button(
                self.act_buttons_frame,
                text=f"{display_name} ({episode_count})",
                width=15,
                command=lambda a=act_name: self._select_act(a)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.act_buttons[act_name] = btn

        # "전체 보기" 버튼 추가
        ttk.Separator(self.act_buttons_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        all_btn = ttk.Button(
            self.act_buttons_frame,
            text="전체 대본",
            width=12,
            command=self._show_all_scripts
        )
        all_btn.pack(side=tk.LEFT, padx=3)

    def _get_act_display_name(self, act_name: str) -> str:
        """막 이름을 표시용 텍스트로 변환"""
        # Act1_지옥의시작 -> 1막: 지옥의시작
        match = re.match(r'Act(\d+)(?:-(\d+))?_(.+)', act_name)
        if match:
            main_num = match.group(1)
            sub_num = match.group(2)
            title = match.group(3)
            if sub_num:
                return f"{main_num}-{sub_num}막"
            else:
                return f"{main_num}막"
        return act_name

    def _select_act(self, act_name: str):
        """막 선택"""
        self.current_act = act_name
        self.current_episode_num = 0

        # 막 버튼 상태 업데이트
        self._update_act_button_state()

        # 에피소드 버튼 생성
        self._create_episode_buttons()

        # 첫 에피소드 자동 선택
        episodes = self.episodes_by_act.get(act_name, [])
        if episodes:
            self._select_episode(episodes[0].get('episode_num', 1))

    def _update_act_button_state(self):
        """막 버튼 선택 상태 업데이트"""
        for act_name, btn in self.act_buttons.items():
            if act_name == self.current_act:
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])

    def _create_episode_buttons(self):
        """현재 막의 에피소드 버튼 생성"""
        if not self.episode_buttons_frame:
            return

        # 기존 버튼 제거
        for widget in self.episode_buttons_frame.winfo_children():
            widget.destroy()
        self.episode_buttons.clear()

        episodes = self.episodes_by_act.get(self.current_act, [])

        if not episodes:
            ttk.Label(
                self.episode_buttons_frame,
                text="(에피소드 없음)",
                font=("맑은 고딕", 9),
                foreground="gray"
            ).pack(side=tk.LEFT)
            return

        # 각 에피소드별 버튼 생성
        for ep in episodes:
            ep_num = ep.get('episode_num', 0)
            ep_title = ep.get('title', '')

            # 버튼 텍스트 (번호 + 짧은 제목)
            short_title = ep_title[:6] + ".." if len(ep_title) > 6 else ep_title
            btn_text = f"EP{ep_num:02d}"

            btn = ttk.Button(
                self.episode_buttons_frame,
                text=btn_text,
                width=8,
                command=lambda n=ep_num: self._select_episode(n)
            )
            btn.pack(side=tk.LEFT, padx=2)

            # 툴팁으로 전체 제목 표시
            self._create_tooltip(btn, f"EP{ep_num}: {ep_title}")

            self.episode_buttons[ep_num] = btn

        # "막 전체" 버튼 추가
        ttk.Separator(self.episode_buttons_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        act_all_btn = ttk.Button(
            self.episode_buttons_frame,
            text="막 전체",
            width=8,
            command=self._show_current_act_all
        )
        act_all_btn.pack(side=tk.LEFT, padx=2)

    def _create_tooltip(self, widget, text: str):
        """위젯에 툴팁 추가"""
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="lightyellow", padding=3)
            label.pack()
            widget._tooltip = tooltip
            widget.after(2000, lambda: tooltip.destroy() if tooltip.winfo_exists() else None)

        def hide_tooltip(event):
            if hasattr(widget, '_tooltip') and widget._tooltip.winfo_exists():
                widget._tooltip.destroy()

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def _select_episode(self, episode_num: int):
        """에피소드 선택"""
        self.current_episode_num = episode_num

        # 에피소드 버튼 상태 업데이트
        self._update_episode_button_state()

        # 에피소드 내용 표시
        self._display_episode(episode_num)

    def _update_episode_button_state(self):
        """에피소드 버튼 선택 상태 업데이트"""
        for ep_num, btn in self.episode_buttons.items():
            if ep_num == self.current_episode_num:
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])

    def _display_episode(self, episode_num: int):
        """에피소드 내용 표시"""
        episodes = self.episodes_by_act.get(self.current_act, [])

        # 해당 에피소드 찾기
        episode = None
        for ep in episodes:
            if ep.get('episode_num') == episode_num:
                episode = ep
                break

        if not episode:
            return

        content = episode.get('content', '')
        title = episode.get('title', '')
        char_count = episode.get('char_count', len(content))

        # 뷰어에 표시
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0, content)
            self.script_viewer.config(state=tk.DISABLED)
            # 스크롤을 맨 위로
            self.script_viewer.see("1.0")

        # 글자 수 표시
        if self.script_char_count_label:
            act_display = self._get_act_display_name(self.current_act)
            self.script_char_count_label.config(
                text=f"{act_display} | EP{episode_num}: {title} | {char_count:,}자"
            )

    def _show_current_act_all(self):
        """현재 막의 모든 에피소드 표시"""
        episodes = self.episodes_by_act.get(self.current_act, [])

        if not episodes:
            return

        # 에피소드 버튼 선택 해제
        self.current_episode_num = 0
        self._update_episode_button_state()

        # 전체 내용 생성
        lines = []
        total_chars = 0

        act_display = self._get_act_display_name(self.current_act)
        lines.append("=" * 80)
        lines.append(f"【 {act_display} 전체 대본 】")
        lines.append("=" * 80)
        lines.append("")

        for ep in episodes:
            ep_num = ep.get('episode_num', 0)
            ep_title = ep.get('title', '')
            content = ep.get('content', '')
            char_count = len(content)
            total_chars += char_count

            lines.append("-" * 60)
            lines.append(f"▶ EP{ep_num:02d}: {ep_title} ({char_count:,}자)")
            lines.append("-" * 60)
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("")

        lines.append("=" * 80)
        lines.append(f"【 {act_display} 총 글자 수: {total_chars:,}자 】")
        lines.append("=" * 80)

        full_text = "\n".join(lines)

        # 뷰어에 표시
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0, full_text)
            self.script_viewer.config(state=tk.DISABLED)
            self.script_viewer.see("1.0")

        # 글자 수 표시
        if self.script_char_count_label:
            self.script_char_count_label.config(
                text=f"{act_display} 전체 | {len(episodes)}개 에피소드 | {total_chars:,}자"
            )

    def _show_all_scripts(self):
        """전체 대본 표시 (모든 막, 모든 에피소드)"""
        if not self.episodes_by_act:
            return

        # 선택 상태 초기화
        self.current_act = ""
        self.current_episode_num = 0

        # 막 버튼 선택 해제
        for btn in self.act_buttons.values():
            btn.state(['!pressed'])

        # 에피소드 버튼 비우기
        if self.episode_buttons_frame:
            for widget in self.episode_buttons_frame.winfo_children():
                widget.destroy()

        # 전체 내용 생성
        lines = []
        total_chars = 0
        total_episodes = 0

        lines.append("=" * 80)
        lines.append("【 전체 대본 】")
        lines.append("=" * 80)
        lines.append("")

        for act_name in self.act_names:
            episodes = self.episodes_by_act.get(act_name, [])
            act_display = self._get_act_display_name(act_name)

            # 막 제목에서 부제목 추출
            match = re.match(r'Act\d+(?:-\d+)?_(.+)', act_name)
            act_subtitle = match.group(1) if match else ""

            lines.append("=" * 80)
            lines.append(f"【 {act_display}: {act_subtitle} 】")
            lines.append("=" * 80)
            lines.append("")

            for ep in episodes:
                ep_num = ep.get('episode_num', 0)
                ep_title = ep.get('title', '')
                content = ep.get('content', '')
                char_count = len(content)
                total_chars += char_count
                total_episodes += 1

                lines.append("-" * 60)
                lines.append(f"▶ EP{ep_num:02d}: {ep_title} ({char_count:,}자)")
                lines.append("-" * 60)
                lines.append("")
                lines.append(content)
                lines.append("")
                lines.append("")

        lines.append("=" * 80)
        lines.append(f"【 전체 {len(self.act_names)}막, {total_episodes}개 에피소드, 총 {total_chars:,}자 】")
        lines.append("=" * 80)

        full_text = "\n".join(lines)

        # 뷰어에 표시
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0, full_text)
            self.script_viewer.config(state=tk.DISABLED)
            self.script_viewer.see("1.0")

        # 글자 수 표시
        if self.script_char_count_label:
            self.script_char_count_label.config(
                text=f"전체 대본 | {len(self.act_names)}막 {total_episodes}개 에피소드 | {total_chars:,}자"
            )

    def save(self) -> bool:
        """데이터 저장 (대본 탭은 읽기 전용이므로 항상 True)"""
        return True
