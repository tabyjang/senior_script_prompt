"""
이미지 생성 탭
인물별 7개 이미지 프롬프트 생성 및 관리를 제공합니다.
장면 생성 탭을 기반으로 구현
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
from typing import Optional, Dict, List
from .base_tab import BaseTab
from utils.json_utils import extract_json_from_text
import threading
import time
import json
from pathlib import Path


# 이미지 제목 매핑
IMAGE_TITLES = {
    1: "전신샷 (Full Body Shot)",
    2: "옆모습 전신샷 (Side Profile Full Body Shot)",
    3: "대각선 옆모습 전신샷 (Diagonal Side Profile Full Body Shot)",
    4: "초상화 (Portrait)",
    5: "초상화 옆모습 (Side Profile)",
    6: "액션 (Action)",
    7: "자연스러운 배경에 있는 모습 (Natural Background)"
}


class ImageGenerationTab(BaseTab):
    """이미지 생성 탭 클래스"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        # 인물 선택 변수 초기화
        self.character_var = None
        self.character_combo = None
        self.character_info_viewer = None
        self.images_tab_viewer_frame = None
        self.images_tab_canvas = None
        self.images_tab_right_frame = None
        self.images_tab_paned = None

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "이미지 생성"

    def create_ui(self):
        """
        UI 생성
        - 좌우 분할: 왼쪽(인물 선택 + 인물 정보) | 오른쪽(7개 이미지 목록)
        """
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # 좌우 분할 (PanedWindow)
        paned_horizontal = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 왼쪽: 인물 선택 + 인물 정보
        left_frame = ttk.LabelFrame(paned_horizontal, text="인물 정보", padding=10)
        paned_horizontal.add(left_frame, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        # 인물 선택 영역
        character_select_frame = ttk.Frame(left_frame)
        character_select_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(character_select_frame, text="인물 선택:", font=("맑은 고딕", 10)).pack(side=tk.LEFT, padx=5)

        self.character_var = tk.StringVar()
        self.character_combo = ttk.Combobox(
            character_select_frame,
            textvariable=self.character_var,
            width=30,
            state='readonly'
        )
        self.character_combo.pack(side=tk.LEFT, padx=5)
        self.character_combo.bind('<<ComboboxSelected>>', lambda e: self._on_character_selected())

        # 이미지 생성 버튼
        image_gen_btn = ttk.Button(
            character_select_frame,
            text="🖼️ 이미지 생성 (7개)",
            command=self._generate_current_character
        )
        image_gen_btn.pack(side=tk.LEFT, padx=5)

        # 모든 인물 이미지 생성 버튼
        all_images_gen_btn = ttk.Button(
            character_select_frame,
            text="🔄 모든 이미지 생성",
            command=self._generate_all_characters
        )
        all_images_gen_btn.pack(side=tk.LEFT, padx=5)

        # 인물 정보 표시 영역 (세로로 길게)
        character_info_display_frame = ttk.Frame(left_frame)
        character_info_display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        character_info_display_frame.columnconfigure(0, weight=1)
        character_info_display_frame.rowconfigure(0, weight=1)

        self.character_info_viewer = scrolledtext.ScrolledText(
            character_info_display_frame,
            width=60,
            height=40,
            wrap=tk.WORD,
            font=("맑은 고딕", 11),
            state=tk.DISABLED
        )
        self.character_info_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 오른쪽: 7개 이미지 정보 (세로로 길게)
        right_frame = ttk.LabelFrame(paned_horizontal, text="이미지 목록 (7개)", padding=10)
        paned_horizontal.add(right_frame, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # 스크롤 가능한 이미지 목록
        canvas_images = tk.Canvas(right_frame)
        scrollbar_images = ttk.Scrollbar(right_frame, orient="vertical", command=canvas_images.yview)
        self.images_tab_viewer_frame = ttk.Frame(canvas_images)

        # Canvas에 스크롤 영역 설정
        self.images_tab_viewer_frame.bind(
            "<Configure>",
            lambda e: canvas_images.configure(scrollregion=canvas_images.bbox("all"))
        )

        canvas_images.create_window((0, 0), window=self.images_tab_viewer_frame, anchor="nw")
        canvas_images.configure(yscrollcommand=scrollbar_images.set)

        canvas_images.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_images.grid(row=0, column=1, sticky=(tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # Canvas 참조 저장 (나중에 마우스 휠 재바인딩용)
        self.images_tab_canvas = canvas_images
        self.images_tab_right_frame = right_frame
        self.images_tab_paned = paned_horizontal

        # 마우스 휠 이벤트 바인딩 (변수 할당 후에 호출)
        self._bind_initial_mousewheel(canvas_images)

    def _bind_initial_mousewheel(self, canvas_images):
        """
        초기 마우스 휠 이벤트 바인딩
        """
        def on_mousewheel_images(event):
            """마우스 휠 스크롤 처리 (Windows와 Linux 모두 지원)"""
            try:
                if hasattr(event, 'num'):
                    # Linux
                    if event.num == 4:
                        canvas_images.yview_scroll(-3, "units")
                    elif event.num == 5:
                        canvas_images.yview_scroll(3, "units")
                elif hasattr(event, 'delta'):
                    # Windows
                    if event.delta > 0:
                        canvas_images.yview_scroll(-3, "units")
                    else:
                        canvas_images.yview_scroll(3, "units")
            except:
                pass
            return "break"

        def bind_mousewheel_to_widget(widget):
            """위젯과 모든 자식 위젯에 마우스 휠 바인딩 (재귀적)"""
            if widget is None:
                return
            try:
                widget.bind("<MouseWheel>", on_mousewheel_images, add='+')
                widget.bind("<Button-4>", on_mousewheel_images, add='+')
                widget.bind("<Button-5>", on_mousewheel_images, add='+')
                for child in widget.winfo_children():
                    bind_mousewheel_to_widget(child)
            except:
                pass

        # Canvas에 직접 바인딩
        canvas_images.bind("<MouseWheel>", on_mousewheel_images, add='+')
        canvas_images.bind("<Button-4>", on_mousewheel_images, add='+')
        canvas_images.bind("<Button-5>", on_mousewheel_images, add='+')
        canvas_images.bind("<Enter>", lambda e: canvas_images.focus_set())

        # Frame과 모든 자식 위젯에 바인딩
        bind_mousewheel_to_widget(self.images_tab_viewer_frame)
        bind_mousewheel_to_widget(canvas_images)

        # right_frame 전체 영역에서도 작동하도록
        if hasattr(self, 'images_tab_right_frame') and self.images_tab_right_frame is not None:
            self.images_tab_right_frame.bind("<MouseWheel>", on_mousewheel_images, add='+')
            self.images_tab_right_frame.bind("<Button-4>", on_mousewheel_images, add='+')
            self.images_tab_right_frame.bind("<Button-5>", on_mousewheel_images, add='+')

        # paned_horizontal에도 바인딩
        if hasattr(self, 'images_tab_paned') and self.images_tab_paned is not None:
            self.images_tab_paned.bind("<MouseWheel>", on_mousewheel_images, add='+')
            self.images_tab_paned.bind("<Button-4>", on_mousewheel_images, add='+')
            self.images_tab_paned.bind("<Button-5>", on_mousewheel_images, add='+')

        # Canvas 포커스 설정
        canvas_images.focus_set()

    def update_display(self):
        """
        화면 업데이트
        인물 목록을 콤보박스에 로드
        """
        characters = self.project_data.get_characters()

        # 인물 목록을 콤보박스에 로드
        character_list = [f"인물{i+1}: {ch.get('name', '이름 없음')}"
                         for i, ch in enumerate(characters)]

        if self.character_combo:
            self.character_combo['values'] = character_list
            if character_list and not self.character_var.get():
                self.character_combo.current(0)
                self._on_character_selected()

    def _on_character_selected(self):
        """
        인물 선택 시 인물 정보와 이미지 목록 로드
        """
        if not hasattr(self, 'character_var'):
            return

        selected = self.character_var.get()
        if not selected:
            return

        # 선택된 인물 인덱스 추출
        try:
            char_index = int(selected.split(':')[0].replace('인물', '').strip()) - 1
        except Exception as e:
            print(f"인물 인덱스 추출 오류: {e}")
            return

        # 해당 인물 찾기
        characters = self.project_data.get_characters()
        if char_index < 0 or char_index >= len(characters):
            print(f"인물 인덱스 {char_index}가 유효하지 않습니다.")
            return

        character = characters[char_index]

        # 인물 정보 표시
        self._display_character_info(character)

        # 현재 선택된 인물 저장 (이미지 업로드 시 사용)
        self.current_character = character
        self.current_character_index = char_index
        
        # 이미지 목록 표시 업데이트
        self._update_images_display(character)

    def _display_character_info(self, character: dict):
        """
        인물 정보 표시
        선택된 인물의 모든 키-값 정보를 표시
        """
        if not hasattr(self, 'character_info_viewer'):
            return

        self.character_info_viewer.config(state=tk.NORMAL)
        self.character_info_viewer.delete(1.0, tk.END)

        # 인물의 모든 키-값 정보를 포맷팅하여 표시
        info_lines = []
        for key, value in character.items():
            if isinstance(value, dict):
                # 딕셔너리인 경우 JSON 형식으로 표시
                value_str = json.dumps(value, ensure_ascii=False, indent=2)
                info_lines.append(f"{key}:\n{value_str}\n")
            elif isinstance(value, list):
                # 리스트인 경우 각 항목을 줄바꿈으로 표시
                value_str = '\n'.join([f"  - {item}" if not isinstance(item, dict) else f"  - {json.dumps(item, ensure_ascii=False)}" for item in value])
                info_lines.append(f"{key}:\n{value_str}\n")
            else:
                info_lines.append(f"{key}: {value}\n")

        info_text = '\n'.join(info_lines)
        self.character_info_viewer.insert(1.0, info_text)
        self.character_info_viewer.config(state=tk.DISABLED)

    def _update_images_display(self, character: dict):
        """
        이미지 목록 표시 업데이트
        """
        if not hasattr(self, 'images_tab_viewer_frame'):
            return

        # 기존 위젯 제거
        for widget in self.images_tab_viewer_frame.winfo_children():
            widget.destroy()

        prompts_obj = character.get('image_generation_prompts', {})
        
        # 프롬프트가 없으면 메시지 표시
        has_prompts = any(prompts_obj.get(f'prompt_{i}', '') for i in range(1, 8))
        if not has_prompts:
            # 프롬프트 1이 없고 기존 image_generation_prompt가 있는지 확인
            if not character.get('image_generation_prompt', ''):
                ttk.Label(
                    self.images_tab_viewer_frame,
                    text="이미지 프롬프트가 아직 생성되지 않았습니다.\n\n위의 '🖼️ 이미지 생성 (7개)' 버튼을 클릭하세요.",
                    font=("맑은 고딕", 11)
                ).pack(pady=20)
                return

        # 각 이미지 표시 (1~7)
        for img_num in range(1, 8):
            prompt_key = f"prompt_{img_num}"
            prompt_content = prompts_obj.get(prompt_key, '')
            
            # 프롬프트 1이 없고 기존 image_generation_prompt가 있으면 사용
            if img_num == 1 and not prompt_content:
                prompt_content = character.get('image_generation_prompt', '')
            
            if prompt_content:
                self._create_image_widget(img_num, prompt_content, character)

        # 새로 생성된 위젯들에 마우스 휠 바인딩 재적용
        self._rebind_mousewheel()

    def _create_image_widget(self, img_num: int, prompt_content: str, character: dict):
        """
        이미지 위젯 생성
        """
        image_title = IMAGE_TITLES.get(img_num, f"이미지 {img_num}")
        char_name = character.get('name', '알 수 없음')

        frame = ttk.LabelFrame(
            self.images_tab_viewer_frame,
            text=f"이미지 {img_num}: {image_title}",
            padding=15
        )
        frame.pack(fill=tk.X, padx=15, pady=10)

        # 제목
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(title_frame, text="제목:", font=("맑은 고딕", 10, "bold"), width=12).pack(side=tk.LEFT)
        ttk.Label(title_frame, text=image_title, font=("맑은 고딕", 10)).pack(side=tk.LEFT)

        # 이미지 프롬프트 영역
        prompt_frame = ttk.LabelFrame(frame, text="이미지 프롬프트", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(0, weight=1)

        # 프롬프트 텍스트 영역 (편집 가능)
        prompt_text = scrolledtext.ScrolledText(
            prompt_frame,
            width=80,
            height=15,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
            state=tk.NORMAL
        )
        prompt_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        prompt_text.insert(1.0, prompt_content)
        
        # 자동 저장을 위한 debounce 변수
        save_after_id = None
        
        def on_prompt_text_change(event=None):
            """프롬프트 텍스트 변경 시 자동 저장 (debounce)"""
            nonlocal save_after_id
            if save_after_id:
                self.frame.after_cancel(save_after_id)
            # 2초 후 자동 저장
            save_after_id = self.frame.after(2000, lambda: save_prompt(show_message=False))
        
        # 텍스트 변경 이벤트 바인딩
        prompt_text.bind('<KeyRelease>', on_prompt_text_change)

        # 버튼 영역 (프롬프트 아래)
        btn_frame = ttk.Frame(prompt_frame)
        btn_frame.grid(row=1, column=0, pady=(10, 0), sticky=(tk.W, tk.E))

        def load_from_file():
            """텍스트 파일에서 프롬프트 불러오기"""
            try:
                file_path = filedialog.askopenfilename(
                    title="이미지 프롬프트 텍스트 파일 선택",
                    filetypes=[
                        ("텍스트 파일", "*.txt"),
                        ("모든 파일", "*.*")
                    ]
                )
                
                if not file_path:
                    return
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_text = f.read().strip()
                
                if loaded_text:
                    # 프롬프트 영역에 삽입
                    prompt_text.delete(1.0, tk.END)
                    prompt_text.insert(1.0, loaded_text)
                    
                    # 인물 데이터에 저장
                    save_prompt()
                    
                    messagebox.showinfo("불러오기 완료", "파일에서 프롬프트를 불러왔습니다.")
                else:
                    messagebox.showwarning("경고", "파일이 비어있습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"파일 불러오기 중 오류 발생:\n{e}")

        def paste_from_clipboard():
            """클립보드에서 프롬프트 붙여넣기"""
            try:
                clipboard_text = self.frame.clipboard_get()
                
                if clipboard_text:
                    # 프롬프트 영역에 삽입
                    prompt_text.delete(1.0, tk.END)
                    prompt_text.insert(1.0, clipboard_text)
                    
                    # 인물 데이터에 저장
                    save_prompt()
                    
                    messagebox.showinfo("붙여넣기 완료", "클립보드에서 프롬프트를 붙여넣었습니다.")
                else:
                    messagebox.showwarning("경고", "클립보드에 텍스트가 없습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"클립보드 붙여넣기 중 오류 발생:\n{e}")

        def save_prompt(show_message=True):
            """프롬프트 저장"""
            try:
                # 프롬프트 텍스트 가져오기
                new_prompt_content = prompt_text.get(1.0, tk.END).strip()
                
                # 인물 데이터에 프롬프트 저장
                if 'image_generation_prompts' not in character:
                    character['image_generation_prompts'] = {}
                
                character['image_generation_prompts'][f'prompt_{img_num}'] = new_prompt_content
                
                # 첫 번째 프롬프트를 기본값으로도 설정
                if img_num == 1:
                    character['image_generation_prompt'] = new_prompt_content
                
                # 데이터 업데이트
                characters = self.project_data.get_characters()
                # 현재 인물 찾기 (이름으로 매칭)
                char_name = character.get('name', '')
                found = False
                for idx, char in enumerate(characters):
                    if char.get('name') == char_name:
                        characters[idx] = character
                        found = True
                        break
                
                if not found and hasattr(self, 'current_character_index') and self.current_character_index < len(characters):
                    characters[self.current_character_index] = character
                
                self.project_data.set_characters(characters)
                
                # 파일에 저장
                success = self.file_service.save_characters(characters)
                
                if show_message and success:
                    messagebox.showinfo("저장 완료", f"이미지 프롬프트가 저장되었습니다.\n(이미지 {img_num}: {image_title})")
                elif show_message and not success:
                    messagebox.showerror("저장 실패", "프롬프트 저장 중 오류가 발생했습니다.")
                
                return success
            except Exception as e:
                if show_message:
                    messagebox.showerror("오류", f"프롬프트 저장 중 오류 발생:\n{e}")
                print(f"[이미지 생성 탭] 프롬프트 저장 오류: {e}")
                return False

        def copy_prompt():
            """이미지 프롬프트를 클립보드에 복사"""
            try:
                current_text = prompt_text.get(1.0, tk.END).strip()
                if current_text:
                    self.frame.clipboard_clear()
                    self.frame.clipboard_append(current_text)
                    self.frame.update()
                    messagebox.showinfo("복사 완료", "이미지 프롬프트가 클립보드에 복사되었습니다.")
                else:
                    messagebox.showwarning("경고", "복사할 프롬프트가 없습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"클립보드 복사 중 오류 발생:\n{e}")

        # 파일에서 불러오기 버튼
        load_file_btn = ttk.Button(
            btn_frame,
            text="📂 파일에서 불러오기",
            command=load_from_file,
            width=20
        )
        load_file_btn.pack(side=tk.LEFT, padx=5)

        # 클립보드에서 붙여넣기 버튼
        paste_btn = ttk.Button(
            btn_frame,
            text="📋 클립보드에서 붙여넣기",
            command=paste_from_clipboard,
            width=22
        )
        paste_btn.pack(side=tk.LEFT, padx=5)

        # 저장 버튼
        save_btn = ttk.Button(
            btn_frame,
            text="💾 저장",
            command=save_prompt,
            width=15
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        # 복사 버튼
        copy_btn = ttk.Button(
            btn_frame,
            text="📋 복사",
            command=copy_prompt,
            width=15
        )
        copy_btn.pack(side=tk.LEFT, padx=5)
    
    def _rebind_mousewheel(self):
        """
        마우스 휠 이벤트 재바인딩
        """
        if not hasattr(self, 'images_tab_canvas') or not hasattr(self, 'images_tab_viewer_frame'):
            return

        canvas_images = self.images_tab_canvas

        def on_mousewheel_images(event):
            try:
                if hasattr(event, 'delta'):
                    # Windows
                    delta = event.delta
                    if delta > 0:
                        canvas_images.yview_scroll(-3, "units")
                    else:
                        canvas_images.yview_scroll(3, "units")
                elif hasattr(event, 'num'):
                    # Linux
                    if event.num == 4:
                        canvas_images.yview_scroll(-3, "units")
                    elif event.num == 5:
                        canvas_images.yview_scroll(3, "units")
            except Exception as e:
                print(f"마우스 휠 오류: {e}")
            return "break"

        def bind_mousewheel_to_widget(widget):
            if widget is None:
                return
            try:
                widget.bind("<MouseWheel>", on_mousewheel_images, add='+')
                widget.bind("<Button-4>", on_mousewheel_images, add='+')
                widget.bind("<Button-5>", on_mousewheel_images, add='+')
                for child in widget.winfo_children():
                    bind_mousewheel_to_widget(child)
            except:
                pass

        # Canvas에 직접 바인딩
        canvas_images.bind("<MouseWheel>", on_mousewheel_images, add='+')
        canvas_images.bind("<Button-4>", on_mousewheel_images, add='+')
        canvas_images.bind("<Button-5>", on_mousewheel_images, add='+')
        canvas_images.bind("<Enter>", lambda e: canvas_images.focus_set())

        # 새로 생성된 모든 위젯에 마우스 휠 바인딩
        bind_mousewheel_to_widget(self.images_tab_viewer_frame)

        # right_frame에도 바인딩
        if hasattr(self, 'images_tab_right_frame') and self.images_tab_right_frame is not None:
            right_frame = self.images_tab_right_frame
            right_frame.bind("<MouseWheel>", on_mousewheel_images, add='+')
            right_frame.bind("<Button-4>", on_mousewheel_images, add='+')
            right_frame.bind("<Button-5>", on_mousewheel_images, add='+')

        # paned_horizontal에도 바인딩
        if hasattr(self, 'images_tab_paned') and self.images_tab_paned is not None:
            paned = self.images_tab_paned
            paned.bind("<MouseWheel>", on_mousewheel_images, add='+')
            paned.bind("<Button-4>", on_mousewheel_images, add='+')
            paned.bind("<Button-5>", on_mousewheel_images, add='+')

    def _generate_current_character(self):
        """
        현재 선택된 인물의 이미지 생성
        """
        selected = self.character_var.get()
        if not selected:
            messagebox.showwarning("경고", "인물을 선택해주세요.")
            return

        # 선택된 인물 인덱스 추출
        try:
            char_index = int(selected.split(':')[0].replace('인물', '').strip()) - 1
        except:
            messagebox.showerror("오류", "인물 인덱스를 추출할 수 없습니다.")
            return

        # 인물 찾기
        characters = self.project_data.get_characters()
        if char_index < 0 or char_index >= len(characters):
            messagebox.showerror("오류", f"인물 인덱스 {char_index + 1}이 유효하지 않습니다.")
            return

        character = characters[char_index]
        
        # 현재 선택된 인물 저장 (이미지 업로드 시 사용)
        self.current_character = character
        self.current_character_index = char_index

        # 확인 대화상자
        char_name = character.get('name', '알 수 없음')
        result = messagebox.askyesno(
            "이미지 생성",
            f"{char_name}에 대한 7개의 이미지 프롬프트를 생성하시겠습니까?\n\n"
            f"각 이미지에는 Stable Diffusion 이미지 프롬프트가 생성됩니다.\n\n"
            f"이 작업은 시간이 걸릴 수 있습니다."
        )
        if not result:
            return

        # 이미지 생성 실행
        success = self._generate_images(char_index, character)

        # 생성 성공 시 화면 업데이트
        if success:
            self._on_character_selected()

    def _generate_all_characters(self):
        """
        모든 인물에 대해 이미지 생성
        """
        characters = self.project_data.get_characters()

        if not characters:
            messagebox.showwarning("경고", "인물이 없습니다.")
            return

        # 확인 대화상자
        result = messagebox.askyesno(
            "모든 인물 이미지 생성",
            f"총 {len(characters)}명의 인물에 대해 각각 7개의 이미지 프롬프트를 생성하시겠습니까?\n\n"
            f"각 인물마다 3초씩 딜레이가 있으며, 전체 작업은 시간이 오래 걸릴 수 있습니다.\n\n"
            f"진행 중에는 창을 닫지 마세요."
        )
        if not result:
            return

        # 백그라운드 스레드에서 순차적으로 처리
        thread = threading.Thread(
            target=self._generate_all_images_sequential,
            args=(characters,),
            daemon=True
        )
        thread.start()

    def _generate_all_images_sequential(self, characters):
        """
        모든 인물에 대해 순차적으로 이미지 생성
        """
        total = len(characters)
        success_count = 0
        fail_count = 0

        for idx, character in enumerate(characters, 1):
            char_name = character.get('name', '알 수 없음')

            # 이미지 생성
            try:
                success = self._generate_images(idx - 1, character, show_message=False)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                error_msg = str(e)
                print(f"인물 {char_name} 이미지 생성 오류: {error_msg}")
                # GUI 스레드에서 오류 메시지 표시
                def show_error():
                    messagebox.showerror(
                        "이미지 생성 오류",
                        f"인물 '{char_name}'의 이미지 생성 중 오류가 발생했습니다.\n\n"
                        f"오류: {error_msg}\n\n"
                        f"나머지 인물들은 계속 처리됩니다."
                    )
                self.frame.after(0, show_error)

            # 마지막 인물이 아니면 3초 딜레이
            if idx < total:
                time.sleep(3)

        # 완료 메시지
        def show_completion():
            messagebox.showinfo(
                "완료",
                f"모든 인물의 이미지 생성이 완료되었습니다.\n\n"
                f"성공: {success_count}명\n"
                f"실패: {fail_count}명"
            )
            # 화면 업데이트
            if hasattr(self, 'character_var') and self.character_var.get():
                self._on_character_selected()

        # GUI 업데이트는 메인 스레드에서
        self.frame.after(0, show_completion)

    def _generate_images(self, char_index: int, character: dict, show_message: bool = True) -> bool:
        """
        인물 이미지 프롬프트 생성 (내부 함수)
        """
        # 시놉시스 정보
        synopsis = self.project_data.get_synopsis()

        # 나이 추출 및 Youth age 계산
        char_age_raw = character.get('age', 35)
        if isinstance(char_age_raw, str):
            try:
                char_age = int(char_age_raw)
            except:
                char_age = 35
        else:
            char_age = int(char_age_raw) if char_age_raw else 35

        # Youth age 계산 (나이대별 차감 규칙, 최소 25세)
        if char_age >= 60:
            age_deduction = 20
        elif char_age >= 50:
            age_deduction = 15
        elif char_age >= 40:
            age_deduction = 10
        elif char_age >= 30:
            age_deduction = 7
        else:
            age_deduction = 0
        visual_age = max(25, char_age - age_deduction)

        # LLM 호출
        try:
            prompts = self.content_generator.generate_image_prompts(character, synopsis, visual_age)

            if not prompts:
                if show_message:
                    char_name = character.get('name', '알 수 없음')
                    messagebox.showerror(
                        "이미지 프롬프트 생성 실패",
                        f"{char_name}의 이미지 프롬프트 생성에 실패했습니다.\n\n"
                        f"가능한 원인:\n"
                        f"- API 연결 실패 (인터넷 연결 확인)\n"
                        f"- API 키 미설정 또는 잘못된 키\n"
                        f"- API 제공자 설정 오류\n\n"
                        f"설정 메뉴에서 API 연결을 확인해주세요."
                    )
                return False

            # 인물 데이터에 프롬프트 저장
            if 'image_generation_prompts' not in character:
                character['image_generation_prompts'] = {}

            # 각 프롬프트 저장
            character['image_generation_prompts']['prompt_1'] = prompts.get("full_body_shot", "")
            character['image_generation_prompts']['prompt_2'] = prompts.get("side_profile_full_body_shot", "")
            character['image_generation_prompts']['prompt_3'] = prompts.get("diagonal_side_profile_full_body_shot", "")
            character['image_generation_prompts']['prompt_4'] = prompts.get("portrait", "")
            character['image_generation_prompts']['prompt_5'] = prompts.get("side_profile", "")
            character['image_generation_prompts']['prompt_6'] = prompts.get("action", "")
            character['image_generation_prompts']['prompt_7'] = prompts.get("natural_background", "")

            # 첫 번째 프롬프트를 기본값으로도 설정
            if prompts.get("full_body_shot"):
                character['image_generation_prompt'] = prompts.get("full_body_shot")

            # 데이터 업데이트
            characters = self.project_data.get_characters()
            characters[char_index] = character
            self.project_data.set_characters(characters)

            # 파일에 즉시 자동 저장
            try:
                self.file_service.save_characters(characters)
            except Exception as save_error:
                print(f"경고: 이미지 프롬프트는 생성되었으나 저장 중 오류 발생: {save_error}")

            if show_message:
                char_name = character.get('name', '알 수 없음')
                messagebox.showinfo("완료", f"{char_name}의 이미지 프롬프트가 생성되고 자동 저장되었습니다.\n생성된 이미지: 7개")

            return True

        except Exception as e:
            error_msg = str(e)
            if show_message:
                char_name = character.get('name', '알 수 없음')
                messagebox.showerror(
                    "이미지 프롬프트 생성 오류",
                    f"{char_name}의 이미지 프롬프트 생성 중 오류가 발생했습니다.\n\n"
                    f"오류 내용:\n{error_msg}\n\n"
                    f"해결 방법:\n"
                    f"1. 설정 메뉴에서 API 키와 모델을 확인하세요\n"
                    f"2. 인터넷 연결을 확인하세요\n"
                    f"3. API 제공자(Claude/Gemini/OpenAI) 설정을 확인하세요"
                )
            print(f"이미지 프롬프트 생성 상세 오류 ({char_name}): {error_msg}")
            return False

    def save(self) -> bool:
        """
        데이터 저장
        이미지 생성 탭은 자동 저장되므로 별도 저장 불필요
        """
        return True  # 자동 저장됨

