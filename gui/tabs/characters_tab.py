"""
캐릭터 탭
캐릭터 뷰어 및 에디터를 제공합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_tab import BaseTab
from utils.json_utils import format_json, safe_json_loads
from utils.ui_helpers import create_scrollable_frame
import json


class CharactersTab(BaseTab):
    """캐릭터 탭 클래스"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        # 인물별 탭 변수 초기화
        self.character_tabs = {}
        self.current_character_index = 0
        self.edit_fields = {}  # 편집 필드 참조 저장
        
        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "인물"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # 상단: 인물별 탭 버튼 프레임
        toolbar = ttk.Frame(self.frame)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Label(toolbar, text="캐릭터 관리:", font=("맑은 고딕", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # 인물별 탭 버튼 프레임
        self.character_tabs_frame = ttk.Frame(toolbar)
        self.character_tabs_frame.pack(side=tk.LEFT, padx=5)

        # PanedWindow로 크기 조절 가능하게 (세로 분할)
        paned_vertical = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        paned_vertical.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 중간: 좌우 분할 영역
        content_container = ttk.Frame(paned_vertical)
        paned_vertical.add(content_container, weight=2)
        content_container.columnconfigure(0, weight=1)
        content_container.columnconfigure(1, weight=1)
        content_container.rowconfigure(0, weight=1)

        # 좌우 분할 PanedWindow
        paned_horizontal = ttk.PanedWindow(content_container, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 왼쪽: 읽기 전용 뷰어
        viewer_frame = ttk.LabelFrame(paned_horizontal, text="뷰어", padding=10)
        paned_horizontal.add(viewer_frame, weight=1)
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        # 스크롤 가능한 뷰어
        canvas_viewer, self.viewer_frame, scrollbar_viewer = create_scrollable_frame(viewer_frame)
        canvas_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_viewer.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 오른쪽: 편집 가능한 영역
        editor_container = ttk.LabelFrame(paned_horizontal, text="편집", padding=10)
        paned_horizontal.add(editor_container, weight=1)
        editor_container.columnconfigure(0, weight=1)
        editor_container.rowconfigure(0, weight=1)

        # 스크롤 가능한 편집 영역
        canvas_editor, self.editor_frame, scrollbar_editor = create_scrollable_frame(editor_container)
        canvas_editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_editor.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 저장 버튼 프레임 (편집 영역 하단)
        save_button_frame = ttk.Frame(editor_container)
        save_button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        save_btn = ttk.Button(
            save_button_frame,
            text="저장",
            command=self._save_character_edits
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

        # 하단: 원본 JSON 에디터
        json_editor_frame = ttk.LabelFrame(paned_vertical, text="원본 JSON 에디터", padding=10)
        paned_vertical.add(json_editor_frame, weight=1)
        json_editor_frame.columnconfigure(0, weight=1)
        json_editor_frame.rowconfigure(0, weight=1)

        self.editor = scrolledtext.ScrolledText(
            json_editor_frame,
            width=120,
            height=25,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.editor.bind('<KeyRelease>', lambda e: self.mark_unsaved())

    def update_display(self):
        """화면 업데이트"""
        characters = self.project_data.get_characters()

        if not characters:
            # 뷰어와 편집 영역 초기화
            for widget in self.viewer_frame.winfo_children():
                widget.destroy()
            for widget in self.editor_frame.winfo_children():
                widget.destroy()
            
            ttk.Label(
                self.viewer_frame,
                text="인물 정보가 없습니다.",
                font=("맑은 고딕", 11)
            ).pack(pady=20)
            
            self.editor.delete(1.0, tk.END)
            self.editor.insert(1.0, "[]")
            
            # 인물 탭 버튼 제거
            for widget in self.character_tabs_frame.winfo_children():
                widget.destroy()
            self.character_tabs.clear()
            return

        # 인물별 탭 버튼 생성/업데이트
        self._create_character_tabs(characters)

        # 현재 선택된 인물 인덱스 유효성 검사
        if self.current_character_index >= len(characters):
            self.current_character_index = 0

        # 선택된 인물만 표시
        selected_char = characters[self.current_character_index]
        
        # 뷰어와 편집 영역 업데이트
        self._create_viewer_widget(selected_char)
        self._create_editor_widget(selected_char)

        # JSON 에디터에 선택된 인물만 표시
        self.editor.delete(1.0, tk.END)
        json_str = format_json(selected_char)
        self.editor.insert(1.0, json_str)

    def _create_character_tabs(self, characters):
        """인물별 탭 버튼 생성"""
        # 기존 탭 버튼 제거
        for widget in self.character_tabs_frame.winfo_children():
            widget.destroy()
        self.character_tabs.clear()

        # 인물 수만큼 탭 버튼 생성
        for idx in range(len(characters)):
            char_name = characters[idx].get('name', f'인물{idx + 1}')
            btn = ttk.Button(
                self.character_tabs_frame,
                text=f"인물{idx + 1} ({char_name})",
                width=15,
                command=lambda i=idx: self._switch_character_tab(i)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.character_tabs[idx] = btn

        # 현재 선택된 탭 버튼 상태 설정
        if self.current_character_index in self.character_tabs:
            self.character_tabs[self.current_character_index].state(['pressed'])

    def _switch_character_tab(self, char_index: int):
        """인물별 탭 전환"""
        # 이전 탭 버튼 상태 해제
        if self.current_character_index in self.character_tabs:
            self.character_tabs[self.current_character_index].state(['!pressed'])

        self.current_character_index = char_index
        
        # 새 탭 버튼 상태 설정
        if char_index in self.character_tabs:
            self.character_tabs[char_index].state(['pressed'])

        # 화면 업데이트
        self.update_display()

    def _create_viewer_widget(self, char: dict):
        """읽기 전용 뷰어 위젯 생성"""
        # 기존 위젯 제거
        for widget in self.viewer_frame.winfo_children():
            widget.destroy()

        # 인물 정보를 키값과 함께 세로로 나열
        self._display_dict_recursive(self.viewer_frame, char, "")

    def _display_dict_recursive(self, parent, data, prefix=""):
        """딕셔너리를 재귀적으로 표시"""
        if isinstance(data, dict):
            for key, value in data.items():
                # _filename 같은 내부 키는 제외
                if key == '_filename':
                    continue
                    
                current_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    # 딕셔너리인 경우
                    frame = ttk.LabelFrame(parent, text=f"{key}:", padding=5)
                    frame.pack(fill=tk.X, padx=5, pady=2)
                    self._display_dict_recursive(frame, value, current_key)
                elif isinstance(value, list):
                    # 리스트인 경우
                    label = ttk.Label(
                        parent,
                        text=f"{key}:",
                        font=("맑은 고딕", 9, "bold")
                    )
                    label.pack(anchor=tk.W, padx=5, pady=2)
                    
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            item_frame = ttk.LabelFrame(parent, text=f"  [{i}]:", padding=5)
                            item_frame.pack(fill=tk.X, padx=10, pady=2)
                            self._display_dict_recursive(item_frame, item, f"{current_key}[{i}]")
                        else:
                            item_label = ttk.Label(
                                parent,
                                text=f"  [{i}]: {item}",
                                font=("맑은 고딕", 9)
                            )
                            item_label.pack(anchor=tk.W, padx=15, pady=1)
                else:
                    # 단순 값인 경우
                    value_str = str(value) if value is not None else ""
                    # 긴 텍스트는 줄바꿈
                    if len(value_str) > 100:
                        label = ttk.Label(
                            parent,
                            text=f"{key}:",
                            font=("맑은 고딕", 9, "bold")
                        )
                        label.pack(anchor=tk.W, padx=5, pady=2)
                        
                        text_widget = scrolledtext.ScrolledText(
                            parent,
                            height=3,
                            wrap=tk.WORD,
                            font=("맑은 고딕", 9),
                            state=tk.DISABLED
                        )
                        text_widget.pack(fill=tk.X, padx=10, pady=2)
                        text_widget.insert(1.0, value_str)
                    else:
                        label = ttk.Label(
                            parent,
                            text=f"{key}: {value_str}",
                            font=("맑은 고딕", 9)
                        )
                        label.pack(anchor=tk.W, padx=5, pady=2)
        else:
            # 딕셔너리가 아닌 경우
            label = ttk.Label(
                parent,
                text=str(data),
                font=("맑은 고딕", 9)
            )
            label.pack(anchor=tk.W, padx=5, pady=2)

    def _create_editor_widget(self, char: dict):
        """편집 가능한 위젯 생성"""
        # 기존 위젯 제거
        for widget in self.editor_frame.winfo_children():
            widget.destroy()
        self.edit_fields.clear()

        # 인물 정보를 키값과 함께 세로로 나열하고 편집 필드 생성
        self._create_edit_fields_recursive(self.editor_frame, char, "")

    def _create_edit_fields_recursive(self, parent, data, prefix=""):
        """편집 필드를 재귀적으로 생성"""
        if isinstance(data, dict):
            for key, value in data.items():
                # _filename 같은 내부 키는 제외
                if key == '_filename':
                    continue
                    
                current_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    # 딕셔너리인 경우 - JSON 형식으로 편집
                    frame = ttk.LabelFrame(parent, text=f"{key}:", padding=5)
                    frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    label = ttk.Label(frame, text="(JSON 형식으로 편집)", font=("맑은 고딕", 8))
                    label.pack(anchor=tk.W, padx=5)
                    
                    text_widget = scrolledtext.ScrolledText(
                        frame,
                        height=5,
                        wrap=tk.WORD,
                        font=("Consolas", 9)
                    )
                    text_widget.pack(fill=tk.X, padx=5, pady=2)
                    text_widget.insert(1.0, format_json(value))
                    self.edit_fields[current_key] = ('dict', text_widget)
                    
                elif isinstance(value, list):
                    # 리스트인 경우 - JSON 형식으로 편집
                    label = ttk.Label(
                        parent,
                        text=f"{key}:",
                        font=("맑은 고딕", 9, "bold")
                    )
                    label.pack(anchor=tk.W, padx=5, pady=2)
                    
                    label2 = ttk.Label(parent, text="(JSON 형식으로 편집)", font=("맑은 고딕", 8))
                    label2.pack(anchor=tk.W, padx=10)
                    
                    text_widget = scrolledtext.ScrolledText(
                        parent,
                        height=4,
                        wrap=tk.WORD,
                        font=("Consolas", 9)
                    )
                    text_widget.pack(fill=tk.X, padx=10, pady=2)
                    text_widget.insert(1.0, format_json(value))
                    self.edit_fields[current_key] = ('list', text_widget)
                    
                else:
                    # 단순 값인 경우
                    value_str = str(value) if value is not None else ""
                    
                    # 긴 텍스트는 ScrolledText, 짧은 것은 Entry
                    if len(value_str) > 50 or '\n' in value_str:
                        label = ttk.Label(
                            parent,
                            text=f"{key}:",
                            font=("맑은 고딕", 9, "bold")
                        )
                        label.pack(anchor=tk.W, padx=5, pady=2)
                        
                        text_widget = scrolledtext.ScrolledText(
                            parent,
                            height=3,
                            wrap=tk.WORD,
                            font=("맑은 고딕", 9)
                        )
                        text_widget.pack(fill=tk.X, padx=10, pady=2)
                        text_widget.insert(1.0, value_str)
                        self.edit_fields[current_key] = ('text', text_widget)
                    else:
                        frame = ttk.Frame(parent)
                        frame.pack(fill=tk.X, padx=5, pady=2)
                        
                        label = ttk.Label(
                            frame,
                            text=f"{key}:",
                            font=("맑은 고딕", 9, "bold"),
                            width=15,
                            anchor=tk.W
                        )
                        label.pack(side=tk.LEFT, padx=5)
                        
                        entry = ttk.Entry(frame, font=("맑은 고딕", 9))
                        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                        entry.insert(0, value_str)
                        self.edit_fields[current_key] = ('entry', entry)

    def _save_character_edits(self):
        """편집된 인물 정보 저장"""
        characters = self.project_data.get_characters()
        
        if not characters or self.current_character_index >= len(characters):
            messagebox.showwarning("경고", "저장할 인물 정보가 없습니다.")
            return

        try:
            # 현재 인물 데이터 복사
            char = characters[self.current_character_index].copy()
            
            # 편집 필드에서 값 읽어서 업데이트
            for key_path, (field_type, widget) in self.edit_fields.items():
                if field_type == 'entry':
                    value = widget.get()
                elif field_type == 'text':
                    value = widget.get(1.0, tk.END).strip()
                elif field_type in ('dict', 'list'):
                    json_str = widget.get(1.0, tk.END).strip()
                    try:
                        value = safe_json_loads(json_str)
                        if value is None:
                            continue
                    except:
                        messagebox.showerror("오류", f"{key_path}의 JSON 형식이 올바르지 않습니다.")
                        return
                else:
                    continue
                
                # 키 경로를 따라 딕셔너리 업데이트
                self._update_nested_dict(char, key_path, value)
            
            # 인물 리스트 업데이트
            characters[self.current_character_index] = char
            self.project_data.set_characters(characters)
            
            # 파일 저장
            if self.file_service.save_characters(characters):
                messagebox.showinfo("완료", "인물 정보가 저장되었습니다.")
                self.mark_unsaved()
                # 화면 업데이트
                self.update_display()
            else:
                messagebox.showerror("오류", "파일 저장에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류가 발생했습니다: {e}")

    def _update_nested_dict(self, data: dict, key_path: str, value):
        """중첩된 딕셔너리의 값을 업데이트"""
        keys = key_path.split('.')
        current = data
        
        # 마지막 키를 제외한 모든 키를 따라가기
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 마지막 키에 값 설정
        final_key = keys[-1]
        current[final_key] = value

    def save(self) -> bool:
        """데이터 저장 (JSON 에디터에서)"""
        json_str = self.editor.get(1.0, tk.END).strip()
        if json_str:
            try:
                char_data = safe_json_loads(json_str)
                if char_data is not None:
                    characters = self.project_data.get_characters()
                    if characters and self.current_character_index < len(characters):
                        characters[self.current_character_index] = char_data
                        self.project_data.set_characters(characters)
                        if self.file_service.save_characters(characters):
                            # 화면 업데이트
                            self.update_display()
                            return True
            except Exception as e:
                messagebox.showerror("오류", f"JSON 파싱 오류: {e}")
        return False
