"""
챕터 탭
챕터 목록 뷰어를 제공합니다.
원본 viewer_editor.py의 로직을 완전히 이식한 버전
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import re
from .base_tab import BaseTab


class ChaptersTab(BaseTab):
    """챕터 탭 클래스 - 원본 로직 완전 이식"""

    def get_tab_name(self) -> str:
        return "챕터"

    def create_ui(self):
        """
        UI 생성
        원본 create_chapters_tab() 메서드의 로직을 완전히 이식
        - 상단: 전체 대본 생성 버튼
        - PanedWindow로 영역 분할
        - 뷰어: 스크롤 가능한 Canvas에 챕터 카드들 표시
        """
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # 상단: 챕터 관리 버튼들
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 파일에서 새로고침",
            command=self.update_display
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

        apply_synopsis_btn = ttk.Button(
            button_frame,
            text="🧩 시놉시스 → 챕터 반영",
            command=self._apply_synopsis_to_chapters
        )
        apply_synopsis_btn.pack(side=tk.LEFT, padx=5)

        add_chapter_btn = ttk.Button(
            button_frame,
            text="➕ 새 챕터 추가",
            command=self._add_new_chapter
        )
        add_chapter_btn.pack(side=tk.LEFT, padx=5)

        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        generate_all_btn = ttk.Button(
            button_frame,
            text="🔄 전체 대본 생성",
            command=self._generate_all_scripts
        )
        generate_all_btn.pack(side=tk.LEFT, padx=5)

        # PanedWindow로 크기 조절 가능하게 (상하 분할)
        paned_vertical = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        paned_vertical.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 상단: 좌우 분할 영역
        top_container = ttk.Frame(paned_vertical)
        paned_vertical.add(top_container, weight=2)
        top_container.columnconfigure(0, weight=1)
        top_container.rowconfigure(0, weight=1)

        # 좌우 분할 PanedWindow
        paned_horizontal = ttk.PanedWindow(top_container, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 왼쪽: 챕터 목록 뷰어
        chapters_list_frame = ttk.LabelFrame(paned_horizontal, text="챕터 목록", padding=10)
        paned_horizontal.add(chapters_list_frame, weight=2)
        chapters_list_frame.columnconfigure(0, weight=1)
        chapters_list_frame.rowconfigure(0, weight=1)

        # 스크롤 가능한 뷰어 (Canvas + Scrollbar)
        self.canvas_viewer = tk.Canvas(chapters_list_frame)
        self.scrollbar_viewer = ttk.Scrollbar(
            chapters_list_frame,
            orient="vertical",
            command=self.canvas_viewer.yview
        )
        self.chapters_viewer_frame = ttk.Frame(self.canvas_viewer)

        # Canvas 스크롤 영역 설정
        self.chapters_viewer_frame.bind(
            "<Configure>",
            lambda e: self.canvas_viewer.configure(scrollregion=self.canvas_viewer.bbox("all"))
        )

        # Canvas 안에 Frame을 넣고, Canvas 폭에 맞게 Frame 폭을 동기화(빈 여백/잘림 방지)
        self._viewer_window_id = self.canvas_viewer.create_window((0, 0), window=self.chapters_viewer_frame, anchor="nw")
        self.canvas_viewer.bind(
            "<Configure>",
            lambda e: self.canvas_viewer.itemconfigure(self._viewer_window_id, width=e.width)
        )
        self.canvas_viewer.configure(yscrollcommand=self.scrollbar_viewer.set)

        # 마우스 휠 이벤트 바인딩 (Canvas와 모든 자식 위젯에)
        self._bind_initial_mousewheel()

        # Canvas와 Scrollbar 배치
        self.canvas_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar_viewer.grid(row=0, column=1, sticky=(tk.N, tk.S))
        chapters_list_frame.columnconfigure(0, weight=1)
        chapters_list_frame.rowconfigure(0, weight=1)

        # 오른쪽: 대본 에디터 영역
        script_display_frame = ttk.LabelFrame(paned_horizontal, text="대본 에디터", padding=10)
        paned_horizontal.add(script_display_frame, weight=1)
        script_display_frame.columnconfigure(0, weight=1)
        script_display_frame.rowconfigure(1, weight=1)

        # 헤더(챕터 표시 + 저장/불러오기)
        header_frame = ttk.Frame(script_display_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)

        self.script_chapter_label = ttk.Label(
            header_frame,
            text="챕터를 선택하세요",
            font=("맑은 고딕", 11, "bold"),
        )
        self.script_chapter_label.grid(row=0, column=0, sticky=tk.W)

        script_btn_frame = ttk.Frame(header_frame)
        script_btn_frame.grid(row=0, column=1, sticky=tk.E)

        ttk.Button(
            script_btn_frame,
            text="💾 대본 저장",
            command=self._save_current_script,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            script_btn_frame,
            text="📂 대본 불러오기",
            command=self._reload_current_script_from_file,
        ).pack(side=tk.LEFT, padx=5)

        # 대본 내용 입력/편집
        self.script_viewer = scrolledtext.ScrolledText(
            script_display_frame,
            width=60,
            height=40,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
        )
        self.script_viewer.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.script_viewer.bind("<KeyRelease>", lambda e: self.mark_unsaved())

        # 현재 선택된 챕터 번호 추적
        self.current_selected_chapter_num = None

        # PanedWindow 참조 저장 (마우스 휠 재바인딩용)
        self.paned = paned_vertical

    def _bind_initial_mousewheel(self):
        """
        초기 마우스 휠 이벤트 바인딩
        원본 create_chapters_tab() 내부의 마우스 휠 바인딩 로직
        """
        def on_mousewheel(event):
            """마우스 휠 스크롤 처리"""
            self.canvas_viewer.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        def bind_mousewheel_to_widget(widget):
            """위젯과 모든 자식 위젯에 재귀적으로 마우스 휠 바인딩"""
            widget.bind("<MouseWheel>", on_mousewheel)
            widget.bind("<Enter>", lambda e: self.canvas_viewer.focus_set())
            for child in widget.winfo_children():
                bind_mousewheel_to_widget(child)

        # Canvas에 직접 바인딩
        self.canvas_viewer.bind("<MouseWheel>", on_mousewheel)
        self.canvas_viewer.bind("<Enter>", lambda e: self.canvas_viewer.focus_set())

        # Frame과 모든 자식 위젯에 바인딩
        bind_mousewheel_to_widget(self.chapters_viewer_frame)

    def update_display(self):
        """
        화면 업데이트
        원본 update_chapters_display() 메서드의 로직을 완전히 이식
        시놉시스 기반으로 인물 프로필 파일과 챕터 파일 생성
        """
        # 파일에서 최신 데이터 다시 로드 (챕터 세부정보 입력 탭에서 저장한 데이터 반영)
        try:
            all_data = self.file_service.load_all_data()
            self.project_data.data = all_data
        except Exception as e:
            print(f"데이터 로드 오류: {e}")

        # NOTE:
        # - 시놉시스는 수시로 변할 수 있으므로, 자동으로 챕터를 덮어쓰지 않음
        # - 필요할 때만 상단 버튼 '시놉시스 → 챕터 반영'으로 병합 수행

        # 기존 위젯 제거
        for widget in self.chapters_viewer_frame.winfo_children():
            widget.destroy()

        chapters = self.project_data.get_chapters()

        if not chapters:
            ttk.Label(
                self.chapters_viewer_frame,
                text="챕터 정보가 없습니다.\n시놉시스 입력 탭에서 챕터를 입력해주세요.",
                font=("맑은 고딕", 11)
            ).pack(pady=20)
            # 오른쪽 대본 에디터 초기화
            self.current_selected_chapter_num = None
            try:
                self.script_chapter_label.config(text="챕터를 선택하세요")
                self.script_viewer.delete(1.0, tk.END)
            except Exception:
                pass
            return

        # 뷰어에 챕터 정보 표시
        for idx, chapter in enumerate(chapters):
            self._create_chapter_widget(idx, chapter)

        # 마우스 휠 이벤트 재바인딩 (새로 생성된 위젯들에)
        self._rebind_mousewheel()

    def _apply_synopsis_to_chapters(self):
        """시놉시스의 챕터 내용을 기존 챕터 파일에 병합 적용"""
        synopsis = self.project_data.get_synopsis()
        if not synopsis:
            messagebox.showwarning("경고", "시놉시스 정보가 없습니다.")
            return

        result = messagebox.askyesno(
            "시놉시스 반영",
            "시놉시스의 챕터 내용을 챕터 파일에 병합 적용하시겠습니까?\n\n"
            "- 기존 content_detail/대본 등은 유지하고\n"
            "- 시놉시스의 content/title만 업데이트합니다."
        )
        if not result:
            return

        try:
            self._create_files_from_synopsis()
            self.update_display()
            messagebox.showinfo("완료", "시놉시스 내용이 챕터에 반영되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"시놉시스 반영 중 오류:\n{e}")

    def _add_new_chapter(self):
        """새 챕터 추가 (빈 챕터 생성 후 저장)"""
        chapters = self.file_service.load_chapters()
        if not chapters:
            chapters = []

        max_num = 0
        for ch in chapters:
            try:
                max_num = max(max_num, int(ch.get("chapter_number", 0)))
            except Exception:
                continue

        new_num = max_num + 1
        from utils.file_utils import get_chapter_filename

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
            # (추가) synopsis.json에도 빈 챕터 내용 생성 (내용 저장 대상)
            try:
                synopsis = self.file_service.load_synopsis()
                if not isinstance(synopsis, dict):
                    synopsis = {}
                syn_chapters = synopsis.get("chapters")
                if not isinstance(syn_chapters, dict):
                    syn_chapters = {}
                syn_key = f"chapter_{new_num:02d}"
                if syn_key not in syn_chapters:
                    syn_chapters[syn_key] = ""
                synopsis["chapters"] = syn_chapters
                self.file_service.save_synopsis(synopsis)
                self.project_data.set_synopsis(synopsis)
            except Exception:
                pass

            # (선택) 스크립트 파일도 빈 파일로 생성해둠
            try:
                self.file_service.save_script_file(new_num, "")
            except Exception:
                pass

            self.project_data.set_chapters(chapters)
            self.update_display()
            messagebox.showinfo("완료", f"챕터 {new_num}이 추가되었습니다.")
        else:
            messagebox.showerror("오류", "새 챕터 저장에 실패했습니다.")

    def _save_chapter_content_to_synopsis(self, chapter_num: int, widget: scrolledtext.ScrolledText):
        """챕터 '내용'을 synopsis.json의 chapters에 저장 (공식 원본)"""
        try:
            content = widget.get(1.0, tk.END).strip()

            synopsis = self.file_service.load_synopsis()
            if not isinstance(synopsis, dict):
                synopsis = {}

            syn_chapters = synopsis.get("chapters")
            if not isinstance(syn_chapters, dict):
                syn_chapters = {}

            syn_key = f"chapter_{chapter_num:02d}"
            syn_chapters[syn_key] = content
            synopsis["chapters"] = syn_chapters

            if not self.file_service.save_synopsis(synopsis):
                messagebox.showerror("오류", "시놉시스 저장에 실패했습니다.")
                return

            # 메모리 데이터 갱신
            self.project_data.set_synopsis(synopsis)

            # (동기화) 챕터 파일의 content도 동일하게 맞춰둠 (content_detail은 유지)
            try:
                chapters = self.file_service.load_chapters()
                target = None
                for ch in chapters:
                    if ch.get("chapter_number") == chapter_num:
                        target = ch
                        break
                if target is not None:
                    target["content"] = content
                    self.file_service.save_chapter(target)
                    # project_data chapters도 갱신
                    for i, ch in enumerate(self.project_data.get_chapters()):
                        if ch.get("chapter_number") == chapter_num:
                            self.project_data.data["chapters"][i]["content"] = content
                            break
            except Exception:
                pass

            messagebox.showinfo("완료", f"챕터 {chapter_num} 내용이 시놉시스에 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"내용 저장 중 오류:\n{e}")

    def _save_chapter_detail_to_file(self, chapter_num: int, widget: scrolledtext.ScrolledText):
        """챕터 '세부 정보(content_detail)'를 chapter_XX.json에 저장"""
        try:
            detail = widget.get(1.0, tk.END).strip()
            chapters = self.file_service.load_chapters()
            target = None
            for ch in chapters:
                if ch.get("chapter_number") == chapter_num:
                    target = ch
                    break
            if target is None:
                messagebox.showerror("오류", f"챕터 {chapter_num} 파일을 찾을 수 없습니다.")
                return

            target["content_detail"] = detail
            if not self.file_service.save_chapter(target):
                messagebox.showerror("오류", "세부 정보 저장에 실패했습니다.")
                return

            # 메모리 데이터 갱신
            for i, ch in enumerate(self.project_data.get_chapters()):
                if ch.get("chapter_number") == chapter_num:
                    self.project_data.data["chapters"][i]["content_detail"] = detail
                    break

            messagebox.showinfo("완료", f"챕터 {chapter_num} 세부 정보가 저장되었습니다. (03_chapters)")
        except Exception as e:
            messagebox.showerror("오류", f"세부정보 저장 중 오류:\n{e}")

    def _create_chapter_widget(self, idx: int, chapter: dict):
        """
        챕터 뷰어 위젯 생성
        원본 create_chapter_viewer_widget() 메서드의 로직을 완전히 이식

        각 챕터를 카드 형식으로 표시:
        - 챕터 번호와 제목
        - 내용 (content)
        - 세부 정보 (content_detail)
        - 분위기 (mood) - 있으면 표시
        """
        num = chapter.get('chapter_number', idx + 1)
        frame = ttk.LabelFrame(
            self.chapters_viewer_frame,
            text=f"챕터 {num}",
            padding=15
        )
        frame.pack(fill=tk.X, padx=15, pady=10)

        # 카드 클릭 시 오른쪽 대본 자동 로드/연동
        frame.bind("<Button-1>", lambda e, n=num: self._select_chapter(n))

        # 제목
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            title_frame,
            text="제목:",
            font=("맑은 고딕", 10, "bold"),
            width=12
        ).pack(side=tk.LEFT)
        title_value = ttk.Label(
            title_frame,
            text=chapter.get('title', ''),
            font=("맑은 고딕", 10)
        )
        title_value.pack(side=tk.LEFT)
        title_frame.bind("<Button-1>", lambda e, n=num: self._select_chapter(n))
        title_value.bind("<Button-1>", lambda e, n=num: self._select_chapter(n))

        # === 챕터 내용(시놉시스 원본) ===
        synopsis = self.project_data.get_synopsis() or {}
        syn_chapters = synopsis.get("chapters", {}) if isinstance(synopsis, dict) else {}
        syn_key = f"chapter_{num:02d}"
        content = ""
        if isinstance(syn_chapters, dict) and syn_key in syn_chapters:
            content = str(syn_chapters.get(syn_key) or "")
        else:
            content = str(chapter.get("content", "") or chapter.get("summary", "") or "")

        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.X, pady=5)
        content_frame.columnconfigure(1, weight=1)

        ttk.Label(
            content_frame,
            text="내용:",
            font=("맑은 고딕", 10, "bold"),
            width=12
        ).grid(row=0, column=0, sticky=tk.NW)

        content_text = scrolledtext.ScrolledText(
            content_frame,
            height=4,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
        )
        content_text.grid(row=0, column=1, sticky=(tk.W, tk.E))
        content_text.insert(1.0, content)
        content_text.bind("<KeyRelease>", lambda e: self.mark_unsaved())
        # 내용 박스에 포커스가 오면 해당 챕터 선택(오른쪽 대본 로드)
        content_text.bind("<FocusIn>", lambda e, n=num: self._select_chapter(n))

        ttk.Button(
            content_frame,
            text="내용 저장",
            command=lambda n=num, w=content_text: self._save_chapter_content_to_synopsis(n, w),
            width=12,
        ).grid(row=1, column=1, sticky=tk.E, pady=(6, 0))

        # === 챕터 세부 정보(03_chapters/chapter_XX.json) ===
        detailed_content = str(chapter.get("content_detail", "") or "")
        detailed_frame = ttk.Frame(frame)
        detailed_frame.pack(fill=tk.X, pady=5)
        detailed_frame.columnconfigure(1, weight=1)

        ttk.Label(
            detailed_frame,
            text="세부 정보:",
            font=("맑은 고딕", 10, "bold"),
            width=12
        ).grid(row=0, column=0, sticky=tk.NW)

        detailed_text = scrolledtext.ScrolledText(
            detailed_frame,
            height=10,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
        )
        detailed_text.grid(row=0, column=1, sticky=(tk.W, tk.E))
        detailed_text.insert(1.0, detailed_content)
        detailed_text.bind("<KeyRelease>", lambda e: self.mark_unsaved())
        detailed_text.bind("<FocusIn>", lambda e, n=num: self._select_chapter(n))

        ttk.Button(
            detailed_frame,
            text="세부정보 저장",
            command=lambda n=num, w=detailed_text: self._save_chapter_detail_to_file(n, w),
            width=12,
        ).grid(row=1, column=1, sticky=tk.E, pady=(6, 0))

        # 분위기 (있으면 표시)
        mood = chapter.get('mood', '')
        if mood:
            mood_frame = ttk.Frame(frame)
            mood_frame.pack(fill=tk.X, pady=5)
            ttk.Label(
                mood_frame,
                text="분위기:",
                font=("맑은 고딕", 10, "bold"),
                width=12
            ).pack(side=tk.LEFT)
            ttk.Label(
                mood_frame,
                text=mood,
                font=("맑은 고딕", 10)
            ).pack(side=tk.LEFT)

        # 대본 생성 버튼
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        generate_btn = ttk.Button(
            button_frame,
            text="📝 대본 생성",
            command=lambda n=num: self._generate_script_for_chapter(n),
            width=15
        )
        generate_btn.pack(side=tk.LEFT, padx=5)
        # "대본 보기" 버튼 제거: 챕터 카드 클릭 시 자동 로드/연동

    def _select_chapter(self, chapter_num: int):
        """
        챕터 선택 → 오른쪽 대본 에디터 자동 로드/연동
        """
        try:
            self._update_script_display(chapter_num)
        except Exception:
            pass

    def _rebind_mousewheel(self):
        """
        마우스 휠 이벤트 재바인딩
        원본 _bind_mousewheel_to_chapters_viewer() 메서드의 로직을 완전히 이식

        새로 생성된 위젯들에 마우스 휠 이벤트를 다시 바인딩합니다.
        PanedWindow 구조를 탐색하여 Canvas를 찾아 바인딩합니다.
        """
        # PanedWindow에서 Canvas 찾기
        if hasattr(self, 'paned'):
            for pane_name in self.paned.panes():
                pane = self.paned.nametowidget(pane_name)
                for child in pane.winfo_children():
                    if isinstance(child, tk.Canvas):
                        # Canvas 참조 저장
                        canvas = child

                        def on_mousewheel(event):
                            """마우스 휠 스크롤 처리"""
                            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                            return "break"

                        def bind_to_widget(w):
                            """위젯과 모든 자식 위젯에 재귀적으로 마우스 휠 바인딩"""
                            w.bind("<MouseWheel>", on_mousewheel)
                            # 텍스트/버튼 위에 마우스가 있어도 Canvas가 휠을 받도록 포커스 이동
                            w.bind("<Enter>", lambda e, c=canvas: c.focus_set())
                            for c in w.winfo_children():
                                bind_to_widget(c)

                        # Canvas에 직접 바인딩
                        canvas.bind("<MouseWheel>", on_mousewheel)
                        canvas.bind("<Enter>", lambda e, c=canvas: c.focus_set())

                        # chapters_viewer_frame과 모든 자식 위젯에 바인딩
                        bind_to_widget(self.chapters_viewer_frame)
                        return

    def _generate_script_for_chapter(self, chapter_num: int):
        """
        특정 챕터의 대본 생성
        Args:
            chapter_num: 챕터 번호
        """
        self._generate_script(chapter_num, show_message=True)

    def _generate_script(self, chapter_num: int, show_message: bool = True) -> bool:
        """
        챕터 대본 생성 (내부 함수)
        scripts_tab.py의 _generate_script() 로직을 재사용

        Args:
            chapter_num: 챕터 번호
            show_message: 완료 메시지 표시 여부

        Returns:
            생성 성공 여부
        """
        # 챕터 찾기
        chapters = self.project_data.get_chapters()
        chapter = None
        chapter_index = -1
        for i, ch in enumerate(chapters):
            if ch.get('chapter_number') == chapter_num:
                chapter = ch
                chapter_index = i
                break

        if not chapter:
            if show_message:
                messagebox.showerror("오류", f"챕터 {chapter_num}을 찾을 수 없습니다.")
            return False

        # 시놉시스 정보
        synopsis = self.project_data.get_synopsis()

        # 인물 정보
        characters = self.project_data.get_characters()
        characters_info = self._format_characters_for_prompt(characters)

        # 이전 챕터 대본 (연속성 유지)
        previous_script = ""
        if chapter_num > 1:
            prev_chapter = None
            for ch in chapters:
                if ch.get('chapter_number') == chapter_num - 1:
                    prev_chapter = ch
                    break
            prev_script_full = ""
            if prev_chapter and prev_chapter.get('script'):
                prev_script_full = prev_chapter.get('script', '')
            else:
                # 04_scripts 파일 우선 로드
                try:
                    prev_data = self.file_service.load_script_file(chapter_num - 1)
                    if isinstance(prev_data, dict):
                        prev_script_full = str(prev_data.get("script", "") or "")
                except Exception:
                    prev_script_full = ""
            if prev_script_full:
                # 이전 대본의 마지막 1000자만 포함
                if len(prev_script_full) > 1000:
                    prev_script_full = "..." + prev_script_full[-1000:]
                previous_script = prev_script_full

        # LLM 호출
        try:
            script = self.content_generator.generate_script(
                chapter,
                synopsis,
                characters_info,
                previous_script
            )

            if not script:
                if show_message:
                    messagebox.showerror("오류", "대본 생성에 실패했습니다.")
                return False

            # 챕터 데이터에 대본 저장
            chapter['script'] = script.strip()
            chapter['script_length'] = len(script.strip())
            chapter['script_generated_at'] = datetime.now().isoformat()

            # 데이터 업데이트
            chapters[chapter_index] = chapter
            self.project_data.set_chapters(chapters)

            # 파일에 즉시 자동 저장
            try:
                # 스크립트는 04_scripts에 저장(챕터 번호=스크립트 번호)
                self.file_service.save_script_file(chapter_num, chapter['script'])
            except Exception as save_error:
                print(f"경고: 대본은 생성되었으나 저장 중 오류 발생: {save_error}")

            # 화면 업데이트
            self.update_display()
            
            # 오른쪽 대본 영역 업데이트
            self._update_script_display(chapter_num)

            if show_message:
                messagebox.showinfo("완료", f"챕터 {chapter_num}의 대본이 생성되고 자동 저장되었습니다.\n글자 수: {len(script.strip())}자")

            return True

        except Exception as e:
            if show_message:
                messagebox.showerror("오류", f"대본 생성 중 오류 발생:\n{e}")
            return False

    def _generate_all_scripts(self):
        """
        모든 챕터의 대본 생성
        scripts_tab.py의 _generate_all_chapters() 로직을 재사용
        """
        chapters = self.project_data.get_chapters()
        if not chapters:
            messagebox.showwarning("경고", "챕터 정보가 없습니다.")
            return

        # 확인 대화상자
        result = messagebox.askyesno(
            "대본 일괄 생성",
            f"{len(chapters)}개 챕터의 대본을 모두 생성하시겠습니까?\n\n"
            f"이 작업은 시간이 걸릴 수 있습니다."
        )
        if not result:
            return

        # 모든 챕터 대본 생성
        success_count = 0
        for ch in chapters:
            chapter_num = ch.get('chapter_number', 0)
            if chapter_num > 0:
                if self._generate_script(chapter_num, show_message=False):
                    success_count += 1

        messagebox.showinfo("완료", f"{success_count}/{len(chapters)}개 챕터의 대본이 생성되었습니다.")
        self.update_display()  # 화면 업데이트

    def _show_script_for_chapter(self, chapter_num: int):
        """
        특정 챕터의 대본을 오른쪽 영역에 표시
        Args:
            chapter_num: 챕터 번호
        """
        self._update_script_display(chapter_num)

    def _update_script_display(self, chapter_num: int):
        """
        오른쪽 대본 표시 영역 업데이트
        Args:
            chapter_num: 챕터 번호
        """
        # 챕터 찾기
        chapters = self.project_data.get_chapters()
        chapter = None
        for ch in chapters:
            if ch.get('chapter_number') == chapter_num:
                chapter = ch
                break

        if not chapter:
            return

        # 현재 선택된 챕터 번호 저장
        self.current_selected_chapter_num = chapter_num

        # 챕터 번호 라벨 업데이트
        chapter_title = chapter.get('title', '')
        if chapter_title:
            self.script_chapter_label.config(text=f"챕터 {chapter_num}: {chapter_title}")
        else:
            self.script_chapter_label.config(text=f"챕터 {chapter_num}")

        # 대본 내용 업데이트 (04_scripts 파일 우선)
        script_text = ""
        try:
            data = self.file_service.load_script_file(chapter_num)
            if isinstance(data, dict):
                script_text = str(data.get("script", "") or "")
        except Exception:
            script_text = ""

        if not script_text:
            script_text = str(chapter.get("script", "") or "")

        self.script_viewer.delete(1.0, tk.END)
        if script_text:
            self.script_viewer.insert(1.0, script_text)
        else:
            self.script_viewer.insert(1.0, f"챕터 {chapter_num}의 대본이 없습니다.\n\n오른쪽에서 직접 입력하고 '대본 저장'을 누르세요.")

    def _save_current_script(self):
        """오른쪽 대본 에디터 내용을 04_scripts/chapter_XX_script.json에 저장"""
        chapter_num = self.current_selected_chapter_num
        if not chapter_num:
            messagebox.showwarning("경고", "먼저 왼쪽에서 챕터를 선택하세요.")
            return

        script = self.script_viewer.get(1.0, tk.END).rstrip()
        ok = self.file_service.save_script_file(int(chapter_num), script)
        if ok:
            # 메모리에도 반영(표시/생성 로직 호환)
            try:
                for i, ch in enumerate(self.project_data.get_chapters()):
                    if ch.get("chapter_number") == int(chapter_num):
                        self.project_data.data["chapters"][i]["script"] = script
                        break
            except Exception:
                pass
            messagebox.showinfo("완료", f"챕터 {chapter_num} 대본이 저장되었습니다. (04_scripts)")
        else:
            messagebox.showerror("오류", "대본 저장에 실패했습니다.")

    def _reload_current_script_from_file(self):
        """04_scripts 파일에서 현재 챕터 대본을 다시 불러오기"""
        chapter_num = self.current_selected_chapter_num
        if not chapter_num:
            messagebox.showwarning("경고", "먼저 왼쪽에서 챕터를 선택하세요.")
            return

        data = self.file_service.load_script_file(int(chapter_num))
        script = ""
        if isinstance(data, dict):
            script = str(data.get("script", "") or "")
        self.script_viewer.delete(1.0, tk.END)
        self.script_viewer.insert(1.0, script)
        messagebox.showinfo("완료", f"챕터 {chapter_num} 대본을 파일에서 불러왔습니다.")

    def _format_characters_for_prompt(self, characters: list) -> str:
        """
        인물 정보를 프롬프트용 텍스트로 포맷팅
        scripts_tab.py의 로직을 재사용
        """
        if not characters:
            return "등장인물 정보 없음"

        result = []
        for char in characters:
            name = char.get('name', '알 수 없음')
            age = char.get('age', '불명')
            gender = char.get('gender', '불명')
            personality = char.get('personality', '불명')
            background = char.get('background', '불명')

            char_info = f"- {name} ({age}세, {gender}): {personality}"
            if background and background != '불명':
                char_info += f"\n  배경: {background}"
            result.append(char_info)

        return '\n'.join(result)

    def _create_files_from_synopsis(self):
        """시놉시스 기반으로 인물 프로필 파일과 챕터 파일 생성"""
        synopsis = self.project_data.get_synopsis()
        
        if not synopsis:
            return
        
        # 1. 등장인물 파일 생성
        synopsis_characters = synopsis.get('characters', [])
        if synopsis_characters:
            characters = []
            for syn_char in synopsis_characters:
                # 시놉시스 구조를 그대로 사용
                character = {
                    'name': syn_char.get('name', ''),
                    'age': syn_char.get('age', ''),
                    'occupation': syn_char.get('occupation', ''),
                    'personality': syn_char.get('personality', ''),
                    'appearance': syn_char.get('appearance', ''),
                    'traits': syn_char.get('traits', ''),
                    'desire': syn_char.get('desire', ''),
                    'role': syn_char.get('role', '')
                }
                # 파일명 생성 (정규화 함수 사용)
                from utils.file_utils import get_character_filename
                char_name = character.get('name', 'character')
                character['_filename'] = get_character_filename(char_name)
                characters.append(character)
            
            # 인물 데이터 설정 및 저장
            self.project_data.set_characters(characters)
            self.file_service.save_characters(characters)
        
        # 2. 챕터 파일 생성 (기존 파일이 있으면 병합)
        synopsis_chapters = synopsis.get('chapters', {})
        if synopsis_chapters:
            # 기존 챕터 파일 먼저 로드 (content_detail, script 등 보존을 위해)
            # 덮어쓰지 않고 기존 데이터를 보존하기 위해 파일에서 최신 데이터를 로드합니다.
            existing_chapters = self.file_service.load_chapters()
            existing_dict = {ch.get('chapter_number', 0): ch for ch in existing_chapters}
            
            chapters = []
            
            # 챕터 번호 순서대로 정렬
            sorted_keys = sorted(synopsis_chapters.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
            
            for key in sorted_keys:
                chapter_content = synopsis_chapters[key]
                
                # 챕터 내용에서 번호, 단계, 내용 추출
                chapter_number = None
                chapter_stage = None
                chapter_title = None
                content = str(chapter_content)
                
                # 패턴 1: "챕터 1 (도입): 내용" 형식
                pattern1 = r'챕터\s*(\d+)\s*\(([^)]+)\)\s*[:：]\s*(.+)'
                match1 = re.match(pattern1, content, re.DOTALL)
                if match1:
                    chapter_number = int(match1.group(1))
                    chapter_stage = match1.group(2).strip()
                    content = match1.group(3).strip()
                else:
                    # 패턴 2: "[도입] 제목: 내용" 형식
                    pattern2 = r'\[([^\]]+)\]\s*([^:：]+?)\s*[:：]\s*(.+)'
                    match2 = re.match(pattern2, content, re.DOTALL)
                    if match2:
                        chapter_stage = match2.group(1).strip()
                        chapter_title = match2.group(2).strip()
                        content = match2.group(3).strip()
                    else:
                        # 패턴 3: "chapter_1" 키에서 번호 추출
                        if '_' in key:
                            try:
                                chapter_number = int(key.split('_')[1])
                            except:
                                pass
                
                # 챕터 번호가 없으면 순서대로 할당
                if chapter_number is None:
                    chapter_number = len(chapters) + 1
                
                # 제목 결정
                if chapter_title:
                    title = chapter_title
                elif chapter_stage:
                    title = chapter_stage
                else:
                    title = f'챕터 {chapter_number}'
                
                # 기존 챕터 파일이 있으면 병합 (덮어쓰지 않음)
                if chapter_number in existing_dict:
                    # 기존 데이터 보존 (content_detail, script 등 추가 정보 보존)
                    existing_chapter = existing_dict[chapter_number]
                    # 시놉시스 정보는 content 필드에만 업데이트
                    existing_chapter['content'] = content
                    # 제목도 업데이트 (시놉시스의 제목이 있으면)
                    if title and title != existing_chapter.get('title', ''):
                        existing_chapter['title'] = title
                    # _filename이 없으면 추가
                    if '_filename' not in existing_chapter:
                        from utils.file_utils import get_chapter_filename
                        existing_chapter['_filename'] = get_chapter_filename(chapter_number)
                    # 기존 챕터를 리스트에 추가 (content_detail, script 등이 보존됨)
                    chapters.append(existing_chapter)
                else:
                    # 새 챕터면 생성
                    chapter = {
                        'chapter_number': chapter_number,
                        'title': title,
                        'content': content,
                        'script': ''
                    }
                    # 파일명 생성 (정규화 함수 사용)
                    from utils.file_utils import get_chapter_filename
                    chapter['_filename'] = get_chapter_filename(chapter_number)
                    chapters.append(chapter)
            
            # 챕터 데이터 설정 및 저장
            self.project_data.set_chapters(chapters)
            self.file_service.save_chapters(chapters)

    def save(self) -> bool:
        """
        데이터 저장
        현재 로드된 챕터 데이터를 파일로 저장
        """
        try:
            chapters = self.project_data.get_chapters()
            if not isinstance(chapters, list):
                return False
            return self.file_service.save_chapters(chapters)
        except Exception:
            return False
