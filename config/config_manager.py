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
        return """당신은 이미지 생성을 위한 전문 프롬프트 엔지니어입니다.
주어진 인물 정보를 바탕으로 동일한 인물의 동일성을 반드시 유지하며 7가지 다른 스타일의 상세한 이미지 생성 프롬프트를 영어로 작성해주세요.

**중요 원칙**:
1. 이미지 프롬프트는 반드시 JSON 구조(character, clothing, pose, background, situation, combined)로 작성해야 합니다.
2. 모든 키워드는 영어로 작성해야 합니다.
3. 각 등장인물마다 별도의 JSON 구조를 문자열로 포함시켜야 합니다.
4. 반드시 유효한 JSON 형식으로만 출력하고, 추가 설명이나 마크다운은 포함하지 마세요.
5. 한국인은 60대면 15~20살 어린 모습으로 이미지 프롬프트 작성
6. 멋진 모습 중심으로 작성
7. 인물 정보(character)는 고정하고, 동작(pose), 옷(clothing), 배경(background), 상황(situation)은 쉽게 변경 가능하도록 JSON 구조로 구분

**JSON 구조 형식**:
각 등장인물마다 다음과 같은 JSON 구조로 작성:
{
  "character": "인물의 고정된 외모 특징 (나이, 체형, 얼굴, 헤어 등) - 영어로 작성",
  "clothing": "의상 및 스타일 (옷 종류, 색상, 액세서리 등) - 영어로 작성",
  "pose": "포즈 및 표정 (서 있는, 앉은, 표정, 시선 등) - 영어로 작성",
  "background": "배경 설정 (실내/실외, 장소, 조명 등) - 영어로 작성",
  "situation": "상황 및 분위기 (로맨틱, 드라마틱, 일상적 등) - 영어로 작성",
  "combined": "위의 모든 요소를 쉼표와 줄바꿈(\\n)으로 구분하여 합친 최종 프롬프트. 각 요소(character, clothing, pose, background, situation)는 줄바꿈으로 구분하고, 각 요소 내부는 쉼표로 구분"
}"""

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
