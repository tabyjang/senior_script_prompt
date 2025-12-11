"""
인물 세부정보 입력 탭
사용자가 JSON 형식으로 인물 세부 정보를 입력하고 파싱하여 저장합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from typing import Dict, Any, List
from .base_tab import BaseTab
from utils.json_utils import format_json, safe_json_loads


class CharacterDetailsInputTab(BaseTab):
    """인물 세부정보 입력 탭 클래스"""

    def get_tab_name(self) -> str:
        return "인물 세부정보 입력"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # 좌우 분할
        paned_horizontal = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 왼쪽: JSON 입력 영역
        input_frame = ttk.LabelFrame(paned_horizontal, text="인물 세부정보 JSON 입력", padding=10)
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

        # JSON 입력 영역
        self.json_input = scrolledtext.ScrolledText(
            input_frame,
            width=60,
            height=40,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.json_input.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 실시간 파싱을 위한 이벤트 바인딩
        self.json_input.bind('<KeyRelease>', self._on_text_change)

        # 오른쪽: 파싱 결과 미리보기
        result_frame = ttk.LabelFrame(paned_horizontal, text="파싱 결과 미리보기", padding=10)
        paned_horizontal.add(result_frame, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.parsed_result_text = scrolledtext.ScrolledText(
            result_frame,
            width=60,
            height=40,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.parsed_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def update_display(self):
        """화면 업데이트"""
        pass

    def _clear_input(self):
        """입력 영역 지우기"""
        self.json_input.delete(1.0, tk.END)
        self.parsed_result_text.config(state=tk.NORMAL)
        self.parsed_result_text.delete(1.0, tk.END)
        self.parsed_result_text.config(state=tk.DISABLED)
    
    def _on_text_change(self, event=None):
        """입력 텍스트 변경 시 실시간 파싱"""
        # 입력이 너무 빠르면 성능 문제가 있을 수 있으므로 약간의 지연 후 파싱
        if hasattr(self, '_parsing_after_id'):
            self.frame.after_cancel(self._parsing_after_id)
        
        # 1000ms 후에 파싱 실행 (debounce) - 자동 저장을 위해 조금 더 긴 시간 설정
        self._parsing_after_id = self.frame.after(1000, self._perform_realtime_parsing)
    
    def _perform_realtime_parsing(self):
        """실제 실시간 파싱 수행 및 자동 저장"""
        json_text = self.json_input.get(1.0, tk.END).strip()
        
        if not json_text:
            # 입력이 비어있으면 오른쪽 칸도 비우기
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            self.parsed_result_text.config(state=tk.DISABLED)
            return
        
        try:
            # 파싱 실행
            parsed_data = self._parse_character_details(json_text)
            
            # 오른쪽 칸에 JSON 형식으로 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            if parsed_data:
                json_str = format_json(parsed_data)
                self.parsed_result_text.insert(1.0, json_str)
                
                # 파싱이 성공하면 자동 저장
                try:
                    self._merge_and_save_character_details(parsed_data)
                    # 저장 성공 표시 (간단한 인디케이터)
                    self.parsed_result_text.insert(tk.END, "\n\n[자동 저장 완료]")
                except Exception as save_error:
                    # 저장 실패 시 오류 표시
                    self.parsed_result_text.insert(tk.END, f"\n\n[자동 저장 실패: {str(save_error)}]")
            else:
                self.parsed_result_text.insert(1.0, "파싱 결과가 없습니다.\n\nJSON 형식을 확인해주세요.")
            self.parsed_result_text.config(state=tk.DISABLED)
        except Exception as e:
            # 오류 발생 시 오류 메시지 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            self.parsed_result_text.insert(1.0, f"파싱 오류:\n{str(e)}")
            self.parsed_result_text.config(state=tk.DISABLED)

    def _parse_and_save(self):
        """JSON을 파싱하고 저장"""
        json_text = self.json_input.get(1.0, tk.END).strip()
        
        if not json_text:
            messagebox.showwarning("경고", "입력된 JSON이 없습니다.")
            return

        try:
            # JSON 파싱
            character_details = self._parse_character_details(json_text)
            
            if not character_details:
                messagebox.showerror("오류", "파싱에 실패했습니다. JSON 형식을 확인해주세요.")
                return

            # 인물 데이터 병합 및 저장
            self._merge_and_save_character_details(character_details)
            
            # 파싱 결과 오른쪽 칸에 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            json_str = format_json(character_details)
            self.parsed_result_text.insert(1.0, json_str)
            self.parsed_result_text.config(state=tk.DISABLED)

            messagebox.showinfo(
                "완료", 
                f"인물 세부정보가 파싱되어 저장되었습니다.\n\n"
                f"처리된 인물 수: {len(character_details)}명\n\n"
                f"참고: 입력 시 자동 저장도 작동합니다.\n\n"
                f"확인 방법:\n"
                f"1. 오른쪽 '파싱 결과 미리보기'에서 JSON 형식 확인\n"
                f"2. 사이드바의 '인물' 탭을 클릭하여 저장된 세부 정보 확인"
            )

        except Exception as e:
            messagebox.showerror("오류", f"파싱 중 오류가 발생했습니다:\n{e}")

    def _parse_character_details(self, json_text: str) -> List[Dict[str, Any]]:
        """
        JSON 텍스트를 파싱하여 인물 세부 정보 추출
        
        Args:
            json_text: JSON 형식의 텍스트
            
        Returns:
            인물 세부 정보 리스트
        """
        try:
            # JSON 파싱
            data = safe_json_loads(json_text)
            
            if not data:
                return []
            
            # 배열인지 확인
            if not isinstance(data, list):
                return []
            
            character_details = []
            
            # 각 항목의 character_profile 추출
            for item in data:
                if isinstance(item, dict) and 'character_profile' in item:
                    profile = item['character_profile']
                    if isinstance(profile, dict):
                        character_details.append(profile)
            
            return character_details
            
        except Exception as e:
            raise Exception(f"JSON 파싱 오류: {e}")

    def _merge_and_save_character_details(self, character_details: List[Dict[str, Any]]):
        """
        기존 인물 데이터에 세부 정보 병합 및 저장

        Args:
            character_details: 파싱된 인물 세부 정보 리스트
        """
        # 현재 인물 데이터 가져오기
        characters = self.project_data.get_characters()

        # 인물 이름을 키로 하는 딕셔너리 생성 (빠른 검색을 위해)
        character_dict = {char.get('name', ''): char for char in characters}

        # 세부 정보 병합
        for detail in character_details:
            # 키 정규화: 하이픈을 언더스코어로, 소문자로 변환
            normalized_detail = self._normalize_keys(detail)

            name = normalized_detail.get('name', '')
            if not name:
                continue

            if name in character_dict:
                # 기존 인물이 있으면 세부 정보 병합
                existing_char = character_dict[name]
                # 기본 정보는 유지하고 세부 정보만 업데이트
                existing_char.update(normalized_detail)
            else:
                # 새 인물이면 추가
                characters.append(normalized_detail)
                character_dict[name] = normalized_detail

        # 인물 데이터 설정 및 저장
        self.project_data.set_characters(characters)
        self.file_service.save_characters(characters)

        # 인물 탭 업데이트
        if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'tabs'):
            if 'characters' in self.parent.master.tabs:
                self.parent.master.tabs['characters'].update_display()

    def _normalize_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        딕셔너리의 키를 정규화 (하이픈 → 언더스코어, 소문자 변환)

        Args:
            data: 원본 딕셔너리

        Returns:
            키가 정규화된 딕셔너리
        """
        normalized = {}
        for key, value in data.items():
            # 키 정규화: 하이픈을 언더스코어로, 소문자로 변환
            normalized_key = key.replace('-', '_').lower()

            # 값이 딕셔너리면 재귀적으로 정규화
            if isinstance(value, dict):
                normalized[normalized_key] = self._normalize_keys(value)
            # 값이 리스트면 각 항목이 딕셔너리인 경우 정규화
            elif isinstance(value, list):
                normalized[normalized_key] = [
                    self._normalize_keys(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                normalized[normalized_key] = value

        return normalized

    def save(self) -> bool:
        """데이터 저장 (자동 저장되므로 항상 True 반환)"""
        return True

