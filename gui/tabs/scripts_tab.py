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
        self.frame.rowconfigure(1, weight=1)

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

        # 글자 수 표시 라벨
        self.script_char_count_label = ttk.Label(toolbar, text="", font=("맑은 고딕", 9))
        self.script_char_count_label.pack(side=tk.LEFT, padx=10)

        # 하단: 뷰어/에디터 영역
        content_frame = ttk.Frame(self.frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # PanedWindow로 크기 조절 가능하게
        paned = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 상단: 뷰어 영역 (읽기 전용)
        viewer_frame = ttk.LabelFrame(paned, text="대본 뷰어 (TTS 복사용)", padding=10)
        paned.add(viewer_frame, weight=1)
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        self.script_viewer = scrolledtext.ScrolledText(
            viewer_frame,
            width=120,
            height=20,
            wrap=tk.WORD,
            font=("맑은 고딕", 11),
            state=tk.DISABLED
        )
        self.script_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 하단: 에디터 영역
        editor_frame = ttk.LabelFrame(paned, text="대본 에디터", padding=10)
        paned.add(editor_frame, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.script_editor = scrolledtext.ScrolledText(
            editor_frame,
            width=120,
            height=20,
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

        # 해당 챕터 찾기
        chapters = self.project_data.get_chapters()
        chapter = None
        for ch in chapters:
            if ch.get('chapter_number') == chapter_num:
                chapter = ch
                break

        if not chapter:
            return

        # 대본 표시
        script = chapter.get('script', '')

        # 뷰어 업데이트 (읽기 전용)
        if self.script_viewer:
            self.script_viewer.config(state=tk.NORMAL)
            self.script_viewer.delete(1.0, tk.END)
            if script:
                self.script_viewer.insert(1.0, script)
            else:
                self.script_viewer.insert(1.0, "대본이 아직 생성되지 않았습니다.\n\n'대본 생성 (LLM)' 버튼을 눌러 자동 생성하세요.")
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

            # 챕터 데이터에 대본 저장
            chapter['script'] = script.strip()
            chapter['script_length'] = len(script.strip())
            chapter['script_generated_at'] = datetime.now().isoformat()

            # 데이터 업데이트
            chapters[chapter_index] = chapter
            self.project_data.set_chapters(chapters)

            # 파일에 즉시 자동 저장
            try:
                # 단일 챕터만 저장
                single_chapter_list = [chapter]
                self.file_service.save_chapters(single_chapter_list)
            except Exception as save_error:
                print(f"경고: 대본은 생성되었으나 저장 중 오류 발생: {save_error}")

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
                    # 챕터 데이터 업데이트
                    ch['script'] = script_text
                    ch['script_length'] = len(script_text)
                    ch['script_generated_at'] = datetime.now().isoformat()

                    # 데이터 업데이트
                    chapters[i] = ch
                    self.project_data.set_chapters(chapters)

                    # 파일 저장 (단일 챕터만)
                    single_chapter_list = [ch]
                    return self.file_service.save_chapters(single_chapter_list)

            return False
        except Exception as e:
            print(f"대본 저장 중 오류 발생: {e}")
            return False
