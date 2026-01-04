"""
챕터 탭
막 > 에피소드 계층 구조로 표시합니다.
"""

import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab
import json


class ChapterDetailsInputTab(BaseTab):
    """챕터 탭 클래스"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        self.acts_data = {}  # 막별 에피소드 데이터
        self.current_act = None
        self.current_episode = None
        self.act_buttons = {}
        self.episode_notebook = None
        self.content_frame = None

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "챕터"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)  # 에피소드 영역이 확장

        # ========== 상단: 막 선택 영역 ==========
        act_frame = ttk.Frame(self.frame)
        act_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(10, 5))

        ttk.Label(
            act_frame,
            text="막 선택",
            font=("맑은 고딕", 11, "bold")
        ).pack(side=tk.LEFT, padx=(0, 15))

        # 막 버튼 컨테이너
        self.act_button_frame = ttk.Frame(act_frame)
        self.act_button_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ========== 하단: 에피소드 탭 + 콘텐츠 영역 (전체 공간 사용) ==========
        episode_frame = ttk.Frame(self.frame)
        episode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        episode_frame.columnconfigure(0, weight=1)
        episode_frame.rowconfigure(0, weight=1)

        # 에피소드 Notebook (큰 탭)
        style = ttk.Style()
        style.configure(
            "Episode.TNotebook.Tab",
            font=("맑은 고딕", 11, "bold"),
            padding=[15, 8]
        )
        style.configure(
            "Episode.TNotebook",
            tabposition="n"
        )

        self.episode_notebook = ttk.Notebook(episode_frame, style="Episode.TNotebook")
        self.episode_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.episode_notebook.bind("<<NotebookTabChanged>>", self._on_episode_changed)

    def update_display(self):
        """화면 업데이트"""
        # 데이터 로드
        chapters = self.project_data.get_chapters()

        if not chapters:
            self._show_empty_state()
            return

        # 막별로 그룹화
        self.acts_data = self._group_by_act(chapters)

        # 막 버튼 생성
        self._create_act_buttons()

        # 첫 번째 막 선택
        if self.acts_data:
            first_act = list(self.acts_data.keys())[0]
            self._select_act(first_act)

    def _show_empty_state(self):
        """빈 상태 표시"""
        # 기존 버튼 제거
        for widget in self.act_button_frame.winfo_children():
            widget.destroy()

        # 에피소드 탭 제거
        for tab_id in self.episode_notebook.tabs():
            self.episode_notebook.forget(tab_id)

        # 빈 메시지
        empty_frame = ttk.Frame(self.episode_notebook, padding=20)
        self.episode_notebook.add(empty_frame, text="데이터 없음")
        ttk.Label(
            empty_frame,
            text="등록된 챕터/에피소드가 없습니다.\n\nscenes 폴더에 에피소드 JSON 파일을 추가하세요.",
            font=("맑은 고딕", 11),
            justify=tk.CENTER
        ).pack(expand=True)

    def _group_by_act(self, chapters: list) -> dict:
        """챕터들을 막별로 그룹화"""
        acts = {}
        for chapter in chapters:
            act = chapter.get('act', '') or chapter.get('_folder', '기타')
            act_title = chapter.get('act_title', '')

            # 막 키 생성 (예: "1막" 또는 "1막_일상의붕괴")
            act_key = act
            if not act_key:
                # _folder에서 추출 (예: "1막_일상의붕괴")
                folder = chapter.get('_folder', '')
                if folder:
                    act_key = folder.split('_')[0] if '_' in folder else folder

            if not act_key:
                act_key = '기타'

            if act_key not in acts:
                acts[act_key] = {
                    'title': act_title or act_key,
                    'episodes': []
                }

            acts[act_key]['episodes'].append(chapter)

        # 각 막의 에피소드를 번호순 정렬
        for act_key in acts:
            acts[act_key]['episodes'].sort(key=lambda x: x.get('chapter_number', 0))

        return acts

    def _create_act_buttons(self):
        """막 버튼들 생성"""
        # 기존 버튼 제거
        for widget in self.act_button_frame.winfo_children():
            widget.destroy()
        self.act_buttons.clear()

        # 막 순서 정렬 (1막, 2막, 3막...)
        sorted_acts = sorted(self.acts_data.keys(), key=lambda x: self._extract_act_number(x))

        for act_key in sorted_acts:
            act_info = self.acts_data[act_key]
            episode_count = len(act_info['episodes'])

            # 버튼 텍스트: "1막 (3)" 형태
            btn_text = f"  {act_key}  ({episode_count})  "

            btn = ttk.Button(
                self.act_button_frame,
                text=btn_text,
                command=lambda a=act_key: self._select_act(a),
                width=15
            )
            btn.pack(side=tk.LEFT, padx=3, pady=2)
            self.act_buttons[act_key] = btn

    def _extract_act_number(self, act_key: str) -> int:
        """막 키에서 숫자 추출 (정렬용)"""
        import re
        match = re.search(r'(\d+)', act_key)
        return int(match.group(1)) if match else 999

    def _select_act(self, act_key: str):
        """막 선택"""
        self.current_act = act_key

        # 버튼 상태 업데이트
        for key, btn in self.act_buttons.items():
            if key == act_key:
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])

        # 해당 막의 에피소드 탭 생성
        self._create_episode_tabs(act_key)

    def _create_episode_tabs(self, act_key: str):
        """선택된 막의 에피소드 탭들 생성"""
        # 기존 탭 제거
        for tab_id in self.episode_notebook.tabs():
            self.episode_notebook.forget(tab_id)

        act_info = self.acts_data.get(act_key, {})
        episodes = act_info.get('episodes', [])

        if not episodes:
            empty_frame = ttk.Frame(self.episode_notebook, padding=20)
            self.episode_notebook.add(empty_frame, text="에피소드 없음")
            return

        # 각 에피소드별 탭 생성
        for episode in episodes:
            ep_num = episode.get('chapter_number', 0)
            ep_title = episode.get('title', f'에피소드 {ep_num}')

            # 탭 프레임 - 전체 공간 사용
            tab_frame = ttk.Frame(self.episode_notebook)
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.rowconfigure(0, weight=1)

            # 탭 라벨: "EP01 갑작스러운이별" 형태
            tab_label = f"  EP{ep_num:02d}. {ep_title}  "

            self.episode_notebook.add(tab_frame, text=tab_label)

            # 에피소드 내용 표시
            self._create_episode_view(tab_frame, episode)

    def _on_episode_changed(self, event=None):
        """에피소드 탭 변경 시"""
        pass

    def _create_episode_view(self, parent_frame, episode: dict):
        """에피소드 정보 뷰 생성"""
        # 스크롤바를 위한 컨테이너 (pack 사용)
        container = ttk.Frame(parent_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 스크롤 가능한 캔버스
        canvas = tk.Canvas(container, highlightthickness=0, bg="white")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        # 내용을 담을 프레임
        content_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)

        # pack 배치 - 전체 공간 채우기
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 캔버스에 프레임 추가
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # 프레임 크기 변경 시 스크롤 영역 업데이트
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        content_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # 마우스 휠 스크롤
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", on_mousewheel)
        content_frame.bind("<MouseWheel>", on_mousewheel)

        # 2열 레이아웃 설정
        content_frame.columnconfigure(0, weight=0, minsize=130)  # 키 열
        content_frame.columnconfigure(1, weight=1)  # 값 열

        # 에피소드 정보 표시
        row = 0
        priority_keys = [
            'chapter_number', 'title', 'act', 'act_title', 'work_title',
            'main_locations', 'characters', 'core_emotion',
            'scenes', 'total_scenes', 'key_objects',
            'content', 'content_detail', 'script'
        ]

        # 우선 키 먼저 표시
        for key in priority_keys:
            if key in episode and episode[key]:
                row = self._add_info_row(content_frame, row, key, episode[key], canvas)

        # 나머지 키 표시
        for key, value in episode.items():
            if key not in priority_keys and not key.startswith('_') and value:
                row = self._add_info_row(content_frame, row, key, value, canvas)

    def _add_info_row(self, parent, row: int, key: str, value, canvas) -> int:
        """정보 행 추가"""
        display_key = self._get_display_key(key)
        formatted_value = self._format_value(value)

        # 키 레이블 (왼쪽)
        key_label = ttk.Label(
            parent,
            text=display_key,
            font=("맑은 고딕", 11, "bold"),
            foreground="#0066cc",
            anchor="e",
            width=14
        )
        key_label.grid(row=row, column=0, sticky=(tk.E, tk.N), padx=(10, 15), pady=10)

        # 값 표시 (오른쪽)
        if '\n' in formatted_value or len(formatted_value) > 80:
            # 여러 줄 텍스트
            line_count = min(formatted_value.count('\n') + 1, 15)
            value_text = tk.Text(
                parent,
                wrap=tk.WORD,
                font=("맑은 고딕", 10),
                height=line_count,
                relief=tk.FLAT,
                bg="#f8f8f8",
                padx=10,
                pady=8
            )
            value_text.insert(1.0, formatted_value)
            value_text.config(state=tk.DISABLED)
            value_text.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)

            # 마우스 휠 이벤트 전파
            def on_text_mousewheel(event, c=canvas):
                c.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return "break"
            value_text.bind("<MouseWheel>", on_text_mousewheel)
        else:
            # 한 줄 텍스트
            value_label = ttk.Label(
                parent,
                text=formatted_value,
                font=("맑은 고딕", 11),
                wraplength=700,
                justify=tk.LEFT,
                anchor="w"
            )
            value_label.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=10)

        # 구분선
        separator = ttk.Separator(parent, orient=tk.HORIZONTAL)
        separator.grid(row=row + 1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=2)

        return row + 2

    def _get_display_key(self, key: str) -> str:
        """키를 한글 표시명으로 변환"""
        key_map = {
            'chapter_number': '에피소드',
            'title': '제목',
            'content': '내용 요약',
            'content_detail': '상세 내용',
            'script': '대본',
            'scenes': '장면 목록',
            'description': '설명',
            'act': '막',
            'act_title': '막 제목',
            'episode': '에피소드',
            'summary': '요약',
            'work_title': '작품명',
            'main_locations': '주요 장소',
            'characters': '등장인물',
            'core_emotion': '핵심 감정',
            'total_scenes': '장면 수',
            'key_objects': '핵심 오브젝트'
        }
        return key_map.get(key, key)

    def _format_value(self, value) -> str:
        """값을 읽기 쉽게 포맷팅"""
        if isinstance(value, dict):
            lines = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{k}:")
                    lines.append(f"  {json.dumps(v, ensure_ascii=False, indent=2)}")
                else:
                    lines.append(f"{k}: {v}")
            return '\n'.join(lines)
        elif isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                return ', '.join(value) if len(value) <= 5 else '\n'.join([f"• {item}" for item in value])
            else:
                lines = []
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        # scenes 구조 (scene_id, scene_name 등)
                        if 'scene_id' in item or 'scene_name' in item:
                            scene_id = item.get('scene_id', f's{i+1:02d}')
                            scene_name = item.get('scene_name', '')
                            location = item.get('location', '')
                            time_str = item.get('time', '')
                            emotion = item.get('emotion', '')

                            line = f"[{scene_id}] {scene_name}"
                            if location:
                                line += f"\n      장소: {location}"
                            if time_str:
                                line += f" | 시간: {time_str}"
                            if emotion:
                                line += f" | 감정: {emotion}"
                            lines.append(line)
                        # key_objects 구조
                        elif 'object' in item:
                            obj_name = item.get('object', '')
                            symbol = item.get('symbol', '')
                            scenes = item.get('scenes', [])
                            line = f"• {obj_name}"
                            if symbol:
                                line += f" - {symbol}"
                            if scenes:
                                line += f" (장면: {', '.join(scenes)})"
                            lines.append(line)
                        else:
                            # 기타 딕셔너리
                            scene_num = item.get('scene_number', i + 1)
                            scene_desc = item.get('description', item.get('content', ''))
                            if scene_desc:
                                lines.append(f"[장면 {scene_num}] {scene_desc[:100]}...")
                            else:
                                lines.append(json.dumps(item, ensure_ascii=False))
                    else:
                        lines.append(f"• {item}")
                return '\n'.join(lines)
        else:
            return str(value) if value else ""

    def save(self) -> bool:
        """데이터 저장"""
        return True
