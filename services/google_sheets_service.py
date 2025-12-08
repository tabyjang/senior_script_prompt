"""
구글 시트 서비스
OAuth2 인증을 통해 구글 시트에 데이터를 내보냅니다.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

try:
    import gspread
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """OAuth2 리다이렉트 콜백 처리"""
    
    def do_GET(self):
        """GET 요청 처리"""
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("""
            <html>
            <head><title>인증 완료</title></head>
            <body>
                <h1>인증이 완료되었습니다!</h1>
                <p>이 창을 닫아도 됩니다.</p>
                <script>setTimeout(function(){window.close();}, 2000);</script>
            </body>
            </html>
            """.encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: No authorization code received")
    
    def log_message(self, format, *args):
        """로그 메시지 무시"""
        pass


class GoogleSheetsService:
    """구글 시트 서비스 클래스"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    REDIRECT_URI = 'http://localhost:8080'
    
    def __init__(self, config_manager):
        """
        Args:
            config_manager: ConfigManager 인스턴스
        """
        self.config = config_manager
        self.client = None
        self.credentials = None
        
    @staticmethod
    def is_available() -> bool:
        """gspread 패키지 설치 여부 확인"""
        return GSPREAD_AVAILABLE
    
    def _get_credentials_path(self) -> Path:
        """인증 정보 파일 경로"""
        return Path(self.config.get("google_sheets_token_path", 
                                    str(Path.home() / ".senior_contents_google_token.json")))
    
    def _get_client_credentials(self) -> Optional[Dict[str, str]]:
        """클라이언트 ID와 시크릿 가져오기"""
        client_id = self.config.get("google_sheets_client_id", "").strip()
        client_secret = self.config.get("google_sheets_client_secret", "").strip()
        
        if not client_id or not client_secret:
            return None
        
        return {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [self.REDIRECT_URI]
            }
        }
    
    def _load_credentials(self) -> Optional[Credentials]:
        """저장된 인증 정보 로드"""
        token_path = self._get_credentials_path()
        
        if not token_path.exists():
            return None
        
        try:
            with open(token_path, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            credentials = Credentials.from_authorized_user_info(token_data, self.SCOPES)
            
            # 토큰 갱신 필요 시
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                self._save_credentials(credentials)
            
            return credentials
        except Exception as e:
            print(f"인증 정보 로드 오류: {e}")
            return None
    
    def _save_credentials(self, credentials: Credentials):
        """인증 정보 저장"""
        token_path = self._get_credentials_path()
        try:
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            with open(token_path, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"인증 정보 저장 오류: {e}")
    
    def authenticate(self) -> bool:
        """OAuth2 인증 수행"""
        if not GSPREAD_AVAILABLE:
            raise ImportError("gspread 패키지가 설치되지 않았습니다. pip install gspread google-auth google-auth-oauthlib google-auth-httplib2")
        
        # 기존 인증 정보 확인
        credentials = self._load_credentials()
        if credentials and credentials.valid:
            self.credentials = credentials
            return True
        
        # 클라이언트 정보 확인
        client_config = self._get_client_credentials()
        if not client_config:
            raise ValueError("구글 시트 클라이언트 ID와 시크릿이 설정되지 않았습니다.")
        
        # OAuth2 플로우 생성
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=self.REDIRECT_URI
        )
        
        # 인증 URL 생성
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        # 로컬 서버 시작 (콜백 수신용)
        server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
        server.auth_code = None
        
        # 서버를 별도 스레드에서 실행
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # 브라우저 열기
        print(f"브라우저에서 인증을 진행해주세요: {auth_url}")
        webbrowser.open(auth_url)
        
        # 인증 코드 대기 (최대 5분)
        import time
        timeout = 300
        start_time = time.time()
        while server.auth_code is None:
            if time.time() - start_time > timeout:
                server.shutdown()
                raise TimeoutError("인증 시간이 초과되었습니다.")
            time.sleep(0.5)
        
        auth_code = server.auth_code
        server.shutdown()
        
        # 토큰 교환
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # 인증 정보 저장
        self._save_credentials(credentials)
        self.credentials = credentials
        
        return True
    
    def connect(self) -> bool:
        """구글 시트 연결"""
        if not GSPREAD_AVAILABLE:
            return False
        
        # 인증 확인
        if not self.credentials:
            credentials = self._load_credentials()
            if not credentials or not credentials.valid:
                return False
            self.credentials = credentials
        
        try:
            self.client = gspread.authorize(self.credentials)
            return True
        except Exception as e:
            print(f"구글 시트 연결 오류: {e}")
            return False
    
    def test_connection(self, spreadsheet_id: str) -> bool:
        """구글 시트 연결 테스트"""
        if not spreadsheet_id:
            return False
        
        if not self.connect():
            return False
        
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            # 첫 번째 시트 접근 시도
            sheet = spreadsheet.sheet1
            return True
        except Exception as e:
            print(f"구글 시트 접근 오류: {e}")
            return False
    
    def export_data(self, project_data, spreadsheet_id: str) -> bool:
        """프로젝트 데이터를 구글 시트로 내보내기"""
        if not self.connect():
            return False
        
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # 1. 시놉시스 시트
            self._export_synopsis(spreadsheet, project_data.get_synopsis())
            
            # 2. 등장인물 시트
            self._export_characters(spreadsheet, project_data.get_characters())
            
            # 3. 챕터 목록 시트
            chapters = project_data.get_chapters()
            self._export_chapter_list(spreadsheet, chapters)
            
            # 4. 각 챕터별 시트
            for chapter in chapters:
                self._export_chapter(spreadsheet, chapter)
            
            # 5. 이미지 스크립트 통합 시트
            self._export_image_scripts(spreadsheet, chapters)
            
            return True
        except Exception as e:
            print(f"데이터 내보내기 오류: {e}")
            return False
    
    def _get_or_create_sheet(self, spreadsheet, sheet_name: str):
        """시트 가져오기 또는 생성"""
        try:
            return spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            return spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
    
    def _export_synopsis(self, spreadsheet, synopsis: Dict[str, Any]):
        """시놉시스 내보내기"""
        sheet = self._get_or_create_sheet(spreadsheet, "시놉시스")
        
        # 헤더
        headers = ["항목", "내용"]
        sheet.clear()
        sheet.append_row(headers)
        
        # 데이터
        for key, value in synopsis.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False, indent=2)
            sheet.append_row([key, str(value)])
    
    def _export_characters(self, spreadsheet, characters: List[Dict[str, Any]]):
        """등장인물 내보내기"""
        sheet = self._get_or_create_sheet(spreadsheet, "등장인물")
        
        # 헤더
        headers = ["이름", "나이", "성별", "성격", "배경", "역할"]
        sheet.clear()
        sheet.append_row(headers)
        
        # 데이터
        for char in characters:
            row = [
                char.get('name', ''),
                char.get('age', ''),
                char.get('gender', ''),
                char.get('personality', ''),
                char.get('background', ''),
                char.get('role', '')
            ]
            sheet.append_row(row)
    
    def _export_chapter_list(self, spreadsheet, chapters: List[Dict[str, Any]]):
        """챕터 목록 내보내기"""
        sheet = self._get_or_create_sheet(spreadsheet, "챕터 목록")
        
        # 헤더
        headers = ["챕터 번호", "제목", "요약"]
        sheet.clear()
        sheet.append_row(headers)
        
        # 데이터
        for chapter in chapters:
            row = [
                chapter.get('chapter_number', ''),
                chapter.get('title', ''),
                chapter.get('summary', '')
            ]
            sheet.append_row(row)
    
    def _export_chapter(self, spreadsheet, chapter: Dict[str, Any]):
        """개별 챕터 내보내기"""
        chapter_num = chapter.get('chapter_number', 1)
        sheet_name = f"챕터_{chapter_num}"
        sheet = self._get_or_create_sheet(spreadsheet, sheet_name)
        
        # 챕터 정보
        sheet.clear()
        sheet.append_row(["챕터 정보"])
        sheet.append_row(["챕터 번호", chapter.get('chapter_number', '')])
        sheet.append_row(["제목", chapter.get('title', '')])
        sheet.append_row(["요약", chapter.get('summary', '')])
        sheet.append_row([])  # 빈 행
        
        # 대본
        sheet.append_row(["대본"])
        script = chapter.get('script', '')
        if script:
            # 대본을 여러 행으로 분할
            script_lines = script.split('\n')
            for line in script_lines:
                sheet.append_row([line])
        else:
            sheet.append_row(["대본이 없습니다."])
        sheet.append_row([])  # 빈 행
        
        # 장면 목록
        scenes = chapter.get('scenes', [])
        if scenes:
            sheet.append_row(["장면 목록"])
            sheet.append_row(["장면 번호", "제목", "이미지 프롬프트"])
            for scene in scenes:
                row = [
                    scene.get('scene_number', ''),
                    scene.get('title', ''),
                    scene.get('image_prompt', '')
                ]
                sheet.append_row(row)
        else:
            sheet.append_row(["장면이 없습니다."])
    
    def _export_image_scripts(self, spreadsheet, chapters: List[Dict[str, Any]]):
        """이미지 스크립트 통합 내보내기"""
        sheet = self._get_or_create_sheet(spreadsheet, "이미지 스크립트")
        
        # 헤더
        headers = ["챕터", "장면 번호", "장면 제목", "이미지 프롬프트"]
        sheet.clear()
        sheet.append_row(headers)
        
        # 데이터
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number', '')
            scenes = chapter.get('scenes', [])
            
            for scene in scenes:
                row = [
                    chapter_num,
                    scene.get('scene_number', ''),
                    scene.get('title', ''),
                    scene.get('image_prompt', '')
                ]
                sheet.append_row(row)

