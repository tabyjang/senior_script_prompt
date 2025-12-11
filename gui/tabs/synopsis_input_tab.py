"""
시놉시스 입력 탭
사용자가 텍스트로 시놉시스 정보를 입력하고 파싱하여 저장합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import re
import json
from typing import Dict, Any, List
from .base_tab import BaseTab
from utils.json_utils import format_json


class SynopsisInputTab(BaseTab):
    """시놉시스 입력 탭 클래스"""

    def get_tab_name(self) -> str:
        return "시놉시스 입력"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # 좌우 분할
        paned_horizontal = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 왼쪽: 시놉시스 입력 영역
        input_frame = ttk.LabelFrame(paned_horizontal, text="시놉시스 입력", padding=10)
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

        save_as_new_btn = ttk.Button(
            button_frame,
            text="📁 새 프로젝트로 저장",
            command=self._parse_and_save_as_new_project,
            width=22
        )
        save_as_new_btn.pack(side=tk.LEFT, padx=5)

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
        self.text_input.bind('<Button-1>', self._on_text_change)
        self.text_input.bind('<ButtonRelease-1>', self._on_text_change)

        # 오른쪽: 실시간 파싱 결과 표시 영역
        result_frame = ttk.LabelFrame(paned_horizontal, text="파싱 결과 (JSON)", padding=10)
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
        # 기존 시놉시스 데이터가 있으면 로드
        synopsis = self.project_data.get_synopsis()
        if synopsis:
            # 파싱된 데이터를 텍스트 형식으로 변환하여 표시 (선택사항)
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
        
        # 500ms 후에 파싱 실행 (debounce)
        self._parsing_after_id = self.frame.after(500, self._perform_realtime_parsing)
    
    def _perform_realtime_parsing(self):
        """실제 실시간 파싱 수행"""
        text = self.text_input.get(1.0, tk.END).strip()
        
        if not text:
            # 입력이 비어있으면 오른쪽 칸도 비우기
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            self.parsed_result_text.config(state=tk.DISABLED)
            return
        
        try:
            # 파싱 실행
            parsed_data = self._parse_synopsis_text(text)
            
            # 오른쪽 칸에 JSON 형식으로 표시
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            if parsed_data:
                json_str = format_json(parsed_data)
                self.parsed_result_text.insert(1.0, json_str)
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
            parsed_data = self._parse_synopsis_text(text)
            
            if not parsed_data:
                messagebox.showerror("오류", "파싱에 실패했습니다. 텍스트 형식을 확인해주세요.")
                return

            # 기존 시놉시스 데이터와 병합
            existing_synopsis = self.project_data.get_synopsis()
            if existing_synopsis:
                # 기존 데이터 유지하면서 새 데이터로 업데이트
                existing_synopsis.update(parsed_data)
                parsed_data = existing_synopsis

            # 파싱 결과 오른쪽 칸에 표시 (이미 실시간으로 표시되어 있을 수 있음)
            self.parsed_result_text.config(state=tk.NORMAL)
            self.parsed_result_text.delete(1.0, tk.END)
            json_str = format_json(parsed_data)
            self.parsed_result_text.insert(1.0, json_str)
            self.parsed_result_text.config(state=tk.DISABLED)

            # 프로젝트 폴더 자동 생성 (제목이 있으면 항상 생성)
            title = parsed_data.get('title', '').strip()
            if title:
                # 현재 프로젝트 경로 확인
                try:
                    current_project_path = Path(self.file_service.project_path)
                    if not current_project_path.is_absolute():
                        # 상대 경로인 경우 절대 경로로 변환
                        import os
                        current_project_path = Path(os.getcwd()) / current_project_path
                    current_project_path = current_project_path.resolve()
                except Exception as e:
                    print(f"[시놉시스 저장] 경로 확인 오류: {e}")
                    current_project_path = None
                
                # 프로젝트 폴더가 이미 생성되어 있는지 확인
                is_project_folder = False
                if current_project_path and current_project_path.exists():
                    synopsis_file = current_project_path / "synopsis.json"
                    # synopsis.json이 있고, 폴더명이 프로젝트 형식(001_제목)인 경우
                    is_project_folder = (
                        synopsis_file.exists() and 
                        current_project_path.name.startswith('0') and 
                        '_' in current_project_path.name
                    )
                
                if not is_project_folder:
                    # 프로젝트 폴더 생성
                    print(f"[시놉시스 저장] 프로젝트 폴더 생성 시작: 제목={title}")
                    print(f"[시놉시스 저장] 현재 경로: {current_project_path}")
                    new_project_path = self.file_service.create_project_folder(
                        title=title,
                        category="01_man"
                    )
                    
                    if new_project_path:
                        print(f"[시놉시스 저장] 프로젝트 폴더 생성 완료: {new_project_path}")
                        # 프로젝트 경로 업데이트
                        self.file_service.set_project_path(new_project_path)
                        self.project_data.project_path = str(new_project_path)
                        
                        # 메인 윈도우의 project_path도 업데이트 (접근 가능한 경우)
                        if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'project_path'):
                            self.parent.master.project_path = new_project_path
                    else:
                        print(f"[시놉시스 저장] 프로젝트 폴더 생성 실패")
                        import tkinter.messagebox as msgbox
                        msgbox.showerror("오류", "프로젝트 폴더 생성에 실패했습니다.\n콘솔 로그를 확인해주세요.")
                else:
                    print(f"[시놉시스 저장] 기존 프로젝트 폴더 사용: {current_project_path}")

            # 데이터 저장
            self._save_synopsis_data(parsed_data)
            
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류가 발생했습니다:\n{e}")
            import traceback
            traceback.print_exc()

    def _parse_and_save_as_new_project(self):
        """텍스트를 파싱하고 새 프로젝트로 저장"""
        text = self.text_input.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showwarning("경고", "입력된 텍스트가 없습니다.")
            return

        try:
            # 텍스트 파싱
            parsed_data = self._parse_synopsis_text(text)
            
            if not parsed_data:
                messagebox.showerror("오류", "파싱에 실패했습니다. 텍스트 형식을 확인해주세요.")
                return

            # 제목 확인
            title = parsed_data.get('title', '').strip()
            if not title:
                messagebox.showwarning("경고", "시놉시스에 제목이 없습니다. 제목을 입력해주세요.")
                return

            # 폴더 선택 다이얼로그
            # 초기 디렉토리 설정 (현재 프로젝트 경로의 상위 폴더 또는 01_man 폴더)
            initial_dir = None
            try:
                current_path = Path(self.file_service.project_path)
                if current_path.exists():
                    # 01_man 폴더 찾기
                    test_path = current_path
                    for _ in range(5):
                        if test_path.name == "01_man":
                            initial_dir = str(test_path)
                            break
                        test_path = test_path.parent
                    
                    if not initial_dir:
                        initial_dir = str(current_path.parent)
            except Exception:
                pass

            project_dir = filedialog.askdirectory(
                title="프로젝트 폴더 선택 (또는 새 폴더 생성 위치 선택)",
                initialdir=initial_dir
            )
            
            if not project_dir:
                return  # 사용자가 취소한 경우

            project_path = Path(project_dir).resolve()
            
            # 선택한 폴더가 이미 프로젝트 폴더인지 확인
            synopsis_file = project_path / "synopsis.json"
            is_existing_project = synopsis_file.exists()
            
            if is_existing_project:
                # 기존 프로젝트 폴더인 경우 덮어쓰기 확인
                response = messagebox.askyesno(
                    "기존 프로젝트 덮어쓰기",
                    f"선택한 폴더는 이미 프로젝트 폴더입니다.\n"
                    f"기존 시놉시스를 덮어쓰시겠습니까?\n\n"
                    f"경로: {project_path}\n"
                    f"주의: 기존 시놉시스 데이터가 교체됩니다."
                )
                if not response:
                    return
            else:
                # 새 폴더인 경우 프로젝트 폴더 생성 확인
                if not project_path.exists():
                    # 폴더가 없으면 생성할지 확인
                    response = messagebox.askyesno(
                        "새 프로젝트 폴더 생성",
                        f"선택한 경로에 폴더가 없습니다.\n"
                        f"새 프로젝트 폴더를 생성하시겠습니까?\n\n"
                        f"경로: {project_path}"
                    )
                    if not response:
                        return
                    project_path.mkdir(parents=True, exist_ok=True)
                
                # 프로젝트 폴더 구조 생성 (하위 폴더들)
                (project_path / "02_characters").mkdir(exist_ok=True)
                (project_path / "03_chapters").mkdir(exist_ok=True)
                (project_path / "04_scripts").mkdir(exist_ok=True)

            # 프로젝트 경로 업데이트
            self.file_service.set_project_path(project_path)
            self.project_data.project_path = project_path
            
            # 메인 윈도우의 project_path도 업데이트
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'project_path'):
                self.parent.master.project_path = project_path
                # 설정 파일에 마지막 프로젝트 경로 저장
                if hasattr(self.parent.master, 'config'):
                    self.parent.master.config.set_last_project_path(str(project_path))

            # 데이터 저장
            self._save_synopsis_data(parsed_data)
            
            # 모든 탭 업데이트
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'tabs'):
                for tab in self.parent.master.tabs.values():
                    tab.update_display()
            
            # 메인 윈도우의 데이터 로드 및 상태바 업데이트
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, '_load_project_data'):
                self.parent.master._load_project_data()
            
            # 윈도우 제목 업데이트
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'root'):
                self.parent.master.root.title(f"프로젝트 뷰어/에디터 - {title}")
            
            messagebox.showinfo(
                "저장 완료",
                f"새 프로젝트로 저장되었습니다.\n\n"
                f"제목: {title}\n"
                f"경로: {project_path}"
            )

        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류가 발생했습니다:\n{e}")
            import traceback
            traceback.print_exc()

    def _save_synopsis_data(self, parsed_data: Dict[str, Any]):
        """시놉시스 데이터 저장 및 동기화"""
        # 데이터 저장
        self.project_data.set_synopsis(parsed_data)
        success = self.file_service.save_synopsis(parsed_data)

        if success:
            # 시놉시스의 등장인물을 인물 탭에 동기화
            self._sync_characters_from_synopsis()
            
            # 시놉시스의 챕터를 챕터 탭에 동기화
            self._sync_chapters_from_synopsis()
            
            # 시놉시스 탭 업데이트를 위해 부모 노트북의 모든 자식 위젯 확인
            # 노트북의 모든 탭을 순회하며 시놉시스 탭 찾기
            try:
                for tab_id in self.parent.tabs():
                    tab_widget = self.parent.nametowidget(tab_id)
                    # 시놉시스 탭인지 확인 (클래스 이름으로)
                    if hasattr(tab_widget, 'winfo_children'):
                        for child in tab_widget.winfo_children():
                            # BaseTab의 update_display를 호출할 수 있는 방법
                            # 실제로는 메인 윈도우의 tabs 딕셔너리에 접근해야 함
                            pass
            except:
                pass
            
            messagebox.showinfo(
                "완료",
                "시놉시스가 파싱되어 저장되었습니다.\n\n"
                "확인 방법:\n"
                "1. 오른쪽 '파싱 결과 (JSON)'에서 JSON 형식 확인\n"
                "2. 사이드바의 '시놉시스' 탭을 클릭하여 파싱된 데이터 확인\n"
                "3. '인물' 탭에서 등장인물 정보 확인\n"
                "4. '챕터' 탭에서 챕터 정보 확인"
            )
        else:
            messagebox.showerror("오류", "파싱은 성공했으나 저장에 실패했습니다.")

    def _parse_synopsis_text(self, text: str) -> Dict[str, Any]:
        """
        입력된 텍스트를 파싱하여 구조화된 데이터로 변환
        
        Args:
            text: 입력된 텍스트
            
        Returns:
            파싱된 시놉시스 데이터 딕셔너리
        """
        result = {}

        # 1. 제목 (번호 있거나 없거나, 꺾쇠괄호 제거)
        title_match = re.search(r'(?:1\.\s*)?제목\s*\n\s*(.+?)(?=\n\s*(?:2\.\s*)?시놉시스|$)', text, re.DOTALL | re.IGNORECASE)
        if not title_match:
            # 꺾쇠괄호 형식도 시도
            title_match = re.search(r'(?:1\.\s*)?제목\s*\n\s*[<〈](.+?)[>〉](?=\n|$)', text, re.DOTALL | re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # 꺾쇠괄호 제거
            title = re.sub(r'^[<〈]|[>〉]$', '', title).strip()
            result['title'] = title

        # 2. 시놉시스
        synopsis_match = re.search(r'(?:2\.\s*)?시놉시스\s*\n\s*(.+?)(?=\n\s*(?:3\.\s*)?전체\s*줄거리|$)', text, re.DOTALL | re.IGNORECASE)
        if synopsis_match:
            result['synopsis'] = synopsis_match.group(1).strip()

        # 3. 전체 줄거리
        full_story_match = re.search(r'(?:3\.\s*)?전체\s*줄거리\s*\n\s*(.+?)(?=\n\s*(?:4\.\s*)?등장인물|$)', text, re.DOTALL | re.IGNORECASE)
        if full_story_match:
            result['full_story'] = full_story_match.group(1).strip()

        # 4. 등장인물
        characters = self._parse_characters(text)
        if characters:
            result['characters'] = characters

        # 5. 8챕터 구성
        chapters = self._parse_chapters(text)
        if chapters:
            result['chapters'] = chapters

        # 6. 주요 사건 전개
        main_events_match = re.search(r'(?:6\.\s*)?주요\s*사건\s*전개\s*\n\s*(.+?)(?=\n\s*(?:7\.\s*)?감동을\s*주는|$)', text, re.DOTALL | re.IGNORECASE)
        if main_events_match:
            result['main_events'] = main_events_match.group(1).strip()

        # 7. 감동을 주는 사건 (보조사건 포함)
        touching_match = re.search(r'(?:7\.\s*)?감동을\s*주는\s*(?:보조)?사건\s*(?:\([^)]+\))?\s*\n\s*(.+?)(?=\n\s*(?:8\.\s*)?기쁨을\s*주는|$)', text, re.DOTALL | re.IGNORECASE)
        if touching_match:
            result['touching_events'] = touching_match.group(1).strip()

        # 8. 기쁨을 주는 사건 (보조사건 포함)
        joyful_match = re.search(r'(?:8\.\s*)?기쁨을\s*주는\s*(?:보조)?사건\s*(?:\([^)]+\))?\s*\n\s*(.+?)(?=\n\s*(?:9\.\s*)?충격을\s*주는|$)', text, re.DOTALL | re.IGNORECASE)
        if joyful_match:
            result['joyful_events'] = joyful_match.group(1).strip()

        # 9. 충격을 주는 사건 (필수사건 포함)
        shocking_match = re.search(r'(?:9\.\s*)?충격을\s*주는\s*(?:필수)?사건\s*(?:\([^)]+\))?\s*\n\s*(.+?)(?=\n\s*(?:10\.\s*)?키\s*오브젝트|$)', text, re.DOTALL | re.IGNORECASE)
        if shocking_match:
            result['shocking_events'] = shocking_match.group(1).strip()

        # 10. 키 오브젝트 (& 보조 오브젝트 포함)
        key_objects_match = re.search(r'(?:10\.\s*)?키\s*오브젝트\s*(?:&[^&]*보조\s*오브젝트)?\s*\n\s*(.+?)(?=\n\s*(?:11\.\s*)?(?:핵심\s*재미|오디오북)|$)', text, re.DOTALL | re.IGNORECASE)
        if key_objects_match:
            result['key_objects'] = key_objects_match.group(1).strip()

        # 11. 핵심 재미 및 성공 전략 분석 (선택적)
        strategy_match = re.search(r'(?:11\.\s*)?핵심\s*재미\s*및\s*성공\s*전략\s*분석\s*\n\s*(.+?)(?=\n\s*(?:12\.\s*)?오디오북|$)', text, re.DOTALL | re.IGNORECASE)
        if strategy_match:
            result['success_strategy'] = strategy_match.group(1).strip()

        # 12. 오디오북 대본 예시 (Narrative Script 포함)
        audiobook_match = re.search(r'(?:12\.\s*)?(?:11\.\s*)?오디오북\s*대본\s*(?:\(Narrative\s*Script\))?\s*(?:예시)?\s*\n\s*(.+?)$', text, re.DOTALL | re.IGNORECASE)
        if audiobook_match:
            result['audiobook_script_example'] = audiobook_match.group(1).strip()

        return result

    def _parse_characters(self, text: str) -> List[Dict[str, Any]]:
        """
        등장인물 섹션 파싱 (유연한 파싱 규칙)

        우선순위:
        1. [{...}, {...}] JSON 배열 형식
        2. "name" 키값 기준으로 블록 분할 + 모든 키-값 러프하게 파싱

        Args:
            text: 전체 텍스트

        Returns:
            등장인물 배열
        """
        characters = []

        # 등장인물 섹션 찾기 (번호 있거나 없거나, 괄호 내용 포함)
        characters_section_match = re.search(
            r'(?:4\.\s*)?등장인물\s*(?:\([^)]+\))?\s*\n\s*(.+?)(?=\n\s*(?:5\.\s*)?8?챕터\s*구성|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )

        if not characters_section_match:
            return characters

        characters_text = characters_section_match.group(1).strip()

        # ===== 1순위: [{...}, {...}] JSON 배열 형식 파싱 =====
        # [ 로 시작하고 ] 로 끝나는 JSON 배열 찾기
        json_array_match = re.search(r'\[\s*\{.+\}\s*\]', characters_text, re.DOTALL)
        if json_array_match:
            json_text = json_array_match.group(0)
            try:
                # JSON 파싱 시도
                parsed_json = json.loads(json_text)
                if isinstance(parsed_json, list):
                    print(f"[파싱] JSON 배열 형식으로 {len(parsed_json)}명 파싱 성공")
                    return parsed_json
            except json.JSONDecodeError as e:
                print(f"[파싱] JSON 배열 형식이지만 파싱 실패: {e}")
                # JSON 파싱 실패 시 2순위로 넘어감

        # ===== 2순위: "name" 키값 기준 러프 파싱 =====
        # "name" 또는 name으로 블록 분할
        character_blocks = re.split(
            r'(?=\s*(?:-\s*)?["\']?\s*name\s*["\']?\s*[:：])',
            characters_text,
            flags=re.IGNORECASE
        )

        for block in character_blocks:
            block = block.strip()
            if not block:
                continue

            # name이 없으면 건너뛰기
            if not re.search(r'["\']?\s*name\s*["\']?\s*[:：]', block, re.IGNORECASE):
                continue

            character = self._parse_character_block_flexible(block)

            if character and 'name' in character:
                characters.append(character)
                print(f"[파싱] 인물 파싱 완료: {character.get('name')} (키: {len(character)}개)")

        return characters

    def _parse_character_block_flexible(self, block: str) -> Dict[str, Any]:
        """
        인물 블록을 유연하게 파싱
        name 아래 모든 키-값 쌍을 찾아서 파싱

        지원 형식:
        - "key": "value"
        - "key": value
        - key: "value"
        - key: value
        - - key: value
        - key-name: value (하이픈 포함)
        - key_name: value (언더스코어 포함)

        Args:
            block: 인물 정보 텍스트 블록

        Returns:
            파싱된 인물 딕셔너리
        """
        character = {}

        # 모든 키-값 쌍 찾기
        # 패턴: 키(따옴표 선택), 콜론, 값(따옴표 선택)
        # (?:-\s*)? : 선택적 하이픈 (리스트 형식)
        # ["\']?\s* : 선택적 따옴표 + 공백
        # ([\w\-]+) : 키 이름 (알파벳, 숫자, 언더스코어, 하이픈)
        # \s*["\']? : 공백 + 선택적 따옴표
        # \s*[:：]\s* : 콜론 (한글 콜론 포함)
        # 값 부분: 따옴표로 묶인 값 또는 다음 키까지

        key_value_pattern = r'(?:-\s*)?["\']?\s*([\w\-]+)\s*["\']?\s*[:：]\s*(?:["\']([^"\']+)["\']|([^\n]+?)(?=\n\s*(?:-\s*)?["\']?\s*[\w\-]+\s*["\']?\s*[:：]|$))'

        matches = re.finditer(key_value_pattern, block, re.IGNORECASE | re.MULTILINE)

        for match in matches:
            # 키 정규화:
            # 1. 하이픈을 언더스코어로 변환
            # 2. 소문자로 변환 (일관성 유지)
            key = match.group(1).strip()
            key = key.replace('-', '_')  # 하이픈을 언더스코어로 변환
            key = key.lower()  # 소문자로 정규화

            # 값은 따옴표 안 또는 밖
            value = (match.group(2) or match.group(3) or '').strip()

            # 값 정리
            value = value.rstrip(',').strip()

            # 빈 값은 건너뛰기
            if not value:
                continue

            # 숫자 변환 시도 (age 등)
            if key == 'age':
                try:
                    value = int(value)
                except:
                    pass

            # 캐릭터에 추가
            character[key] = value

        return character

    def _parse_chapters(self, text: str) -> Dict[str, str]:
        """
        8챕터 구성 파싱
        
        Args:
            text: 전체 텍스트
            
        Returns:
            챕터 딕셔너리 ({"chapter_1": "내용", ...})
        """
        chapters = {}
        
        # 챕터 섹션 찾기 (번호 있거나 없거나, 괄호 내용 포함)
        chapters_section_match = re.search(
            r'(?:5\.\s*)?8?챕터\s*구성\s*(?:\([^)]+\))?\s*\n\s*(.+?)(?=\n\s*(?:6\.\s*)?주요\s*사건|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )
        
        if not chapters_section_match:
            return chapters

        chapters_text = chapters_section_match.group(1)
        
        # 먼저 합쳐진 챕터를 분리하는 패턴 확인: \n숫자.\t챕터숫자 : 형식
        # 이 패턴이 있으면 하나의 문자열로 합쳐진 챕터들을 분리
        separator_pattern = r'\n(\d+)\.\s*\t?\s*챕터\s*(\d+)\s*[:：]\s*'
        separator_matches = list(re.finditer(separator_pattern, chapters_text, re.IGNORECASE))
        
        if separator_matches:
            # 합쳐진 챕터들을 분리
            # 첫 번째 챕터는 구분자 이전까지
            first_chapter_end = separator_matches[0].start()
            first_chapter_text = chapters_text[:first_chapter_end].strip()
            
            # 첫 번째 챕터 파싱
            if first_chapter_text:
                # 첫 번째 챕터 형식 확인: [도입] 제목: 내용 또는 챕터 1 (도입): 내용
                first_bracket_match = re.match(r'\[([^\]]+)\]\s*([^:：]+?)\s*[:：]\s*(.+)', first_chapter_text, re.DOTALL)
                if first_bracket_match:
                    bracket_type = first_bracket_match.group(1).strip()
                    chapter_title = first_bracket_match.group(2).strip()
                    chapter_content = first_bracket_match.group(3).strip()
                    chapters['chapter_1'] = f"[{bracket_type}] {chapter_title}: {chapter_content}"
                else:
                    # 기본 형식
                    chapters['chapter_1'] = first_chapter_text
            
            # 나머지 챕터들 파싱
            for i, match in enumerate(separator_matches):
                chapter_num = match.group(2).strip()  # 챕터 번호
                start_pos = match.end()  # 내용 시작 위치
                
                # 다음 구분자까지 또는 끝까지
                if i + 1 < len(separator_matches):
                    end_pos = separator_matches[i + 1].start()
                else:
                    end_pos = len(chapters_text)
                
                chapter_content = chapters_text[start_pos:end_pos].strip()
                
                # 챕터 내용 저장
                chapters[f'chapter_{chapter_num}'] = chapter_content
        else:
            # 합쳐진 챕터가 없으면 기존 로직 사용
            # 챕터 추출: 여러 패턴 지원 (우선순위 순)
            # 1. •	챕터 1 (도입): 내용 형식 (불릿 포인트 + 괄호)
            # 2. [도입] 제목: 내용 형식 (대괄호)
            # 3. 챕터1: 내용 형식 (기본)
            
            # 패턴 1: •	챕터 1 (도입): 내용 (최우선)
            bullet_pattern = r'•\s*챕터\s*(\d+)\s*\(([^)]+)\)\s*[:：]\s*(.+?)(?=\n\s*•|$)'
            bullet_matches = list(re.finditer(bullet_pattern, chapters_text, re.DOTALL | re.IGNORECASE))
            
            if bullet_matches:
                # 불릿 포인트 형식이 있으면 우선 사용
                for match in bullet_matches:
                    chapter_num = match.group(1).strip()
                    chapter_stage = match.group(2).strip()  # (도입), (전개) 등
                    chapter_content = match.group(3).strip()  # 내용
                    
                    # 단계 정보와 내용을 합쳐서 저장
                    full_content = f"챕터 {chapter_num} ({chapter_stage}): {chapter_content}"
                    chapters[f'chapter_{chapter_num}'] = full_content
            else:
                # 패턴 2: [대괄호] 제목: 내용 (숫자 없이 순서대로)
                bracket_pattern = r'\[([^\]]+)\]\s*([^:：\n]+?)\s*[:：]\s*(.+?)(?=\n\s*\[|$)'
                bracket_matches = list(re.finditer(bracket_pattern, chapters_text, re.DOTALL | re.IGNORECASE))
                
                if bracket_matches:
                    # 대괄호 형식이 있으면 사용
                    chapter_index = 1
                    for match in bracket_matches:
                        bracket_type = match.group(1).strip()  # [도입], [전개] 등
                        chapter_title = match.group(2).strip()  # 제목
                        chapter_content = match.group(3).strip()  # 내용
                        
                        # 제목과 내용을 합쳐서 저장
                        full_content = f"[{bracket_type}] {chapter_title}: {chapter_content}"
                        chapters[f'chapter_{chapter_index}'] = full_content
                        chapter_index += 1
                else:
                    # 패턴 3: 챕터 숫자 포함 형식
                    number_pattern = r'(?:\[[^\]]+\]\s*)?(?:챕터\s*)?(\d+)\s*[:：]\s*(.+?)(?=\n\s*(?:\[[^\]]+\]\s*)?(?:챕터\s*)?\d+|$)'
                    number_matches = re.finditer(number_pattern, chapters_text, re.DOTALL | re.IGNORECASE)
                    
                    for match in number_matches:
                        chapter_num = match.group(1)
                        chapter_content = match.group(2).strip()
                        
                        # 대괄호 제목이 있으면 포함
                        if chapter_content.startswith('['):
                            bracket_match = re.match(r'\[([^\]]+)\]\s*(.+)', chapter_content)
                            if bracket_match:
                                chapter_title = bracket_match.group(1)
                                chapter_content = bracket_match.group(2).strip()
                                chapters[f'chapter_{chapter_num}'] = f"[{chapter_title}] {chapter_content}"
                            else:
                                chapters[f'chapter_{chapter_num}'] = chapter_content
                        else:
                            chapters[f'chapter_{chapter_num}'] = chapter_content

        return chapters

    def _sync_characters_from_synopsis(self):
        """시놉시스의 등장인물을 인물 탭에 동기화"""
        synopsis = self.project_data.get_synopsis()
        synopsis_characters = synopsis.get('characters', [])
        
        if synopsis_characters:
            # 시놉시스의 등장인물을 인물 데이터로 변환
            characters = []
            for syn_char in synopsis_characters:
                # 시놉시스 구조를 그대로 사용 (필요한 키만 추출)
                character = {
                    'name': syn_char.get('name', ''),
                    'age': syn_char.get('age', ''),
                    'occupation': syn_char.get('occupation', ''),
                    'personality': syn_char.get('personality', ''),
                    'appearance': syn_char.get('appearance', ''),
                    'traits': syn_char.get('traits', ''),
                    'desire': syn_char.get('desire', ''),
                    'role': syn_char.get('role', '')
                }
                characters.append(character)
            
            # 인물 데이터 설정 및 저장
            self.project_data.set_characters(characters)
            self.file_service.save_characters(characters)
            
            # 인물 탭 업데이트
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'tabs'):
                if 'characters' in self.parent.master.tabs:
                    self.parent.master.tabs['characters'].update_display()
        else:
            # 시놉시스에 등장인물이 없으면 인물 데이터 초기화
            self.project_data.set_characters([])
            self.file_service.save_characters([])
            
            # 인물 탭 업데이트
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'tabs'):
                if 'characters' in self.parent.master.tabs:
                    self.parent.master.tabs['characters'].update_display()

    def _sync_chapters_from_synopsis(self):
        """시놉시스의 챕터를 챕터 탭에 동기화"""
        synopsis = self.project_data.get_synopsis()
        synopsis_chapters = synopsis.get('chapters', {})
        
        if synopsis_chapters:
            # 시놉시스의 챕터 딕셔너리를 챕터 리스트로 변환
            chapters = []
            
            # 챕터 번호 순서대로 정렬
            sorted_keys = sorted(synopsis_chapters.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
            
            for key in sorted_keys:
                chapter_content = synopsis_chapters[key]
                
                # 챕터 내용에서 번호, 단계, 내용 추출
                # 형식: "챕터 1 (도입): 내용" 또는 "[도입] 제목: 내용" 또는 "내용"
                chapter_number = None
                chapter_stage = None
                chapter_title = None
                content = str(chapter_content)
                
                # 패턴 1: "챕터 1 (도입): 내용" 형식
                pattern1 = r'챕터\s*(\d+)\s*\(([^)]+)\)\s*[:：]\s*(.+)'
                match1 = re.match(pattern1, content, re.DOTALL)
                if match1:
                    chapter_number = int(match1.group(1))
                    chapter_stage = match1.group(2).strip()
                    content = match1.group(3).strip()
                else:
                    # 패턴 2: "[도입] 제목: 내용" 형식
                    pattern2 = r'\[([^\]]+)\]\s*([^:：]+?)\s*[:：]\s*(.+)'
                    match2 = re.match(pattern2, content, re.DOTALL)
                    if match2:
                        chapter_stage = match2.group(1).strip()  # [도입], [전개] 등
                        chapter_title = match2.group(2).strip()  # 제목
                        content = match2.group(3).strip()
                    else:
                        # 패턴 3: "chapter_1" 키에서 번호 추출
                        if '_' in key:
                            try:
                                chapter_number = int(key.split('_')[1])
                            except:
                                pass
                
                # 챕터 번호가 없으면 순서대로 할당
                if chapter_number is None:
                    chapter_number = len(chapters) + 1
                
                # 제목 결정: chapter_title이 있으면 사용, 없으면 chapter_stage 사용, 둘 다 없으면 기본값
                if chapter_title:
                    title = chapter_title
                elif chapter_stage:
                    title = chapter_stage
                else:
                    title = f'챕터 {chapter_number}'
                
                # 챕터 데이터 생성
                chapter = {
                    'chapter_number': chapter_number,
                    'title': title,
                    'content': content,
                    'script': ''  # 대본은 나중에 생성
                }
                chapters.append(chapter)
            
            # 챕터 데이터 설정 및 저장
            self.project_data.set_chapters(chapters)
            self.file_service.save_chapters(chapters)
            
            # 챕터 탭 업데이트
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'tabs'):
                if 'chapters' in self.parent.master.tabs:
                    self.parent.master.tabs['chapters'].update_display()
        else:
            # 시놉시스에 챕터가 없으면 챕터 데이터 초기화
            self.project_data.set_chapters([])
            self.file_service.save_chapters([])
            
            # 챕터 탭 업데이트
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, 'tabs'):
                if 'chapters' in self.parent.master.tabs:
                    self.parent.master.tabs['chapters'].update_display()

    def save(self) -> bool:
        """데이터 저장 (자동 저장되므로 항상 True 반환)"""
        return True
