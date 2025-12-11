"""
파일명 및 경로 처리 유틸리티
파일명 정규화, 프로젝트 폴더 이름 생성 등의 유틸리티 함수를 제공합니다.
"""

import re
from pathlib import Path
from typing import Optional


def normalize_filename(name: str) -> str:
    """
    파일명 정규화
    파일명에 사용할 수 없는 문자를 제거하거나 변환합니다.
    
    Args:
        name: 원본 이름
        
    Returns:
        정규화된 파일명
        
    Examples:
        >>> normalize_filename("김태주")
        '김태주'
        >>> normalize_filename("캐릭터: 이름")
        '캐릭터_ 이름'
        >>> normalize_filename("file<>name")
        'file__name'
    """
    if not name:
        return ""
    
    # 파일명에 사용할 수 없는 문자 목록
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    normalized = name
    for char in invalid_chars:
        normalized = normalized.replace(char, '_')
    
    # 연속된 언더스코어를 하나로 변환
    normalized = re.sub(r'_+', '_', normalized)
    
    # 앞뒤 공백 및 언더스코어 제거
    normalized = normalized.strip(' _')
    
    return normalized


def normalize_project_folder_name(project_number: int, title: str) -> str:
    """
    프로젝트 폴더 이름 정규화
    프로젝트 번호와 제목을 조합하여 정규화된 폴더 이름을 생성합니다.
    
    Args:
        project_number: 프로젝트 번호
        title: 제목
        
    Returns:
        정규화된 폴더 이름 (예: "001_사돈_그_선을_넘어도_되겠습니까")
        
    Examples:
        >>> normalize_project_folder_name(1, "사돈, 그 선을 넘어도 되겠습니까?")
        '001_사돈_그_선을_넘어도_되겠습니까'
        >>> normalize_project_folder_name(10, "Test Project")
        '010_Test_Project'
    """
    if not title:
        return f"{project_number:03d}"
    
    # 제목 정규화
    # 1. 공백을 언더스코어로 변환
    normalized_title = title.replace(' ', '_')
    
    # 2. 파일명에 사용할 수 없는 문자 제거
    normalized_title = normalize_filename(normalized_title)
    
    # 3. 특수문자 제거 (한글, 영문, 숫자, 언더스코어, 하이픈만 허용)
    # 한글 유니코드 범위: \uAC00-\uD7A3
    normalized_title = re.sub(r'[^\w\uAC00-\uD7A3_-]', '', normalized_title)
    
    # 4. 연속된 언더스코어를 하나로 변환
    normalized_title = re.sub(r'_+', '_', normalized_title)
    
    # 5. 앞뒤 공백 및 언더스코어 제거
    normalized_title = normalized_title.strip(' _')
    
    # 6. 프로젝트 번호와 조합
    if normalized_title:
        return f"{project_number:03d}_{normalized_title}"
    else:
        return f"{project_number:03d}"


def get_character_filename(character_name: str) -> str:
    """
    캐릭터 프로필 파일명 생성
    
    Args:
        character_name: 캐릭터 이름
        
    Returns:
        정규화된 파일명 (예: "김태주_profile.json")
        
    Examples:
        >>> get_character_filename("김태주")
        '김태주_profile.json'
        >>> get_character_filename("캐릭터: 이름")
        '캐릭터_이름_profile.json'
    """
    normalized_name = normalize_filename(character_name)
    if not normalized_name:
        normalized_name = "character"
    return f"{normalized_name}_profile.json"


def get_chapter_filename(chapter_number: int) -> str:
    """
    챕터 파일명 생성
    
    Args:
        chapter_number: 챕터 번호
        
    Returns:
        정규화된 파일명 (예: "chapter_01.json")
        
    Examples:
        >>> get_chapter_filename(1)
        'chapter_01.json'
        >>> get_chapter_filename(10)
        'chapter_10.json'
    """
    return f"chapter_{chapter_number:02d}.json"


def get_next_project_number(base_path: Path, category: str = "01_man") -> int:
    """
    다음 프로젝트 번호 결정 (자동 증가)
    
    Args:
        base_path: 프로젝트 루트 경로 (예: senior_contents/senior_project_manager/)
        category: 카테고리 폴더명 (예: "01_man")
        
    Returns:
        다음 프로젝트 번호 (예: 1, 2, 3, ...)
        
    Examples:
        >>> get_next_project_number(Path("../"), "01_man")
        1  # 첫 번째 프로젝트
        >>> get_next_project_number(Path("../"), "01_man")
        2  # 두 번째 프로젝트 (001_제목 폴더가 이미 있는 경우)
    """
    category_path = base_path / category
    if not category_path.exists():
        return 1
    
    # 기존 프로젝트 폴더 확인
    existing_numbers = []
    for folder in category_path.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            # 001_제목 형식 확인
            if folder_name.startswith('0') and '_' in folder_name:
                try:
                    num_str = folder_name.split('_')[0]
                    num = int(num_str)
                    existing_numbers.append(num)
                except (ValueError, IndexError):
                    pass
    
    if existing_numbers:
        return max(existing_numbers) + 1
    else:
        return 1

