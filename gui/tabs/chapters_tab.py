"""
챕터 탭
챕터 목록을 사이드바 트리뷰 구조로 표시합니다.
대본 탭과 동일한 UI 구조를 사용합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import re
from typing import Optional, Dict, List, Any
from .base_tab import BaseTab
from utils.file_utils import get_chapter_filename, get_character_filename
from utils.ui_helpers import ActEpisodeTreeView


class ChaptersTab(BaseTab):
    """챕터 탭 클래스 - 사이드바 트리뷰 구조"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        # 데이터
        self.chapters_by_act: Dict[str, List[Dict[str, Any]]] = {}
        self.current_act: str = ""
        self.current_chapter_num: int = 0
        self.current_chapter: Optional[Dict[str, Any]] = None

        # UI 요소
        self.tree_view: Optional[ActEpisodeTreeView] = None
        self.info_label: Optional[ttk.Label] = None
        self.content_text: Optional[scrolledtext.ScrolledText] = None
        self.detail_text: Optional[scrolledtext.ScrolledText] = None
        self.script_text: Optional[scrolledtext.ScrolledText] = None

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "챕터"

    def create_ui(self):
        """UI 생성 - 사이드바 트리뷰 + 콘텐츠 영역 (대본 탭과 동일한 구조)"""
        self.frame.columnconfigure(0, weight=0)  # 사이드바
        self.frame.columnconfigure(1, weight=1)  # 콘텐츠
        self.frame.rowconfigure(0, weight=1)

        # ===== 왼쪽: 사이드바 트리뷰 =====
        sidebar_frame = ttk.Frame(self.frame, padding=(5, 5, 0, 5))
        sidebar_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))

        self.tree_view = ActEpisodeTreeView(
            parent=sidebar_frame,
            on_select_callback=self._on_chapter_select,
            on_select_all_callback=self._on_show_all,
            width=240,
            all_button_text="전체 챕터"
        )

        # ===== 오른쪽: 콘텐츠 영역 =====
        content_frame = ttk.Frame(self.frame, padding=5)
        content_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        # 상단: 정보 표시 + 버튼
        header_frame = ttk.Frame(content_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        header_frame.columnconfigure(0, weight=1)

        self.info_label = ttk.Label(
            header_frame,
            text="챕터를 선택하세요",
            font=("맑은 고딕", 11, "bold"),
            foreground="#333"
        )
        self.info_label.grid(row=0, column=0, sticky=tk.W)

        btn_row = ttk.Frame(header_frame)
        btn_row.grid(row=0, column=1, sticky=tk.E)

        ttk.Button(
            btn_row,
            text="새로고침",
            command=self.update_display
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_row,
            text="새 챕터",
            command=self._add_new_chapter
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_row,
            text="대본 생성",
            command=self._generate_script
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_row,
            text="전체 저장",
            command=self._save_all
        ).pack(side=tk.LEFT, padx=2)

        # 에디터 영역 (노트북으로 탭 구성)
        editor_notebook = ttk.Notebook(content_frame)
        editor_notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 탭 1: 내용
        content_tab = ttk.Frame(editor_notebook, padding=8)
        editor_notebook.add(content_tab, text="내용")
        content_tab.columnconfigure(0, weight=1)
        content_tab.rowconfigure(0, weight=1)

        self.content_text = scrolledtext.ScrolledText(
            content_tab,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
            height=8
        )
        self.content_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_text.bind("<KeyRelease>", lambda e: self.mark_unsaved())

        ttk.Button(
            content_tab,
            text="내용 저장",
            command=self._save_content
        ).grid(row=1, column=0, sticky=tk.E, pady=(5, 0))

        # 탭 2: 세부 정보
        detail_tab = ttk.Frame(editor_notebook, padding=8)
        editor_notebook.add(detail_tab, text="세부 정보")
        detail_tab.columnconfigure(0, weight=1)
        detail_tab.rowconfigure(0, weight=1)

        self.detail_text = scrolledtext.ScrolledText(
            detail_tab,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
            height=12
        )
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.detail_text.bind("<KeyRelease>", lambda e: self.mark_unsaved())

        ttk.Button(
            detail_tab,
            text="세부 정보 저장",
            command=self._save_detail
        ).grid(row=1, column=0, sticky=tk.E, pady=(5, 0))

        # 탭 3: 대본
        script_tab = ttk.Frame(editor_notebook, padding=8)
        editor_notebook.add(script_tab, text="대본")
        script_tab.columnconfigure(0, weight=1)
        script_tab.rowconfigure(0, weight=1)

        self.script_text = scrolledtext.ScrolledText(
            script_tab,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
            height=20
        )
        self.script_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.script_text.bind("<KeyRelease>", lambda e: self.mark_unsaved())

        script_btn_frame = ttk.Frame(script_tab)
        script_btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Button(
            script_btn_frame,
            text="대본 저장",
            command=self._save_script
        ).pack(side=tk.RIGHT, padx=2)

        ttk.Button(
            script_btn_frame,
            text="파일에서 불러오기",
            command=self._reload_script
        ).pack(side=tk.RIGHT, padx=2)

    def update_display(self):
        """화면 업데이트"""
        # 파일에서 최신 데이터 로드
        try:
            all_data = self.file_service.load_all_data()
            self.project_data.data = all_data
        except Exception as e:
            print(f"데이터 로드 오류: {e}")

        chapters = self.project_data.get_chapters()

        if not chapters:
            self._show_no_data_message()
            return

        # 챕터 데이터를 막/에피소드 구조로 변환
        self.chapters_by_act = self._convert_chapters_to_act_structure(chapters)

        # 트리뷰에 데이터 로드
        if self.tree_view:
            self.tree_view.load_data(self.chapters_by_act)

        # 첫 챕터 자동 선택
        if self.chapters_by_act:
            first_act = list(self.chapters_by_act.keys())[0]
            chapters_in_act = self.chapters_by_act.get(first_act, [])
            if chapters_in_act:
                self._on_chapter_select(first_act, chapters_in_act[0])

    def _convert_chapters_to_act_structure(self, chapters: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        챕터 데이터를 막/에피소드 구조로 변환

        챕터에 act 필드가 있으면 그 값으로 그룹화,
        없으면 "전체" 막으로 통합
        """
        result: Dict[str, List[Dict[str, Any]]] = {}

        for chapter in chapters:
            # 막 이름 결정
            act = chapter.get("act", "") or chapter.get("_folder", "")
            if not act:
                act = "Act1_전체"

            # 에피소드 데이터 형태로 변환
            chapter_data = {
                "episode_num": chapter.get("chapter_number", 0),
                "chapter_number": chapter.get("chapter_number", 0),
                "title": chapter.get("title", f"챕터 {chapter.get('chapter_number', 0)}"),
                "content": chapter.get("content", ""),
                "content_detail": chapter.get("content_detail", ""),
                "script": chapter.get("script", ""),
                "_original": chapter  # 원본 데이터 참조
            }

            if act not in result:
                result[act] = []
            result[act].append(chapter_data)

        # 각 막 내에서 챕터 번호로 정렬
        for act in result:
            result[act].sort(key=lambda x: x.get("chapter_number", 0))

        return result

    def _show_no_data_message(self):
        """데이터 없음 메시지"""
        if self.tree_view:
            self.tree_view.load_data({})

        if self.info_label:
            self.info_label.config(text="챕터 정보 없음")

        # 에디터 비우기
        for text_widget in [self.content_text, self.detail_text, self.script_text]:
            if text_widget:
                text_widget.delete(1.0, tk.END)
                text_widget.insert(1.0, "챕터 정보가 없습니다.\n시놉시스 입력 탭에서 챕터를 입력해주세요.")

    def _on_chapter_select(self, act_name: str, chapter_data: Dict[str, Any]):
        """챕터 선택 시 콜백"""
        self.current_act = act_name
        self.current_chapter_num = chapter_data.get("chapter_number", 0)
        self.current_chapter = chapter_data.get("_original", chapter_data)

        # 정보 표시
        title = chapter_data.get("title", "")
        if self.info_label:
            self.info_label.config(text=f"챕터 {self.current_chapter_num}: {title}")

        # 내용 표시
        content = chapter_data.get("content", "")
        if self.content_text:
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, content)

        # 세부 정보 표시
        detail = chapter_data.get("content_detail", "")
        if self.detail_text:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, detail)

        # 대본 표시 (파일에서 로드)
        script = ""
        try:
            data = self.file_service.load_script_file(self.current_chapter_num)
            if isinstance(data, dict):
                script = str(data.get("script", "") or "")
        except Exception:
            pass

        if not script:
            script = chapter_data.get("script", "")

        if self.script_text:
            self.script_text.delete(1.0, tk.END)
            self.script_text.insert(1.0, script)

    def _on_show_all(self, act_name: Optional[str]):
        """전체 보기 콜백"""
        if act_name is None:
            self._show_all_chapters()
        else:
            self._show_act_chapters(act_name)

    def _show_act_chapters(self, act_name: str):
        """특정 막의 모든 챕터 요약 표시"""
        chapters = self.chapters_by_act.get(act_name, [])
        if not chapters:
            return

        self.current_act = act_name
        self.current_chapter_num = 0
        self.current_chapter = None

        # 정보 표시
        if self.info_label:
            self.info_label.config(text=f"{act_name} 전체 ({len(chapters)}개 챕터)")

        # 요약 텍스트 생성
        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"  {act_name} 전체 요약")
        lines.append(f"{'='*60}")
        lines.append("")

        for ch in chapters:
            num = ch.get("chapter_number", 0)
            title = ch.get("title", "")
            content = ch.get("content", "")[:100]
            if len(ch.get("content", "")) > 100:
                content += "..."

            lines.append(f"[챕터 {num}] {title}")
            lines.append(f"  {content}")
            lines.append("")

        summary = "\n".join(lines)

        # 내용 탭에 요약 표시
        if self.content_text:
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, summary)

        # 다른 탭 비우기
        if self.detail_text:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, "(막 전체 선택 - 개별 챕터를 선택하세요)")

        if self.script_text:
            self.script_text.delete(1.0, tk.END)
            self.script_text.insert(1.0, "(막 전체 선택 - 개별 챕터를 선택하세요)")

    def _show_all_chapters(self):
        """전체 챕터 요약 표시"""
        self.current_act = ""
        self.current_chapter_num = 0
        self.current_chapter = None

        total_chapters = sum(len(chs) for chs in self.chapters_by_act.values())

        # 정보 표시
        if self.info_label:
            self.info_label.config(text=f"전체 챕터 ({total_chapters}개)")

        # 요약 텍스트 생성
        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"  전체 챕터 요약")
        lines.append(f"{'='*60}")
        lines.append("")

        for act_name, chapters in self.chapters_by_act.items():
            lines.append(f"--- {act_name} ({len(chapters)}개) ---")
            for ch in chapters:
                num = ch.get("chapter_number", 0)
                title = ch.get("title", "")
                lines.append(f"  [챕터 {num}] {title}")
            lines.append("")

        summary = "\n".join(lines)

        # 내용 탭에 요약 표시
        if self.content_text:
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, summary)

        # 다른 탭 비우기
        if self.detail_text:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, "(전체 선택 - 개별 챕터를 선택하세요)")

        if self.script_text:
            self.script_text.delete(1.0, tk.END)
            self.script_text.insert(1.0, "(전체 선택 - 개별 챕터를 선택하세요)")

    def _save_content(self):
        """내용 저장"""
        if not self.current_chapter_num:
            messagebox.showwarning("경고", "먼저 챕터를 선택하세요.")
            return

        content = self.content_text.get(1.0, tk.END).strip()

        try:
            # 시놉시스에 저장
            synopsis = self.file_service.load_synopsis()
            if not isinstance(synopsis, dict):
                synopsis = {}

            syn_chapters = synopsis.get("chapters", {})
            if not isinstance(syn_chapters, dict):
                syn_chapters = {}

            syn_key = f"chapter_{self.current_chapter_num:02d}"
            syn_chapters[syn_key] = content
            synopsis["chapters"] = syn_chapters

            self.file_service.save_synopsis(synopsis)
            self.project_data.set_synopsis(synopsis)

            # 챕터 파일에도 저장
            chapters = self.file_service.load_chapters()
            for ch in chapters:
                if ch.get("chapter_number") == self.current_chapter_num:
                    ch["content"] = content
                    self.file_service.save_chapter(ch)
                    break

            messagebox.showinfo("완료", f"챕터 {self.current_chapter_num} 내용이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류: {e}")

    def _save_detail(self):
        """세부 정보 저장"""
        if not self.current_chapter_num:
            messagebox.showwarning("경고", "먼저 챕터를 선택하세요.")
            return

        detail = self.detail_text.get(1.0, tk.END).strip()

        try:
            chapters = self.file_service.load_chapters()
            for ch in chapters:
                if ch.get("chapter_number") == self.current_chapter_num:
                    ch["content_detail"] = detail
                    self.file_service.save_chapter(ch)
                    break

            messagebox.showinfo("완료", f"챕터 {self.current_chapter_num} 세부 정보가 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류: {e}")

    def _save_script(self):
        """대본 저장"""
        if not self.current_chapter_num:
            messagebox.showwarning("경고", "먼저 챕터를 선택하세요.")
            return

        script = self.script_text.get(1.0, tk.END).strip()

        try:
            self.file_service.save_script_file(self.current_chapter_num, script)
            messagebox.showinfo("완료", f"챕터 {self.current_chapter_num} 대본이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류: {e}")

    def _reload_script(self):
        """대본 파일에서 다시 로드"""
        if not self.current_chapter_num:
            messagebox.showwarning("경고", "먼저 챕터를 선택하세요.")
            return

        try:
            data = self.file_service.load_script_file(self.current_chapter_num)
            script = ""
            if isinstance(data, dict):
                script = str(data.get("script", "") or "")

            self.script_text.delete(1.0, tk.END)
            self.script_text.insert(1.0, script)
            messagebox.showinfo("완료", f"챕터 {self.current_chapter_num} 대본을 불러왔습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"불러오기 중 오류: {e}")

    def _save_all(self):
        """전체 저장"""
        if not self.current_chapter_num:
            messagebox.showwarning("경고", "먼저 챕터를 선택하세요.")
            return

        try:
            # 내용 저장
            content = self.content_text.get(1.0, tk.END).strip()
            detail = self.detail_text.get(1.0, tk.END).strip()
            script = self.script_text.get(1.0, tk.END).strip()

            # 챕터 파일 업데이트
            chapters = self.file_service.load_chapters()
            for ch in chapters:
                if ch.get("chapter_number") == self.current_chapter_num:
                    ch["content"] = content
                    ch["content_detail"] = detail
                    self.file_service.save_chapter(ch)
                    break

            # 시놉시스 업데이트
            synopsis = self.file_service.load_synopsis()
            if not isinstance(synopsis, dict):
                synopsis = {}
            syn_chapters = synopsis.get("chapters", {})
            if not isinstance(syn_chapters, dict):
                syn_chapters = {}
            syn_key = f"chapter_{self.current_chapter_num:02d}"
            syn_chapters[syn_key] = content
            synopsis["chapters"] = syn_chapters
            self.file_service.save_synopsis(synopsis)

            # 대본 파일 저장
            self.file_service.save_script_file(self.current_chapter_num, script)

            messagebox.showinfo("완료", f"챕터 {self.current_chapter_num}의 모든 내용이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류: {e}")

    def _add_new_chapter(self):
        """새 챕터 추가"""
        chapters = self.file_service.load_chapters()
        if not chapters:
            chapters = []

        # 다음 챕터 번호 계산
        max_num = 0
        for ch in chapters:
            try:
                max_num = max(max_num, int(ch.get("chapter_number", 0)))
            except Exception:
                continue

        new_num = max_num + 1
        new_chapter = {
            "chapter_number": new_num,
            "title": f"챕터 {new_num}",
            "content": "",
            "content_detail": "",
            "script": "",
            "_filename": get_chapter_filename(new_num),
        }
        chapters.append(new_chapter)
        chapters.sort(key=lambda x: x.get("chapter_number", 0))

        if self.file_service.save_chapters(chapters):
            self.project_data.set_chapters(chapters)
            self.update_display()
            messagebox.showinfo("완료", f"챕터 {new_num}이 추가되었습니다.")
        else:
            messagebox.showerror("오류", "새 챕터 저장에 실패했습니다.")

    def _generate_script(self):
        """대본 생성"""
        if not self.current_chapter_num:
            messagebox.showwarning("경고", "먼저 챕터를 선택하세요.")
            return

        # 챕터 찾기
        chapters = self.project_data.get_chapters()
        chapter = None
        chapter_index = -1
        for i, ch in enumerate(chapters):
            if ch.get("chapter_number") == self.current_chapter_num:
                chapter = ch
                chapter_index = i
                break

        if not chapter:
            messagebox.showerror("오류", f"챕터 {self.current_chapter_num}을 찾을 수 없습니다.")
            return

        # 시놉시스 정보
        synopsis = self.project_data.get_synopsis()

        # 인물 정보
        characters = self.project_data.get_characters()
        characters_info = self._format_characters_for_prompt(characters)

        # 이전 챕터 대본
        previous_script = ""
        if self.current_chapter_num > 1:
            try:
                prev_data = self.file_service.load_script_file(self.current_chapter_num - 1)
                if isinstance(prev_data, dict):
                    prev_script_full = str(prev_data.get("script", "") or "")
                    if len(prev_script_full) > 1000:
                        prev_script_full = "..." + prev_script_full[-1000:]
                    previous_script = prev_script_full
            except Exception:
                pass

        # LLM 호출
        try:
            script = self.content_generator.generate_script(
                chapter,
                synopsis,
                characters_info,
                previous_script
            )

            if not script:
                messagebox.showerror("오류", "대본 생성에 실패했습니다.")
                return

            # 대본 저장
            script = script.strip()
            chapter["script"] = script
            chapter["script_length"] = len(script)
            chapter["script_generated_at"] = datetime.now().isoformat()

            chapters[chapter_index] = chapter
            self.project_data.set_chapters(chapters)

            # 파일에 저장
            self.file_service.save_script_file(self.current_chapter_num, script)

            # UI 업데이트
            if self.script_text:
                self.script_text.delete(1.0, tk.END)
                self.script_text.insert(1.0, script)

            messagebox.showinfo("완료", f"챕터 {self.current_chapter_num}의 대본이 생성되었습니다.\n글자 수: {len(script)}자")

        except Exception as e:
            messagebox.showerror("오류", f"대본 생성 중 오류: {e}")

    def _format_characters_for_prompt(self, characters: list) -> str:
        """인물 정보를 프롬프트용 텍스트로 포맷팅"""
        if not characters:
            return "등장인물 정보 없음"

        result = []
        for char in characters:
            name = char.get("name", "알 수 없음")
            age = char.get("age", "불명")
            gender = char.get("gender", "불명")
            personality = char.get("personality", "불명")
            background = char.get("background", "불명")

            char_info = f"- {name} ({age}세, {gender}): {personality}"
            if background and background != "불명":
                char_info += f"\n  배경: {background}"
            result.append(char_info)

        return "\n".join(result)

    def save(self) -> bool:
        """데이터 저장"""
        try:
            chapters = self.project_data.get_chapters()
            if not isinstance(chapters, list):
                return False
            return self.file_service.save_chapters(chapters)
        except Exception:
            return False
