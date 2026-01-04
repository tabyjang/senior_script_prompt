"""
ComfyUI Tab
ComfyUI integration for batch image generation.
선택한 프로젝트의 캐릭터 이미지 프롬프트와 장면 프롬프트만 표시합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from .base_tab import BaseTab


class ComfyUITab(BaseTab):
    """ComfyUI batch processing tab"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """Initialize"""
        self.comfyui = None
        self.builder = None
        self.is_processing = False
        self.stop_requested = False

        # 프롬프트 데이터
        self.prompt_items: List[Dict[str, Any]] = []

        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "ComfyUI"

    def create_ui(self):
        """Create UI"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # Top: Connection status and controls
        top_frame = ttk.LabelFrame(self.frame, text="ComfyUI 연결", padding=10)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        top_frame.columnconfigure(1, weight=1)

        # Status indicator
        ttk.Label(top_frame, text="상태:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.status_label = ttk.Label(top_frame, text="연결 안됨", foreground="gray")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Connect button
        self.connect_btn = ttk.Button(top_frame, text="연결", command=self._connect)
        self.connect_btn.grid(row=0, column=2, padx=5)

        # Workflow template
        ttk.Label(top_frame, text="워크플로우:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=(10, 0))
        self.workflow_label = ttk.Label(top_frame, text="로드 안됨", foreground="gray")
        self.workflow_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(10, 0))

        self.load_workflow_btn = ttk.Button(top_frame, text="워크플로우 로드", command=self._load_workflow)
        self.load_workflow_btn.grid(row=1, column=2, padx=5, pady=(10, 0))

        # Resolution selector
        ttk.Label(top_frame, text="해상도:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=(10, 0))

        res_frame = ttk.Frame(top_frame)
        res_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=(10, 0))

        self.resolution_var = tk.StringVar(value="HD")
        self.resolution_options = {
            "HD": (1920, 1088),
            "2K": (2560, 1408),
            "4K": (3840, 2176)
        }

        for res_name in ["HD", "2K", "4K"]:
            w, h = self.resolution_options[res_name]
            ttk.Radiobutton(
                res_frame,
                text=f"{res_name} ({w}x{h})",
                variable=self.resolution_var,
                value=res_name,
                command=self._on_resolution_changed
            ).pack(side=tk.LEFT, padx=10)

        # Main content: Left (prompt list) | Right (log)
        main_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Left: Prompt list
        left_frame = ttk.LabelFrame(main_paned, text="프롬프트 목록", padding=10)
        main_paned.add(left_frame, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        # Project info and refresh
        info_frame = ttk.Frame(left_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.project_label = ttk.Label(info_frame, text="프로젝트: -", font=("맑은 고딕", 10, "bold"))
        self.project_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(info_frame, text="새로고침", command=self._refresh_prompt_list).pack(side=tk.RIGHT, padx=5)

        # Filter frame
        filter_frame = ttk.Frame(left_frame)
        filter_frame.grid(row=0, column=0, sticky=tk.E, pady=(0, 10))

        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="전체", variable=self.filter_var, value="all",
                        command=self._refresh_prompt_list).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="캐릭터", variable=self.filter_var, value="character",
                        command=self._refresh_prompt_list).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="장면", variable=self.filter_var, value="scene",
                        command=self._refresh_prompt_list).pack(side=tk.LEFT, padx=5)

        # Prompt list with treeview
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("type", "name", "count", "status")
        self.prompt_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        self.prompt_tree.heading("type", text="타입")
        self.prompt_tree.heading("name", text="이름")
        self.prompt_tree.heading("count", text="프롬프트")
        self.prompt_tree.heading("status", text="상태")
        self.prompt_tree.column("type", width=80)
        self.prompt_tree.column("name", width=200)
        self.prompt_tree.column("count", width=80)
        self.prompt_tree.column("status", width=80)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.prompt_tree.yview)
        self.prompt_tree.configure(yscrollcommand=scrollbar.set)

        self.prompt_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Selection buttons
        sel_frame = ttk.Frame(left_frame)
        sel_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(sel_frame, text="전체 선택", command=self._select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(sel_frame, text="선택 해제", command=self._deselect_all).pack(side=tk.LEFT, padx=5)

        # Right: Log and controls
        right_frame = ttk.LabelFrame(main_paned, text="생성 로그", padding=10)
        main_paned.add(right_frame, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # Log viewer
        self.log_viewer = scrolledtext.ScrolledText(
            right_frame,
            width=50,
            height=20,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.log_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(right_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        self.progress_label = ttk.Label(right_frame, text="준비")
        self.progress_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))

        # Bottom: Action buttons
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=10)

        self.generate_btn = ttk.Button(
            bottom_frame,
            text="선택 항목 생성",
            command=self._generate_selected,
            state=tk.DISABLED
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            bottom_frame,
            text="중지",
            command=self._stop_generation,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(bottom_frame, text="로그 지우기", command=self._clear_log).pack(side=tk.RIGHT, padx=5)

    def update_display(self):
        """Update display - 현재 프로젝트의 프롬프트 로드"""
        self._refresh_prompt_list()

    def _refresh_prompt_list(self):
        """현재 프로젝트의 프롬프트 목록 새로고침"""
        # Clear existing items
        for item in self.prompt_tree.get_children():
            self.prompt_tree.delete(item)

        self.prompt_items = []

        # 프로젝트 경로 확인
        project_path = self.file_service.project_path
        if not project_path or not project_path.exists():
            self.project_label.config(text="프로젝트: (선택 안됨)")
            return

        project_name = project_path.name
        self.project_label.config(text=f"프로젝트: {project_name}")

        filter_type = self.filter_var.get()

        # 1. 캐릭터 이미지 프롬프트 로드
        if filter_type in ("all", "character"):
            self._load_character_prompts(project_path)

        # 2. 장면 프롬프트 로드
        if filter_type in ("all", "scene"):
            self._load_scene_prompts(project_path)

        # 통계 로그
        char_count = sum(1 for p in self.prompt_items if p["type"] == "캐릭터")
        scene_count = sum(1 for p in self.prompt_items if p["type"] == "장면")
        self._log(f"로드 완료: 캐릭터 {char_count}개, 장면 {scene_count}개")

    def _load_character_prompts(self, project_path: Path):
        """캐릭터 이미지 프롬프트 로드"""
        # characters 폴더 확인
        char_dirs = [
            project_path / "characters",
            project_path / "02_characters"
        ]

        for char_dir in char_dirs:
            if not char_dir.exists():
                continue

            # image_prompts 폴더 확인
            prompts_dir = char_dir / "image_prompts"
            if prompts_dir.exists():
                for json_file in sorted(prompts_dir.glob("*.json")):
                    self._add_character_prompt_file(json_file)

            # 캐릭터 프로필 파일에서도 프롬프트 확인
            for json_file in sorted(char_dir.glob("*.json")):
                self._add_character_from_profile(json_file)

    def _add_character_prompt_file(self, json_file: Path):
        """캐릭터 이미지 프롬프트 파일 추가"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            char_name = data.get("character_name", json_file.stem)
            prompts = data.get("image_generation_prompts", {})
            prompt_count = len(prompts)

            if prompt_count > 0:
                item_data = {
                    "type": "캐릭터",
                    "name": char_name,
                    "count": prompt_count,
                    "file_path": str(json_file),
                    "prompts": prompts,
                    "source": "image_prompts"
                }
                self.prompt_items.append(item_data)

                item_id = self.prompt_tree.insert(
                    "", "end",
                    values=("캐릭터", char_name, f"{prompt_count}개", "준비")
                )
                item_data["tree_id"] = item_id

        except Exception as e:
            pass

    def _add_character_from_profile(self, json_file: Path):
        """캐릭터 프로필 파일에서 이미지 프롬프트 추가"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 캐릭터 이름 추출 (다양한 형식 지원)
            char_name = (
                data.get("name", "") or
                data.get("character_name", "") or
                data.get("metadata", {}).get("character_name_kr", "") or
                data.get("character_info", {}).get("name_kr", "")
            )
            if not char_name:
                return

            # 이미 추가된 캐릭터인지 확인
            for item in self.prompt_items:
                if item["type"] == "캐릭터" and item["name"] == char_name:
                    return

            prompts = {}
            prompt_count = 0

            # 1. versions 배열 형식 (새 구조)
            versions = data.get("versions", [])
            if versions and isinstance(versions, list):
                for i, ver in enumerate(versions, start=1):
                    if isinstance(ver, dict) and ver.get("positive"):
                        prompts[f"prompt_{i}"] = {
                            "combined": ver.get("positive", ""),
                            "version_id": ver.get("version_id", ""),
                            "version_name": ver.get("version_name", ""),
                            "description": ver.get("description", "")
                        }
                prompt_count = len(prompts)

            # 2. image_generation_prompts 형식 (기존 구조)
            if prompt_count == 0:
                old_prompts = data.get("image_generation_prompts", {})
                if isinstance(old_prompts, str):
                    try:
                        old_prompts = json.loads(old_prompts)
                    except:
                        old_prompts = {}

                if isinstance(old_prompts, dict):
                    prompts = old_prompts
                    prompt_count = len([k for k in prompts.keys() if k.startswith("prompt_")])

            if prompt_count > 0:
                item_data = {
                    "type": "캐릭터",
                    "name": char_name,
                    "count": prompt_count,
                    "file_path": str(json_file),
                    "prompts": prompts,
                    "source": "profile"
                }
                self.prompt_items.append(item_data)

                item_id = self.prompt_tree.insert(
                    "", "end",
                    values=("캐릭터", char_name, f"{prompt_count}개", "준비")
                )
                item_data["tree_id"] = item_id

        except Exception as e:
            pass

    def _load_scene_prompts(self, project_path: Path):
        """장면 프롬프트 로드"""
        scenes_dir = project_path / "scenes"
        if not scenes_dir.exists():
            return

        # scenes 폴더 내의 모든 하위 폴더 검색 (1막_제목, Act1_제목 등 다양한 형식)
        for act_folder in sorted(scenes_dir.iterdir()):
            if not act_folder.is_dir():
                continue

            for json_file in sorted(act_folder.glob("*.json")):
                self._add_scene_file(json_file, act_folder.name)

        # scenes 폴더에 직접 있는 JSON 파일도 확인
        for json_file in sorted(scenes_dir.glob("*.json")):
            self._add_scene_file(json_file, "")

    def _add_scene_file(self, json_file: Path, act_name: str):
        """장면 파일 추가"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            scenes = data.get("scenes", [])
            scene_count = len(scenes)

            if scene_count > 0:
                # 이름 생성: Act_제목/EP01_제목
                display_name = f"{act_name}/{json_file.stem}"

                item_data = {
                    "type": "장면",
                    "name": display_name,
                    "count": scene_count,
                    "file_path": str(json_file),
                    "scenes": scenes,
                    "source": "scenes"
                }
                self.prompt_items.append(item_data)

                item_id = self.prompt_tree.insert(
                    "", "end",
                    values=("장면", display_name, f"{scene_count}개", "준비")
                )
                item_data["tree_id"] = item_id

        except Exception as e:
            pass

    def _connect(self):
        """Connect to ComfyUI"""
        try:
            from services.comfyui_service import ComfyUIService, ZImageWorkflowBuilder

            self.comfyui = ComfyUIService()

            if self.comfyui.is_connected():
                stats = self.comfyui.get_system_stats()
                version = stats.get("system", {}).get("comfyui_version", "unknown") if stats else "unknown"
                self.status_label.config(text=f"연결됨 (v{version})", foreground="green")
                self._log(f"ComfyUI v{version} 연결됨")

                # Try to load default workflow
                self._try_default_workflow()

                self.generate_btn.config(state=tk.NORMAL)
            else:
                self.status_label.config(text="연결 실패", foreground="red")
                self._log("ComfyUI 연결 실패. http://127.0.0.1:8188 에서 실행 중인지 확인하세요.")

        except Exception as e:
            self.status_label.config(text="오류", foreground="red")
            self._log(f"연결 오류: {e}")

    def _try_default_workflow(self):
        """Try to load default workflow template"""
        default_path = Path(__file__).parent.parent.parent / "prompts" / "workflows" / "z_image_turbo.json"
        if default_path.exists():
            self._load_workflow_file(str(default_path))

    def _load_workflow(self):
        """Load workflow template file"""
        file_path = filedialog.askopenfilename(
            title="ComfyUI 워크플로우 선택 (API 형식)",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path(__file__).parent.parent.parent / "prompts" / "workflows")
        )
        if file_path:
            self._load_workflow_file(file_path)

    def _load_workflow_file(self, path: str):
        """Load workflow from file"""
        try:
            from services.comfyui_service import ZImageWorkflowBuilder

            self.builder = ZImageWorkflowBuilder(path)
            if self.builder.template:
                filename = Path(path).name
                self.workflow_label.config(text=filename, foreground="green")
                self._log(f"워크플로우 로드: {filename}")
            else:
                self.workflow_label.config(text="로드 실패", foreground="red")
                self._log(f"워크플로우 로드 실패: {path}")

        except Exception as e:
            self.workflow_label.config(text="오류", foreground="red")
            self._log(f"워크플로우 로드 오류: {e}")

    def _select_all(self):
        """Select all items"""
        for item in self.prompt_tree.get_children():
            self.prompt_tree.selection_add(item)

    def _deselect_all(self):
        """Deselect all items"""
        self.prompt_tree.selection_remove(self.prompt_tree.selection())

    def _log(self, message: str):
        """Add message to log"""
        self.log_viewer.config(state=tk.NORMAL)
        self.log_viewer.insert(tk.END, message + "\n")
        self.log_viewer.see(tk.END)
        self.log_viewer.config(state=tk.DISABLED)

    def _clear_log(self):
        """Clear log"""
        self.log_viewer.config(state=tk.NORMAL)
        self.log_viewer.delete(1.0, tk.END)
        self.log_viewer.config(state=tk.DISABLED)

    def _on_resolution_changed(self):
        """Handle resolution change"""
        res_name = self.resolution_var.get()
        width, height = self.resolution_options.get(res_name, (1920, 1088))
        self._log(f"해상도: {res_name} ({width}x{height})")

    def _generate_selected(self):
        """Generate images for selected items"""
        if not self.comfyui or not self.comfyui.is_connected():
            messagebox.showerror("오류", "ComfyUI에 연결되지 않았습니다")
            return

        if not self.builder or not self.builder.template:
            messagebox.showerror("오류", "워크플로우가 로드되지 않았습니다")
            return

        selected = self.prompt_tree.selection()
        if not selected:
            messagebox.showwarning("경고", "선택된 항목이 없습니다")
            return

        # 선택된 항목 찾기
        selected_items = []
        total_prompts = 0

        for item_id in selected:
            for item_data in self.prompt_items:
                if item_data.get("tree_id") == item_id:
                    selected_items.append(item_data)
                    total_prompts += item_data["count"]
                    break

        # 확인
        result = messagebox.askyesno(
            "생성 확인",
            f"{len(selected_items)}개 항목 ({total_prompts}개 프롬프트)의 이미지를 생성하시겠습니까?\n\n"
            f"시간이 오래 걸릴 수 있습니다."
        )
        if not result:
            return

        # 백그라운드에서 생성 시작
        self.is_processing = True
        self.stop_requested = False
        self.generate_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        thread = threading.Thread(target=self._process_items, args=(selected_items,), daemon=True)
        thread.start()

    def _process_items(self, items: List[Dict[str, Any]]):
        """선택된 항목 처리 (백그라운드)"""
        total_prompts = sum(item["count"] for item in items)
        processed = 0

        project_name = self.file_service.project_path.name if self.file_service.project_path else "unknown"

        for item in items:
            if self.stop_requested:
                self._update_ui(lambda: self._log("사용자에 의해 중지됨"))
                break

            item_type = item["type"]
            item_name = item["name"]
            tree_id = item.get("tree_id")

            self._update_ui(lambda n=item_name, t=item_type: self._log(f"\n처리 중: [{t}] {n}"))
            self._update_ui(lambda i=tree_id: self.prompt_tree.set(i, "status", "처리중..."))

            try:
                if item_type == "캐릭터":
                    processed += self._process_character_item(item, project_name)
                else:
                    processed += self._process_scene_item(item, project_name)

                self._update_ui(lambda i=tree_id: self.prompt_tree.set(i, "status", "완료"))

            except Exception as e:
                self._update_ui(lambda e=e: self._log(f"오류: {e}"))
                self._update_ui(lambda i=tree_id: self.prompt_tree.set(i, "status", "오류"))

            # 진행률 업데이트
            progress = (processed / total_prompts) * 100 if total_prompts > 0 else 0
            self._update_ui(lambda p=progress: self.progress_var.set(p))
            self._update_ui(lambda ps=processed, ts=total_prompts:
                           self.progress_label.config(text=f"{ps}/{ts} 프롬프트"))

        # 완료
        self._update_ui(lambda: self._log(f"\n생성 완료: {processed}/{total_prompts} 프롬프트"))
        self._update_ui(lambda: self.progress_label.config(text="완료"))
        self._update_ui(lambda: self.generate_btn.config(state=tk.NORMAL))
        self._update_ui(lambda: self.stop_btn.config(state=tk.DISABLED))
        self.is_processing = False

    def _process_character_item(self, item: Dict[str, Any], project_name: str) -> int:
        """캐릭터 이미지 프롬프트 처리"""
        prompts = item.get("prompts", {})
        char_name = item["name"]
        processed = 0

        res_name = self.resolution_var.get()
        width, height = self.resolution_options.get(res_name, (1920, 1088))
        self.builder.set_image_size(width, height)

        for prompt_key, prompt_data in prompts.items():
            if self.stop_requested:
                break

            # prompt_1, prompt_2, ... 형태
            if not prompt_key.startswith("prompt_"):
                continue

            prompt_num = prompt_key.replace("prompt_", "")

            # 프롬프트 데이터 파싱
            positive = ""

            if isinstance(prompt_data, str):
                # JSON 문자열인 경우 파싱 시도
                try:
                    parsed = json.loads(prompt_data)
                    if isinstance(parsed, dict):
                        positive = parsed.get("combined", "")
                    else:
                        positive = prompt_data  # 그냥 문자열이면 그대로 사용
                except:
                    positive = prompt_data  # 파싱 실패시 그대로 사용

            elif isinstance(prompt_data, dict):
                # 딕셔너리인 경우 combined 필드 확인
                positive = prompt_data.get("combined", "")
                if not positive:
                    # combined가 없으면 개별 필드 조합
                    parts = []
                    for k in ["character", "clothing", "pose", "background", "situation"]:
                        v = prompt_data.get(k, "")
                        if v:
                            parts.append(v)
                    positive = " ".join(parts)

            if not positive:
                continue

            version_name = ""
            if isinstance(prompt_data, dict):
                version_name = prompt_data.get("version_name", "")

            display_name = f"{char_name} v{prompt_num}"
            if version_name:
                display_name = f"{char_name} {version_name}"

            self._update_ui(lambda dn=display_name: self._log(f"  생성 중: {dn}..."))

            # 장면 데이터 형태로 변환
            scene_data = {
                "scene_id": f"{char_name}_p{prompt_num}",
                "image_prompts": {
                    "positive": positive,
                    "negative": ""
                }
            }

            workflow = self.builder.build_from_scene(scene_data, project_name=project_name)

            prompt_id = self.comfyui.queue_prompt(workflow)
            if prompt_id:
                result = self.comfyui.wait_for_completion(prompt_id, timeout=180)
                if result:
                    outputs = result.get("outputs", {})
                    for node_id, output in outputs.items():
                        if "images" in output:
                            for img in output["images"]:
                                filename = img.get("filename", "unknown")
                                self._update_ui(lambda fn=filename: self._log(f"    -> {fn}"))
                    processed += 1
                else:
                    self._update_ui(lambda: self._log(f"    [타임아웃]"))
            else:
                self._update_ui(lambda: self._log(f"    [실패]"))

        return processed

    def _process_scene_item(self, item: Dict[str, Any], project_name: str) -> int:
        """장면 프롬프트 처리"""
        scenes = item.get("scenes", [])
        processed = 0

        res_name = self.resolution_var.get()
        width, height = self.resolution_options.get(res_name, (1920, 1088))
        self.builder.set_image_size(width, height)

        for scene_idx, scene in enumerate(scenes):
            if self.stop_requested:
                break

            scene_id = scene.get("scene_id", f"s{scene_idx+1}")

            self._update_ui(lambda sid=scene_id: self._log(f"  생성 중: {sid}..."))

            workflow = self.builder.build_from_scene(scene, project_name=project_name)

            prompt_id = self.comfyui.queue_prompt(workflow)
            if prompt_id:
                result = self.comfyui.wait_for_completion(prompt_id, timeout=180)
                if result:
                    outputs = result.get("outputs", {})
                    for node_id, output in outputs.items():
                        if "images" in output:
                            for img in output["images"]:
                                filename = img.get("filename", "unknown")
                                self._update_ui(lambda fn=filename: self._log(f"    -> {fn}"))
                    processed += 1
                else:
                    self._update_ui(lambda sid=scene_id: self._log(f"    [타임아웃] {sid}"))
            else:
                self._update_ui(lambda sid=scene_id: self._log(f"    [실패] {sid}"))

        return processed

    def _update_ui(self, func):
        """Update UI from background thread"""
        self.frame.after(0, func)

    def _stop_generation(self):
        """Stop generation"""
        self.stop_requested = True
        self._log("생성 중지 중...")

    def save(self) -> bool:
        """Save (nothing to save)"""
        return True
