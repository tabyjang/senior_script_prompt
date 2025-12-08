"""
프로젝트 데이터 모델
시놉시스, 캐릭터, 챕터 등의 데이터 구조를 정의합니다.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path


class ProjectData:
    """프로젝트 데이터 관리 클래스"""

    def __init__(self, project_path: str = "01_man/001_gym_romance"):
        self.project_path = Path(project_path)
        self.data: Dict[str, Any] = {
            'synopsis': {},
            'characters': [],
            'chapters': []
        }
        self.unsaved_changes: Dict[str, bool] = {}

    def get_synopsis(self) -> Dict[str, Any]:
        """시놉시스 데이터 반환"""
        return self.data.get('synopsis', {})

    def set_synopsis(self, synopsis: Dict[str, Any]):
        """시놉시스 데이터 설정"""
        self.data['synopsis'] = synopsis
        self.mark_unsaved('synopsis')

    def get_characters(self) -> List[Dict[str, Any]]:
        """캐릭터 리스트 반환"""
        return self.data.get('characters', [])

    def set_characters(self, characters: List[Dict[str, Any]]):
        """캐릭터 리스트 설정"""
        self.data['characters'] = characters
        self.mark_unsaved('characters')

    def get_chapters(self) -> List[Dict[str, Any]]:
        """챕터 리스트 반환"""
        return self.data.get('chapters', [])

    def set_chapters(self, chapters: List[Dict[str, Any]]):
        """챕터 리스트 설정"""
        self.data['chapters'] = chapters
        self.mark_unsaved('chapters')

    def get_chapter_by_number(self, chapter_num: int) -> Optional[Dict[str, Any]]:
        """챕터 번호로 챕터 찾기"""
        for chapter in self.get_chapters():
            if chapter.get('chapter_number') == chapter_num:
                return chapter
        return None

    def mark_unsaved(self, key: str):
        """저장되지 않은 변경사항 표시"""
        self.unsaved_changes[key] = True

    def clear_unsaved(self):
        """저장되지 않은 변경사항 초기화"""
        self.unsaved_changes.clear()

    def has_unsaved_changes(self) -> bool:
        """저장되지 않은 변경사항 확인"""
        return bool(self.unsaved_changes)
