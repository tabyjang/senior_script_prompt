"""
복사/붙여넣기 탭
구글 스프레드시트에 붙여넣기 가능한 TSV 형식으로 데이터를 제공합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from .base_tab import BaseTab


class CopyPasteTab(BaseTab):
    """복사/붙여넣기 탭 클래스"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        self.data_type_var = None
        self.data_text = None
        self.current_data_type = "scenes"
        
        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "복사/붙여넣기"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # 상단: 데이터 타입 선택
        top_frame = ttk.Frame(self.frame, padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(
            top_frame,
            text="데이터 타입:",
            font=("맑은 고딕", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)

        self.data_type_var = tk.StringVar(value="scenes")
        scenes_radio = ttk.Radiobutton(
            top_frame,
            text="장면 이미지 프롬프트",
            variable=self.data_type_var,
            value="scenes",
            command=self._on_data_type_changed
        )
        scenes_radio.pack(side=tk.LEFT, padx=10)

        characters_radio = ttk.Radiobutton(
            top_frame,
            text="인물 이미지 프롬프트",
            variable=self.data_type_var,
            value="characters",
            command=self._on_data_type_changed
        )
        characters_radio.pack(side=tk.LEFT, padx=10)

        # 오른쪽 버튼 영역
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT, padx=10)

        # 새로고침 버튼
        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 새로고침",
            command=self._refresh_data,
            width=15
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 전체 복사 버튼
        copy_btn = ttk.Button(
            button_frame,
            text="📋 전체 복사",
            command=self._copy_to_clipboard,
            width=15
        )
        copy_btn.pack(side=tk.LEFT, padx=5)

        # 중간: TSV 데이터 표시 영역
        data_frame = ttk.LabelFrame(self.frame, text="구글 스프레드시트 붙여넣기용 데이터 (TSV 형식)", padding=10)
        data_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)

        self.data_text = scrolledtext.ScrolledText(
            data_frame,
            width=120,
            height=40,
            wrap=tk.NONE,  # 줄바꿈 없음 (TSV 형식 유지)
            font=("Consolas", 10)
        )
        self.data_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 하단: 안내 메시지
        info_frame = ttk.Frame(self.frame, padding="10")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        info_label = ttk.Label(
            info_frame,
            text="💡 사용 방법: 위의 데이터를 복사하여 구글 스프레드시트에 붙여넣기(Ctrl+V)하면 자동으로 열이 나뉩니다.",
            font=("맑은 고딕", 9),
            foreground="gray"
        )
        info_label.pack()

        # 초기 데이터 로드
        self._on_data_type_changed()

    def _on_data_type_changed(self):
        """데이터 타입 변경 시 호출"""
        self.current_data_type = self.data_type_var.get()
        self.update_display()

    def update_display(self):
        """화면 업데이트"""
        if self.current_data_type == "scenes":
            tsv_data = self._format_scenes_to_tsv()
        else:
            tsv_data = self._format_characters_to_tsv()

        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(1.0, tsv_data)

    def _format_scenes_to_tsv(self) -> str:
        """
        장면 이미지 프롬프트를 TSV 형식으로 변환
        형식: 챕터번호\t장면번호\t장면제목\t이미지프롬프트
        """
        chapters = self.project_data.get_chapters()
        
        if not chapters:
            return "장면 데이터가 없습니다."

        # 헤더
        lines = ["챕터번호\t장면번호\t장면제목\t이미지프롬프트"]

        # 각 챕터의 각 장면
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number', '')
            scenes = chapter.get('scenes', [])
            
            for scene in scenes:
                scene_num = scene.get('scene_number', '')
                scene_title = scene.get('title', '')
                image_prompt = scene.get('image_prompt', '')
                
                # TSV 형식: 탭으로 구분, 줄바꿈 제거
                scene_title_clean = scene_title.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                image_prompt_clean = image_prompt.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                
                line = f"{chapter_num}\t{scene_num}\t{scene_title_clean}\t{image_prompt_clean}"
                lines.append(line)

        return '\n'.join(lines)

    def _format_characters_to_tsv(self) -> str:
        """
        인물 이미지 프롬프트를 TSV 형식으로 변환
        형식: 인물이름\t프롬프트번호\t프롬프트내용
        """
        characters = self.project_data.get_characters()
        
        if not characters:
            return "인물 데이터가 없습니다."

        # 헤더
        lines = ["인물이름\t프롬프트번호\t프롬프트내용"]

        # 각 인물의 각 프롬프트
        for char in characters:
            char_name = char.get('name', '알 수 없음')
            prompts_obj = char.get('image_generation_prompts', {})
            
            # 프롬프트 1~7
            for prompt_num in range(1, 8):
                prompt_key = f"prompt_{prompt_num}"
                prompt_content = prompts_obj.get(prompt_key, '')
                
                # 프롬프트 1이 없고 기존 image_generation_prompt가 있으면 사용
                if prompt_num == 1 and not prompt_content:
                    prompt_content = char.get('image_generation_prompt', '')
                
                if prompt_content:
                    # JSON 형식의 중괄호 제거
                    prompt_clean = self._remove_json_braces(prompt_content)
                    # TSV 형식: 탭으로 구분, 줄바꿈 제거
                    prompt_clean = prompt_clean.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                    line = f"{char_name}\t{prompt_num}\t{prompt_clean}"
                    lines.append(line)

        return '\n'.join(lines)

    def _refresh_data(self):
        """데이터 새로고침"""
        try:
            # 데이터 다시 로드
            self.update_display()
            messagebox.showinfo("새로고침 완료", "데이터가 새로고침되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"데이터 새로고침 중 오류 발생:\n{e}")

    def _remove_json_braces(self, prompt_content: str) -> str:
        """
        JSON 형식의 프롬프트에서 중괄호를 제거하고 내용만 추출
        예: {"character": "...", "combined": "..."} -> combined 내용만
        """
        if not prompt_content or not prompt_content.strip():
            return prompt_content
        
        content_stripped = prompt_content.strip()
        
        # 1차 시도: 직접 JSON 파싱 (중괄호로 시작/끝나는 경우)
        if content_stripped.startswith('{') and content_stripped.endswith('}'):
            try:
                prompt_json = json.loads(content_stripped)
                return self._extract_content_from_json(prompt_json)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # 2차 시도: 이스케이프된 JSON 문자열 (예: "{\"character\": ...}")
        if content_stripped.startswith('"') and content_stripped.endswith('"'):
            try:
                # 이스케이프 제거 후 파싱
                unescaped = json.loads(content_stripped)  # 이스케이프된 문자열을 파싱
                if isinstance(unescaped, str):
                    # 파싱 결과가 문자열이면 다시 JSON 파싱 시도
                    if unescaped.strip().startswith('{') and unescaped.strip().endswith('}'):
                        prompt_json = json.loads(unescaped)
                        return self._extract_content_from_json(prompt_json)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        
        # 3차 시도: 중괄호가 포함된 문자열에서 JSON 추출 시도
        # 첫 번째 { 와 마지막 } 찾기
        first_brace = content_stripped.find('{')
        last_brace = content_stripped.rfind('}')
        if first_brace >= 0 and last_brace > first_brace:
            try:
                json_str = content_stripped[first_brace:last_brace + 1]
                prompt_json = json.loads(json_str)
                return self._extract_content_from_json(prompt_json)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # 모든 시도 실패 시 원본 반환
        return prompt_content
    
    def _extract_content_from_json(self, prompt_json: dict) -> str:
        """
        JSON 딕셔너리에서 내용 추출
        combined 필드 우선, 없으면 모든 필드 조합
        """
        if not isinstance(prompt_json, dict):
            return str(prompt_json)
        
        # combined 필드가 있으면 그것만 사용
        if 'combined' in prompt_json and prompt_json['combined']:
            combined = prompt_json['combined']
            # combined가 문자열이면 그대로 반환
            if isinstance(combined, str):
                return combined
            # combined가 다른 타입이면 문자열로 변환
            return str(combined)
        
        # combined가 없으면 모든 필드를 조합
        parts = []
        for key, value in prompt_json.items():
            if key != 'combined' and value:  # combined는 이미 처리했으므로 제외
                if isinstance(value, str):
                    parts.append(value)
                else:
                    parts.append(str(value))
        
        if parts:
            return ' '.join(parts)
        
        # 내용이 없으면 빈 문자열 반환
        return ''

    def _copy_to_clipboard(self):
        """전체 데이터를 클립보드에 복사"""
        try:
            data = self.data_text.get(1.0, tk.END).strip()
            
            if not data or data == "장면 데이터가 없습니다." or data == "인물 데이터가 없습니다.":
                messagebox.showwarning("경고", "복사할 데이터가 없습니다.")
                return

            # 클립보드에 복사
            self.frame.clipboard_clear()
            self.frame.clipboard_append(data)
            self.frame.update()  # 클립보드 업데이트 확실히 하기

            data_type_name = "장면 이미지 프롬프트" if self.current_data_type == "scenes" else "인물 이미지 프롬프트"
            messagebox.showinfo(
                "복사 완료",
                f"{data_type_name} 데이터가 클립보드에 복사되었습니다.\n\n"
                f"구글 스프레드시트에서 Ctrl+V로 붙여넣기 하세요."
            )
        except Exception as e:
            messagebox.showerror("오류", f"클립보드 복사 중 오류 발생:\n{e}")

    def save(self) -> bool:
        """
        데이터 저장
        이 탭은 읽기 전용이므로 저장 불필요
        """
        return True

