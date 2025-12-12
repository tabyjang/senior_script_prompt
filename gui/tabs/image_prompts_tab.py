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


# 이미지 타입 번호 및 제목 매핑
IMAGE_TYPE_TITLES = {
    1: "전신샷",
    2: "옆모습 전신샷",
    3: "대각선 옆모습 전신샷",
    4: "초상화",
    5: "초상화 옆모습",
    6: "액션",
    7: "자연스러운 배경",
    8: "추가 프롬프트"
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
            text="🔄 이미지 프롬프트 자동 생성 (7종류)",
            command=self._generate_image_prompts
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        # 하단: 인물별 프롬프트 편집 영역
        content_frame = ttk.Frame(self.frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # PanedWindow로 크기 조절 가능하게 (세로 분할)
        paned_vertical = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        paned_vertical.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 상단: 뷰어 영역 (좌우 분할)
        viewer_container = ttk.Frame(paned_vertical)
        paned_vertical.add(viewer_container, weight=2)
        viewer_container.columnconfigure(0, weight=1)
        viewer_container.columnconfigure(1, weight=1)
        viewer_container.rowconfigure(0, weight=1)

        # 좌우 분할 PanedWindow
        paned_horizontal = ttk.PanedWindow(viewer_container, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 왼쪽: 뷰어 영역
        viewer_frame = ttk.LabelFrame(paned_horizontal, text="뷰어", padding=10)
        paned_horizontal.add(viewer_frame, weight=2)
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
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        # 오른쪽: 시스템 프롬프트 편집 영역
        system_prompt_frame = ttk.LabelFrame(paned_horizontal, text="이미지 시스템 프롬프트", padding=10)
        paned_horizontal.add(system_prompt_frame, weight=1)
        system_prompt_frame.columnconfigure(0, weight=1)
        system_prompt_frame.rowconfigure(0, weight=1)

        self.image_system_prompt_editor = scrolledtext.ScrolledText(
            system_prompt_frame,
            width=60,
            height=40,
            wrap=tk.WORD,
            font=("맑은 고딕", 10)
        )
        self.image_system_prompt_editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.image_system_prompt_editor.bind('<KeyRelease>', lambda e: self._on_system_prompt_edit())

        # 기본 시스템 프롬프트 로드
        self._load_image_system_prompt()

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
        self.paned_horizontal = paned_horizontal
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
        
        # 각 프롬프트 1~8 추출 (에디터에서 8개 슬롯을 항상 보이도록 모두 포함)
        for prompt_num in range(1, 9):
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

        # 각 프롬프트 1~8 표시 (없어도 슬롯은 표시)
        for prompt_num in range(1, 9):
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
        원본 _bind_mousewheel_to_image_prompts_viewer() 메서드의 로직을 완전히 이식

        새로 생성된 위젯들에 마우스 휠 이벤트를 다시 바인딩합니다.
        PanedWindow 구조를 탐색하여 Canvas를 찾아 바인딩합니다.
        """
        # PanedWindow에서 Canvas 찾기
        if hasattr(self, 'paned_horizontal'):
            for pane_name in self.paned_horizontal.panes():
                pane = self.paned_horizontal.nametowidget(pane_name)
                for pane_child in pane.winfo_children():
                    if isinstance(pane_child, tk.Canvas):
                        canvas = pane_child

                        def on_mousewheel(event):
                            """마우스 휠 스크롤 처리"""
                            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                            return "break"

                        def bind_to_widget(w):
                            """위젯과 모든 자식 위젯에 재귀적으로 마우스 휠 바인딩"""
                            w.bind("<MouseWheel>", on_mousewheel)
                            for c in w.winfo_children():
                                bind_to_widget(c)

                        # Canvas에 직접 바인딩
                        canvas.bind("<MouseWheel>", on_mousewheel)
                        canvas.bind("<Enter>", lambda e, c=canvas: c.focus_set())

                        # image_prompts_viewer_frame과 모든 자식 위젯에 바인딩
                        bind_to_widget(self.image_prompts_viewer_frame)
                        return

    def _load_image_system_prompt(self):
        """
        이미지 시스템 프롬프트 로드 (설정 파일 또는 기본값)
        원본 _load_image_system_prompt() 메서드의 로직을 완전히 이식
        """
        # 설정 파일에서 로드 시도
        # ConfigManager를 사용하려면 main_window에서 전달받아야 함
        # 임시로 기본 프롬프트 사용
        default_prompt = """당신은 이미지 생성을 위한 전문 프롬프트 엔지니어입니다.
주어진 인물 정보를 바탕으로 동일한 인물의 동일성을 반드시 유지하며 7가지 다른 스타일의 상세한 이미지 생성 프롬프트를 영어로 작성해주세요.

** 최적화 원칙**:
1. 모든 프롬프트는 **한국인 (Korean, East Asian)** 으로 명시해야 합니다
2. 실제 나이보다 **건강하고 젊어보이고 세련된** 외모로 표현하세요 (동양인은 더 어려보이고, 오디오북에서 젊은 이미지가 좋습니다)
3. 모든 프롬프트에서 동일한 인물의 일관성 유지 (얼굴 특징, 체형, 머리카락 등)
4. 각 프롬프트는 다른 각도, 포즈, 복장이지만 기본 외모는 동일해야 합니다
5. 품질 키워드 : professional photography
6. 카메라 설정 포함: 렌즈 타입, 조명, 구도
7. 부정적 요소 제거: no cartoon, no anime, no distortion
8. 반드시 JSON 형식으로만 응답해주세요"""

        self.image_system_prompt_editor.delete(1.0, tk.END)
        self.image_system_prompt_editor.insert(1.0, default_prompt)

    def _on_system_prompt_edit(self):
        """이미지 시스템 프롬프트 편집 시 호출"""
        # TODO: 설정 파일에 저장하도록 구현
        pass

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
            f"{len(characters)}명의 인물에 대해 각각 7가지 이미지 프롬프트를 생성하시겠습니까?\n\n"
            f"- 전신샷 (Full Body Shot)\n"
            f"- 옆모습 전신샷 (Side Profile Full Body Shot)\n"
            f"- 대각선 옆모습 전신샷 (Diagonal Side Profile Full Body Shot)\n"
            f"- 초상화 (Portrait)\n"
            f"- 초상화 옆모습 (Side Profile)\n"
            f"- 액션 (Action)\n"
            f"- 자연스러운 배경에 있는 모습 (Natural Background)\n\n"
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

            # 시스템 프롬프트 가져오기
            system_prompt = self.image_system_prompt_editor.get(1.0, tk.END).strip()

            # ContentGenerator를 사용하여 프롬프트 생성
            try:
                prompts = self.content_generator.generate_image_prompts(char, synopsis, visual_age)

                if prompts:
                    # image_generation_prompts 초기화
                    if 'image_generation_prompts' not in char:
                        char['image_generation_prompts'] = {}

                    # 각 프롬프트 저장
                    char['image_generation_prompts']['prompt_1'] = prompts.get("full_body_shot", "")
                    char['image_generation_prompts']['prompt_2'] = prompts.get("side_profile_full_body_shot", "")
                    char['image_generation_prompts']['prompt_3'] = prompts.get("diagonal_side_profile_full_body_shot", "")
                    char['image_generation_prompts']['prompt_4'] = prompts.get("portrait", "")
                    char['image_generation_prompts']['prompt_5'] = prompts.get("side_profile", "")
                    char['image_generation_prompts']['prompt_6'] = prompts.get("action", "")
                    char['image_generation_prompts']['prompt_7'] = prompts.get("natural_background", "")

                    # 첫 번째 프롬프트를 기본값으로도 설정
                    if prompts.get("full_body_shot"):
                        char['image_generation_prompt'] = prompts.get("full_body_shot")

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

                    # 프롬프트 번호 유효 범위 (1~8)
                    if not isinstance(prompt_num, int) or prompt_num < 1 or prompt_num > 8:
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
