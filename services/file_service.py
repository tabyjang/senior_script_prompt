"""
파일 서비스
프로젝트 데이터의 파일 I/O를 담당합니다.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class FileService:
    """파일 입출력 서비스 클래스"""

    def __init__(self, project_path: Path):
        self.project_path = project_path

    def load_synopsis(self) -> Dict[str, Any]:
        """시놉시스 파일 로드"""
        synopsis_path = self.project_path / "synopsis.json"
        if synopsis_path.exists():
            try:
                with open(synopsis_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"시놉시스 로드 오류: {e}")
        return {}

    def save_synopsis(self, synopsis: Dict[str, Any]) -> bool:
        """시놉시스 파일 저장"""
        synopsis_path = self.project_path / "synopsis.json"
        try:
            with open(synopsis_path, 'w', encoding='utf-8') as f:
                json.dump(synopsis, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"시놉시스 저장 오류: {e}")
            return False

    def load_characters(self) -> List[Dict[str, Any]]:
        """캐릭터 파일들 로드"""
        characters = []
        characters_dir = self.project_path / "02_characters"

        if characters_dir.exists():
            for char_file in characters_dir.glob("*.json"):
                try:
                    with open(char_file, 'r', encoding='utf-8') as f:
                        char_data = json.load(f)
                        char_data['_filename'] = char_file.name
                        characters.append(char_data)
                except Exception as e:
                    print(f"캐릭터 파일 로드 오류 ({char_file.name}): {e}")

        return characters

    def save_characters(self, characters: List[Dict[str, Any]]) -> bool:
        """캐릭터 파일들 저장"""
        characters_dir = self.project_path / "02_characters"
        characters_dir.mkdir(parents=True, exist_ok=True)

        try:
            for char in characters:
                filename = char.get('_filename', f"{char.get('name', 'character')}_profile.json")
                char_path = characters_dir / filename

                # _filename 제거 후 저장
                save_data = {k: v for k, v in char.items() if k != '_filename'}

                with open(char_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"캐릭터 저장 오류: {e}")
            return False

    def load_chapters(self) -> List[Dict[str, Any]]:
        """챕터 파일들 로드"""
        chapters = []
        chapters_dir = self.project_path / "03_chapters"

        if chapters_dir.exists():
            for chapter_file in sorted(chapters_dir.glob("chapter_*.json")):
                try:
                    with open(chapter_file, 'r', encoding='utf-8') as f:
                        chapter_data = json.load(f)
                        chapter_data['_filename'] = chapter_file.name
                        chapters.append(chapter_data)
                except Exception as e:
                    print(f"챕터 파일 로드 오류 ({chapter_file.name}): {e}")

        return chapters

    def save_chapters(self, chapters: List[Dict[str, Any]]) -> bool:
        """챕터 파일들 저장"""
        chapters_dir = self.project_path / "03_chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        try:
            for chapter in chapters:
                chapter_num = chapter.get('chapter_number', 1)
                filename = chapter.get('_filename', f"chapter_{chapter_num:02d}.json")
                chapter_path = chapters_dir / filename

                # _filename 제거 후 저장
                save_data = {k: v for k, v in chapter.items() if k != '_filename'}

                with open(chapter_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"챕터 저장 오류: {e}")
            return False

    def save_chapter(self, chapter: Dict[str, Any]) -> bool:
        """단일 챕터 파일 저장"""
        chapters_dir = self.project_path / "03_chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        try:
            chapter_num = chapter.get('chapter_number', 1)
            filename = chapter.get('_filename', f"chapter_{chapter_num:02d}.json")
            chapter_path = chapters_dir / filename

            # _filename 제거 후 저장
            save_data = {k: v for k, v in chapter.items() if k != '_filename'}

            with open(chapter_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"챕터 저장 오류: {e}")
            return False

    def load_all_data(self) -> Dict[str, Any]:
        """모든 프로젝트 데이터 로드"""
        return {
            'synopsis': self.load_synopsis(),
            'characters': self.load_characters(),
            'chapters': self.load_chapters()
        }
