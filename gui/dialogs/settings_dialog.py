"""
설정 다이얼로그
LLM API 키 및 설정을 관리합니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from services.llm_service import LLMService


class SettingsDialog:
    """설정 다이얼로그 클래스"""

    def __init__(self, parent, config_manager, project_data=None, file_service=None):
        """
        Args:
            parent: 부모 윈도우
            config_manager: ConfigManager 인스턴스
            project_data: ProjectData 인스턴스 (내보내기용, 선택사항)
            file_service: FileService 인스턴스 (내보내기용, 선택사항)
        """
        self.parent = parent
        self.config = config_manager
        self.project_data = project_data
        self.file_service = file_service

        # 다이얼로그 생성
        self.window = tk.Toplevel(parent)
        self.window.title("설정")
        self.window.geometry("700x800")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(True, True)

        # 중앙 배치
        self._center_window()

        # UI 생성
        self._create_ui()

    def _center_window(self):
        """윈도우를 화면 중앙에 배치"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

    def _create_ui(self):
        """UI 생성"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        row = 0

        # LLM 제공자 선택
        ttk.Label(
            main_frame,
            text="LLM 제공자:",
            font=("맑은 고딕", 10, "bold")
        ).grid(row=row, column=0, sticky=tk.W, pady=10)

        self.provider_var = tk.StringVar(value=self.config.get("provider", "gemini"))
        provider_combo = ttk.Combobox(
            main_frame,
            textvariable=self.provider_var,
            width=25,
            state="readonly"
        )
        provider_combo['values'] = ("gemini", "openai", "anthropic")
        provider_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=10, padx=10)
        provider_combo.bind('<<ComboboxSelected>>', lambda e: self._update_provider_settings())
        row += 1

        # 모델 선택 프레임
        model_frame = ttk.LabelFrame(main_frame, text="모델 설정", padding=10)
        model_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=10)
        row += 1

        # 모델 선택
        ttk.Label(model_frame, text="모델:", font=("맑은 고딕", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, width=40, state="readonly")
        self.model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
        model_frame.columnconfigure(1, weight=1)
        
        # LLM 연결 테스트 버튼 (모델 설정 프레임 내)
        llm_test_btn = ttk.Button(model_frame, text="🔗 연결 테스트", command=self._test_connection, width=15)
        llm_test_btn.grid(row=0, column=2, padx=5)

        # API 키 입력 프레임
        api_frame = ttk.LabelFrame(main_frame, text="API 키 설정", padding=10)
        api_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=10)
        row += 1

        # API 키 입력
        ttk.Label(api_frame, text="API 키:", font=("맑은 고딕", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=40, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)

        # API 키 표시/숨김 버튼
        self.toggle_btn = ttk.Button(api_frame, text="보기", command=self._toggle_api_key_visibility, width=8)
        self.toggle_btn.grid(row=0, column=2, padx=5)
        api_frame.columnconfigure(1, weight=1)
        
        # LLM 설정 저장 버튼 (API 키 설정 프레임 내)
        llm_save_btn = ttk.Button(api_frame, text="💾 저장", command=self._save_settings, width=12)
        llm_save_btn.grid(row=1, column=0, columnspan=3, pady=10)

        # 안내 메시지
        self.info_label = ttk.Label(main_frame, text="", font=("맑은 고딕", 8), foreground="gray")
        self.info_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=10, padx=10)
        row += 1

        # 패키지 설치 상태
        self.warning_label = ttk.Label(main_frame, text="", font=("맑은 고딕", 8), foreground="orange")
        self.warning_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=10, padx=10)
        row += 1

        # 구분선
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20, padx=10)
        row += 1

        # 구글 시트 설정 프레임
        sheets_frame = ttk.LabelFrame(main_frame, text="구글 시트 내보내기", padding=10)
        sheets_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=10)
        row += 1

        # 구글 시트 사용 체크박스
        self.sheets_enabled_var = tk.BooleanVar(value=self.config.get("google_sheets_enabled", False))
        sheets_check = ttk.Checkbutton(
            sheets_frame,
            text="구글 시트 내보내기 사용",
            variable=self.sheets_enabled_var,
            command=self._update_sheets_ui_state
        )
        sheets_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)

        # 클라이언트 ID
        ttk.Label(sheets_frame, text="클라이언트 ID:", font=("맑은 고딕", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.client_id_var = tk.StringVar(value=self.config.get("google_sheets_client_id", ""))
        client_id_entry = ttk.Entry(sheets_frame, textvariable=self.client_id_var, width=40)
        client_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
        sheets_frame.columnconfigure(1, weight=1)

        # 클라이언트 시크릿
        ttk.Label(sheets_frame, text="클라이언트 시크릿:", font=("맑은 고딕", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.client_secret_var = tk.StringVar(value=self.config.get("google_sheets_client_secret", ""))
        client_secret_entry = ttk.Entry(sheets_frame, textvariable=self.client_secret_var, width=40, show="*")
        client_secret_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)

        # 시크릿 표시/숨김 버튼
        self.toggle_secret_btn = ttk.Button(sheets_frame, text="보기", command=lambda: self._toggle_secret_visibility(client_secret_entry), width=8)
        self.toggle_secret_btn.grid(row=2, column=2, padx=5)

        # 구글 시트 ID
        ttk.Label(sheets_frame, text="구글 시트 ID:", font=("맑은 고딕", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.sheet_id_var = tk.StringVar(value=self.config.get("google_sheets_spreadsheet_id", ""))
        sheet_id_entry = ttk.Entry(sheets_frame, textvariable=self.sheet_id_var, width=40)
        sheet_id_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)

        # 구글 시트 안내
        sheets_info = ttk.Label(
            sheets_frame,
            text="구글 시트 ID는 시트 URL에서 확인할 수 있습니다.\n예: https://docs.google.com/spreadsheets/d/[시트ID]/edit",
            font=("맑은 고딕", 8),
            foreground="gray"
        )
        sheets_info.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)

        # 구글 시트 패키지 설치 상태
        self.sheets_warning_label = ttk.Label(sheets_frame, text="", font=("맑은 고딕", 8), foreground="orange")
        self.sheets_warning_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)

        # 구글 시트 연결 상태
        self.sheets_status_label = ttk.Label(sheets_frame, text="", font=("맑은 고딕", 8), foreground="green")
        self.sheets_status_label.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=5)

        # 구글 시트 버튼 프레임
        sheets_button_frame = ttk.Frame(sheets_frame)
        sheets_button_frame.grid(row=7, column=0, columnspan=3, pady=10)

        ttk.Button(sheets_button_frame, text="구글 계정 연결", command=self._connect_google_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(sheets_button_frame, text="연결 테스트", command=self._test_sheets_connection).pack(side=tk.LEFT, padx=5)

        # 초기 UI 상태 업데이트
        self._update_sheets_ui_state()
        self._check_sheets_packages()

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)

        # 내보내기 버튼 (프로젝트 데이터가 있을 때만 표시)
        if self.project_data:
            ttk.Button(button_frame, text="📤 구글 시트로 내보내기", command=self._export_to_sheets).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="연결 테스트", command=self._test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="저장", command=self._save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

        # 그리드 가중치 설정
        main_frame.columnconfigure(1, weight=1)

        # 초기 설정 로드
        self._update_provider_settings()

    def _toggle_api_key_visibility(self):
        """API 키 표시/숨김 토글"""
        if self.api_key_entry['show'] == '*':
            self.api_key_entry.config(show='')
            self.toggle_btn.config(text="숨기기")
        else:
            self.api_key_entry.config(show='*')
            self.toggle_btn.config(text="보기")

    def _update_provider_settings(self):
        """제공자에 따라 UI 업데이트"""
        provider = self.provider_var.get()

        # 모델 목록 업데이트
        if provider == "gemini":
            self.model_combo['values'] = ("gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro")
            self.model_var.set(self.config.get("model", "gemini-1.5-flash"))
            self.api_key_var.set(self.config.get("api_key", ""))
            self.info_label.config(text="API 키는 Google AI Studio에서 발급받을 수 있습니다.\nhttps://makersuite.google.com/app/apikey")

            if not LLMService.is_provider_available("gemini"):
                self.warning_label.config(text="⚠ 경고: google-generativeai 패키지가 설치되지 않았습니다.\n설치: pip install google-generativeai")
            else:
                self.warning_label.config(text="")

        elif provider == "openai":
            self.model_combo['values'] = ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo")
            self.model_var.set(self.config.get("openai_model", "gpt-4o"))
            self.api_key_var.set(self.config.get("openai_api_key", ""))
            self.info_label.config(text="API 키는 OpenAI Platform에서 발급받을 수 있습니다.\nhttps://platform.openai.com/api-keys")

            if not LLMService.is_provider_available("openai"):
                self.warning_label.config(text="⚠ 경고: openai 패키지가 설치되지 않았습니다.\n설치: pip install openai")
            else:
                self.warning_label.config(text="")

        elif provider == "anthropic":
            self.model_combo['values'] = ("claude-3-5-haiku-20241022", "claude-sonnet-4-5-20250929", "claude-3-opus-20240229")
            self.model_var.set(self.config.get("anthropic_model", "claude-3-5-haiku-20241022"))
            self.api_key_var.set(self.config.get("anthropic_api_key", ""))
            self.info_label.config(text="API 키는 Anthropic Console에서 발급받을 수 있습니다.\nhttps://console.anthropic.com/")

            if not LLMService.is_provider_available("anthropic"):
                self.warning_label.config(text="⚠ 경고: anthropic 패키지가 설치되지 않았습니다.\n설치: pip install anthropic")
            else:
                self.warning_label.config(text="")

    def _test_connection(self):
        """API 연결 테스트"""
        provider = self.provider_var.get()
        api_key = self.api_key_var.get().strip()
        model = self.model_var.get()

        if not api_key:
            messagebox.showerror("연결 테스트", "API 키를 입력해주세요.")
            return

        # 임시 설정으로 LLMService 생성
        from config.config_manager import ConfigManager
        temp_config = ConfigManager()
        temp_config.set("provider", provider)

        if provider == "gemini":
            temp_config.set("api_key", api_key)
            temp_config.set("model", model)
        elif provider == "openai":
            temp_config.set("openai_api_key", api_key)
            temp_config.set("openai_model", model)
        elif provider == "anthropic":
            temp_config.set("anthropic_api_key", api_key)
            temp_config.set("anthropic_model", model)

        llm = LLMService(temp_config)

        try:
            response = llm.call("안녕하세요")
            if response:
                messagebox.showinfo("연결 테스트", f"{provider.upper()} API 연결 성공!")
        except Exception as e:
            messagebox.showerror("연결 테스트", f"API 연결 실패:\n{str(e)[:500]}")

    def _toggle_secret_visibility(self, entry):
        """클라이언트 시크릿 표시/숨김 토글"""
        if entry['show'] == '*':
            entry.config(show='')
            self.toggle_secret_btn.config(text="숨기기")
        else:
            entry.config(show='*')
            self.toggle_secret_btn.config(text="보기")

    def _update_sheets_ui_state(self):
        """구글 시트 UI 상태 업데이트"""
        enabled = self.sheets_enabled_var.get()
        # UI 요소 활성화/비활성화는 필요시 구현

    def _check_sheets_packages(self):
        """구글 시트 패키지 설치 여부 확인"""
        try:
            from services.google_sheets_service import GoogleSheetsService
            if not GoogleSheetsService.is_available():
                self.sheets_warning_label.config(
                    text="⚠ 경고: 구글 시트 패키지가 설치되지 않았습니다.\n설치: pip install gspread google-auth google-auth-oauthlib google-auth-httplib2"
                )
            else:
                self.sheets_warning_label.config(text="")
        except Exception as e:
            self.sheets_warning_label.config(text=f"⚠ 오류: {str(e)}")

    def _connect_google_account(self):
        """구글 계정 연결 (OAuth2)"""
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()

        if not client_id or not client_secret:
            messagebox.showerror("오류", "클라이언트 ID와 시크릿을 입력해주세요.")
            return

        # 설정에 임시 저장
        self.config.set("google_sheets_client_id", client_id)
        self.config.set("google_sheets_client_secret", client_secret)

        try:
            from services.google_sheets_service import GoogleSheetsService
            if not GoogleSheetsService.is_available():
                messagebox.showerror("오류", "구글 시트 패키지가 설치되지 않았습니다.\npip install gspread google-auth google-auth-oauthlib google-auth-httplib2")
                return

            service = GoogleSheetsService(self.config)
            if service.authenticate():
                messagebox.showinfo("성공", "구글 계정 연결이 완료되었습니다!")
                self.sheets_status_label.config(text="✓ 구글 계정 연결됨")
            else:
                messagebox.showerror("오류", "구글 계정 연결에 실패했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"구글 계정 연결 중 오류 발생:\n{str(e)[:500]}")

    def _test_sheets_connection(self):
        """구글 시트 연결 테스트"""
        sheet_id = self.sheet_id_var.get().strip()
        if not sheet_id:
            messagebox.showerror("오류", "구글 시트 ID를 입력해주세요.")
            return

        try:
            from services.google_sheets_service import GoogleSheetsService
            if not GoogleSheetsService.is_available():
                messagebox.showerror("오류", "구글 시트 패키지가 설치되지 않았습니다.")
                return

            service = GoogleSheetsService(self.config)
            if service.test_connection(sheet_id):
                messagebox.showinfo("성공", "구글 시트 연결 성공!")
                self.sheets_status_label.config(text="✓ 구글 시트 연결됨")
            else:
                messagebox.showerror("오류", "구글 시트 연결에 실패했습니다.\n시트 ID와 권한을 확인해주세요.")
        except Exception as e:
            messagebox.showerror("오류", f"구글 시트 연결 테스트 중 오류 발생:\n{str(e)[:500]}")

    def _export_to_sheets(self):
        """구글 시트로 데이터 내보내기"""
        if not self.project_data:
            messagebox.showerror("오류", "프로젝트 데이터가 없습니다.")
            return

        sheet_id = self.sheet_id_var.get().strip()
        if not sheet_id:
            messagebox.showerror("오류", "구글 시트 ID를 입력해주세요.")
            return

        try:
            from services.google_sheets_service import GoogleSheetsService
            if not GoogleSheetsService.is_available():
                messagebox.showerror("오류", "구글 시트 패키지가 설치되지 않았습니다.")
                return

            # 확인 대화상자
            result = messagebox.askyesno(
                "구글 시트 내보내기",
                "모든 프로젝트 데이터를 구글 시트로 내보내시겠습니까?\n\n"
                "내보내기 항목:\n"
                "- 시놉시스\n"
                "- 등장인물\n"
                "- 챕터 목록\n"
                "- 각 챕터별 상세 정보 및 대본\n"
                "- 이미지 스크립트"
            )
            if not result:
                return

            service = GoogleSheetsService(self.config)
            
            # 진행 상황 표시
            self.window.config(cursor="wait")
            self.window.update()

            if service.export_data(self.project_data, sheet_id):
                messagebox.showinfo("성공", "구글 시트로 데이터 내보내기가 완료되었습니다!")
            else:
                messagebox.showerror("오류", "데이터 내보내기에 실패했습니다.\n연결 상태와 권한을 확인해주세요.")

            self.window.config(cursor="")
        except Exception as e:
            self.window.config(cursor="")
            messagebox.showerror("오류", f"데이터 내보내기 중 오류 발생:\n{str(e)[:500]}")

    def _save_settings(self):
        """설정 저장"""
        provider = self.provider_var.get()
        self.config.set("provider", provider)

        if provider == "gemini":
            self.config.set("model", self.model_var.get())
            self.config.set("api_key", self.api_key_var.get())
        elif provider == "openai":
            self.config.set("openai_model", self.model_var.get())
            self.config.set("openai_api_key", self.api_key_var.get())
        elif provider == "anthropic":
            self.config.set("anthropic_model", self.model_var.get())
            self.config.set("anthropic_api_key", self.api_key_var.get())

        # 구글 시트 설정 저장
        self.config.set("google_sheets_enabled", self.sheets_enabled_var.get())
        self.config.set("google_sheets_client_id", self.client_id_var.get())
        self.config.set("google_sheets_client_secret", self.client_secret_var.get())
        self.config.set("google_sheets_spreadsheet_id", self.sheet_id_var.get())

        if self.config.save():
            messagebox.showinfo("설정 저장", "설정이 저장되었습니다.")
            self.window.destroy()
