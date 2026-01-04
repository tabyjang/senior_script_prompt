"""
장면 프롬프트 탭
에피소드별 장면 프롬프트를 막(Act) > 에피소드 구조로 표시합니다.
대본 탭과 동일한 사이드바 트리뷰 구조를 사용합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import re
import json
from typing import Optional, Dict, List, Any
from .base_tab import BaseTab
from utils.ui_helpers import ActEpisodeTreeView


class ImagePromptsInputTab(BaseTab):
    """장면 프롬프트 탭 클래스 - 사이드바 트리뷰 구조"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        # 데이터
        self.episodes_by_act: Dict[str, List[Dict[str, Any]]] = {}
        self.current_act: str = ""
        self.current_episode_num: int = 0
        self.current_scenes: List[Dict[str, Any]] = []

        # UI 요소
        self.tree_view: Optional[ActEpisodeTreeView] = None
        self.info_label: Optional[ttk.Label] = None
        self.scenes_frame: Optional[ttk.Frame] = None
        self.canvas: Optional[tk.Canvas] = None
        self.scrollbar: Optional[ttk.Scrollbar] = None

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "장면 프롬프트"

    def create_ui(self):
        """UI 생성 - 사이드바 트리뷰 + 장면 프롬프트 영역"""
        self.frame.columnconfigure(0, weight=0)  # 사이드바
        self.frame.columnconfigure(1, weight=1)  # 콘텐츠
        self.frame.rowconfigure(0, weight=1)

        # ===== 왼쪽: 사이드바 트리뷰 =====
        sidebar_frame = ttk.Frame(self.frame, padding=(5, 5, 0, 5))
        sidebar_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))

        self.tree_view = ActEpisodeTreeView(
            parent=sidebar_frame,
            on_select_callback=self._on_episode_select,
            on_select_all_callback=self._on_show_all,
            width=240,
            all_button_text="전체 장면"
        )

        # ===== 오른쪽: 콘텐츠 영역 =====
        content_frame = ttk.Frame(self.frame, padding=5)
        content_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        # 상단: 정보 표시 + 복사 버튼
        header_frame = ttk.Frame(content_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        header_frame.columnconfigure(0, weight=1)

        self.info_label = ttk.Label(
            header_frame,
            text="에피소드를 선택하세요",
            font=("맑은 고딕", 11, "bold"),
            foreground="#333"
        )
        self.info_label.grid(row=0, column=0, sticky=tk.W)

        # 복사 버튼
        ttk.Button(
            header_frame,
            text="전체 복사",
            command=self._copy_all_prompts
        ).grid(row=0, column=1, sticky=tk.E)

        # 장면 프롬프트 표시 영역 (스크롤 가능)
        scenes_container = ttk.LabelFrame(content_frame, text="장면 프롬프트", padding=5)
        scenes_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scenes_container.columnconfigure(0, weight=1)
        scenes_container.rowconfigure(0, weight=1)

        # Canvas + Scrollbar
        self.canvas = tk.Canvas(scenes_container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(scenes_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scenes_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scenes_frame, anchor="nw")

        self.scenes_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # 마우스 휠 바인딩
        self._bind_mousewheel()

        # 배치
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def _bind_mousewheel(self):
        """마우스 휠 이벤트 바인딩"""
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        def bind_to_widget(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_to_widget(child)

        self.canvas.bind("<MouseWheel>", on_mousewheel)
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        bind_to_widget(self.scenes_frame)

    def update_display(self):
        """화면 업데이트 - scenes 폴더에서 장면 데이터 로드"""
        # scenes 폴더에서 에피소드 데이터 로드
        self.episodes_by_act = self._load_scene_episodes()

        if not self.episodes_by_act:
            self._show_no_data_message()
            return

        # 트리뷰에 데이터 로드
        if self.tree_view:
            self.tree_view.load_data(self.episodes_by_act)

        # 첫 에피소드 자동 선택
        if self.episodes_by_act:
            first_act = list(self.episodes_by_act.keys())[0]
            episodes = self.episodes_by_act.get(first_act, [])
            if episodes:
                self._on_episode_select(first_act, episodes[0])

    def _load_scene_episodes(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        scenes 폴더에서 에피소드별 장면 데이터 로드

        Returns:
            막별 에피소드 리스트 딕셔너리
        """
        episodes_by_act: Dict[str, List[Dict[str, Any]]] = {}

        try:
            # scenes 폴더 찾기
            scenes_folder = self.file_service.project_path / "scenes"
            if not scenes_folder.exists():
                return episodes_by_act

            # 각 Act 폴더 검색
            for act_folder in sorted(scenes_folder.iterdir()):
                if not act_folder.is_dir():
                    continue

                act_name = act_folder.name
                episodes_list: List[Dict[str, Any]] = []

                # 각 JSON 파일 로드
                for json_file in sorted(act_folder.glob("*.json")):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            ep_data = json.load(f)

                        metadata = ep_data.get('metadata', {})
                        scenes = ep_data.get('scenes', [])

                        # 에피소드 번호 추출
                        ep_num = metadata.get('episode') or metadata.get('chapter') or 0
                        if not ep_num:
                            match = re.search(r'(?:EP)?(\d+)', json_file.stem)
                            if match:
                                ep_num = int(match.group(1))

                        # 제목 추출
                        ep_title = metadata.get('episode_title') or metadata.get('chapter_title') or ''
                        if not ep_title:
                            title_match = re.search(r'(?:EP\d+_|\d+화_)(.+)$', json_file.stem)
                            if title_match:
                                ep_title = title_match.group(1)
                            else:
                                ep_title = json_file.stem

                        episode_data = {
                            "episode_num": ep_num,
                            "title": ep_title,
                            "scenes": scenes,
                            "file_path": str(json_file),
                            "filename": json_file.name,
                            "scene_count": len(scenes)
                        }

                        episodes_list.append(episode_data)

                    except Exception:
                        pass

                # 에피소드 번호로 정렬
                episodes_list.sort(key=lambda x: x.get('episode_num', 0))

                if episodes_list:
                    episodes_by_act[act_name] = episodes_list

        except Exception:
            pass

        return episodes_by_act

    def _show_no_data_message(self):
        """데이터 없음 메시지"""
        if self.tree_view:
            self.tree_view.load_data({})

        if self.info_label:
            self.info_label.config(text="장면 데이터 없음")

        # 기존 위젯 제거
        for widget in self.scenes_frame.winfo_children():
            widget.destroy()

        ttk.Label(
            self.scenes_frame,
            text="장면 데이터가 없습니다.\n\n"
                 "프로젝트 폴더 내에 'scenes' 폴더를 확인해주세요.\n"
                 "예: scenes/Act1_제목/EP01_에피소드제목.json",
            font=("맑은 고딕", 11),
            justify=tk.CENTER
        ).pack(pady=50)

    def _on_episode_select(self, act_name: str, episode_data: Dict[str, Any]):
        """에피소드 선택 시 콜백"""
        self.current_act = act_name
        self.current_episode_num = episode_data.get("episode_num", 0)
        self.current_scenes = episode_data.get("scenes", [])

        # 정보 표시
        ep_title = episode_data.get("title", "")
        scene_count = len(self.current_scenes)
        act_display = self._get_act_display_short(act_name)

        if self.info_label:
            self.info_label.config(
                text=f"{act_display} > EP{self.current_episode_num:02d}: {ep_title}  ({scene_count}개 장면)"
            )

        # 장면 프롬프트 표시
        self._display_scenes(self.current_scenes)

    def _on_show_all(self, act_name: Optional[str]):
        """
        전체 보기 콜백
        act_name이 None이면 전체, 아니면 해당 막 전체
        """
        if act_name is None:
            self._show_all_scenes()
        else:
            self._show_act_scenes(act_name)

    def _display_scenes(self, scenes: List[Dict[str, Any]]):
        """장면 프롬프트 위젯들 표시"""
        # 기존 위젯 제거
        for widget in self.scenes_frame.winfo_children():
            widget.destroy()

        if not scenes:
            ttk.Label(
                self.scenes_frame,
                text="장면 프롬프트가 없습니다.",
                font=("맑은 고딕", 11)
            ).pack(pady=20)
            return

        # 각 장면별 프롬프트 표시
        for i, scene in enumerate(scenes, start=1):
            self._create_scene_widget(i, scene)

        # 마우스 휠 재바인딩
        self._rebind_mousewheel()

    def _create_scene_widget(self, scene_num: int, scene: Dict[str, Any]):
        """단일 장면 프롬프트 위젯 생성"""
        # 장면 정보 추출
        scene_title = scene.get('scene_title', scene.get('title', f'장면 {scene_num}'))
        location = scene.get('location', '')
        emotion = scene.get('emotion', scene.get('core_emotion', ''))
        characters = scene.get('characters', [])

        # 이미지 프롬프트 추출
        image_prompts = scene.get('image_prompts', {})
        positive = image_prompts.get('positive', '')
        negative = image_prompts.get('negative', '')

        # 또는 다른 형태의 프롬프트
        if not positive:
            positive = scene.get('positive_prompt', scene.get('prompt', ''))
        if not negative:
            negative = scene.get('negative_prompt', '')

        # 프레임 생성
        scene_frame = ttk.LabelFrame(
            self.scenes_frame,
            text=f"장면 {scene_num}: {scene_title}",
            padding=10
        )
        scene_frame.pack(fill=tk.X, padx=5, pady=5)

        # 장면 정보 (한 줄)
        info_parts = []
        if location:
            info_parts.append(f"장소: {location}")
        if emotion:
            info_parts.append(f"감정: {emotion}")
        if characters:
            char_names = ', '.join(characters) if isinstance(characters, list) else str(characters)
            info_parts.append(f"등장: {char_names}")

        if info_parts:
            info_text = " | ".join(info_parts)
            info_label = ttk.Label(
                scene_frame,
                text=info_text,
                font=("맑은 고딕", 9),
                foreground="gray"
            )
            info_label.pack(anchor=tk.W, pady=(0, 5))

        # Positive 프롬프트
        if positive:
            pos_frame = ttk.Frame(scene_frame)
            pos_frame.pack(fill=tk.X, pady=2)

            ttk.Label(
                pos_frame,
                text="Positive:",
                font=("맑은 고딕", 9, "bold"),
                foreground="#2e7d32"
            ).pack(anchor=tk.W)

            pos_text = tk.Text(
                pos_frame,
                wrap=tk.WORD,
                font=("맑은 고딕", 9),
                height=3,
                bg="#f5f5f5",
                relief=tk.FLAT,
                padx=5,
                pady=5
            )
            pos_text.pack(fill=tk.X, pady=2)
            pos_text.insert(1.0, positive)
            pos_text.config(state=tk.DISABLED)

            # 복사 버튼
            ttk.Button(
                pos_frame,
                text="복사",
                width=6,
                command=lambda p=positive: self._copy_to_clipboard(p)
            ).pack(anchor=tk.E)

        # Negative 프롬프트
        if negative:
            neg_frame = ttk.Frame(scene_frame)
            neg_frame.pack(fill=tk.X, pady=2)

            ttk.Label(
                neg_frame,
                text="Negative:",
                font=("맑은 고딕", 9, "bold"),
                foreground="#c62828"
            ).pack(anchor=tk.W)

            neg_text = tk.Text(
                neg_frame,
                wrap=tk.WORD,
                font=("맑은 고딕", 9),
                height=2,
                bg="#fff3e0",
                relief=tk.FLAT,
                padx=5,
                pady=5
            )
            neg_text.pack(fill=tk.X, pady=2)
            neg_text.insert(1.0, negative)
            neg_text.config(state=tk.DISABLED)

            ttk.Button(
                neg_frame,
                text="복사",
                width=6,
                command=lambda n=negative: self._copy_to_clipboard(n)
            ).pack(anchor=tk.E)

        # 프롬프트가 없는 경우
        if not positive and not negative:
            ttk.Label(
                scene_frame,
                text="(프롬프트 없음)",
                font=("맑은 고딕", 9),
                foreground="gray"
            ).pack(anchor=tk.W)

    def _show_act_scenes(self, act_name: str):
        """특정 막의 모든 장면 표시"""
        episodes = self.episodes_by_act.get(act_name, [])
        if not episodes:
            return

        self.current_act = act_name
        self.current_episode_num = 0

        # 모든 장면 수집
        all_scenes = []
        for ep in episodes:
            ep_num = ep.get("episode_num", 0)
            ep_title = ep.get("title", "")
            scenes = ep.get("scenes", [])
            for scene in scenes:
                scene_with_ep = dict(scene)
                scene_with_ep['_episode_info'] = f"EP{ep_num:02d}: {ep_title}"
                all_scenes.append(scene_with_ep)

        # 정보 표시
        act_display = self._get_act_display_short(act_name)
        if self.info_label:
            self.info_label.config(
                text=f"{act_display} 전체  ({len(episodes)}개 에피소드, {len(all_scenes)}개 장면)"
            )

        # 기존 위젯 제거
        for widget in self.scenes_frame.winfo_children():
            widget.destroy()

        # 에피소드별로 구분해서 장면 표시
        scene_idx = 0
        for ep in episodes:
            ep_num = ep.get("episode_num", 0)
            ep_title = ep.get("title", "")
            scenes = ep.get("scenes", [])

            # 에피소드 구분 라벨
            ep_label = ttk.Label(
                self.scenes_frame,
                text=f"━━━ EP{ep_num:02d}: {ep_title} ({len(scenes)}개 장면) ━━━",
                font=("맑은 고딕", 10, "bold"),
                foreground="#1565c0"
            )
            ep_label.pack(fill=tk.X, pady=(15, 5), padx=5)

            for scene in scenes:
                scene_idx += 1
                self._create_scene_widget(scene_idx, scene)

        self._rebind_mousewheel()

    def _show_all_scenes(self):
        """전체 장면 표시"""
        self.current_act = ""
        self.current_episode_num = 0

        total_scenes = 0
        total_episodes = 0

        for act_name, episodes in self.episodes_by_act.items():
            total_episodes += len(episodes)
            for ep in episodes:
                total_scenes += len(ep.get("scenes", []))

        # 정보 표시
        if self.info_label:
            self.info_label.config(
                text=f"전체 장면  ({len(self.episodes_by_act)}막 {total_episodes}개 에피소드, {total_scenes}개 장면)"
            )

        # 기존 위젯 제거
        for widget in self.scenes_frame.winfo_children():
            widget.destroy()

        # 막별로 구분해서 표시
        scene_idx = 0
        sorted_acts = sorted(
            self.episodes_by_act.keys(),
            key=lambda x: self._act_sort_key(x)
        )

        for act_name in sorted_acts:
            episodes = self.episodes_by_act.get(act_name, [])
            act_display = self._get_act_display_short(act_name)

            # 막 구분 라벨
            act_label = ttk.Label(
                self.scenes_frame,
                text=f"══════ {act_display} ══════",
                font=("맑은 고딕", 11, "bold"),
                foreground="#4a148c"
            )
            act_label.pack(fill=tk.X, pady=(20, 5), padx=5)

            for ep in episodes:
                ep_num = ep.get("episode_num", 0)
                ep_title = ep.get("title", "")
                scenes = ep.get("scenes", [])

                # 에피소드 구분 라벨
                ep_label = ttk.Label(
                    self.scenes_frame,
                    text=f"── EP{ep_num:02d}: {ep_title} ({len(scenes)}개 장면) ──",
                    font=("맑은 고딕", 10),
                    foreground="#1565c0"
                )
                ep_label.pack(fill=tk.X, pady=(10, 3), padx=10)

                for scene in scenes:
                    scene_idx += 1
                    self._create_scene_widget(scene_idx, scene)

        self._rebind_mousewheel()

    def _rebind_mousewheel(self):
        """마우스 휠 재바인딩"""
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        def bind_to_widget(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_to_widget(child)

        self.canvas.bind("<MouseWheel>", on_mousewheel)
        bind_to_widget(self.scenes_frame)

    def _copy_to_clipboard(self, text: str):
        """텍스트를 클립보드에 복사"""
        self.frame.clipboard_clear()
        self.frame.clipboard_append(text)

        # 복사 완료 알림
        original_text = self.info_label.cget("text")
        self.info_label.config(text="복사 완료!", foreground="green")
        self.frame.after(1500, lambda: self.info_label.config(text=original_text, foreground="#333"))

    def _copy_all_prompts(self):
        """현재 표시된 모든 프롬프트 복사"""
        if not self.current_scenes and self.current_episode_num > 0:
            return

        lines = []

        # 현재 선택된 상태에 따라 다르게 처리
        if self.current_episode_num > 0:
            # 단일 에피소드
            for i, scene in enumerate(self.current_scenes, start=1):
                self._append_scene_to_lines(lines, i, scene)
        else:
            # 전체 또는 막 전체
            scene_idx = 0
            for act_name, episodes in self.episodes_by_act.items():
                if self.current_act and self.current_act != act_name:
                    continue

                for ep in episodes:
                    ep_num = ep.get("episode_num", 0)
                    ep_title = ep.get("title", "")
                    scenes = ep.get("scenes", [])

                    lines.append(f"\n=== EP{ep_num:02d}: {ep_title} ===\n")

                    for scene in scenes:
                        scene_idx += 1
                        self._append_scene_to_lines(lines, scene_idx, scene)

        if lines:
            all_text = "\n".join(lines)
            self._copy_to_clipboard(all_text)

    def _append_scene_to_lines(self, lines: List[str], scene_num: int, scene: Dict[str, Any]):
        """장면 프롬프트를 lines에 추가"""
        scene_title = scene.get('scene_title', scene.get('title', f'장면 {scene_num}'))
        image_prompts = scene.get('image_prompts', {})
        positive = image_prompts.get('positive', '') or scene.get('positive_prompt', scene.get('prompt', ''))
        negative = image_prompts.get('negative', '') or scene.get('negative_prompt', '')

        lines.append(f"[장면 {scene_num}] {scene_title}")
        if positive:
            lines.append(f"Positive: {positive}")
        if negative:
            lines.append(f"Negative: {negative}")
        lines.append("")

    def _get_act_display_short(self, act_name: str) -> str:
        """막 이름을 짧은 표시용 텍스트로 변환"""
        match = re.match(r'Act(\d+)(?:-(\d+))?_(.+)', act_name)
        if match:
            main_num = match.group(1)
            sub_num = match.group(2)
            title = match.group(3)
            if sub_num:
                return f"{main_num}-{sub_num}막: {title}"
            else:
                return f"{main_num}막: {title}"
        return act_name

    def _act_sort_key(self, act_name: str) -> tuple:
        """막 이름 정렬 키"""
        match = re.search(r'Act(\d+)(?:-(\d+))?', act_name)
        if match:
            main_num = int(match.group(1))
            sub_num = int(match.group(2)) if match.group(2) else 0
            return (main_num, sub_num)
        return (999, 0)

    def save(self) -> bool:
        """데이터 저장 (읽기 전용이므로 항상 True)"""
        return True
