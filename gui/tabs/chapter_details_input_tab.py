"""
챕터 세부정보 입력 탭
사용자가 텍스트 형식으로 챕터 세부 정보를 입력하고 파싱하여 저장합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from typing import Dict, Any, List
from .base_tab import BaseTab
from utils.json_utils import format_json


class ChapterDetailsInputTab(BaseTab):
    """챕터 세부정보 입력 탭 클래스"""

    def get_tab_name(self) -> str:
        return "챕터 세부정보 입력"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # 좌우 분할
        paned_horizontal = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 왼쪽: 텍스트 입력 영역
        input_frame = ttk.LabelFrame(paned_horizontal, text="챕터 세부정보 텍스트 입력", padding=10)
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
        self.text_input.delete(1.0, tk.END)
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
        text = self.text_input.get(1.0, tk.END).strip()

        if not text:
            # 입력이 비어있으면 오른쪽 칸도 비우기
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            self.parsed_result_text.config(state=tk.DISABLED)
            return

        try:
            # 파싱 실행
            parsed_data = self._parse_chapter_details(text)

            # 오른쪽 칸에 JSON 형식으로 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            if parsed_data:
                json_str = format_json(parsed_data)
                self.parsed_result_text.insert(1.0, json_str)

                # 파싱이 성공하면 자동 저장
                try:
                    self._merge_and_save_chapter_details(parsed_data)
                    # 저장 성공 표시 (간단한 인디케이터)
                    self.parsed_result_text.insert(tk.END, "\n\n[자동 저장 완료]")
                except Exception as save_error:
                    # 저장 실패 시 오류 표시
                    self.parsed_result_text.insert(tk.END, f"\n\n[자동 저장 실패: {str(save_error)}]")
            else:
                self.parsed_result_text.insert(1.0, "파싱 결과가 없습니다.\n\n입력 형식을 확인해주세요.")
            self.parsed_result_text.config(state=tk.DISABLED)
        except Exception as e:
            # 오류 발생 시 오류 메시지 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            self.parsed_result_text.insert(1.0, f"파싱 오류:\n{str(e)}")
            self.parsed_result_text.config(state=tk.DISABLED)

    def _parse_and_save(self):
        """텍스트를 파싱하고 저장"""
        text = self.text_input.get(1.0, tk.END).strip()

        if not text:
            messagebox.showwarning("경고", "입력된 텍스트가 없습니다.")
            return

        try:
            # 텍스트 파싱
            chapter_details = self._parse_chapter_details(text)

            if not chapter_details:
                messagebox.showerror("오류", "파싱에 실패했습니다. 텍스트 형식을 확인해주세요.")
                return

            # 챕터 데이터 병합 및 저장
            self._merge_and_save_chapter_details(chapter_details)

            # 파싱 결과 오른쪽 칸에 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            json_str = format_json(chapter_details)
            self.parsed_result_text.insert(1.0, json_str)
            self.parsed_result_text.config(state=tk.DISABLED)

            messagebox.showinfo(
                "완료",
                f"챕터 세부정보가 파싱되어 저장되었습니다.\n\n"
                f"처리된 챕터 수: {len(chapter_details)}개\n\n"
                f"참고: 입력 시 자동 저장도 작동합니다.\n\n"
                f"확인 방법:\n"
                f"1. 오른쪽 '파싱 결과 미리보기'에서 JSON 형식 확인\n"
                f"2. 사이드바의 '챕터' 탭을 클릭하여 저장된 세부 정보 확인"
            )

        except Exception as e:
            messagebox.showerror("오류", f"파싱 중 오류가 발생했습니다:\n{e}")
            import traceback
            traceback.print_exc()

    def _parse_chapter_details(self, text: str) -> List[Dict[str, Any]]:
        """
        텍스트를 파싱하여 챕터 세부 정보 추출

        형식:
        챕터 1
        제목 : 백미러는 거짓말을 하지 않는다
        [내용 상세 설명]
        • 사건: ...
        • 오브젝트 활용: ...

        Args:
            text: 입력된 텍스트

        Returns:
            챕터 세부 정보 리스트
        """
        try:
            chapter_details = []

            # 챕터 블록으로 분할 (챕터 1, 챕터 2, ... 또는 챕터1, 챕터2, ...)
            chapter_pattern = r'챕터\s*(\d+)'
            chapter_blocks = re.split(f'(?={chapter_pattern})', text, flags=re.IGNORECASE)

            for block in chapter_blocks:
                block = block.strip()
                if not block:
                    continue

                # 챕터 번호 추출
                chapter_num_match = re.search(chapter_pattern, block, re.IGNORECASE)
                if not chapter_num_match:
                    continue

                chapter_number = int(chapter_num_match.group(1))

                # 제목 추출 (제목 : 백미러는 거짓말을 하지 않는다)
                title_match = re.search(r'제목\s*[:：]\s*(.+?)(?=\n|$)', block, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else f"챕터 {chapter_number}"

                # 내용 상세 설명 추출 ([내용 상세 설명] 이후 모든 텍스트)
                content_match = re.search(r'\[내용\s*상세\s*설명\]\s*\n\s*(.+)', block, re.DOTALL | re.IGNORECASE)
                detailed_content = content_match.group(1).strip() if content_match else ""

                # 챕터 정보 딕셔너리 생성
                chapter_info = {
                    "chapter_number": chapter_number,
                    "title": title,
                    "content_detail": detailed_content
                }

                chapter_details.append(chapter_info)
                print(f"[파싱] 챕터 {chapter_number} 파싱 완료: {title}")

            return chapter_details

        except Exception as e:
            raise Exception(f"챕터 파싱 오류: {e}")

    def _merge_and_save_chapter_details(self, chapter_details: List[Dict[str, Any]]):
        """
        기존 챕터 데이터에 세부 정보 병합 및 저장

        파일에서 최신 챕터 데이터를 먼저 로드하여 메모리 데이터가 아닌
        실제 파일의 최신 정보를 반영합니다.

        Args:
            chapter_details: 파싱된 챕터 세부 정보 리스트
        """
        # 파일에서 최신 챕터 데이터 먼저 로드 (메모리 데이터가 아닌 실제 파일에서)
        # 이렇게 하면 다른 탭에서 저장한 최신 정보를 반영할 수 있습니다.
        chapters = self.file_service.load_chapters()

        # 챕터가 없으면 빈 리스트로 초기화
        if not chapters:
            chapters = []

        # 챕터 번호를 키로 하는 딕셔너리 생성 (빠른 검색을 위해)
        chapter_dict = {ch.get('chapter_number', 0): ch for ch in chapters}

        # 세부 정보 병합
        for detail in chapter_details:
            chapter_number = detail.get('chapter_number', 0)
            if chapter_number == 0:
                continue

            if chapter_number in chapter_dict:
                # 기존 챕터가 있으면 세부 정보 병합
                existing_chapter = chapter_dict[chapter_number]
                # 제목 업데이트 (세부정보의 제목 우선)
                if detail.get('title'):
                    existing_chapter['title'] = detail['title']
                # 상세 내용 추가/업데이트
                if detail.get('content_detail'):
                    existing_chapter['content_detail'] = detail['content_detail']

                # _filename이 없으면 추가
                if '_filename' not in existing_chapter:
                    from utils.file_utils import get_chapter_filename
                    existing_chapter['_filename'] = get_chapter_filename(chapter_number)

                print(f"[챕터 세부정보] 챕터 {chapter_number} 업데이트: {existing_chapter.get('title')}")
            else:
                # 새 챕터면 추가
                from utils.file_utils import get_chapter_filename
                new_chapter = {
                    'chapter_number': chapter_number,
                    'title': detail.get('title', f'챕터 {chapter_number}'),
                    'content': '',  # 기본 content는 빈 문자열
                    'content_detail': detail.get('content_detail', ''),
                    'script': '',  # 대본도 빈 문자열로 초기화
                    '_filename': get_chapter_filename(chapter_number)
                }
                chapters.append(new_chapter)
                chapter_dict[chapter_number] = new_chapter
                print(f"[챕터 세부정보] 챕터 {chapter_number} 생성: {new_chapter.get('title')}")

        # 챕터 번호순으로 정렬
        chapters.sort(key=lambda x: x.get('chapter_number', 0))

        # 챕터 데이터 설정 및 저장
        self.project_data.set_chapters(chapters)

        # 파일에 저장
        save_result = self.file_service.save_chapters(chapters)
        if save_result:
            print(f"[챕터 세부정보] {len(chapters)}개 챕터 파일 저장 완료")
        else:
            print(f"[챕터 세부정보] 파일 저장 실패")

        # 챕터 탭 업데이트 (탭이 열려있는 경우에만)
        if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'tabs'):
            if 'chapters' in self.parent.master.tabs:
                # 탭 업데이트는 사용자가 챕터 탭을 클릭할 때만 호출되도록 주석 처리
                # self.parent.master.tabs['chapters'].update_display()
                pass

    def save(self) -> bool:
        """데이터 저장 (자동 저장되므로 항상 True 반환)"""
        return True
