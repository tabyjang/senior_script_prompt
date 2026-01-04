"""
LLM 서비스
Gemini, OpenAI, Anthropic API 호출을 통합 관리합니다.
Lazy Import 방식으로 프로그램 시작 시간 최적화
"""

import os
from typing import Optional

# LLM 모듈 참조 (lazy import)
_genai = None
_openai = None
_anthropic = None


def _import_genai():
    """google.generativeai lazy import"""
    global _genai
    if _genai is None:
        try:
            import google.generativeai as genai
            _genai = genai
        except ImportError:
            _genai = False
    return _genai if _genai is not False else None


def _import_openai():
    """openai lazy import"""
    global _openai
    if _openai is None:
        try:
            import openai
            _openai = openai
        except ImportError:
            _openai = False
    return _openai if _openai is not False else None


def _import_anthropic():
    """anthropic lazy import"""
    global _anthropic
    if _anthropic is None:
        try:
            import anthropic
            _anthropic = anthropic
        except ImportError:
            _anthropic = False
    return _anthropic if _anthropic is not False else None


class LLMService:
    """LLM API 호출 서비스 클래스"""

    def __init__(self, config_manager):
        """
        Args:
            config_manager: ConfigManager 인스턴스
        """
        self.config = config_manager

    def call(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """
        LLM 호출

        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트 (선택적)

        Returns:
            LLM 응답 텍스트 또는 None (오류 시)
        """
        provider = self.config.get("provider", "gemini")

        if provider == "gemini":
            return self._call_gemini(prompt, system_prompt)
        elif provider == "openai":
            return self._call_openai(prompt, system_prompt)
        elif provider == "anthropic":
            return self._call_anthropic(prompt, system_prompt)
        else:
            raise ValueError(f"지원하지 않는 제공자: {provider}")

    def _call_gemini(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Gemini API 호출"""
        genai = _import_genai()
        if genai is None:
            raise ImportError("google-generativeai 패키지가 설치되지 않았습니다.\n설치: pip install google-generativeai")

        api_key = self.config.get("api_key", "").strip()
        if not api_key:
            raise ValueError("Gemini API 키가 설정되지 않았습니다.")

        if not api_key or len(api_key) < 10:
            raise ValueError("API 키가 유효하지 않습니다.")

        model_name = self.config.get("model", "gemini-1.5-flash")

        # 환경변수로 설정
        os.environ['GOOGLE_API_KEY'] = api_key
        genai.configure(api_key=api_key)

        # 모델 생성
        model = genai.GenerativeModel(model_name)

        # 시스템 프롬프트가 있으면 프롬프트에 포함
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        # API 호출
        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
            }
        )

        # 응답 확인
        if not response or not hasattr(response, 'text'):
            raise ValueError("API 응답이 올바르지 않습니다.")

        return response.text

    def _call_openai(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """OpenAI API 호출"""
        openai = _import_openai()
        if openai is None:
            raise ImportError("openai 패키지가 설치되지 않았습니다.\n설치: pip install openai")

        api_key = self.config.get("openai_api_key", "").strip()
        if not api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

        if len(api_key) < 10:
            raise ValueError("API 키가 유효하지 않습니다.")

        model_name = self.config.get("openai_model", "gpt-4o")

        # OpenAI 클라이언트 생성
        client = openai.OpenAI(api_key=api_key)

        # O1 시리즈는 다른 파라미터 사용
        if model_name.startswith("o1"):
            # O1 모델은 system prompt를 지원하지 않음
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": full_prompt}]
            )
        else:
            # 일반 GPT 모델
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=4096
            )

        # 응답 검증
        if not response or not response.choices or len(response.choices) == 0:
            raise ValueError("API 응답이 올바르지 않습니다.")

        if not hasattr(response.choices[0].message, 'content') or not response.choices[0].message.content:
            raise ValueError("API 응답에 내용이 없습니다.")

        return response.choices[0].message.content

    def _call_anthropic(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Anthropic API 호출"""
        anthropic = _import_anthropic()
        if anthropic is None:
            raise ImportError("anthropic 패키지가 설치되지 않았습니다.\n설치: pip install anthropic")

        api_key = self.config.get("anthropic_api_key", "").strip()
        if not api_key:
            raise ValueError("Anthropic API 키가 설정되지 않았습니다.")

        model_name = self.config.get("anthropic_model", "claude-3-5-haiku-20241022")

        client = anthropic.Anthropic(api_key=api_key)

        # 메시지 구성
        messages = []
        if system_prompt:
            messages.append({"role": "user", "content": f"{system_prompt}\n\n{prompt}"})
        else:
            messages.append({"role": "user", "content": prompt})

        response = client.messages.create(
            model=model_name,
            max_tokens=4096,
            messages=messages
        )

        # 응답에서 텍스트 추출
        if response.content and len(response.content) > 0:
            return response.content[0].text
        else:
            raise ValueError("API 응답에 내용이 없습니다.")

    @staticmethod
    def is_provider_available(provider: str) -> bool:
        """
        LLM 제공자가 사용 가능한지 확인

        Args:
            provider: 제공자 이름 (gemini, openai, anthropic)

        Returns:
            사용 가능 여부
        """
        if provider == "gemini":
            return _import_genai() is not None
        elif provider == "openai":
            return _import_openai() is not None
        elif provider == "anthropic":
            return _import_anthropic() is not None
        return False
