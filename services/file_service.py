"""
파일 서비스
프로젝트 데이터의 파일 I/O를 담당합니다.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.file_utils import normalize_filename, get_character_filename, get_chapter_filename, normalize_project_folder_name, get_next_project_number


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
                # 파일명 생성 (기존 _filename이 있으면 사용, 없으면 정규화된 이름 사용)
                if '_filename' in char:
                    filename = char['_filename']
                else:
                    char_name = char.get('name', 'character')
                    filename = get_character_filename(char_name)
                
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
                # 파일명 생성 (기존 _filename이 있으면 사용, 없으면 정규화된 이름 사용)
                if '_filename' in chapter:
                    filename = chapter['_filename']
                else:
                    filename = get_chapter_filename(chapter_num)
                
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
            # 파일명 생성 (기존 _filename이 있으면 사용, 없으면 정규화된 이름 사용)
            if '_filename' in chapter:
                filename = chapter['_filename']
            else:
                filename = get_chapter_filename(chapter_num)
            
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

    def get_character_image_dir(self, character_name: str) -> Path:
        """
        캐릭터 이미지 디렉토리 경로 반환
        Args:
            character_name: 캐릭터 이름
        Returns:
            이미지 디렉토리 경로
        """
        images_dir = self.project_path / "02_characters" / "images" / character_name
        images_dir.mkdir(parents=True, exist_ok=True)
        return images_dir

    def save_character_image(self, character_name: str, prompt_num: int, image_path: Path) -> Optional[str]:
        """
        캐릭터 이미지 파일 저장
        Args:
            character_name: 캐릭터 이름
            prompt_num: 프롬프트 번호 (1~7)
            image_path: 원본 이미지 파일 경로
        Returns:
            저장된 이미지의 상대 경로 또는 None (실패 시)
        """
        try:
            # 이미지 디렉토리 생성
            images_dir = self.get_character_image_dir(character_name)
            
            # 파일 확장자 유지
            ext = image_path.suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                ext = '.jpg'  # 기본값
            
            # 저장할 파일명: prompt_1.jpg, prompt_2.jpg 등
            target_filename = f"prompt_{prompt_num}{ext}"
            target_path = images_dir / target_filename
            
            # 파일 복사
            shutil.copy2(image_path, target_path)
            
            # 상대 경로 반환 (프로젝트 경로 기준)
            relative_path = f"images/{character_name}/{target_filename}"
            return relative_path
        except Exception as e:
            print(f"이미지 저장 오류 ({character_name}, prompt_{prompt_num}): {e}")
            return None

    def load_character_image_path(self, character_name: str, prompt_num: int) -> Optional[Path]:
        """
        캐릭터 이미지 파일 경로 로드
        Args:
            character_name: 캐릭터 이름
            prompt_num: 프롬프트 번호 (1~7)
        Returns:
            이미지 파일 경로 또는 None (없을 경우)
        """
        images_dir = self.get_character_image_dir(character_name)
        
        # 가능한 확장자들 확인
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            image_path = images_dir / f"prompt_{prompt_num}{ext}"
            if image_path.exists():
                return image_path
        
        return None

    def delete_character_image(self, character_name: str, prompt_num: int) -> bool:
        """
        캐릭터 이미지 파일 삭제
        Args:
            character_name: 캐릭터 이름
            prompt_num: 프롬프트 번호 (1~7)
        Returns:
            삭제 성공 여부
        """
        try:
            images_dir = self.get_character_image_dir(character_name)
            
            # 가능한 확장자들 확인하여 삭제
            deleted = False
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                image_path = images_dir / f"prompt_{prompt_num}{ext}"
                if image_path.exists():
                    image_path.unlink()
                    deleted = True
            
            return deleted
        except Exception as e:
            print(f"이미지 삭제 오류 ({character_name}, prompt_{prompt_num}): {e}")
            return False

    def create_project_folder(self, title: str, category: str = "01_man", base_path: Optional[Path] = None) -> Optional[Path]:
        """
        프로젝트 폴더 생성
        프로젝트 번호는 자동 증가 방식으로 결정됩니다.
        
        Args:
            title: 프로젝트 제목
            category: 카테고리 폴더명 (예: "01_man")
            base_path: 프로젝트 루트 경로 (None이면 자동으로 찾음)
            
        Returns:
            생성된 프로젝트 폴더 경로 또는 None (실패 시)
        """
        try:
            # 프로젝트 루트 경로 결정
            if base_path is None:
                import os
                # 현재 실행 중인 파일의 위치를 기준으로 찾기
                # main.py 또는 editors_app 폴더에서 실행 중
                current_file = Path(__file__).resolve()  # file_service.py의 위치
                # file_service.py는 services/ 폴더에 있음
                # editors_app/services/file_service.py -> editors_app의 parent가 01_man
                
                # editors_app 폴더 찾기
                editors_app_path = None
                test_path = current_file.parent  # services/
                for _ in range(3):  # 최대 3단계까지
                    if test_path.name == "editors_app":
                        editors_app_path = test_path
                        break
                    test_path = test_path.parent
                
                if editors_app_path:
                    # editors_app의 parent가 01_man인지 확인
                    parent_name = editors_app_path.parent.name
                    if parent_name == category:
                        # 01_man 폴더를 찾음
                        # base_path는 01_man 폴더 자체 (프로젝트는 01_man 안에 직접 생성)
                        base_path = editors_app_path.parent
                    else:
                        # 01_man 폴더가 없으면 생성
                        category_path = editors_app_path.parent / category
                        category_path.mkdir(parents=True, exist_ok=True)
                        base_path = category_path
                    print(f"[프로젝트 폴더 생성] editors_app 경로: {editors_app_path}")
                    print(f"[프로젝트 폴더 생성] 카테고리 폴더 (base_path): {base_path}")
                else:
                    # editors_app을 찾지 못한 경우, 현재 프로젝트 경로 기준
                    try:
                        current_path = Path(self.project_path)
                        if not current_path.is_absolute():
                            # 상대 경로인 경우 절대 경로로 변환
                            current_path = Path(os.getcwd()) / current_path
                        current_path = current_path.resolve()
                    except Exception as e:
                        print(f"[프로젝트 폴더 생성] 경로 변환 오류: {e}")
                        current_path = Path(os.getcwd())
                    
                    # 상위 디렉토리로 올라가면서 01_man 폴더 찾기
                    test_path = current_path
                    base_path = None
                    for _ in range(5):
                        if test_path.name == category:
                            base_path = test_path.parent
                            break
                        elif test_path.name == "editors_app":
                            if test_path.parent.name == category:
                                base_path = test_path.parent.parent
                                break
                        test_path = test_path.parent
                    
                    if base_path is None:
                        # 찾지 못한 경우, 현재 경로의 parent.parent 사용
                        base_path = current_path.parent.parent
                        print(f"[프로젝트 폴더 생성] 경로를 찾지 못해 기본 경로 사용: {base_path}")
                
                print(f"[프로젝트 폴더 생성] 최종 base_path: {base_path}")
            
            # base_path가 존재하지 않으면 생성
            if not base_path.exists():
                print(f"[경고] base_path가 존재하지 않습니다: {base_path}")
                # base_path 생성 시도
                try:
                    base_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    print(f"[오류] base_path 생성 실패: {e}")
                    return None
            
            # 다음 프로젝트 번호 결정
            # base_path가 이미 01_man인 경우 직접 처리
            if base_path.name == category:
                # base_path가 이미 카테고리 폴더인 경우
                category_path = base_path
                base_for_number = base_path.parent
            else:
                # base_path가 상위 폴더인 경우
                category_path = base_path / category
                base_for_number = base_path
            
            # 프로젝트 번호 결정
            if not category_path.exists():
                project_number = 1
            else:
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
                    project_number = max(existing_numbers) + 1
                else:
                    project_number = 1
            
            print(f"[프로젝트 폴더 생성] 프로젝트 번호: {project_number}")
            
            # 폴더명 생성
            folder_name = normalize_project_folder_name(project_number, title)
            # base_path가 이미 01_man이므로, 그 안에 직접 생성
            project_path = base_path / folder_name
            print(f"[프로젝트 폴더 생성] 생성할 경로: {project_path}")
            
            # 폴더 생성
            project_path.mkdir(parents=True, exist_ok=True)
            print(f"[프로젝트 폴더 생성] 폴더 생성 완료: {project_path}")
            
            # 하위 폴더 생성
            (project_path / "02_characters").mkdir(exist_ok=True)
            (project_path / "03_chapters").mkdir(exist_ok=True)
            (project_path / "04_scripts").mkdir(exist_ok=True)
            print(f"[프로젝트 폴더 생성] 하위 폴더 생성 완료")
            
            return project_path
        except Exception as e:
            print(f"프로젝트 폴더 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def set_project_path(self, new_path: Path):
        """
        프로젝트 경로 변경
        Args:
            new_path: 새로운 프로젝트 경로
        """
        self.project_path = new_path

    def save_script_file(self, chapter_number: int, script: str, scenes: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        대본 파일 저장
        Args:
            chapter_number: 챕터 번호
            script: 대본 텍스트
            scenes: 장면 리스트 (선택사항)
        Returns:
            저장 성공 여부
        """
        scripts_dir = self.project_path / "04_scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        script_data = {
            "chapter_number": chapter_number,
            "script": script,
            "script_length": len(script),
            "script_generated_at": datetime.now().isoformat()
        }
        
        if scenes:
            script_data["scenes"] = scenes
            script_data["scenes_generated_at"] = datetime.now().isoformat()
        
        filename = f"chapter_{chapter_number:02d}_script.json"
        script_path = scripts_dir / filename
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"대본 파일 저장 오류: {e}")
            return False

    def load_script_file(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """
        대본 파일 로드
        Args:
            chapter_number: 챕터 번호
        Returns:
            대본 데이터 딕셔너리 또는 None (없을 경우)
        """
        scripts_dir = self.project_path / "04_scripts"
        filename = f"chapter_{chapter_number:02d}_script.json"
        script_path = scripts_dir / filename
        
        if script_path.exists():
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"대본 파일 로드 오류 ({filename}): {e}")
        
        return None

    def save_scenes_to_script(self, chapter_number: int, scenes: List[Dict[str, Any]]) -> bool:
        """
        장면 정보를 대본 파일에 추가/업데이트
        대본 파일이 없으면 생성합니다.
        
        Args:
            chapter_number: 챕터 번호
            scenes: 장면 리스트
        Returns:
            저장 성공 여부
        """
        # 기존 대본 파일 로드
        script_data = self.load_script_file(chapter_number)
        
        if script_data is None:
            # 대본 파일이 없으면 빈 대본으로 생성
            script_data = {
                "chapter_number": chapter_number,
                "script": "",
                "script_length": 0,
                "script_generated_at": datetime.now().isoformat()
            }
        
        # 장면 정보 업데이트
        script_data["scenes"] = scenes
        script_data["scenes_generated_at"] = datetime.now().isoformat()
        
        # 저장
        scripts_dir = self.project_path / "04_scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        filename = f"chapter_{chapter_number:02d}_script.json"
        script_path = scripts_dir / filename
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"장면 정보 저장 오류: {e}")
            return False
