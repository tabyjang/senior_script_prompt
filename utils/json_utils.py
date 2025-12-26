"""
JSON 처리 유틸리티
JSON 파싱, 포맷팅 등의 유틸리티 함수를 제공합니다.
"""

import json
from typing import Any, Dict, Optional


def extract_json_from_text(text: str) -> str:
    """
    텍스트에서 JSON 추출 (마크다운 코드 블록 제거)

    Args:
        text: JSON이 포함된 텍스트

    Returns:
        추출된 JSON 문자열
    """
    text = text.strip()

    # ```json ... ``` 형식 제거
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    return text


def safe_json_loads(text: str, default: Any = None) -> Any:
    """
    안전한 JSON 파싱 (오류 시 기본값 반환)

    Args:
        text: JSON 문자열
        default: 파싱 실패 시 반환할 기본값

    Returns:
        파싱된 객체 또는 기본값
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default


def format_json(data: Any, indent: int = 2) -> str:
    """
    JSON 포맷팅

    Args:
        data: JSON으로 변환할 데이터
        indent: 들여쓰기 레벨

    Returns:
        포맷된 JSON 문자열
    """
    return json.dumps(data, ensure_ascii=False, indent=indent)


def merge_dicts(base: Dict, update: Dict) -> Dict:
    """
    딕셔너리 병합 (재귀적)

    Args:
        base: 기본 딕셔너리
        update: 업데이트할 딕셔너리

    Returns:
        병합된 딕셔너리
    """
    result = base.copy()

    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result
