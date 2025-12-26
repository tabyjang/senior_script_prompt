"""
캐릭터 탭
캐릭터 뷰어 및 에디터를 제공합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_tab import BaseTab
from utils.json_utils import format_json, safe_json_loads
from utils.ui_helpers import create_scrollable_frame
from utils.file_utils import normalize_character_name


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

        # 좌우 분할 PanedWindow
        self.paned_horizontal = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        self.paned_horizontal.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 왼쪽: 읽기 전용 뷰어
        viewer_frame = ttk.LabelFrame(self.paned_horizontal, text="뷰어", padding=10)
        self.paned_horizontal.add(viewer_frame, weight=1)
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        # 스크롤 가능한 뷰어
        canvas_viewer, self.viewer_frame, scrollbar_viewer = create_scrollable_frame(viewer_frame)
        canvas_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_viewer.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 오른쪽: 편집 가능한 영역
        self.editor_container = ttk.LabelFrame(self.paned_horizontal, text="편집", padding=10)
        self.paned_horizontal.add(self.editor_container, weight=1)
        self.editor_container.columnconfigure(0, weight=1)
        self.editor_container.rowconfigure(0, weight=1)
        
        # 편집 영역의 최소 너비 설정 (일관된 크기 유지)
        self.editor_container.config(width=400)  # 최소 너비 설정

        # 스크롤 가능한 편집 영역
        canvas_editor, self.editor_frame, scrollbar_editor = create_scrollable_frame(self.editor_container)
        canvas_editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_editor.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 저장 버튼 프레임 (편집 영역 하단)
        save_button_frame = ttk.Frame(self.editor_container)
        save_button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        save_btn = ttk.Button(
            save_button_frame,
            text="저장",
            command=self._save_character_edits
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

    def update_display(self):
        """화면 업데이트"""
        # 파일에서 최신 데이터 다시 로드 (인물/세부정보 입력 탭에서 저장한 데이터 반영)
        try:
            all_data = self.file_service.load_all_data()
            self.project_data.data = all_data
        except Exception as e:
            print(f"데이터 로드 오류: {e}")

        # 캐릭터 프로필(인포) + 캐릭터 디테일 로드 후 통합
        characters = self._get_characters_from_synopsis_or_data()
        details_list = []
        try:
            details_list = self.file_service.load_character_details()
        except Exception as e:
            print(f"캐릭터 디테일 로드 오류: {e}")

        self._details_by_name = self._build_details_map(details_list)

        if not characters:
            # 뷰어와 편집 영역 초기화
            for widget in self.viewer_frame.winfo_children():
                widget.destroy()
            for widget in self.editor_frame.winfo_children():
                widget.destroy()
            
            ttk.Label(
                self.viewer_frame,
                text="인물 정보가 없습니다.\n시놉시스 입력 탭에서 등장인물을 입력해주세요.",
                font=("맑은 고딕", 11)
            ).pack(pady=20)
            
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
        selected_detail = self._details_by_name.get(self._normalize_name(selected_char.get("name", "")), {})
        
        # 뷰어와 편집 영역 업데이트
        self._create_viewer_widget(selected_char, selected_detail)
        self._create_editor_widget(selected_char, selected_detail)

    def _normalize_name(self, name: str) -> str:
        """캐릭터 이름 정규화 - file_utils의 함수 사용"""
        return normalize_character_name(name)

    def _build_details_map(self, details_list):
        """
        디테일 리스트를 name 기준으로 매핑
        - 파일에서 온 _detail_filename은 유지
        """
        details_by_name = {}
        if not isinstance(details_list, list):
            return details_by_name

        for d in details_list:
            if not isinstance(d, dict):
                continue
            name = self._normalize_name(d.get("name", ""))
            if not name:
                continue
            details_by_name[name] = d
        return details_by_name

    def _get_characters_from_synopsis_or_data(self):
        """
        기존 인물 데이터(세부 정보 포함)를 우선 사용하고, 시놉시스의 기본 정보로 업데이트
        시놉시스에 등장인물이 있으면 이름을 기준으로 매칭하여 기본 정보만 업데이트하고,
        세부 정보는 기존 인물 데이터의 것을 유지합니다.
        """
        # 기존 인물 데이터를 먼저 가져옴 (세부 정보 포함)
        characters = self.project_data.get_characters()
        
        synopsis = self.project_data.get_synopsis()
        synopsis_characters = synopsis.get('characters', [])
        
        if synopsis_characters:
            # 인물 이름을 키로 하는 딕셔너리 생성 (빠른 검색을 위해)
            character_dict = {self._normalize_name(char.get('name', '')): char for char in characters}
            
            # 시놉시스의 등장인물로 기본 정보만 업데이트
            for syn_char in synopsis_characters:
                name = syn_char.get('name', '')
                if not name:
                    continue
                name_key = self._normalize_name(name)
                name_clean = name_key
                
                if name_key in character_dict:
                    # 기존 인물이 있으면 기본 정보만 업데이트 (세부 정보 유지)
                    existing_char = character_dict[name_key]
                    # 저장 이름도 공백 제거 형태로 통일
                    existing_char['name'] = name_clean
                    # 기본 정보 필드만 업데이트 (시놉시스에 값이 있으면 사용, 없으면 기존 값 유지)
                    existing_char.update({
                        'age': syn_char.get('age', existing_char.get('age', '')),
                        'occupation': syn_char.get('occupation', existing_char.get('occupation', '')),
                        'personality': syn_char.get('personality', existing_char.get('personality', '')),
                        'appearance': syn_char.get('appearance', existing_char.get('appearance', '')),
                        'traits': syn_char.get('traits', existing_char.get('traits', '')),
                        'desire': syn_char.get('desire', existing_char.get('desire', '')),
                        'role': syn_char.get('role', existing_char.get('role', ''))
                    })
                else:
                    # 새 인물이면 시놉시스 정보로 추가
                    characters.append({
                        'name': name_clean,
                        'age': syn_char.get('age', ''),
                        'occupation': syn_char.get('occupation', ''),
                        'personality': syn_char.get('personality', ''),
                        'appearance': syn_char.get('appearance', ''),
                        'traits': syn_char.get('traits', ''),
                        'desire': syn_char.get('desire', ''),
                        'role': syn_char.get('role', '')
                    })
        
        return characters

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

    def _create_viewer_widget(self, char: dict, detail: dict):
        """읽기 전용 뷰어 위젯 생성 - 캐릭터 인포(프로필) + 캐릭터 디테일 분리 표시"""
        # 기존 위젯 제거
        for widget in self.viewer_frame.winfo_children():
            widget.destroy()

        # 기본 정보 필드 (시놉시스에서 가져온 정보)
        basic_info_fields = ['name', 'age', 'occupation', 'personality', 'appearance', 'traits', 'desire', 'role']
        
        # 캐릭터 인포 섹션(프로필)
        basic_info_frame = ttk.LabelFrame(self.viewer_frame, text="캐릭터 인포 (프로필)", padding=10)
        basic_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        for field in basic_info_fields:
            if field in char:
                value = char[field]
                value_str = str(value) if value is not None else ""
                
                if len(value_str) > 100:
                    label = ttk.Label(
                        basic_info_frame,
                        text=f"{field}:",
                        font=("맑은 고딕", 9, "bold")
                    )
                    label.pack(anchor=tk.W, padx=5, pady=2)
                    
                    text_widget = scrolledtext.ScrolledText(
                        basic_info_frame,
                        height=3,
                        wrap=tk.WORD,
                        font=("맑은 고딕", 9),
                        state=tk.DISABLED
                    )
                    text_widget.pack(fill=tk.X, padx=10, pady=2)
                    text_widget.insert(1.0, value_str)
                else:
                    label = ttk.Label(
                        basic_info_frame,
                        text=f"{field}: {value_str}",
                        font=("맑은 고딕", 9)
                    )
                    label.pack(anchor=tk.W, padx=5, pady=2)
        
        # 캐릭터 디테일 섹션(별도 파일)
        detail_info_frame = ttk.LabelFrame(self.viewer_frame, text="캐릭터 디테일", padding=10)
        detail_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if not detail:
            ttk.Label(
                detail_info_frame,
                text="(캐릭터 디테일 파일이 없습니다. '인물 세부정보 입력' 탭에서 입력/저장하면 생성됩니다.)",
                font=("맑은 고딕", 9),
                foreground="gray"
            ).pack(anchor=tk.W, padx=5, pady=2)
        # 세부 정보 필드 목록
        detail_info_fields = [
            'id', 'role_type', 'relation_to_protagonist',
            'appearance_visual', 'sensory_scent', 'sensory_touch', 'fashion_style',
            'personality_surface', 'personality_deep', 'trauma_or_lack',
            'desire_conscious', 'desire_unconscious',
            'voice_tone', 'speech_habit', 'breathing_sound'
        ]
        
        for field in detail_info_fields:
            if field in detail:
                value = detail[field]
                value_str = str(value) if value is not None else ""
                
                if len(value_str) > 100:
                    label = ttk.Label(
                        detail_info_frame,
                        text=f"{field}:",
                        font=("맑은 고딕", 9, "bold")
                    )
                    label.pack(anchor=tk.W, padx=5, pady=2)
                    
                    text_widget = scrolledtext.ScrolledText(
                        detail_info_frame,
                        height=3,
                        wrap=tk.WORD,
                        font=("맑은 고딕", 9),
                        state=tk.DISABLED
                    )
                    text_widget.pack(fill=tk.X, padx=10, pady=2)
                    text_widget.insert(1.0, value_str)
                else:
                    label = ttk.Label(
                        detail_info_frame,
                        text=f"{field}: {value_str}",
                        font=("맑은 고딕", 9)
                    )
                    label.pack(anchor=tk.W, padx=5, pady=2)
        
        # 나머지 필드들 (기본 정보와 세부 정보에 포함되지 않은 필드)
        remaining_fields = {k: v for k, v in char.items() 
                          if k not in basic_info_fields + ['_filename']}
        
        if remaining_fields:
            other_info_frame = ttk.LabelFrame(self.viewer_frame, text="기타 정보", padding=10)
            other_info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            for key, value in remaining_fields.items():
                value_str = str(value) if value is not None else ""
                if len(value_str) > 100:
                    label = ttk.Label(
                        other_info_frame,
                        text=f"{key}:",
                        font=("맑은 고딕", 9, "bold")
                    )
                    label.pack(anchor=tk.W, padx=5, pady=2)
                    
                    text_widget = scrolledtext.ScrolledText(
                        other_info_frame,
                        height=3,
                        wrap=tk.WORD,
                        font=("맑은 고딕", 9),
                        state=tk.DISABLED
                    )
                    text_widget.pack(fill=tk.X, padx=10, pady=2)
                    text_widget.insert(1.0, value_str)
                else:
                    label = ttk.Label(
                        other_info_frame,
                        text=f"{key}: {value_str}",
                        font=("맑은 고딕", 9)
                    )
                    label.pack(anchor=tk.W, padx=5, pady=2)

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

    def _create_editor_widget(self, char: dict, detail: dict):
        """편집 가능한 위젯 생성 - 캐릭터 인포(프로필) + 캐릭터 디테일을 분리하여 표시"""
        # 기존 위젯 제거
        for widget in self.editor_frame.winfo_children():
            widget.destroy()
        self.edit_fields.clear()
        
        # 편집 영역의 너비를 일관되게 유지하기 위해 최소 너비 설정
        # PanedWindow의 sash 위치를 조정하여 편집 영역 크기 유지
        if hasattr(self, 'paned_horizontal'):
            # 편집 영역의 너비를 일정하게 유지 (전체의 약 40% 정도)
            try:
                # PanedWindow의 sash 위치 조정 (전체 너비의 60% 지점)
                paned_width = self.paned_horizontal.winfo_width()
                if paned_width > 0:
                    sash_pos = int(paned_width * 0.6)
                    self.paned_horizontal.sashpos(0, sash_pos)
            except:
                pass  # sash 위치 조정 실패 시 무시

        # 기본 정보 필드 (시놉시스에서 가져온 정보)
        basic_info_fields = ['name', 'age', 'occupation', 'personality', 'appearance', 'traits', 'desire', 'role']
        
        # 캐릭터 인포 섹션(프로필)
        basic_info_frame = ttk.LabelFrame(self.editor_frame, text="캐릭터 인포 (프로필)", padding=10)
        basic_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        for field in basic_info_fields:
            value = char.get(field, '')
            value_str = str(value) if value is not None else ""
            
            frame = ttk.Frame(basic_info_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            # 키값 라벨
            label = ttk.Label(
                frame,
                text=f"{field}:",
                font=("맑은 고딕", 9, "bold"),
                width=20,
                anchor=tk.W
            )
            label.pack(side=tk.LEFT, padx=5)
            
            # 밸류값 입력 필드
            # name은 매칭 키이므로 여기서는 변경 불가(디테일 파일과 연결이 깨질 수 있음)
            if field == "name":
                entry = ttk.Entry(frame, font=("맑은 고딕", 9), width=50, state="disabled")
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                entry.insert(0, value_str)
                self.edit_fields[field] = ('profile_entry_disabled', entry)
                continue

            if len(value_str) > 50 or '\n' in value_str:
                text_widget = scrolledtext.ScrolledText(
                    frame,
                    height=3,
                    wrap=tk.WORD,
                    font=("맑은 고딕", 9),
                    width=50  # 최소 너비 설정
                )
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
                text_widget.insert(1.0, value_str)
                self.edit_fields[field] = ('profile_text', text_widget)
            else:
                entry = ttk.Entry(frame, font=("맑은 고딕", 9), width=50)  # 최소 너비 설정
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                entry.insert(0, value_str)
                self.edit_fields[field] = ('profile_entry', entry)
        
        # 캐릭터 디테일 섹션(별도 파일)
        detail_info_frame = ttk.LabelFrame(self.editor_frame, text="캐릭터 디테일", padding=10)
        detail_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 세부 정보 필드 목록
        detail_info_fields = [
            'id', 'role_type', 'relation_to_protagonist',
            'appearance_visual', 'sensory_scent', 'sensory_touch', 'fashion_style',
            'personality_surface', 'personality_deep', 'trauma_or_lack',
            'desire_conscious', 'desire_unconscious',
            'voice_tone', 'speech_habit', 'breathing_sound'
        ]
        
        for field in detail_info_fields:
            value = (detail or {}).get(field, '')
            value_str = str(value) if value is not None else ""
            
            frame = ttk.Frame(detail_info_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            # 키값 라벨
            label = ttk.Label(
                frame,
                text=f"{field}:",
                font=("맑은 고딕", 9, "bold"),
                width=20,
                anchor=tk.W
            )
            label.pack(side=tk.LEFT, padx=5)
            
            # 밸류값 입력 필드
            if len(value_str) > 50 or '\n' in value_str:
                text_widget = scrolledtext.ScrolledText(
                    frame,
                    height=3,
                    wrap=tk.WORD,
                    font=("맑은 고딕", 9),
                    width=50  # 최소 너비 설정
                )
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
                text_widget.insert(1.0, value_str)
                self.edit_fields[field] = ('detail_text', text_widget)
            else:
                entry = ttk.Entry(frame, font=("맑은 고딕", 9), width=50)  # 최소 너비 설정
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                entry.insert(0, value_str)
                self.edit_fields[field] = ('detail_entry', entry)
        
        # 나머지 필드들 (기본 정보와 세부 정보에 포함되지 않은 필드)
        remaining_fields = {k: v for k, v in char.items() 
                          if k not in basic_info_fields + ['_filename']}
        
        if remaining_fields:
            other_info_frame = ttk.LabelFrame(self.editor_frame, text="기타 정보", padding=10)
            other_info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            for key, value in remaining_fields.items():
                value_str = str(value) if value is not None else ""
                
                frame = ttk.Frame(other_info_frame)
                frame.pack(fill=tk.X, padx=5, pady=2)
                
                # 키값 라벨
                label = ttk.Label(
                    frame,
                    text=f"{key}:",
                    font=("맑은 고딕", 9, "bold"),
                    width=20,
                    anchor=tk.W
                )
                label.pack(side=tk.LEFT, padx=5)
                
                # 밸류값 입력 필드
                if len(value_str) > 50 or '\n' in value_str:
                    text_widget = scrolledtext.ScrolledText(
                        frame,
                        height=3,
                        wrap=tk.WORD,
                        font=("맑은 고딕", 9),
                        width=50  # 최소 너비 설정
                    )
                    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
                    text_widget.insert(1.0, value_str)
                    self.edit_fields[key] = ('profile_text', text_widget)
                else:
                    entry = ttk.Entry(frame, font=("맑은 고딕", 9), width=50)  # 최소 너비 설정
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    entry.insert(0, value_str)
                    self.edit_fields[key] = ('profile_entry', entry)
        
        # 편집 영역 크기 일관성 유지를 위한 업데이트
        self.frame.update_idletasks()
        if hasattr(self, 'paned_horizontal'):
            try:
                # PanedWindow의 sash 위치를 조정하여 편집 영역 크기 유지
                paned_width = self.paned_horizontal.winfo_width()
                if paned_width > 100:  # 최소 너비 확인
                    # 편집 영역이 전체의 약 40% 정도 되도록 설정
                    sash_pos = int(paned_width * 0.6)
                    self.paned_horizontal.sashpos(0, sash_pos)
            except:
                pass  # sash 위치 조정 실패 시 무시


    def _save_character_edits(self):
        """편집된 인물 정보 저장"""
        characters = self.project_data.get_characters()
        
        if not characters or self.current_character_index >= len(characters):
            messagebox.showwarning("경고", "저장할 인물 정보가 없습니다.")
            return

        try:
            # 현재 인물(프로필) 데이터 복사
            char = characters[self.current_character_index].copy()
            char_name = self._normalize_name(char.get("name", ""))
            if not char_name:
                messagebox.showerror("오류", "캐릭터 이름(name)이 없어 저장할 수 없습니다.")
                return

            # 기존 디테일 로드
            existing_detail = {}
            try:
                details_list = self.file_service.load_character_details()
                details_by_name = self._build_details_map(details_list)
                existing_detail = details_by_name.get(char_name, {})
            except Exception:
                existing_detail = {}

            detail_to_save = existing_detail.copy() if isinstance(existing_detail, dict) else {}
            detail_to_save["name"] = char.get("name", "")
            
            # 편집 필드에서 값 읽어서 업데이트
            for key, (field_type, widget) in self.edit_fields.items():
                if field_type in ["profile_entry", "detail_entry"]:
                    value = widget.get()
                elif field_type in ["profile_text", "detail_text"]:
                    value = widget.get(1.0, tk.END).strip()
                else:
                    # profile_entry_disabled 등
                    continue
                
                if field_type.startswith("profile_"):
                    char[key] = value
                elif field_type.startswith("detail_"):
                    detail_to_save[key] = value
            
            # 인물 리스트 업데이트
            characters[self.current_character_index] = char
            self.project_data.set_characters(characters)
            
            # 파일 저장
            profile_ok = self.file_service.save_characters(characters)
            detail_ok = self.file_service.save_character_detail(detail_to_save, character_index=self.current_character_index + 1)

            if profile_ok and detail_ok:
                messagebox.showinfo("완료", "인물(프로필)과 캐릭터 디테일이 저장되었습니다.")
                self.mark_unsaved()
                # 화면 업데이트
                self.update_display()
            else:
                messagebox.showerror("오류", "파일 저장에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류가 발생했습니다: {e}")

    def save(self) -> bool:
        """데이터 저장 (편집 필드에서)"""
        return self._save_character_edits()
