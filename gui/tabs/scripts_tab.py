"""
대본 탭
챕터별 TTS용 나레이션 대본 뷰어 및 에디터를 제공합니다.
원본 viewer_editor.py의 로직을 완전히 이식한 버전
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from typing import Optional, Dict
from .base_tab import BaseTab


class ScriptsTab(BaseTab):
    """대본 탭 클래스 - 원본 로직 완전 이식"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        # 챕터 선택 변수 초기화
        self.script_chapter_var = None
        self.script_chapter_combo = None
        self.script_char_count_label = None
        self.script_viewer = None
        self.script_editor = None

        # 전체 보기 모드 변수
        self.is_full_view_mode = False
        self.full_view_btn = None

        # 챕터 탭 버튼 변수
        self.chapter_buttons_frame = None
        self.chapter_buttons = {}
        self.current_chapter_num = 1

        # 좌우 분할 구조 변수
        self.chapter_listbox = None
        self.chapter_list_data = []  # (chapter_num, title, has_script) 튜플 리스트

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "대본"

    def create_ui(self):
        """
        UI 생성
        원본 create_scripts_tab() 메서드의 로직을 완전히 이식
        - 상단: 챕터 선택 콤보박스 + 대본 생성 버튼 + 글자 수 표시
        - 하단: PanedWindow로 분할 (뷰어 | 에디터)
        """
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)  # 콘텐츠 영역이 row=2로 변경됨

        # 상단: 챕터 선택 + 대본 생성 버튼
        toolbar = ttk.Frame(self.frame)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(toolbar, text="챕터 선택:", font=("맑은 고딕", 10)).pack(side=tk.LEFT, padx=5)

        # 챕터 선택 콤보박스
        self.script_chapter_var = tk.StringVar()
        self.script_chapter_combo = ttk.Combobox(
            toolbar,
            textvariable=self.script_chapter_var,
            width=30,
            state='readonly'
        )
        self.script_chapter_combo.pack(side=tk.LEFT, padx=5)
        self.script_chapter_combo.bind('<<ComboboxSelected>>', lambda e: self._on_chapter_selected())

        # 대본 저장/불러오기 버튼
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        save_btn = ttk.Button(
            toolbar,
            text="💾 대본 저장",
            command=self._save_current_script,
            width=14
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        reload_btn = ttk.Button(
            toolbar,
            text="📂 대본 불러오기",
            command=self._reload_current_script_from_file,
            width=16
        )
        reload_btn.pack(side=tk.LEFT, padx=5)

        # 대본 생성 버튼
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        generate_btn = ttk.Button(
            toolbar,
            text="🔄 대본 생성 (LLM)",
            command=self._generate_current_chapter
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        # 모든 챕터 대본 생성 버튼
        generate_all_btn = ttk.Button(
            toolbar,
            text="🔄 모든 챕터 대본 생성",
            command=self._generate_all_chapters
        )
        generate_all_btn.pack(side=tk.LEFT, padx=5)

        # 전체 대본 보기 버튼 (구분선 추가)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        self.full_view_btn = ttk.Button(
            toolbar,
            text="📖 전체 대본 보기",
            command=self._toggle_full_view_mode,
            width=16
        )
        self.full_view_btn.pack(side=tk.LEFT, padx=5)

        # 글자 수 표시 라벨
        self.script_char_count_label = ttk.Label(toolbar, text="", font=("맑은 고딕", 9))
        self.script_char_count_label.pack(side=tk.LEFT, padx=10)

        # 챕터 탭 버튼 프레임 (2번째 줄)
        chapter_btn_row = ttk.Frame(self.frame)
        chapter_btn_row.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))

        ttk.Label(chapter_btn_row, text="챕터 바로가기:", font=("맑은 고딕", 9)).pack(side=tk.LEFT, padx=5)

        self.chapter_buttons_frame = ttk.Frame(chapter_btn_row)
        self.chapter_buttons_frame.pack(side=tk.LEFT, padx=5)

        # 하단: 좌우 분할 영역 (row를 2로 변경)
        content_frame = ttk.Frame(self.frame)
        content_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # 좌우 분할 PanedWindow
        paned_horizontal = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ===== 왼쪽: 챕터 목록 영역 =====
        left_frame = ttk.LabelFrame(paned_horizontal, text="챕터 목록", padding=10)
        paned_horizontal.add(left_frame, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)

        # 챕터 리스트박스 + 스크롤바
        list_container = ttk.Frame(left_frame)
        list_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        self.chapter_listbox = tk.Listbox(
            list_container,
            font=("맑은 고딕", 11),
            selectmode=tk.SINGLE,
            activestyle='dotbox',
            width=25,
            height=20
        )
        self.chapter_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        list_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.chapter_listbox.yview)
        list_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.chapter_listbox.config(yscrollcommand=list_scrollbar.set)

        # 리스트박스 선택 이벤트
        self.chapter_listbox.bind('<<ListboxSelect>>', self._on_listbox_select)

        # ===== 오른쪽: 대본 뷰어/에디터 영역 =====
        right_frame = ttk.Frame(paned_horizontal)
        paned_horizontal.add(right_frame, weight=4)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # 상하 분할 PanedWindow (뷰어 | 에디터)
        paned_vertical = ttk.PanedWindow(right_frame, orient=tk.VERTICAL)
        paned_vertical.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 상단: 뷰어 영역 (읽기 전용)
        viewer_frame = ttk.LabelFrame(paned_vertical, text="대본 뷰어 (TTS 복사용)", padding=10)
        paned_vertical.add(viewer_frame, weight=1)
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        self.script_viewer = scrolledtext.ScrolledText(
            viewer_frame,
            width=100,
            height=15,
            wrap=tk.WORD,
            font=("맑은 고딕", 11),
            state=tk.DISABLED
        )
        self.script_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 하단: 에디터 영역
        editor_frame = ttk.LabelFrame(paned_vertical, text="대본 에디터", padding=10)
        paned_vertical.add(editor_frame, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.script_editor = scrolledtext.ScrolledText(
            editor_frame,
            width=100,
            height=15,
            wrap=tk.WORD,
            font=("맑은 고딕", 11)
        )
        self.script_editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.script_editor.bind('<KeyRelease>', lambda e: self.mark_unsaved())

    def update_display(self):
        """
        화면 업데이트
        원본 update_scripts_display() 메서드의 로직을 완전히 이식
        """
        chapters = self.project_data.get_chapters()

        # 챕터 목록을 콤보박스에 로드
        chapter_list = [f"챕터 {ch.get('chapter_number', i+1)}: {ch.get('title', '제목 없음')}"
                       for i, ch in enumerate(chapters)]

        if self.script_chapter_combo:
            self.script_chapter_combo['values'] = chapter_list
            if chapter_list and not self.script_chapter_var.get():
                self.script_chapter_combo.current(0)
                self._on_chapter_selected()

        # 챕터 탭 버튼 생성/업데이트
        self._create_chapter_buttons(chapters)

        # 챕터 리스트박스 업데이트
        self._update_chapter_listbox(chapters)

    def _create_chapter_buttons(self, chapters):
        """챕터 바로가기 버튼 생성"""
        if not self.chapter_buttons_frame:
            return

        # 기존 버튼 제거
        for widget in self.chapter_buttons_frame.winfo_children():
            widget.destroy()
        self.chapter_buttons.clear()

        if not chapters:
            ttk.Label(
                self.chapter_buttons_frame,
                text="(챕터 없음)",
                font=("맑은 고딕", 9),
                foreground="gray"
            ).pack(side=tk.LEFT)
            return

        # 챕터별 버튼 생성
        for ch in sorted(chapters, key=lambda x: x.get('chapter_number', 0)):
            chapter_num = ch.get('chapter_number', 0)
            chapter_title = ch.get('title', '')

            # 버튼 텍스트: 짧은 제목 (최대 8자)
            short_title = chapter_title[:8] + "..." if len(chapter_title) > 8 else chapter_title
            btn_text = f"{chapter_num}. {short_title}" if short_title else f"챕터 {chapter_num}"

            btn = ttk.Button(
                self.chapter_buttons_frame,
                text=btn_text,
                width=12,
                command=lambda cn=chapter_num: self._switch_to_chapter(cn)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.chapter_buttons[chapter_num] = btn

        # 현재 선택된 버튼 강조
        self._update_chapter_button_state()

    def _switch_to_chapter(self, chapter_num: int):
        """챕터 버튼 클릭 시 해당 챕터로 전환"""
        # 전체 보기 모드면 개별 보기로 전환
        if self.is_full_view_mode:
            self.is_full_view_mode = False
            self.full_view_btn.config(text="📖 전체 대본 보기")

        self.current_chapter_num = chapter_num

        # 콤보박스도 동기화
        chapters = self.project_data.get_chapters()
        for i, ch in enumerate(chapters):
            if ch.get('chapter_number') == chapter_num:
                self.script_chapter_combo.current(i)
                break

        self._on_chapter_selected()
        self._update_chapter_button_state()

    def _update_chapter_button_state(self):
        """현재 선택된 챕터 버튼 강조"""
        for ch_num, btn in self.chapter_buttons.items():
            if ch_num == self.current_chapter_num:
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])

    def _update_chapter_listbox(self, chapters):
        """챕터 리스트박스 업데이트"""
        if not self.chapter_listbox:
            return

        # 기존 항목 삭제
        self.chapter_listbox.delete(0, tk.END)
        self.chapter_list_data.clear()

        if not chapters:
            self.chapter_listbox.insert(tk.END, "(챕터 없음)")
            return

        # 챕터별 항목 추가
        for ch in sorted(chapters, key=lambda x: x.get('chapter_number', 0)):
            chapter_num = ch.get('chapter_number', 0)
            chapter_title = ch.get('title', '제목 없음')

            # 대본 존재 여부 확인
            has_script = False
            try:
                script_data = self.file_service.load_script_file(chapter_num)
                if isinstance(script_data, dict) and script_data.get("script", "").strip():
                    has_script = True
            except Exception:
                pass

            if not has_script:
                has_script = bool((ch.get('script', '') or "").strip())

            # 글자 수 표시
            script_len = 0
            if has_script:
                try:
                    script_data = self.file_service.load_script_file(chapter_num)
                    if isinstance(script_data, dict):
                        script_len = len((script_data.get("script") or "").strip())
                except Exception:
                    script_len = len((ch.get('script', '') or "").strip())

            # 리스트 항목 텍스트
            status_icon = "✅" if has_script else "⬜"
            if script_len > 0:
                display_text = f"{status_icon} {chapter_num}. {chapter_title} ({script_len:,}자)"
            else:
                display_text = f"{status_icon} {chapter_num}. {chapter_title}"

            self.chapter_listbox.insert(tk.END, display_text)
            self.chapter_list_data.append((chapter_num, chapter_title, has_script))

        # 현재 선택된 챕터 표시
        self._sync_listbox_selection()

    def _sync_listbox_selection(self):
        """리스트박스 선택 상태를 현재 챕터와 동기화"""
        if not self.chapter_listbox or not self.chapter_list_data:
            return

        for i, (ch_num, _, _) in enumerate(self.chapter_list_data):
            if ch_num == self.current_chapter_num:
                self.chapter_listbox.selection_clear(0, tk.END)
                self.chapter_listbox.selection_set(i)
                self.chapter_listbox.see(i)
                break

    def _on_listbox_select(self, event):
        """리스트박스에서 챕터 선택 시"""
        if not self.chapter_listbox or not self.chapter_list_data:
            return

        selection = self.chapter_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index >= len(self.chapter_list_data):
            return

        chapter_num, _, _ = self.chapter_list_data[index]

        # 전체 보기 모드면 개별 보기로 전환
        if self.is_full_view_mode:
            self.is_full_view_mode = False
            self.full_view_btn.config(text="📖 전체 대본 보기")

        self.current_chapter_num = chapter_num

        # 콤보박스 동기화
        chapters = self.project_data.get_chapters()
        for i, ch in enumerate(chapters):
            if ch.get('chapter_number') == chapter_num:
                self.script_chapter_combo.current(i)
                break

        self._on_chapter_selected()
        self._update_chapter_button_state()

    def _on_chapter_selected(self):
        """
        챕터 선택 시 대본 로드
        원본 on_script_chapter_selected() 메서드의 로직을 완전히 이식
        """
        selected = self.script_chapter_var.get()
        if not selected:
            return

        # 선택된 챕터 번호 추출 (예: "챕터 1: 새로운 시작" -> 1)
        try:
            chapter_num = int(selected.split(':')[0].replace('챕터', '').strip())
        except:
            return

        # 현재 챕터 번호 업데이트 및 버튼 상태 갱신
        self.current_chapter_num = chapter_num
        self._update_chapter_button_state()

        # 해당 챕터 찾기
        chapters = self.project_data.get_chapters()
        chapter = None
        for ch in chapters:
            if ch.get('chapter_number') == chapter_num:
                chapter = ch
                break

        if not chapter:
            return

        # 대본 표시 (04_scripts 파일 우선)
        script = ""
        try:
            script_data = self.file_service.load_script_file(chapter_num)
            if isinstance(script_data, dict):
                script = (script_data.get("script") or "").strip()
        except Exception:
            script = ""

        # fallback: 챕터 파일에 저장된 script
        if not script:
            script = (chapter.get('script', '') or "").strip()

        # 뷰어 업데이트 (읽기 전용)
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            if script:
                self.script_viewer.insert(1.0, script)
            else:
                self.script_viewer.insert(1.0, "대본이 아직 없습니다.\n\n- '대본 저장'으로 직접 입력한 내용을 저장하거나\n- '대본 생성 (LLM)'으로 자동 생성하세요.")
            self.script_viewer.config(state=tk.DISABLED)

        # 에디터 업데이트
        if self.script_editor:
            self.script_editor.delete(1.0, tk.END)
            if script:
                self.script_editor.insert(1.0, script)
            else:
                self.script_editor.insert(1.0, "")

        # 글자 수 표시 (툴바에)
        if self.script_char_count_label:
            if script:
                char_count = len(script)
                self.script_char_count_label.config(text=f"📝 {char_count:,}자")
            else:
                self.script_char_count_label.config(text="")

    def _save_current_script(self):
        """대본 에디터 내용을 파일로 저장 (04_scripts/)"""
        ok = self.save()
        if ok:
            messagebox.showinfo("완료", "대본이 저장되었습니다. (04_scripts 폴더)")
            # 저장 후 화면 재로딩(파일 기준 표시)
            self._on_chapter_selected()
        else:
            messagebox.showerror("오류", "대본 저장에 실패했습니다.\n\n챕터 선택/파일 경로를 확인해주세요.")

    def _reload_current_script_from_file(self):
        """현재 선택된 챕터의 대본을 04_scripts 파일에서 다시 로드"""
        selected = self.script_chapter_var.get()
        if not selected:
            messagebox.showwarning("경고", "챕터를 선택해주세요.")
            return

        try:
            chapter_num = int(selected.split(':')[0].replace('챕터', '').strip())
        except Exception:
            messagebox.showerror("오류", "챕터 번호를 추출할 수 없습니다.")
            return

        script_data = None
        try:
            script_data = self.file_service.load_script_file(chapter_num)
        except Exception as e:
            messagebox.showerror("오류", f"대본 파일 로드 중 오류:\n{e}")
            return

        if not script_data or not isinstance(script_data, dict):
            messagebox.showwarning("경고", "저장된 대본 파일이 없습니다. (04_scripts)")
            return

        script = (script_data.get("script") or "").strip()

        # 뷰어/에디터 동시 업데이트
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0, script)
            self.script_viewer.config(state=tk.DISABLED)

        if self.script_editor:
            self.script_editor.delete(1.0, tk.END)
            self.script_editor.insert(1.0, script)

        if self.script_char_count_label:
            self.script_char_count_label.config(text=f"📝 {len(script):,}자" if script else "")

    def _generate_current_chapter(self):
        """
        선택한 챕터의 대본 생성 (LLM)
        원본 generate_script_for_chapter() 메서드의 로직을 완전히 이식
        """
        selected = self.script_chapter_var.get()
        if not selected:
            messagebox.showwarning("경고", "챕터를 선택해주세요.")
            return

        # 선택된 챕터 번호 추출
        try:
            chapter_num = int(selected.split(':')[0].replace('챕터', '').strip())
        except:
            messagebox.showerror("오류", "챕터 번호를 추출할 수 없습니다.")
            return

        # 대본 생성 실행
        self._generate_script(chapter_num)

    def _generate_all_chapters(self):
        """
        모든 챕터의 대본 생성 (LLM)
        원본 generate_all_scripts() 메서드의 로직을 완전히 이식
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
        self._on_chapter_selected()  # 화면 업데이트

    def _generate_script(self, chapter_num: int, show_message: bool = True) -> bool:
        """
        챕터 대본 생성 (내부 함수)
        원본 _generate_script() 메서드의 로직을 완전히 이식

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
            if prev_chapter and prev_chapter.get('script'):
                prev_script_full = prev_chapter.get('script', '')
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

            # 챕터 데이터에 대본 저장 (참조용)
            chapter['script'] = script.strip()
            chapter['script_length'] = len(script.strip())
            chapter['script_generated_at'] = datetime.now().isoformat()

            # 데이터 업데이트
            chapters[chapter_index] = chapter
            self.project_data.set_chapters(chapters)

            # 대본 파일에 별도 저장 (04_scripts/ 폴더)
            try:
                self.file_service.save_script_file(
                    chapter_number=chapter_num,
                    script=script.strip()
                )
            except Exception as save_error:
                print(f"경고: 대본 파일 저장 중 오류 발생: {save_error}")
            
            # 챕터 파일도 저장 (참조용)
            try:
                single_chapter_list = [chapter]
                self.file_service.save_chapters(single_chapter_list)
            except Exception as save_error:
                print(f"경고: 챕터 파일 저장 중 오류 발생: {save_error}")

            # 화면 업데이트
            self._on_chapter_selected()

            if show_message:
                messagebox.showinfo("완료", f"챕터 {chapter_num}의 대본이 생성되고 자동 저장되었습니다.\n글자 수: {len(script.strip())}자")

            return True

        except Exception as e:
            if show_message:
                messagebox.showerror("오류", f"대본 생성 중 오류 발생:\n{e}")
            return False

    def _format_characters_for_prompt(self, characters: list) -> str:
        """
        인물 정보를 프롬프트용 텍스트로 포맷팅
        원본 _format_characters_for_prompt() 메서드의 로직을 이식
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

    def save(self) -> bool:
        """
        데이터 저장
        현재 선택된 챕터의 대본을 에디터에서 가져와서 저장
        원본 save_all() 메서드의 scripts 저장 로직을 이식
        """
        # 현재 선택된 챕터의 대본 저장
        selected = self.script_chapter_var.get()
        if not selected:
            return True  # 선택된 챕터가 없으면 성공으로 간주

        try:
            chapter_num = int(selected.split(':')[0].replace('챕터', '').strip())
            # 에디터에서 대본 텍스트 가져오기
            script_text = self.script_editor.get(1.0, tk.END).strip()

            # 해당 챕터 찾기
            chapters = self.project_data.get_chapters()
            for i, ch in enumerate(chapters):
                if ch.get('chapter_number') == chapter_num:
                    # 챕터 데이터 업데이트 (참조용)
                    ch['script'] = script_text
                    ch['script_length'] = len(script_text)
                    ch['script_generated_at'] = datetime.now().isoformat()

                    # 데이터 업데이트
                    chapters[i] = ch
                    self.project_data.set_chapters(chapters)

                    # 대본 파일에 별도 저장 (04_scripts/ 폴더)
                    script_saved = self.file_service.save_script_file(
                        chapter_number=chapter_num,
                        script=script_text
                    )
                    
                    # 챕터 파일도 저장 (참조용)
                    chapter_saved = self.file_service.save_chapters([ch])
                    
                    return script_saved and chapter_saved

            return False
        except Exception as e:
            print(f"대본 저장 중 오류 발생: {e}")
            return False

    def _toggle_full_view_mode(self):
        """전체 대본 보기 모드 토글"""
        self.is_full_view_mode = not self.is_full_view_mode

        if self.is_full_view_mode:
            # 전체 보기 모드로 전환
            self.full_view_btn.config(text="📄 개별 챕터 보기")
            self._show_full_scripts()
        else:
            # 개별 챕터 보기 모드로 복귀
            self.full_view_btn.config(text="📖 전체 대본 보기")
            self._on_chapter_selected()

    def _show_full_scripts(self):
        """모든 챕터의 대본을 한 화면에 표시"""
        chapters = self.project_data.get_chapters()

        if not chapters:
            if self.script_viewer:
                self.script_viewer.config(state=tk.NORMAL)
                self.script_viewer.delete(1.0, tk.END)
                self.script_viewer.insert(1.0, "챕터 정보가 없습니다.")
                self.script_viewer.config(state=tk.DISABLED)
            return

        # 전체 대본 텍스트 생성
        full_script_lines = []
        total_char_count = 0

        for ch in sorted(chapters, key=lambda x: x.get('chapter_number', 0)):
            chapter_num = ch.get('chapter_number', 0)
            chapter_title = ch.get('title', '제목 없음')

            # 대본 로드 (04_scripts 파일 우선)
            script = ""
            try:
                script_data = self.file_service.load_script_file(chapter_num)
                if isinstance(script_data, dict):
                    script = (script_data.get("script") or "").strip()
            except Exception:
                pass

            # fallback: 챕터 파일에 저장된 script
            if not script:
                script = (ch.get('script', '') or "").strip()

            # 구분선 및 챕터 헤더
            full_script_lines.append("=" * 80)
            full_script_lines.append(f"【 챕터 {chapter_num}: {chapter_title} 】")
            if script:
                char_count = len(script)
                total_char_count += char_count
                full_script_lines.append(f"(글자 수: {char_count:,}자)")
            full_script_lines.append("=" * 80)
            full_script_lines.append("")

            # 대본 내용
            if script:
                full_script_lines.append(script)
            else:
                full_script_lines.append("(대본 없음)")

            full_script_lines.append("")
            full_script_lines.append("")

        # 마지막에 총 글자 수 표시
        full_script_lines.append("=" * 80)
        full_script_lines.append(f"【 전체 대본 총 글자 수: {total_char_count:,}자 】")
        full_script_lines.append("=" * 80)

        full_text = "\n".join(full_script_lines)

        # 뷰어에 표시
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            self.script_viewer.insert(1.0, full_text)
            self.script_viewer.config(state=tk.DISABLED)

        # 에디터에도 표시 (편집 불가 안내)
        if self.script_editor:
            self.script_editor.delete(1.0, tk.END)
            self.script_editor.insert(1.0, "※ 전체 보기 모드에서는 편집할 수 없습니다.\n\n'개별 챕터 보기' 버튼을 눌러 편집 모드로 전환하세요.")

        # 글자 수 표시 (툴바)
        if self.script_char_count_label:
            self.script_char_count_label.config(text=f"📝 전체 {total_char_count:,}자")
