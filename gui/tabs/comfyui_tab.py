"""
ComfyUI Tab
ComfyUI integration for batch image generation from scene prompts.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from .base_tab import BaseTab


class ComfyUITab(BaseTab):
    """ComfyUI batch processing tab"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """Initialize"""
        self.comfyui = None
        self.builder = None
        self.is_processing = False
        self.stop_requested = False

        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "ComfyUI"

    def create_ui(self):
        """Create UI"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # Top: Connection status and controls
        top_frame = ttk.LabelFrame(self.frame, text="ComfyUI Connection", padding=10)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        top_frame.columnconfigure(1, weight=1)

        # Status indicator
        ttk.Label(top_frame, text="Status:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.status_label = ttk.Label(top_frame, text="Not connected", foreground="gray")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Connect button
        self.connect_btn = ttk.Button(top_frame, text="Connect", command=self._connect)
        self.connect_btn.grid(row=0, column=2, padx=5)

        # Workflow template
        ttk.Label(top_frame, text="Workflow:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=(10, 0))
        self.workflow_label = ttk.Label(top_frame, text="Not loaded", foreground="gray")
        self.workflow_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(10, 0))

        self.load_workflow_btn = ttk.Button(top_frame, text="Load Workflow", command=self._load_workflow)
        self.load_workflow_btn.grid(row=1, column=2, padx=5, pady=(10, 0))

        # Resolution selector
        ttk.Label(top_frame, text="Resolution:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=(10, 0))

        res_frame = ttk.Frame(top_frame)
        res_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=(10, 0))

        self.resolution_var = tk.StringVar(value="HD")
        # 해상도는 64의 배수여야 함
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

        # Main content: Left (scene list) | Right (log/preview)
        main_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Left: Scene file list
        left_frame = ttk.LabelFrame(main_paned, text="Scene Files", padding=10)
        main_paned.add(left_frame, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        # Scene folder selection
        folder_frame = ttk.Frame(left_frame)
        folder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(folder_frame, text="Select Folder", command=self._select_scene_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Refresh", command=self._refresh_scene_list).pack(side=tk.LEFT, padx=5)

        self.folder_label = ttk.Label(folder_frame, text="No folder selected", foreground="gray")
        self.folder_label.pack(side=tk.LEFT, padx=10)

        # Scene file list with checkboxes
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview for scene files
        columns = ("file", "scenes", "status")
        self.scene_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        self.scene_tree.heading("file", text="File")
        self.scene_tree.heading("scenes", text="Scenes")
        self.scene_tree.heading("status", text="Status")
        self.scene_tree.column("file", width=200)
        self.scene_tree.column("scenes", width=60)
        self.scene_tree.column("status", width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.scene_tree.yview)
        self.scene_tree.configure(yscrollcommand=scrollbar.set)

        self.scene_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Selection buttons
        sel_frame = ttk.Frame(left_frame)
        sel_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(sel_frame, text="Select All", command=self._select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(sel_frame, text="Deselect All", command=self._deselect_all).pack(side=tk.LEFT, padx=5)

        # Right: Log and controls
        right_frame = ttk.LabelFrame(main_paned, text="Generation Log", padding=10)
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

        self.progress_label = ttk.Label(right_frame, text="Ready")
        self.progress_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))

        # Bottom: Action buttons
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=10)

        self.generate_btn = ttk.Button(
            bottom_frame,
            text="Generate Selected",
            command=self._generate_selected,
            state=tk.DISABLED
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            bottom_frame,
            text="Stop",
            command=self._stop_generation,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(bottom_frame, text="Clear Log", command=self._clear_log).pack(side=tk.RIGHT, padx=5)

        # Initialize scene folder path
        self.scene_folder = None
        self._try_default_folder()

    def _try_default_folder(self):
        """Try to load default prompts folder"""
        default_path = Path(__file__).parent.parent.parent / "prompts"
        if default_path.exists():
            self.scene_folder = str(default_path)
            self.folder_label.config(text=str(default_path.name), foreground="black")
            self._refresh_scene_list()

    def _connect(self):
        """Connect to ComfyUI"""
        try:
            from services.comfyui_service import ComfyUIService, ZImageWorkflowBuilder

            self.comfyui = ComfyUIService()

            if self.comfyui.is_connected():
                stats = self.comfyui.get_system_stats()
                version = stats.get("system", {}).get("comfyui_version", "unknown") if stats else "unknown"
                self.status_label.config(text=f"Connected (v{version})", foreground="green")
                self._log(f"Connected to ComfyUI v{version}")

                # Try to load default workflow
                self._try_default_workflow()

                self.generate_btn.config(state=tk.NORMAL)
            else:
                self.status_label.config(text="Connection failed", foreground="red")
                self._log("Failed to connect to ComfyUI. Is it running at http://127.0.0.1:8188?")

        except Exception as e:
            self.status_label.config(text="Error", foreground="red")
            self._log(f"Error connecting: {e}")

    def _try_default_workflow(self):
        """Try to load default workflow template"""
        default_path = Path(__file__).parent.parent.parent / "prompts" / "workflows" / "z_image_turbo.json"
        if default_path.exists():
            self._load_workflow_file(str(default_path))

    def _load_workflow(self):
        """Load workflow template file"""
        file_path = filedialog.askopenfilename(
            title="Select ComfyUI Workflow (API Format)",
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
                self._log(f"Loaded workflow: {filename}")
            else:
                self.workflow_label.config(text="Load failed", foreground="red")
                self._log(f"Failed to load workflow: {path}")

        except Exception as e:
            self.workflow_label.config(text="Error", foreground="red")
            self._log(f"Error loading workflow: {e}")

    def _select_scene_folder(self):
        """Select scene folder"""
        folder = filedialog.askdirectory(
            title="Select Scene Prompts Folder",
            initialdir=self.scene_folder or str(Path(__file__).parent.parent.parent / "prompts")
        )
        if folder:
            self.scene_folder = folder
            self.folder_label.config(text=Path(folder).name, foreground="black")
            self._refresh_scene_list()

    def _refresh_scene_list(self):
        """Refresh scene file list"""
        # Clear existing items
        for item in self.scene_tree.get_children():
            self.scene_tree.delete(item)

        if not self.scene_folder:
            return

        # Find all scene JSON files
        scene_files = []
        for root, dirs, files in os.walk(self.scene_folder):
            for f in files:
                if f.endswith(".json") and "scenes" in root:
                    scene_files.append(os.path.join(root, f))

        # Add to treeview
        for path in sorted(scene_files):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                scene_count = len(data.get("scenes", []))
                rel_path = os.path.relpath(path, self.scene_folder)
                self.scene_tree.insert("", "end", values=(rel_path, scene_count, "Ready"))
            except Exception as e:
                rel_path = os.path.relpath(path, self.scene_folder)
                self.scene_tree.insert("", "end", values=(rel_path, "?", "Error"))

        self._log(f"Found {len(scene_files)} scene files")

    def _select_all(self):
        """Select all items"""
        for item in self.scene_tree.get_children():
            self.scene_tree.selection_add(item)

    def _deselect_all(self):
        """Deselect all items"""
        self.scene_tree.selection_remove(self.scene_tree.selection())

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
        width, height = self.resolution_options.get(res_name, (1920, 1072))
        self._log(f"Resolution: {res_name} ({width}x{height})")

    def _generate_selected(self):
        """Generate images for selected scenes"""
        if not self.comfyui or not self.comfyui.is_connected():
            messagebox.showerror("Error", "Not connected to ComfyUI")
            return

        if not self.builder or not self.builder.template:
            messagebox.showerror("Error", "No workflow template loaded")
            return

        selected = self.scene_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No scenes selected")
            return

        # Get selected file paths
        files = []
        for item in selected:
            values = self.scene_tree.item(item, "values")
            rel_path = values[0]
            full_path = os.path.join(self.scene_folder, rel_path)
            files.append((item, full_path))

        # Confirm
        total_scenes = 0
        for item, path in files:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                total_scenes += len(data.get("scenes", []))
            except:
                pass

        result = messagebox.askyesno(
            "Confirm Generation",
            f"Generate images for {len(files)} files ({total_scenes} scenes)?\n\n"
            f"This may take a while."
        )
        if not result:
            return

        # Start generation in background
        self.is_processing = True
        self.stop_requested = False
        self.generate_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        thread = threading.Thread(target=self._process_files, args=(files,), daemon=True)
        thread.start()

    def _process_files(self, files: List[tuple]):
        """Process selected files (background thread)"""
        import copy

        total_files = len(files)
        processed_scenes = 0
        total_scenes = 0

        # Count total scenes
        for item, path in files:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                total_scenes += len(data.get("scenes", []))
            except:
                pass

        for file_idx, (item, path) in enumerate(files):
            if self.stop_requested:
                self._update_ui(lambda: self._log("Generation stopped by user"))
                break

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    chapter_data = json.load(f)

                scenes = chapter_data.get("scenes", [])
                rel_path = os.path.relpath(path, self.scene_folder)

                self._update_ui(lambda rp=rel_path: self._log(f"\nProcessing: {rp}"))
                self._update_ui(lambda i=item: self.scene_tree.set(i, "status", "Processing..."))

                for scene_idx, scene in enumerate(scenes):
                    if self.stop_requested:
                        break

                    scene_id = scene.get("scene_id", f"s{scene_idx+1}")

                    # Extract project name from file path
                    # path: .../prompts/1년동거5억조건/scenes/... -> "1년동거5억조건"
                    path_parts = Path(path).parts
                    project_name = ""
                    for i, part in enumerate(path_parts):
                        if part == "scenes" and i > 0:
                            project_name = path_parts[i-1]
                            break

                    # Get selected resolution and set before building
                    res_name = self.resolution_var.get()
                    width, height = self.resolution_options.get(res_name, (1920, 1072))
                    self.builder.set_image_size(width, height)

                    # Build workflow with project name
                    workflow = self.builder.build_from_scene(scene, project_name=project_name)

                    # Queue and wait
                    self._update_ui(lambda sid=scene_id, w=width, h=height: self._log(f"  Generating {sid} ({w}x{h})..."))

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
                        else:
                            self._update_ui(lambda sid=scene_id: self._log(f"    [TIMEOUT] {sid}"))
                    else:
                        self._update_ui(lambda sid=scene_id: self._log(f"    [FAILED] {sid}"))

                    processed_scenes += 1

                    # Update progress
                    progress = (processed_scenes / total_scenes) * 100 if total_scenes > 0 else 0
                    self._update_ui(lambda p=progress: self.progress_var.set(p))
                    self._update_ui(lambda ps=processed_scenes, ts=total_scenes:
                                   self.progress_label.config(text=f"{ps}/{ts} scenes"))

                self._update_ui(lambda i=item: self.scene_tree.set(i, "status", "Done"))

            except Exception as e:
                self._update_ui(lambda e=e: self._log(f"Error: {e}"))
                self._update_ui(lambda i=item: self.scene_tree.set(i, "status", "Error"))

        # Completion
        self._update_ui(lambda: self._log(f"\nGeneration complete: {processed_scenes}/{total_scenes} scenes"))
        self._update_ui(lambda: self.progress_label.config(text="Complete"))
        self._update_ui(lambda: self.generate_btn.config(state=tk.NORMAL))
        self._update_ui(lambda: self.stop_btn.config(state=tk.DISABLED))
        self.is_processing = False

    def _update_ui(self, func):
        """Update UI from background thread"""
        self.frame.after(0, func)

    def _stop_generation(self):
        """Stop generation"""
        self.stop_requested = True
        self._log("Stopping generation...")

    def update_display(self):
        """Update display"""
        pass

    def save(self) -> bool:
        """Save (nothing to save)"""
        return True
