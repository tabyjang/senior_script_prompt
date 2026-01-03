"""
TTS Tab
Text-to-Speech tab with multiple engine support.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
from pathlib import Path
from typing import Optional
from .base_tab import BaseTab


class TTSTab(BaseTab):
    """TTS (Text-to-Speech) tab with multi-engine support"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """Initialize"""
        self.tts_service = None
        self.is_processing = False
        self.engine_map = {}  # {display_name: engine_id}

        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "TTS"

    def create_ui(self):
        """Create UI"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # Top: Engine and Voice settings
        top_frame = ttk.LabelFrame(self.frame, text="TTS 설정", padding=10)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(4, weight=1)

        # Engine selection (row 0)
        ttk.Label(top_frame, text="엔진:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.engine_var = tk.StringVar()
        self.engine_combo = ttk.Combobox(
            top_frame,
            textvariable=self.engine_var,
            state="readonly",
            width=25
        )
        self.engine_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.engine_combo.bind('<<ComboboxSelected>>', self._on_engine_change)

        # Engine description label
        self.engine_desc_label = ttk.Label(
            top_frame, text="", foreground="gray", font=("맑은 고딕", 9)
        )
        self.engine_desc_label.grid(row=0, column=2, columnspan=3, sticky=tk.W, padx=10)

        # Voice selection (row 1)
        ttk.Label(top_frame, text="음성:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=(10, 0))
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(
            top_frame,
            textvariable=self.voice_var,
            state="readonly",
            width=25
        )
        self.voice_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(10, 0))

        # Rate slider (row 1)
        ttk.Label(top_frame, text="속도:").grid(row=1, column=2, sticky=tk.W, padx=(20, 5), pady=(10, 0))
        self.rate_var = tk.IntVar(value=0)
        self.rate_scale = ttk.Scale(
            top_frame,
            from_=-50,
            to=100,
            variable=self.rate_var,
            orient=tk.HORIZONTAL,
            length=150,
            command=self._on_rate_change
        )
        self.rate_scale.grid(row=1, column=3, padx=5, pady=(10, 0))
        self.rate_label = ttk.Label(top_frame, text="0%", width=6)
        self.rate_label.grid(row=1, column=4, sticky=tk.W, padx=5, pady=(10, 0))

        # Volume slider (row 2)
        ttk.Label(top_frame, text="볼륨:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=(10, 0))
        self.volume_var = tk.IntVar(value=0)
        self.volume_scale = ttk.Scale(
            top_frame,
            from_=-50,
            to=100,
            variable=self.volume_var,
            orient=tk.HORIZONTAL,
            length=150,
            command=self._on_volume_change
        )
        self.volume_scale.grid(row=2, column=1, sticky=tk.W, padx=5, pady=(10, 0))
        self.volume_label = ttk.Label(top_frame, text="0%", width=6)
        self.volume_label.grid(row=2, column=2, sticky=tk.W, padx=5, pady=(10, 0))

        # Pitch slider (row 2)
        ttk.Label(top_frame, text="피치:").grid(row=2, column=2, sticky=tk.W, padx=(20, 5), pady=(10, 0))
        self.pitch_var = tk.IntVar(value=0)
        self.pitch_scale = ttk.Scale(
            top_frame,
            from_=-50,
            to=50,
            variable=self.pitch_var,
            orient=tk.HORIZONTAL,
            length=150,
            command=self._on_pitch_change
        )
        self.pitch_scale.grid(row=2, column=3, padx=5, pady=(10, 0))
        self.pitch_label = ttk.Label(top_frame, text="0Hz", width=6)
        self.pitch_label.grid(row=2, column=4, sticky=tk.W, padx=5, pady=(10, 0))

        # Voice cloning (row 3) - 참조 음성 선택
        self.speaker_label = ttk.Label(top_frame, text="참조 음성:")
        self.speaker_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=(10, 0))

        self.speaker_var = tk.StringVar(value="")
        self.speaker_entry = ttk.Entry(top_frame, textvariable=self.speaker_var, width=30)
        self.speaker_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=(10, 0))

        self.speaker_btn = ttk.Button(top_frame, text="선택...", width=8, command=self._select_speaker_wav)
        self.speaker_btn.grid(row=3, column=3, sticky=tk.W, padx=5, pady=(10, 0))

        self.speaker_clear_btn = ttk.Button(top_frame, text="초기화", width=8, command=self._clear_speaker_wav)
        self.speaker_clear_btn.grid(row=3, column=4, sticky=tk.W, padx=5, pady=(10, 0))

        # 참조 음성 안내 레이블
        self.speaker_info_label = ttk.Label(
            top_frame,
            text="(Chatterbox만 지원, 5~15초 음성 샘플)",
            foreground="gray",
            font=("맑은 고딕", 8)
        )
        self.speaker_info_label.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=5, pady=(2, 0))

        # Main content: Text input
        main_frame = ttk.LabelFrame(self.frame, text="텍스트 입력", padding=10)
        main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Text area
        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("맑은 고딕", 11),
            height=15
        )
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Text controls
        text_btn_frame = ttk.Frame(main_frame)
        text_btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(text_btn_frame, text="대본 불러오기", command=self._load_script).pack(side=tk.LEFT, padx=5)
        ttk.Button(text_btn_frame, text="텍스트 지우기", command=self._clear_text).pack(side=tk.LEFT, padx=5)

        char_count_frame = ttk.Frame(text_btn_frame)
        char_count_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(char_count_frame, text="글자수:").pack(side=tk.LEFT)
        self.char_count_label = ttk.Label(char_count_frame, text="0")
        self.char_count_label.pack(side=tk.LEFT)

        # Bind text change event
        self.text_area.bind('<KeyRelease>', self._on_text_change)

        # Bottom: Action buttons
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=10)

        # Output folder
        ttk.Label(bottom_frame, text="저장 폴더:").pack(side=tk.LEFT, padx=5)
        self.output_var = tk.StringVar(value="output/tts")
        self.output_entry = ttk.Entry(bottom_frame, textvariable=self.output_var, width=30)
        self.output_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="...", width=3, command=self._select_output_folder).pack(side=tk.LEFT)

        # Generate buttons
        self.generate_btn = ttk.Button(
            bottom_frame,
            text="음성 생성",
            command=self._generate_single
        )
        self.generate_btn.pack(side=tk.RIGHT, padx=5)

        self.play_btn = ttk.Button(
            bottom_frame,
            text="재생",
            command=self._play_last,
            state=tk.DISABLED
        )
        self.play_btn.pack(side=tk.RIGHT, padx=5)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            bottom_frame,
            variable=self.progress_var,
            maximum=100,
            length=150
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=10)

        self.status_label = ttk.Label(bottom_frame, text="준비", foreground="gray")
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # Initialize TTS service
        self._init_tts()

        # Store last generated file
        self.last_generated = None

    def _init_tts(self):
        """Initialize TTS service"""
        try:
            from services.tts_service import TTSService
            self.tts_service = TTSService()

            # Populate engine list
            engines = self.tts_service.get_available_engines()
            if engines:
                engine_names = []
                self.engine_map = {}
                self.engine_desc_map = {}

                for engine_id, display_name, description in engines:
                    engine_names.append(display_name)
                    self.engine_map[display_name] = engine_id
                    self.engine_desc_map[display_name] = description

                self.engine_combo['values'] = engine_names
                self.engine_combo.current(0)
                self._update_engine_description()
                self._update_voices()

                self.status_label.config(
                    text=f"준비 ({len(engines)}개 엔진)",
                    foreground="green"
                )
            else:
                self.status_label.config(text="TTS 엔진 없음", foreground="red")

        except Exception as e:
            self.status_label.config(text=f"TTS 로드 실패: {e}", foreground="red")

    def _on_engine_change(self, event=None):
        """Handle engine selection change"""
        engine_name = self.engine_var.get()
        engine_id = self.engine_map.get(engine_name)

        if engine_id and self.tts_service:
            self.tts_service.set_engine(engine_id)
            self._update_engine_description()
            self._update_voices()

    def _update_engine_description(self):
        """Update engine description label"""
        engine_name = self.engine_var.get()
        desc = self.engine_desc_map.get(engine_name, "")
        self.engine_desc_label.config(text=desc)

    def _update_voices(self):
        """Update voice list for current engine"""
        if self.tts_service:
            voices = self.tts_service.get_voice_names()
            self.voice_combo['values'] = voices
            if voices:
                self.voice_combo.current(0)

    def _on_rate_change(self, value):
        """Handle rate slider change"""
        rate = int(float(value))
        self.rate_label.config(text=f"{rate:+d}%")
        if self.tts_service:
            self.tts_service.set_rate(rate)

    def _on_volume_change(self, value):
        """Handle volume slider change"""
        volume = int(float(value))
        self.volume_label.config(text=f"{volume:+d}%")
        if self.tts_service:
            self.tts_service.set_volume(volume)

    def _on_pitch_change(self, value):
        """Handle pitch slider change"""
        pitch = int(float(value))
        self.pitch_label.config(text=f"{pitch:+d}Hz")
        if self.tts_service:
            self.tts_service.set_pitch(pitch)

    def _on_text_change(self, event=None):
        """Handle text change"""
        text = self.text_area.get("1.0", tk.END).strip()
        self.char_count_label.config(text=str(len(text)))

    def _load_script(self):
        """Load script from file"""
        file_path = filedialog.askopenfilename(
            title="대본 파일 선택",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ],
            initialdir=str(Path(__file__).parent.parent.parent / "prompts")
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self._on_text_change()
            except Exception as e:
                messagebox.showerror("오류", f"파일 로드 실패: {e}")

    def _clear_text(self):
        """Clear text area"""
        self.text_area.delete("1.0", tk.END)
        self._on_text_change()

    def _select_output_folder(self):
        """Select output folder"""
        folder = filedialog.askdirectory(
            title="저장 폴더 선택",
            initialdir=self.output_var.get()
        )
        if folder:
            self.output_var.set(folder)

    def _select_speaker_wav(self):
        """Select speaker reference audio file"""
        file_path = filedialog.askopenfilename(
            title="참조 음성 파일 선택",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.m4a *.flac"),
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*")
            ],
            initialdir=str(Path(__file__).parent.parent.parent / "output" / "tts")
        )
        if file_path:
            self.speaker_var.set(file_path)

    def _clear_speaker_wav(self):
        """Clear speaker reference audio"""
        self.speaker_var.set("")

    def _generate_single(self):
        """Generate single audio file"""
        if not self.tts_service:
            messagebox.showerror("오류", "TTS 서비스가 초기화되지 않았습니다.")
            return

        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("경고", "텍스트를 입력하세요.")
            return

        # Create output directory
        output_dir = Path(self.output_var.get())
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = str(output_dir / f"tts_{timestamp}.mp3")

        # Get speaker wav for voice cloning (if selected)
        speaker_wav = self.speaker_var.get().strip() or None

        # Start generation in background
        self.is_processing = True
        self.generate_btn.config(state=tk.DISABLED)
        self.status_label.config(text="생성 중...", foreground="blue")
        self.progress_var.set(50)

        thread = threading.Thread(
            target=self._do_generate,
            args=(text, output_file, speaker_wav),
            daemon=True
        )
        thread.start()

    def _do_generate(self, text: str, output_file: str, speaker_wav: str = None):
        """Generate audio in background thread"""
        try:
            voice_name = self.voice_var.get()
            success = self.tts_service.generate(text, output_file, voice_name, speaker_wav=speaker_wav)

            if success:
                self.last_generated = output_file
                self._update_ui(lambda: self._on_generate_success(output_file))
            else:
                self._update_ui(lambda: self._on_generate_error("생성 실패"))

        except Exception as e:
            self._update_ui(lambda: self._on_generate_error(str(e)))

    def _on_generate_success(self, output_file: str):
        """Handle successful generation"""
        self.is_processing = False
        self.generate_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
        self.progress_var.set(100)

        # 실제 생성된 파일 확인 (mp3 또는 wav)
        actual_file = output_file
        if not os.path.exists(output_file) and output_file.endswith('.mp3'):
            wav_path = output_file.replace('.mp3', '.wav')
            if os.path.exists(wav_path):
                actual_file = wav_path

        # 실제 파일 경로로 업데이트
        self.last_generated = actual_file
        self.status_label.config(text=f"완료: {Path(actual_file).name}", foreground="green")

    def _on_generate_error(self, error: str):
        """Handle generation error"""
        self.is_processing = False
        self.generate_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_label.config(text=f"오류: {error}", foreground="red")

    def _update_ui(self, func):
        """Update UI from background thread"""
        self.frame.after(0, func)

    def _play_last(self):
        """Play last generated audio"""
        file_to_play = None

        if self.last_generated:
            # mp3 또는 wav 파일 확인
            if os.path.exists(self.last_generated):
                file_to_play = self.last_generated
            elif self.last_generated.endswith('.mp3'):
                wav_path = self.last_generated.replace('.mp3', '.wav')
                if os.path.exists(wav_path):
                    file_to_play = wav_path

        if file_to_play:
            try:
                os.startfile(file_to_play)
            except Exception as e:
                messagebox.showerror("오류", f"재생 실패: {e}")
        else:
            messagebox.showwarning("경고", "재생할 파일이 없습니다.")

    def update_display(self):
        """Update display"""
        pass

    def save(self) -> bool:
        """Save (nothing to save)"""
        return True
