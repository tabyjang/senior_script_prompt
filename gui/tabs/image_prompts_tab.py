"""
이미지 프롬프트 탭
캐릭터별 1~8 이미지 프롬프트 뷰어 및 에디터를 제공합니다.
원본 viewer_editor.py의 로직을 완전히 이식한 버전
"""

import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_tab import BaseTab
from utils.json_utils import format_json, safe_json_loads, extract_json_from_text


# 이미지 타입 번호 및 제목 매핑 (8개 → 12개 확장)
IMAGE_TYPE_TITLES = {
    1: "기본 정면",
    2: "일상 의상",
    3: "외출 의상",
    4: "정장/격식",
    5: "슬픔/감정",
    6: "분노/결의",
    7: "동작 장면",
    8: "대화/상호작용",
    9: "포옹/접촉",
    10: "상징물",
    11: "승리/만족",
    12: "새 시작/평화"
}

# ComfyUI 프롬프트용 카테고리 매핑
COMFYUI_CATEGORIES = {
    1: "기본",
    2: "의상",
    3: "의상",
    4: "의상",
    5: "표정",
    6: "표정",
    7: "동작",
    8: "상호작용",
    9: "상호작용",
    10: "상징물",
    11: "표정",
    12: "동작"
}


class ImagePromptsTab(BaseTab):
    """이미지 프롬프트 탭 클래스 - 원본 로직 완전 이식"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화 - 설정 관리자 추가로 필요"""
        # 먼저 서브탭 변수 초기화
        self.image_prompt_sub_tabs = {}
        self.current_image_prompt_num = 1
        # 인물별 탭 변수 초기화
        self.character_tabs = {}
        self.current_character_index = 0

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "이미지 프롬프트"

    def create_ui(self):
        """
        UI 생성
        원본 create_image_prompts_tab() 메서드의 로직을 완전히 이식
        - 상단: 1~5 서브탭 버튼 + 자동 생성 버튼
        - 중단: 좌우 분할 (뷰어 | 시스템 프롬프트 에디터)
        - 하단: JSON 에디터
        """
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # 상단: 인물별 탭 버튼 + 자동 생성 버튼
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 인물별 탭 버튼은 update_display()에서 동적으로 생성
        # 여기서는 프레임만 생성
        self.character_tabs_frame = ttk.Frame(button_frame)
        self.character_tabs_frame.pack(side=tk.LEFT, padx=5)

        # 구분선
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # 자동 생성 버튼
        generate_btn = ttk.Button(
            button_frame,
            text="🔄 이미지 프롬프트 자동 생성 (12종류)",
            command=self._generate_image_prompts
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        # 구분선
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # ComfyUI 프롬프트 폴더 선택 영역
        comfyui_frame = ttk.Frame(button_frame)
        comfyui_frame.pack(side=tk.LEFT, padx=5)

        ttk.Label(comfyui_frame, text="📂 프롬프트 폴더:").pack(side=tk.LEFT, padx=(0, 5))

        # 폴더 선택 드롭다운
        self.prompt_folder_var = tk.StringVar()
        self.prompt_folder_combo = ttk.Combobox(
            comfyui_frame,
            textvariable=self.prompt_folder_var,
            state="readonly",
            width=25
        )
        self.prompt_folder_combo.pack(side=tk.LEFT, padx=2)
        self.prompt_folder_combo.bind("<<ComboboxSelected>>", self._on_folder_selected)

        # 새로고침 버튼
        refresh_btn = ttk.Button(
            comfyui_frame,
            text="🔄",
            width=3,
            command=self._refresh_prompt_folders
        )
        refresh_btn.pack(side=tk.LEFT, padx=2)

        # 불러오기 버튼
        load_comfyui_btn = ttk.Button(
            comfyui_frame,
            text="불러오기",
            command=self._load_comfyui_prompts
        )
        load_comfyui_btn.pack(side=tk.LEFT, padx=2)

        # 초기 폴더 목록 로드
        self.frame.after(500, self._refresh_prompt_folders)

        # 하단: 인물별 프롬프트 편집 영역
        content_frame = ttk.Frame(self.frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # PanedWindow로 크기 조절 가능하게 (세로 분할)
        paned_vertical = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        paned_vertical.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 상단: 뷰어 영역
        viewer_frame = ttk.LabelFrame(paned_vertical, text="뷰어", padding=10)
        paned_vertical.add(viewer_frame, weight=2)
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        # 스크롤 가능한 뷰어 (Canvas + Scrollbar)
        self.canvas_viewer = tk.Canvas(viewer_frame)
        self.scrollbar_viewer = ttk.Scrollbar(
            viewer_frame,
            orient="vertical",
            command=self.canvas_viewer.yview
        )
        self.image_prompts_viewer_frame = ttk.Frame(self.canvas_viewer)

        # Canvas 스크롤 영역 설정
        self.image_prompts_viewer_frame.bind(
            "<Configure>",
            lambda e: self.canvas_viewer.configure(scrollregion=self.canvas_viewer.bbox("all"))
        )

        self.canvas_viewer.create_window((0, 0), window=self.image_prompts_viewer_frame, anchor="nw")
        self.canvas_viewer.configure(yscrollcommand=self.scrollbar_viewer.set)

        # 마우스 휠 이벤트 바인딩
        self._bind_initial_mousewheel()

        # Canvas와 Scrollbar 배치
        self.canvas_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar_viewer.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 하단: 원본 JSON 에디터
        editor_frame = ttk.LabelFrame(paned_vertical, text="원본 JSON 에디터", padding=10)
        paned_vertical.add(editor_frame, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.editor = scrolledtext.ScrolledText(
            editor_frame,
            width=120,
            height=30,
            wrap=tk.WORD,  # 줄바꿈 활성화
            font=("Consolas", 10)
        )
        self.editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.editor.bind('<KeyRelease>', lambda e: self.mark_unsaved())

        # PanedWindow 참조 저장 (마우스 휠 재바인딩용)
        self.paned_vertical = paned_vertical

    def _bind_initial_mousewheel(self):
        """
        초기 마우스 휠 이벤트 바인딩
        원본 create_image_prompts_tab() 내부의 마우스 휠 바인딩 로직
        """
        def on_mousewheel(event):
            """마우스 휠 스크롤 처리"""
            self.canvas_viewer.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        def bind_mousewheel_to_widget(widget):
            """위젯과 모든 자식 위젯에 재귀적으로 마우스 휠 바인딩"""
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_to_widget(child)

        # Canvas에 직접 바인딩
        self.canvas_viewer.bind("<MouseWheel>", on_mousewheel)
        self.canvas_viewer.bind("<Enter>", lambda e: self.canvas_viewer.focus_set())

        # Frame과 모든 자식 위젯에 바인딩
        bind_mousewheel_to_widget(self.image_prompts_viewer_frame)

    def _switch_sub_tab(self, num):
        """
        이미지 프롬프트 서브탭 전환
        원본 switch_image_prompt_sub_tab() 메서드의 로직을 완전히 이식
        (현재는 사용하지 않지만 호환성을 위해 유지)
        """
        # 이전 서브탭 버튼 상태 해제
        if self.current_image_prompt_num in self.image_prompt_sub_tabs:
            self.image_prompt_sub_tabs[self.current_image_prompt_num].state(['!pressed'])

        self.current_image_prompt_num = num
        if num in self.image_prompt_sub_tabs:
            self.image_prompt_sub_tabs[num].state(['pressed'])

        # 화면 업데이트
        self.update_display()

    def _switch_character_tab(self, char_index: int):
        """
        인물별 탭 전환
        Args:
            char_index: 선택할 인물의 인덱스 (0부터 시작)
        """
        # 이전 탭 버튼 상태 해제
        if self.current_character_index in self.character_tabs:
            self.character_tabs[self.current_character_index].state(['!pressed'])

        self.current_character_index = char_index
        
        # 새 탭 버튼 상태 설정
        if char_index in self.character_tabs:
            self.character_tabs[char_index].state(['pressed'])

        # 화면 업데이트
        self.update_display()

    def update_display(self):
        """
        화면 업데이트
        선택된 인물의 프롬프트 1~8 표시
        """
        # 기존 위젯 제거
        for widget in self.image_prompts_viewer_frame.winfo_children():
            widget.destroy()

        characters = self.project_data.get_characters()

        if not characters:
            ttk.Label(
                self.image_prompts_viewer_frame,
                text="인물 정보가 없습니다.",
                font=("맑은 고딕", 11)
            ).pack(pady=20)
            self.editor.delete(1.0, tk.END)
            self.editor.insert(1.0, "[]")
            # 인물 탭 버튼도 제거
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
        self._create_prompt_widget(0, selected_char)

        # 마우스 휠 이벤트 재바인딩
        self._rebind_mousewheel()

        # 에디터에 JSON 표시 (선택된 인물의 프롬프트만)
        self.editor.delete(1.0, tk.END)

        # 선택된 인물의 모든 프롬프트 데이터 추출
        prompts_data = []
        char_name = selected_char.get('name', '알 수 없음')
        prompts_obj = selected_char.get('image_generation_prompts', {})
        
        # 각 프롬프트 1~12 추출 (에디터에서 12개 슬롯을 항상 보이도록 모두 포함)
        for prompt_num in range(1, 13):
            prompt_key = f"prompt_{prompt_num}"
            prompt_text = prompts_obj.get(prompt_key, '')
            
            # 프롬프트 1이 없고 기존 image_generation_prompt가 있으면 사용
            if prompt_num == 1 and not prompt_text:
                prompt_text = selected_char.get('image_generation_prompt', '')
            
            prompts_data.append({
                "character_name": char_name,
                "prompt_number": prompt_num,
                "prompt": prompt_text or ""
            })

        json_str = format_json(prompts_data)
        self.editor.insert(1.0, json_str)

    def _create_character_tabs(self, characters):
        """
        인물별 탭 버튼 생성
        Args:
            characters: 인물 리스트
        """
        # 기존 탭 버튼 제거
        for widget in self.character_tabs_frame.winfo_children():
            widget.destroy()
        self.character_tabs.clear()

        # 인물 수만큼 탭 버튼 생성
        for idx in range(len(characters)):
            btn = ttk.Button(
                self.character_tabs_frame,
                text=f"인물{idx + 1}",
                width=12,
                command=lambda i=idx: self._switch_character_tab(i)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.character_tabs[idx] = btn

        # 현재 선택된 탭 버튼 상태 설정
        if self.current_character_index in self.character_tabs:
            self.character_tabs[self.current_character_index].state(['pressed'])

    def _create_prompt_widget(self, idx: int, char: dict):
        """
        이미지 프롬프트 뷰어 위젯 생성
        한 인물의 프롬프트 1~8을 모두 표시
        형식: "인물1, 1. 제목: 전신샷"
        """
        # image_generation_prompts는 dict가 정상이며,
        # 과거 데이터/수동 편집으로 문자열(JSON)로 저장된 경우가 있어 방어적으로 정규화한다.
        prompts_obj = char.get('image_generation_prompts', {})
        if isinstance(prompts_obj, str):
            parsed = safe_json_loads(prompts_obj)
            prompts_obj = parsed if isinstance(parsed, dict) else {}
            char['image_generation_prompts'] = prompts_obj
        elif not isinstance(prompts_obj, dict):
            prompts_obj = {}
            char['image_generation_prompts'] = prompts_obj
        char_name = char.get('name', '알 수 없음')

        # 인물 번호 (현재 선택된 인덱스 + 1)
        char_number = self.current_character_index + 1

        # 메인 프레임
        main_frame = ttk.Frame(self.image_prompts_viewer_frame)
        main_frame.pack(fill=tk.X, padx=15, pady=10)

        # 각 프롬프트 1~12 표시 (없어도 슬롯은 표시)
        for prompt_num in range(1, 13):
            prompt_key = f"prompt_{prompt_num}"
            prompt_content = prompts_obj.get(prompt_key, '')

            # 프롬프트 1이 없고 기존 image_generation_prompt가 있으면 사용
            if prompt_num == 1 and not prompt_content:
                prompt_content = char.get('image_generation_prompt', '')

            # 프롬프트가 없으면 표시용 placeholder
            display_content = prompt_content if prompt_content else "(비어있음)"

            # 이미지 타입 제목 가져오기 (프롬프트 JSON에 shot_name이 있으면 우선 사용)
            image_type_title = IMAGE_TYPE_TITLES.get(prompt_num, f"이미지 타입 {prompt_num}")
            try:
                prompt_json = safe_json_loads(prompt_content)
                if isinstance(prompt_json, dict):
                    shot_name = prompt_json.get('shot_name')
                    if isinstance(shot_name, str) and shot_name.strip():
                        image_type_title = shot_name.strip()
            except Exception:
                pass

            # 각 프롬프트를 위한 서브 프레임
            # 제목 형식: "인물1, 1. 제목: 전신샷"
            frame_title = f"인물{char_number}, {prompt_num}. 제목: {image_type_title}"

            prompt_frame = ttk.LabelFrame(
                main_frame,
                text=frame_title,
                padding=10
            )
            prompt_frame.pack(fill=tk.X, pady=5)

            # 프롬프트 텍스트 영역
            prompt_text = scrolledtext.ScrolledText(
                prompt_frame,
                width=80,
                height=5,
                wrap=tk.WORD,
                font=("맑은 고딕", 10),
                state=tk.DISABLED
            )
            prompt_text.pack(fill=tk.BOTH, expand=True)

            # 프롬프트 내용 삽입
            prompt_text.config(state=tk.NORMAL)
            prompt_text.insert(1.0, display_content)
            prompt_text.config(state=tk.DISABLED)

    def _rebind_mousewheel(self):
        """
        마우스 휠 이벤트 재바인딩
        새로 생성된 위젯들에 마우스 휠 이벤트를 다시 바인딩합니다.
        """
        def on_mousewheel(event):
            """마우스 휠 스크롤 처리"""
            self.canvas_viewer.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        def bind_to_widget(w):
            """위젯과 모든 자식 위젯에 재귀적으로 마우스 휠 바인딩"""
            w.bind("<MouseWheel>", on_mousewheel)
            for c in w.winfo_children():
                bind_to_widget(c)

        # Canvas에 직접 바인딩
        self.canvas_viewer.bind("<MouseWheel>", on_mousewheel)
        self.canvas_viewer.bind("<Enter>", lambda e: self.canvas_viewer.focus_set())

        # image_prompts_viewer_frame과 모든 자식 위젯에 바인딩
        bind_to_widget(self.image_prompts_viewer_frame)

    def _generate_image_prompts(self):
        """
        모든 인물에 대해 이미지 프롬프트 7종류 자동 생성
        원본 generate_image_prompts_for_all_characters() 메서드의 로직을 완전히 이식
        """
        # 파일에서 최신 인물 정보 모두 로드 (이미지 정보 포함)
        characters = self.file_service.load_characters()
        if not characters:
            messagebox.showwarning("경고", "인물 정보가 없습니다.")
            return
        
        # 프로젝트 데이터도 업데이트
        self.project_data.set_characters(characters)

        # 확인 대화상자
        result = messagebox.askyesno(
            "이미지 프롬프트 생성",
            f"{len(characters)}명의 인물에 대해 각각 12가지 이미지 프롬프트를 생성하시겠습니까?\n\n"
            f"[의상 버전]\n"
            f"- 기본 정면 / 일상 의상 / 외출 의상 / 정장/격식\n\n"
            f"[표정 버전]\n"
            f"- 슬픔/감정 / 분노/결의 / 승리/만족\n\n"
            f"[동작/상호작용]\n"
            f"- 동작 장면 / 대화 / 포옹/접촉\n\n"
            f"[기타]\n"
            f"- 상징물 / 새 시작/평화\n\n"
            f"시놉시스와 인물 정보를 기반으로 동일한 인물의 동일성을 유지하며 생성합니다.\n"
            f"이 작업은 시간이 걸릴 수 있습니다."
        )
        if not result:
            return

        # 시놉시스 정보
        synopsis = self.project_data.get_synopsis()

        # 각 인물별로 7가지 프롬프트를 생성
        total_characters = len(characters)
        success_count = 0

        for char_idx, char in enumerate(characters):
            char_name = char.get('name', '알 수 없음')

            # 나이 조정 (나이대별 차감 규칙, 최소 25세)
            char_age = char.get('age', 35)
            if isinstance(char_age, str):
                try:
                    char_age = int(char_age)
                except:
                    char_age = 35
            # 60세 이상: 20세 차감, 50세 이상: 15세 차감, 40세 이상: 10세 차감, 30세 이상: 7세 차감
            if char_age >= 60:
                age_deduction = 20
            elif char_age >= 50:
                age_deduction = 15
            elif char_age >= 40:
                age_deduction = 10
            elif char_age >= 30:
                age_deduction = 7
            else:
                # 30세 미만은 최소값 적용
                age_deduction = 0
            visual_age = max(25, char_age - age_deduction)

            # ContentGenerator를 사용하여 프롬프트 생성
            try:
                prompts = self.content_generator.generate_image_prompts(char, synopsis, visual_age)

                if prompts:
                    # image_generation_prompts 초기화
                    if 'image_generation_prompts' not in char:
                        char['image_generation_prompts'] = {}

                    # 12가지 프롬프트 저장 (새로운 ComfyUI 형식)
                    prompt_mapping = {
                        1: "basic_front",          # 기본 정면
                        2: "daily_outfit",         # 일상 의상
                        3: "outing_outfit",        # 외출 의상
                        4: "formal_outfit",        # 정장/격식
                        5: "sad_emotion",          # 슬픔/감정
                        6: "anger_resolve",        # 분노/결의
                        7: "action_scene",         # 동작 장면
                        8: "conversation",         # 대화/상호작용
                        9: "embrace",              # 포옹/접촉
                        10: "symbolic_item",       # 상징물
                        11: "victory",             # 승리/만족
                        12: "new_beginning"        # 새 시작/평화
                    }

                    for num, key in prompt_mapping.items():
                        prompt_content = prompts.get(key, "")
                        if prompt_content:
                            char['image_generation_prompts'][f'prompt_{num}'] = prompt_content

                    # 첫 번째 프롬프트를 기본값으로도 설정
                    if prompts.get("basic_front"):
                        char['image_generation_prompt'] = prompts.get("basic_front")

                    success_count += 1
            except Exception as e:
                print(f"프롬프트 생성 오류 ({char_name}): {e}")

        # 데이터 업데이트
        self.project_data.set_characters(characters)

        # 변경사항 표시
        self.mark_unsaved()

        # 인물 데이터 자동 저장
        self.file_service.save_characters(characters)

        # 화면 업데이트
        self.update_display()

        messagebox.showinfo(
            "완료",
            f"이미지 프롬프트 생성이 완료되었습니다!\n\n"
            f"성공: {success_count}/{total_characters}명\n\n"
            f"각 인물의 JSON 파일에 저장되었습니다."
        )

    def save(self) -> bool:
        """
        데이터 저장
        JSON 에디터의 내용을 파싱하여 각 캐릭터의 프롬프트 데이터로 저장
        모든 인물의 모든 프롬프트를 저장
        """
        json_str = self.editor.get(1.0, tk.END).strip()
        if json_str:
            prompts_data = safe_json_loads(json_str)
            if prompts_data is not None:
                characters = self.project_data.get_characters()
                
                # 각 인물의 image_generation_prompts 초기화
                for char in characters:
                    if 'image_generation_prompts' not in char:
                        char['image_generation_prompts'] = {}

                # JSON 데이터를 파싱하여 각 인물의 프롬프트 저장
                for prompt_item in prompts_data:
                    char_name = prompt_item.get('character_name', '')
                    prompt_num = prompt_item.get('prompt_number', 1)
                    prompt_text = prompt_item.get('prompt', '')
                    prompt_key = f"prompt_{prompt_num}"

                    # 프롬프트 번호 유효 범위 (1~12)
                    if not isinstance(prompt_num, int) or prompt_num < 1 or prompt_num > 12:
                        continue

                    # 해당 인물 찾기
                    for char in characters:
                        if char.get('name') == char_name:
                            # 프롬프트 저장/삭제(빈 문자열이면 제거)
                            if isinstance(prompt_text, str) and prompt_text.strip():
                                char['image_generation_prompts'][prompt_key] = prompt_text
                            else:
                                if prompt_key in char['image_generation_prompts']:
                                    char['image_generation_prompts'].pop(prompt_key, None)
                            
                            # 프롬프트 1을 기본값으로도 설정
                            if prompt_num == 1:
                                if isinstance(prompt_text, str) and prompt_text.strip():
                                    char['image_generation_prompt'] = prompt_text
                                else:
                                    char['image_generation_prompt'] = ""
                            break

                # 데이터 업데이트 및 저장
                self.project_data.set_characters(characters)
                return self.file_service.save_characters(characters)
        return False

    def _get_prompts_base_dir(self):
        """prompts 기본 디렉토리 경로 반환"""
        from pathlib import Path

        project_dir = self.file_service.project_dir
        if not project_dir:
            return None

        # editors_app 디렉토리 찾기 (prompts 폴더가 있는 위치)
        editors_app_dir = Path(project_dir).parent.parent  # 01_man/editors_app
        prompts_base = editors_app_dir / "prompts"

        return prompts_base if prompts_base.exists() else None

    def _refresh_prompt_folders(self):
        """prompts 폴더 목록 새로고침"""
        from pathlib import Path

        prompts_base = self._get_prompts_base_dir()
        if not prompts_base:
            self.prompt_folder_combo['values'] = ["(prompts 폴더 없음)"]
            self.prompt_folder_var.set("(prompts 폴더 없음)")
            return

        # prompts 폴더 내의 하위 폴더들 (이야기별 폴더) 찾기
        folders = []
        for item in prompts_base.iterdir():
            if item.is_dir():
                # characters 폴더가 있는지 확인
                if (item / "characters").exists():
                    folders.append(item.name)

        if folders:
            self.prompt_folder_combo['values'] = sorted(folders)
            # 현재 값이 없거나 목록에 없으면 첫 번째 항목 선택
            current = self.prompt_folder_var.get()
            if not current or current not in folders:
                self.prompt_folder_var.set(folders[0])
        else:
            self.prompt_folder_combo['values'] = ["(프로젝트 폴더 없음)"]
            self.prompt_folder_var.set("(프로젝트 폴더 없음)")

    def _on_folder_selected(self, event=None):
        """폴더 선택 시 호출"""
        selected = self.prompt_folder_var.get()
        if selected and not selected.startswith("("):
            print(f"[ComfyUI] 폴더 선택됨: {selected}")

    def _load_comfyui_prompts(self):
        """
        prompts 폴더에서 ComfyUI 형식의 프롬프트를 불러오기
        드롭다운에서 선택한 폴더의 characters/ 하위 JSON 파일들을 로드
        """
        import os
        from pathlib import Path
        from tkinter import filedialog

        # 선택된 폴더 확인
        selected_folder = self.prompt_folder_var.get()
        if not selected_folder or selected_folder.startswith("("):
            messagebox.showwarning("경고", "프롬프트 폴더를 선택하세요.")
            return

        prompts_base = self._get_prompts_base_dir()
        if not prompts_base:
            messagebox.showwarning("경고", "prompts 폴더를 찾을 수 없습니다.")
            return

        characters_dir = prompts_base / selected_folder / "characters"

        if not characters_dir.exists():
            messagebox.showwarning("경고", f"characters 폴더를 찾을 수 없습니다:\n{characters_dir}")
            return

        # JSON 파일 목록 가져오기
        json_files = list(characters_dir.glob("*.json"))
        if not json_files:
            messagebox.showwarning("경고", f"JSON 파일을 찾을 수 없습니다:\n{characters_dir}")
            return

        # characters_all.json 제외
        json_files = [f for f in json_files if f.name != "characters_all.json"]

        if not json_files:
            messagebox.showwarning("경고", "캐릭터 프롬프트 JSON 파일이 없습니다.")
            return

        # 현재 캐릭터 목록
        characters = self.project_data.get_characters()
        if not characters:
            characters = self.file_service.load_characters()

        loaded_count = 0
        matched_count = 0

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    prompt_data = json.load(f)

                if not isinstance(prompt_data, dict):
                    continue

                char_name = prompt_data.get('character_name', '')
                versions = prompt_data.get('versions', [])

                if not char_name or not versions:
                    continue

                loaded_count += 1

                # 이름으로 캐릭터 찾기
                matched_char = None
                for char in characters:
                    if char.get('name', '').replace(' ', '') == char_name.replace(' ', ''):
                        matched_char = char
                        break

                if not matched_char:
                    print(f"[ComfyUI] 캐릭터 '{char_name}'을 찾을 수 없습니다.")
                    continue

                matched_count += 1

                # image_generation_prompts 초기화
                if 'image_generation_prompts' not in matched_char:
                    matched_char['image_generation_prompts'] = {}

                # 버전별로 프롬프트 저장
                for version in versions:
                    version_id = version.get('version_id', '')
                    if not version_id:
                        continue

                    # v01, v02 형식에서 숫자 추출
                    try:
                        prompt_num = int(version_id.replace('v', ''))
                    except ValueError:
                        continue

                    if prompt_num < 1 or prompt_num > 12:
                        continue

                    # ComfyUI 형식의 프롬프트 구성
                    comfyui_prompt = {
                        "version_name": version.get('version_name', ''),
                        "category": version.get('category', ''),
                        "positive": version.get('positive', ''),
                        "negative": version.get('negative', ''),
                        "output_folder": version.get('output_folder', ''),
                        "filename_prefix": version.get('filename_prefix', '')
                    }

                    # JSON 문자열로 저장
                    matched_char['image_generation_prompts'][f'prompt_{prompt_num}'] = json.dumps(
                        comfyui_prompt, ensure_ascii=False
                    )

                print(f"[ComfyUI] '{char_name}' 프롬프트 로드 완료 ({len(versions)}개 버전)")

            except Exception as e:
                print(f"[ComfyUI] 파일 로드 오류 ({json_file.name}): {e}")

        # 데이터 업데이트
        self.project_data.set_characters(characters)

        # 저장
        self.file_service.save_characters(characters)

        # 화면 업데이트
        self.update_display()

        messagebox.showinfo(
            "완료",
            f"ComfyUI 프롬프트 불러오기 완료!\n\n"
            f"📁 프로젝트: {selected_folder}\n"
            f"📄 로드된 파일: {loaded_count}개\n"
            f"👤 매칭된 캐릭터: {matched_count}명\n\n"
            f"위치: {characters_dir}"
        )
