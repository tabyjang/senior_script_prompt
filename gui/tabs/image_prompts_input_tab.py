"""
이미지 프롬프트 입력 탭
사용자가 텍스트 형식으로 이미지 프롬프트를 입력하고 파싱하여 저장합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
import json
from typing import Dict, Any, List
from .base_tab import BaseTab
from utils.json_utils import format_json, safe_json_loads, extract_json_from_text


class ImagePromptsInputTab(BaseTab):
    """이미지 프롬프트 입력 탭 클래스"""

    def get_tab_name(self) -> str:
        return "이미지 프롬프트 입력"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # 좌우 분할
        paned_horizontal = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 왼쪽: 텍스트 입력 영역
        input_frame = ttk.LabelFrame(paned_horizontal, text="이미지 프롬프트 텍스트 입력", padding=10)
        paned_horizontal.add(input_frame, weight=1)
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)

        # 버튼 영역 (상단)
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))

        parse_btn = ttk.Button(
            button_frame,
            text="📝 파싱 및 저장",
            command=self._parse_and_save,
            width=20
        )
        parse_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ 지우기",
            command=self._clear_input,
            width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # 텍스트 입력 영역
        self.text_input = scrolledtext.ScrolledText(
            input_frame,
            width=60,
            height=40,
            wrap=tk.WORD,
            font=("맑은 고딕", 11)
        )
        self.text_input.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 실시간 파싱을 위한 이벤트 바인딩
        self.text_input.bind('<KeyRelease>', self._on_text_change)

        # 오른쪽: 파싱 결과 미리보기 + 복사 가능한 combined 영역
        result_frame = ttk.LabelFrame(paned_horizontal, text="파싱 결과 미리보기", padding=10)
        paned_horizontal.add(result_frame, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # 상하 분할 (파싱 결과 + combined 복사 영역)
        result_paned = ttk.PanedWindow(result_frame, orient=tk.VERTICAL)
        result_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # 상단: 파싱 결과 JSON 표시
        parsed_json_frame = ttk.LabelFrame(result_paned, text="파싱 결과 (JSON)", padding=5)
        result_paned.add(parsed_json_frame, weight=1)
        parsed_json_frame.columnconfigure(0, weight=1)
        parsed_json_frame.rowconfigure(0, weight=1)

        self.parsed_result_text = scrolledtext.ScrolledText(
            parsed_json_frame,
            width=60,
            height=20,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.parsed_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 하단: Combined 복사 영역
        combined_frame = ttk.LabelFrame(result_paned, text="Combined 프롬프트 (복사 가능)", padding=5)
        result_paned.add(combined_frame, weight=1)
        combined_frame.columnconfigure(0, weight=1)
        combined_frame.rowconfigure(1, weight=1)

        # 복사 버튼
        copy_btn_frame = ttk.Frame(combined_frame)
        copy_btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.copy_combined_btn = ttk.Button(
            copy_btn_frame,
            text="📋 Combined 복사",
            command=self._copy_combined,
            width=20,
            state=tk.DISABLED
        )
        self.copy_combined_btn.pack(side=tk.LEFT, padx=5)

        # Combined 텍스트 영역 (읽기 전용이지만 선택 가능)
        self.combined_text = scrolledtext.ScrolledText(
            combined_frame,
            width=60,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.combined_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def update_display(self):
        """화면 업데이트"""
        pass

    def _clear_input(self):
        """입력 영역 지우기"""
        self.text_input.delete(1.0, tk.END)
        self.parsed_result_text.config(state=tk.NORMAL)
        self.parsed_result_text.delete(1.0, tk.END)
        self.parsed_result_text.config(state=tk.DISABLED)
        self.combined_text.config(state=tk.NORMAL)
        self.combined_text.delete(1.0, tk.END)
        self.combined_text.config(state=tk.DISABLED)
        self.copy_combined_btn.config(state=tk.DISABLED)

    def _on_text_change(self, event=None):
        """입력 텍스트 변경 시 실시간 파싱"""
        # 입력이 너무 빠르면 성능 문제가 있을 수 있으므로 약간의 지연 후 파싱
        if hasattr(self, '_parsing_after_id'):
            self.frame.after_cancel(self._parsing_after_id)

        # 1000ms 후에 파싱 실행 (debounce) - 자동 저장을 위해 조금 더 긴 시간 설정
        self._parsing_after_id = self.frame.after(1000, self._perform_realtime_parsing)

    def _perform_realtime_parsing(self):
        """실제 실시간 파싱 수행 및 자동 저장"""
        text = self.text_input.get(1.0, tk.END).strip()

        if not text:
            # 입력이 비어있으면 오른쪽 칸도 비우기
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            self.parsed_result_text.config(state=tk.DISABLED)
            self.combined_text.config(state=tk.NORMAL)
            self.combined_text.delete(1.0, tk.END)
            self.combined_text.config(state=tk.DISABLED)
            self.copy_combined_btn.config(state=tk.DISABLED)
            return

        try:
            # 파싱 실행
            parsed_data = self._parse_image_prompts(text)

            # 오른쪽 칸에 JSON 형식으로 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            
            # Combined 텍스트 영역 업데이트
            self.combined_text.config(state=tk.NORMAL)
            self.combined_text.delete(1.0, tk.END)
            
            if parsed_data:
                json_str = format_json(parsed_data)
                self.parsed_result_text.insert(1.0, json_str)

                # Combined 내용 수집 및 표시
                combined_texts = []
                for item in parsed_data:
                    char_name = item.get('character_name', '')
                    prompt_num = item.get('prompt_number', 0)
                    prompt_json_str = item.get('prompt_json', '')
                    
                    if prompt_json_str:
                        try:
                            prompt_json = safe_json_loads(prompt_json_str)
                            if prompt_json and 'combined' in prompt_json:
                                combined_texts.append(f"=== {char_name} - 프롬프트 {prompt_num} (Combined) ===\n")
                                combined_texts.append(prompt_json['combined'])
                                combined_texts.append("\n\n")
                        except:
                            pass
                
                if combined_texts:
                    combined_content = ''.join(combined_texts)
                    self.combined_text.insert(1.0, combined_content)
                    self.copy_combined_btn.config(state=tk.NORMAL)
                else:
                    self.combined_text.insert(1.0, "Combined 내용이 없습니다.")
                    self.copy_combined_btn.config(state=tk.DISABLED)

                # 파싱이 성공하면 자동 저장
                try:
                    # 실시간 자동 저장 중에는 인물 미매칭 등의 경고 팝업을 띄우지 않음
                    self._merge_and_save_image_prompts(parsed_data, show_warnings=False)
                    # 저장 성공 표시 (간단한 인디케이터)
                    self.parsed_result_text.insert(tk.END, "\n\n[자동 저장 완료]")
                except Exception as save_error:
                    # 저장 실패 시 오류 표시
                    self.parsed_result_text.insert(tk.END, f"\n\n[자동 저장 실패: {str(save_error)}]")
            else:
                self.parsed_result_text.insert(1.0, "파싱 결과가 없습니다.\n\n입력 형식을 확인해주세요.")
                self.combined_text.insert(1.0, "파싱 결과가 없습니다.")
                self.copy_combined_btn.config(state=tk.DISABLED)
            
            self.parsed_result_text.config(state=tk.DISABLED)
            self.combined_text.config(state=tk.DISABLED)
        except Exception as e:
            # 오류 발생 시 오류 메시지 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            self.parsed_result_text.insert(1.0, f"파싱 오류:\n{str(e)}")
            self.parsed_result_text.config(state=tk.DISABLED)
            self.combined_text.config(state=tk.NORMAL)
            self.combined_text.delete(1.0, tk.END)
            self.combined_text.insert(1.0, f"파싱 오류 발생")
            self.combined_text.config(state=tk.DISABLED)
            self.copy_combined_btn.config(state=tk.DISABLED)

    def _copy_combined(self):
        """Combined 내용을 클립보드에 복사"""
        combined_content = self.combined_text.get(1.0, tk.END).strip()
        if combined_content:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(combined_content)
            messagebox.showinfo("복사 완료", "Combined 프롬프트가 클립보드에 복사되었습니다.")
        else:
            messagebox.showwarning("경고", "복사할 내용이 없습니다.")

    def _parse_and_save(self):
        """텍스트를 파싱하고 저장"""
        text = self.text_input.get(1.0, tk.END).strip()

        if not text:
            messagebox.showwarning("경고", "입력된 텍스트가 없습니다.")
            return

        try:
            # 텍스트 파싱
            image_prompts = self._parse_image_prompts(text)

            if not image_prompts:
                messagebox.showerror("오류", "파싱에 실패했습니다. 텍스트 형식을 확인해주세요.")
                return

            # 인물 데이터 병합 및 저장
            self._merge_and_save_image_prompts(image_prompts)

            # 파싱 결과 오른쪽 칸에 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            json_str = format_json(image_prompts)
            self.parsed_result_text.insert(1.0, json_str)
            self.parsed_result_text.config(state=tk.DISABLED)

            # Combined 내용 표시
            combined_texts = []
            for item in image_prompts:
                char_name = item.get('character_name', '')
                prompt_num = item.get('prompt_number', 0)
                prompt_json_str = item.get('prompt_json', '')
                
                if prompt_json_str:
                    try:
                        prompt_json = safe_json_loads(prompt_json_str)
                        if prompt_json and 'combined' in prompt_json:
                            combined_texts.append(f"=== {char_name} - 프롬프트 {prompt_num} (Combined) ===\n")
                            combined_texts.append(prompt_json['combined'])
                            combined_texts.append("\n\n")
                    except:
                        pass
            
            self.combined_text.config(state=tk.NORMAL)
            self.combined_text.delete(1.0, tk.END)
            if combined_texts:
                combined_content = ''.join(combined_texts)
                self.combined_text.insert(1.0, combined_content)
                self.copy_combined_btn.config(state=tk.NORMAL)
            else:
                self.combined_text.insert(1.0, "Combined 내용이 없습니다.")
                self.copy_combined_btn.config(state=tk.DISABLED)
            self.combined_text.config(state=tk.DISABLED)

            messagebox.showinfo(
                "완료",
                f"이미지 프롬프트가 파싱되어 저장되었습니다.\n\n"
                f"처리된 프롬프트 수: {len(image_prompts)}개\n\n"
                f"참고: 입력 시 자동 저장도 작동합니다.\n\n"
                f"확인 방법:\n"
                f"1. 오른쪽 '파싱 결과 미리보기'에서 JSON 형식 확인\n"
                f"2. 'Combined 프롬프트' 영역에서 복사 가능한 내용 확인\n"
                f"3. 사이드바의 '이미지 프롬프트' 탭을 클릭하여 저장된 프롬프트 확인"
            )

        except Exception as e:
            messagebox.showerror("오류", f"파싱 중 오류가 발생했습니다:\n{e}")
            import traceback
            traceback.print_exc()

    def _parse_image_prompts(self, text: str) -> List[Dict[str, Any]]:
        """
        텍스트를 파싱하여 이미지 프롬프트 정보 추출

        지원 형식 1) (신규) 인물별 8구도 직접 입력 형식:
        1. 김태산 (Main_Male)
        보정 나이: 60세 - 18세 = 42세
        핵심 키워드: ...
        1. 정면 전신샷 "character": "...", "clothing": "...", "pose": "...", "background": "...", "situation": "...", "combined": "..."
        ...
        8. 감동스러운 얼굴 "character": "...", ...

        지원 형식 2) (기존) 인물/프롬프트 + JSON 블록 형식:
        인물1
        프롬프트 1 (전신샷)
        { ... }

        Args:
            text: 입력된 텍스트

        Returns:
            이미지 프롬프트 정보 리스트
        """
        try:
            # 0) JSON 배열 포맷 파싱 시도 (사용자 제공 포맷)
            json_list_parsed = self._parse_image_prompts_json_list(text)
            if json_list_parsed:
                return json_list_parsed

            # 1) 신규 포맷(인물 헤더 + 8구도 라인) 우선 파싱 시도
            direct_parsed = self._parse_image_prompts_direct_8shot(text)
            if direct_parsed:
                return direct_parsed

            # 2) 기존 포맷 파싱 (하위호환)
            image_prompts: List[Dict[str, Any]] = []

            # 인물 블록으로 분할 (인물1, 인물2, ... 또는 인물 1, 인물 2, ...)
            character_pattern = r'인물\s*(\d+)'
            character_blocks = re.split(f'(?={character_pattern})', text, flags=re.IGNORECASE)

            for block in character_blocks:
                block = block.strip()
                if not block:
                    continue

                # 인물 번호 추출
                char_num_match = re.search(character_pattern, block, re.IGNORECASE)
                if not char_num_match:
                    continue

                char_number = int(char_num_match.group(1))

                # 인물 이름 찾기 (파일에서 로드한 인물 정보 사용)
                characters = self.file_service.load_characters()
                char_name = None
                if char_number > 0 and char_number <= len(characters):
                    char_name = characters[char_number - 1].get('name', f'인물{char_number}')
                else:
                    char_name = f'인물{char_number}'

                # 프롬프트 블록 찾기 (프롬프트 1, 프롬프트 2, ... 또는 프롬프트1, 프롬프트2, ...)
                prompt_pattern = r'프롬프트\s*(\d+)'
                prompt_blocks = re.split(f'(?={prompt_pattern})', block, flags=re.IGNORECASE)

                for prompt_block in prompt_blocks:
                    prompt_block = prompt_block.strip()
                    if not prompt_block:
                        continue

                    # 프롬프트 번호 추출
                    prompt_num_match = re.search(prompt_pattern, prompt_block, re.IGNORECASE)
                    if not prompt_num_match:
                        continue

                    prompt_number = int(prompt_num_match.group(1))

                    # 프롬프트 번호 유효성 검사 (1~12)
                    if prompt_number < 1 or prompt_number > 12:
                        continue

                    # JSON 내용 추출 (중괄호로 시작하고 끝나는 JSON 블록)
                    json_match = re.search(r'\{[\s\S]*\}', prompt_block, re.MULTILINE)
                    if json_match:
                        json_str = json_match.group(0).strip()
                        
                        # JSON 유효성 검사
                        try:
                            prompt_json = safe_json_loads(json_str)
                            if prompt_json:
                                # 프롬프트 정보 딕셔너리 생성
                                prompt_info = {
                                    "character_name": char_name,
                                    "character_number": char_number,
                                    "prompt_number": prompt_number,
                                    "prompt_json": json_str  # JSON 문자열로 저장
                                }
                                image_prompts.append(prompt_info)
                                print(f"[파싱] {char_name} - 프롬프트 {prompt_number} 파싱 완료")
                        except Exception as json_error:
                            print(f"[파싱 오류] {char_name} - 프롬프트 {prompt_number}: JSON 파싱 실패 - {json_error}")
                            continue

            return image_prompts

        except Exception as e:
            raise Exception(f"이미지 프롬프트 파싱 오류: {e}")

    def _parse_image_prompts_json_list(self, text: str) -> List[Dict[str, Any]]:
        """
        (추가 지원) JSON 배열 기반 입력 포맷 파싱

        예:
        [
          {
            "character_name": "김태산",
            "prompt_number": 1,
            "prompt": { "character": "...", "clothing": "...", ... }
          }
        ]

        결과는 기존 저장 호환 포맷으로 반환:
        [{"character_name": str, "prompt_number": int, "prompt_json": str}, ...]
        """
        if not text or not text.strip():
            return []

        data = safe_json_loads(text)
        if not isinstance(data, list):
            return []

        results: List[Dict[str, Any]] = []
        any_found = False

        for item in data:
            if not isinstance(item, dict):
                continue
            char_name = (item.get("character_name") or "").strip()
            prompt_number = item.get("prompt_number")
            prompt_obj = item.get("prompt")

            if not char_name:
                continue
            if not isinstance(prompt_number, int) or prompt_number < 1 or prompt_number > 12:
                continue
            if not isinstance(prompt_obj, dict):
                continue

            # combined 자동 생성 (없을 때만)
            combined = str(prompt_obj.get("combined", "") or "").strip()
            if not combined:
                parts = []
                for k in ["character", "clothing", "pose", "background", "situation"]:
                    v = prompt_obj.get(k, "")
                    if isinstance(v, str) and v.strip():
                        parts.append(v.strip())
                prompt_obj["combined"] = " ".join(parts).strip()

            prompt_json_str = json.dumps(prompt_obj, ensure_ascii=False)
            results.append(
                {
                    "character_name": char_name,
                    "prompt_number": prompt_number,
                    "prompt_json": prompt_json_str,
                }
            )
            any_found = True

        if not any_found:
            return []

        # 정렬: 인물명 -> 프롬프트 번호
        results.sort(key=lambda x: (x.get("character_name", ""), x.get("prompt_number", 0)))
        return results

    def _parse_image_prompts_direct_8shot(self, text: str) -> List[Dict[str, Any]]:
        """
        (신규) 인물별 8구도 직접 입력 텍스트 파싱

        - 인물 헤더: '1. 김태산 (Main_Male)' 형태 (단, '"character":' 포함 라인은 제외)
        - 구도 라인: '1. 정면 전신샷 "character": "...", "clothing": "...", ...' 형태
        - 각 구도는 prompt_number 1~8로 저장
        - prompt_json은 캐릭터 JSON의 image_generation_prompts 값과 동일하게 'JSON 문자열'로 저장
        """
        # 전처리
        if not text or not text.strip():
            return []

        normalized = text.replace('\r\n', '\n').replace('\r', '\n')
        lines = normalized.split('\n')

        def is_character_header_line(line: str) -> bool:
            s = (line or "").strip()
            if not s:
                return False
            if '"character"' in s or '"character":' in s:
                return False
            # 예: "1. 김태산 (Main_Male)" 또는 "1. 김태산"
            return re.match(r'^\s*\d+\.\s+.+$', s) is not None

        def is_shot_start_line(line: str) -> bool:
            s = (line or "")
            # 예: '1. 정면 전신샷 "character": "...", ...' 형태
            return re.match(r'^\s*\d+\.\s*(.*?)\s+"character"\s*:', s) is not None

        def parse_quoted_value(raw: str) -> str:
            # raw는 따옴표 내부 콘텐츠(이스케이프 포함 가능)
            try:
                return json.loads(f"\"{raw}\"")
            except Exception:
                return raw

        # key-value 추출 (quoted string)
        kv_re = re.compile(
            r'"(?P<key>character|clothing|pose|background|situation|combined)"\s*:\s*"(?P<value>(?:\\.|[^"\\])*)"',
            re.IGNORECASE
        )

        results: List[Dict[str, Any]] = []
        current_character_name: str | None = None
        current_character_key: str | None = None
        current_character_index = 0  # 입력 등장 순서(1부터)
        current_age_correction: Dict[str, int] | None = None
        current_keywords: List[str] | None = None

        i = 0
        any_detected = False
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # 인물 헤더
            if is_character_header_line(line) and not is_shot_start_line(line):
                m = re.match(r'^\s*(\d+)\.\s*(.+?)(?:\s*\(([^)]+)\))?\s*$', line)
                if m:
                    current_character_index = int(m.group(1))
                    current_character_name = (m.group(2) or "").strip()
                    current_character_key = (m.group(3) or "").strip() if m.group(3) else None
                    current_age_correction = None
                    current_keywords = None
                    any_detected = True
                i += 1
                continue

            # 메타: 보정 나이
            if current_character_name and ('보정 나이' in line):
                nums = [int(x) for x in re.findall(r'\d+', line)]
                if len(nums) >= 3:
                    current_age_correction = {"original": nums[0], "target": nums[1], "result": nums[2]}
                i += 1
                continue

            # 메타: 핵심 키워드
            if current_character_name and line.startswith('핵심 키워드'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    kws = [p.strip() for p in parts[1].split(',') if p.strip()]
                    current_keywords = kws
                i += 1
                continue

            # 구도 라인 (prompt)
            if current_character_name and is_shot_start_line(line):
                # 멀티라인(다음 줄에 "clothing": ... 같은 조각이 붙는 케이스) 대비로 블록 수집
                raw_block = line
                j = i + 1
                while j < len(lines):
                    nxt = lines[j].strip()
                    if not nxt:
                        j += 1
                        continue
                    if is_character_header_line(nxt) and not is_shot_start_line(nxt):
                        break
                    if is_shot_start_line(nxt):
                        break
                    # 키-값 조각 라인만 이어붙이기
                    if '"character"' in nxt or '"clothing"' in nxt or '"pose"' in nxt or '"background"' in nxt or '"situation"' in nxt or '"combined"' in nxt:
                        raw_block += " " + nxt
                        j += 1
                        continue
                    # 그 외 라인은 구도 블록에 포함하지 않음
                    break

                # 번호/구도명 추출
                m = re.match(r'^\s*(\d+)\.\s*(.*?)\s+"character"\s*:\s*', raw_block)
                if m:
                    prompt_number = int(m.group(1))
                    shot_name = (m.group(2) or "").strip()
                    if 1 <= prompt_number <= 8:
                        prompt_dict: Dict[str, Any] = {
                            "shot_name": shot_name
                        }

                        # key-value 추출
                        for kv in kv_re.finditer(raw_block):
                            key = (kv.group('key') or '').lower()
                            value_raw = kv.group('value') or ''
                            prompt_dict[key] = parse_quoted_value(value_raw)

                        # combined 자동 생성 (없을 때만)
                        combined = str(prompt_dict.get('combined', '') or '').strip()
                        if not combined:
                            parts = []
                            for k in ['character', 'clothing', 'pose', 'background', 'situation']:
                                v = prompt_dict.get(k, '')
                                if isinstance(v, str) and v.strip():
                                    parts.append(v.strip())
                            prompt_dict['combined'] = ' '.join(parts).strip()

                        # 메타(선택): 인물 키/키워드/보정 나이 포함(저장 호환에 영향 없음)
                        if current_character_key:
                            prompt_dict['character_key'] = current_character_key
                        if current_age_correction:
                            prompt_dict['age_correction'] = current_age_correction
                        if current_keywords:
                            prompt_dict['keywords'] = current_keywords

                        # 저장 형식: 캐릭터 JSON의 image_generation_prompts에 그대로 들어갈 JSON 문자열
                        prompt_json_str = json.dumps(prompt_dict, ensure_ascii=False)
                        results.append({
                            "character_name": current_character_name,
                            "character_number": current_character_index,
                            "prompt_number": prompt_number,
                            "prompt_json": prompt_json_str
                        })
                        any_detected = True

                i = j
                continue

            i += 1

        # 인물 헤더/구도 패턴이 전혀 감지되지 않으면 신규 포맷 아님
        if not any_detected or not results:
            return []

        # 정렬: 인물 번호 -> 프롬프트 번호
        results.sort(key=lambda x: (x.get('character_number', 0), x.get('prompt_number', 0)))
        return results

    def _merge_and_save_image_prompts(self, image_prompts: List[Dict[str, Any]], show_warnings: bool = True):
        """
        기존 인물 데이터에 이미지 프롬프트 병합 및 저장

        Args:
            image_prompts: 파싱된 이미지 프롬프트 정보 리스트
        """
        # 파일에서 최신 인물 데이터 먼저 로드
        characters = self.file_service.load_characters()

        # 인물이 없으면 빈 리스트로 초기화
        if not characters:
            characters = []

        def _normalize_name(name: str) -> str:
            # 공백 제거(김회장 == 김 회장). 구분이 필요하면 사용자가 '_'를 넣도록 함.
            return ''.join((name or '').split())

        # 인물 이름을 키로 하는 딕셔너리 생성 (빠른 검색을 위해)
        character_dict = {}
        for char in characters:
            key = _normalize_name(char.get('name', ''))
            if key:
                character_dict[key] = char

        missing_names: List[str] = []

        # 프롬프트 병합
        # (추가) 캐릭터별 이미지프롬프트 파일 생성용 수집
        prompts_for_files: Dict[str, Dict[int, Dict[str, Any]]] = {}

        for prompt_info in image_prompts:
            char_name_raw = prompt_info.get('character_name', '')
            char_name = _normalize_name(char_name_raw)
            prompt_number = prompt_info.get('prompt_number', 0)
            prompt_json_str = prompt_info.get('prompt_json', '')

            if not char_name or prompt_number == 0 or not prompt_json_str:
                continue

            # 프롬프트 번호 유효 범위 (1~12)
            if prompt_number < 1 or prompt_number > 12:
                continue

            if char_name in character_dict:
                # 기존 인물이 있으면 프롬프트 업데이트
                existing_char = character_dict[char_name]
                
                # image_generation_prompts 초기화
                if 'image_generation_prompts' not in existing_char or not isinstance(existing_char.get('image_generation_prompts'), dict):
                    existing_char['image_generation_prompts'] = {}

                # 프롬프트 저장 (JSON 문자열로 저장)
                prompt_key = f"prompt_{prompt_number}"
                existing_char['image_generation_prompts'][prompt_key] = prompt_json_str

                # 프롬프트 1을 기본값으로도 설정
                if prompt_number == 1:
                    existing_char['image_generation_prompt'] = prompt_json_str

                print(f"[이미지 프롬프트] {char_name} - 프롬프트 {prompt_number} 업데이트 완료")

                # 파일 저장용 prompt dict 수집
                try:
                    prompt_dict = safe_json_loads(prompt_json_str)
                    if isinstance(prompt_dict, dict):
                        prompts_for_files.setdefault(char_name, {})[prompt_number] = prompt_dict
                except Exception:
                    pass
            else:
                # 새 인물이면 추가 (일반적으로는 발생하지 않아야 함)
                if char_name_raw and char_name_raw not in missing_names:
                    missing_names.append(char_name_raw)
                print(f"[경고] 인물 '{char_name_raw}'을 찾을 수 없습니다. 인물 정보를 먼저 입력해주세요.")

        if show_warnings and missing_names:
            messagebox.showwarning(
                "인물 미매칭 경고",
                "다음 인물을 기존 인물 목록에서 찾지 못해 저장하지 못했습니다:\n\n"
                + "\n".join(f"- {n}" for n in missing_names)
                + "\n\n먼저 '인물 정보' 탭에서 해당 인물을 추가/이름 일치 후 다시 붙여넣기 해주세요."
            )

        # 인물 데이터 설정 및 저장
        self.project_data.set_characters(characters)

        # 파일에 저장
        save_result = self.file_service.save_characters(characters)
        if save_result:
            print(f"[이미지 프롬프트] {len(image_prompts)}개 프롬프트 파일 저장 완료")
        else:
            print(f"[이미지 프롬프트] 파일 저장 실패")

        # (추가) 02_characters/image_prompts/에 캐릭터별 이미지 프롬프트 파일 저장
        # 프로필 순서(인덱스) 기반 넘버링을 맞추기 위해 name -> index 매핑
        try:
            name_to_index = {}
            for idx, c in enumerate(characters, start=1):
                nm = _normalize_name(c.get("name", ""))
                if nm:
                    name_to_index[nm] = idx

            for nm, prompts_by_num in prompts_for_files.items():
                self.file_service.save_character_image_prompts(
                    character_name=nm,
                    prompts_by_number=prompts_by_num,
                    character_index=name_to_index.get(nm),
                )
        except Exception as e:
            print(f"[경고] 이미지 프롬프트 파일(image_prompts) 저장 중 오류: {e}")

    def save(self) -> bool:
        """데이터 저장 (자동 저장되므로 항상 True 반환)"""
        return True

