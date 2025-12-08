"""
설정 관리 모듈
LLM API 키 및 프로젝트 설정을 로드/저장합니다.
"""

import json
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """설정 파일 관리 클래스"""

    def __init__(self):
        self.config_path = Path.home() / ".senior_contents_config.json"
        self.config = self._load_default_config()
        self.load()

    def _load_default_config(self) -> Dict[str, Any]:
        """기본 설정 값 반환"""
        return {
            "provider": "anthropic",
            "model": "gemini-1.5-flash",
            "api_key": "",
            "openai_api_key": "",
            "openai_model": "gpt-4o",
            "anthropic_api_key": "",
            "anthropic_model": "claude-3-5-haiku-20241022",
            "image_system_prompt": self._get_default_image_system_prompt(),
            # 구글 시트 설정
            "google_sheets_enabled": False,
            "google_sheets_spreadsheet_id": "",
            "google_sheets_credentials_path": str(Path.home() / ".senior_contents_google_credentials.json"),
            "google_sheets_token_path": str(Path.home() / ".senior_contents_google_token.json"),
            "google_sheets_client_id": "",
            "google_sheets_client_secret": ""
        }

    def _get_default_image_system_prompt(self) -> str:
        """기본 이미지 시스템 프롬프트"""
        return """당신은 Stable Diffusion 이미지 생성을 위한 전문 프롬프트 엔지니어입니다.
주어진 인물 정보를 바탕으로 동일한 인물의 동일성을 반드시 유지하며 5가지 다른 스타일의 상세한 이미지 생성 프롬프트를 영어로 작성해주세요.

**Stable Diffusion 최적화 원칙**:
1. 모든 프롬프트는 **한국인 (Korean, East Asian)** 으로 명시해야 합니다
2. 실제 나이보다 **건강하고 젊어보이고 세련된** 외모로 표현하세요 (동양인은 더 어려보이고, 오디오북에서 젊은 이미지가 좋습니다)
3. 모든 프롬프트에서 동일한 인물의 일관성 유지 (얼굴 특징, 체형, 머리카락 등)
4. 각 프롬프트는 다른 각도, 포즈, 복장이지만 기본 외모는 동일해야 합니다
5. Stable Diffusion 품질 키워드 포함: 8K, highly detailed, photorealistic, professional photography
6. 카메라 설정 포함: 렌즈 타입, 조명, 구도
7. 부정적 요소 제거: no cartoon, no anime, no distortion
8. 반드시 JSON 형식으로만 응답해주세요"""

    def load(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"설정 파일 로드 오류: {e}")
        return self.config

    def save(self) -> bool:
        """설정 파일 저장"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"설정 저장 오류: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 가져오기"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """설정 값 설정"""
        self.config[key] = value

    def update(self, updates: Dict[str, Any]):
        """설정 일괄 업데이트"""
        self.config.update(updates)
