"""
파일 서비스
프로젝트 데이터의 파일 I/O를 담당합니다.
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.file_utils import (
    normalize_filename,
    normalize_character_name,
    get_character_filename,
    get_character_detail_filename,
    get_numbered_character_profile_filename,
    get_numbered_character_detail_filename,
    get_numbered_character_image_prompts_filename,
    get_chapter_filename,
    normalize_project_folder_name,
    get_next_project_number,
)


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
        characters: List[Dict[str, Any]] = []
        characters_dir = self.project_path / "02_characters"

        if characters_dir.exists():
            merged_by_key: Dict[str, Dict[str, Any]] = {}
            ordered_keys: List[str] = []
            needs_cleanup = False
            for idx, char_file in enumerate(sorted(characters_dir.glob("*.json")), start=1):
                try:
                    with open(char_file, 'r', encoding='utf-8') as f:
                        char_data = json.load(f)
                        char_data['_filename'] = char_file.name

                        # name 정규화: 공백 제거(예: "김회장" == "김 회장")
                        raw_name = char_data.get("name", "")
                        if isinstance(raw_name, str):
                            normalized_name = normalize_character_name(raw_name)
                            if normalized_name != raw_name:
                                needs_cleanup = True
                            char_data["name"] = normalized_name

                        # image_generation_prompts 정규화(과거 데이터 호환)
                        prompts_obj = char_data.get("image_generation_prompts")
                        if isinstance(prompts_obj, str):
                            try:
                                parsed = json.loads(prompts_obj)
                                prompts_obj = parsed if isinstance(parsed, dict) else {}
                            except Exception:
                                prompts_obj = {}
                            char_data["image_generation_prompts"] = prompts_obj
                        elif prompts_obj is None:
                            char_data["image_generation_prompts"] = {}
                        elif not isinstance(prompts_obj, dict):
                            char_data["image_generation_prompts"] = {}

                        # image_prompts 파일이 있으면 프로필에 복원(누락된 prompt만 채움)
                        try:
                            self._sync_image_prompts_into_profile_from_file(char_data, character_index=idx)
                        except Exception as e:
                            print(f"이미지 프롬프트 동기화 오류 ({char_file.name}): {e}")

                        # 중복(공백만 다른 이름 등) 병합: 첫 항목 유지 + 빈 값만 채우기
                        key = normalize_character_name(char_data.get("name", ""))
                        if not key:
                            characters.append(char_data)
                            continue

                        if key not in merged_by_key:
                            merged_by_key[key] = char_data
                            ordered_keys.append(key)
                        else:
                            needs_cleanup = True
                            existing = merged_by_key[key]
                            for k, v in char_data.items():
                                if k in ["_filename"]:
                                    continue
                                if k not in existing or existing.get(k) in ["", None, {}, []]:
                                    existing[k] = v

                            # image_generation_prompts는 dict 병합
                            ex_prompts = existing.get("image_generation_prompts", {})
                            new_prompts = char_data.get("image_generation_prompts", {})
                            if isinstance(ex_prompts, dict) and isinstance(new_prompts, dict):
                                for pk, pv in new_prompts.items():
                                    if pk not in ex_prompts or ex_prompts.get(pk) in ["", None]:
                                        ex_prompts[pk] = pv
                                existing["image_generation_prompts"] = ex_prompts
                except Exception as e:
                    print(f"캐릭터 파일 로드 오류 ({char_file.name}): {e}")

            # 병합 결과를 순서대로 추가
            for k in ordered_keys:
                characters.append(merged_by_key[k])

            # (자동 정리) 공백 정규화/중복 병합이 발생한 경우 파일을 즉시 정리하여
            # 다음 실행부터 "김 회장" 같은 중복 파일이 다시 안 생기도록 한다.
            if needs_cleanup:
                try:
                    self.save_characters(characters)
                except Exception as e:
                    print(f"캐릭터 자동 정리 저장 오류: {e}")

        return characters

    def save_characters(self, characters: List[Dict[str, Any]]) -> bool:
        """캐릭터 파일들 저장"""
        characters_dir = self.project_path / "02_characters"
        characters_dir.mkdir(parents=True, exist_ok=True)

        try:
            expected_files = set()
            for idx, char in enumerate(characters, start=1):
                # 저장 시 항상 순서대로 넘버링된 파일명 부여
                if isinstance(char.get("name"), str):
                    char["name"] = normalize_character_name(char.get("name"))
                char_name = char.get("name", "character")
                filename = get_numbered_character_profile_filename(idx, char_name)
                char["_filename"] = filename
                expected_files.add(filename)
                
                char_path = characters_dir / filename

                # _filename 제거 후 저장
                save_data = {k: v for k, v in char.items() if k != '_filename'}

                with open(char_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)

            # (정리) 현재 예상 파일 목록 외, 02_characters/*.json 제거(구버전/중복 파일 정리)
            try:
                for f in characters_dir.glob("*.json"):
                    if f.name not in expected_files:
                        try:
                            f.unlink()
                        except Exception as e:
                            print(f"파일 삭제 오류 ({f.name}): {e}")
            except Exception as e:
                print(f"캐릭터 파일 정리 중 오류: {e}")

            # (추가) 캐릭터 프로필 저장 시 image_prompts 파일도 동기화 저장 (2중 저장)
            try:
                self._sync_image_prompts_from_profiles(characters)
            except Exception as e:
                print(f"이미지 프롬프트 파일 동기화 저장 오류: {e}")

            return True
        except Exception as e:
            print(f"캐릭터 저장 오류: {e}")
            return False

    def load_character_details(self) -> List[Dict[str, Any]]:
        """캐릭터 디테일 파일들 로드 (02_characters/details/*.json)"""
        details: List[Dict[str, Any]] = []
        details_dir = self.project_path / "02_characters" / "details"

        if details_dir.exists():
            for detail_file in sorted(details_dir.glob("*.json")):
                try:
                    with open(detail_file, "r", encoding="utf-8") as f:
                        detail_data = json.load(f)
                        detail_data["_detail_filename"] = detail_file.name
                        details.append(detail_data)
                except Exception as e:
                    print(f"캐릭터 디테일 파일 로드 오류 ({detail_file.name}): {e}")

        return details

    def get_character_image_prompts_dir(self) -> Path:
        """
        캐릭터 이미지 프롬프트 폴더 경로 반환 (02_characters/image_prompts)
        """
        prompts_dir = self.project_path / "02_characters" / "image_prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        return prompts_dir

    def save_character_image_prompts(
        self,
        character_name: str,
        prompts_by_number: Dict[int, Dict[str, Any]],
        character_index: Optional[int] = None,
    ) -> bool:
        """
        캐릭터 이미지 프롬프트 파일 저장
        - 폴더: 02_characters/image_prompts/
        - 파일: 01_이름_image_prompts.json 형태(프로필 순서 기반)
        - 내용: prompt_1..prompt_8을 dict로 저장
        """
        try:
            if not character_name:
                return False
            if not isinstance(prompts_by_number, dict):
                return False

            prompts_dir = self.get_character_image_prompts_dir()

            # 인덱스가 없으면 프로필(인포) 기준으로 매칭
            if character_index is None:
                characters = self.load_characters()
                name_to_index = self._build_character_index_map(characters)
                norm_name = normalize_character_name(character_name)
                character_index = name_to_index.get(norm_name, 1)

            filename = get_numbered_character_image_prompts_filename(character_index, character_name)
            file_path = prompts_dir / filename

            # 기존 파일이 있으면 병합
            existing_prompts: Dict[str, Any] = {}
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                        if isinstance(existing, dict):
                            existing_prompts = existing.get("image_generation_prompts", {}) if isinstance(existing.get("image_generation_prompts"), dict) else {}
                except Exception:
                    existing_prompts = {}

            merged_prompts = dict(existing_prompts)
            for n, prompt_dict in prompts_by_number.items():
                if not isinstance(n, int) or n < 1 or n > 8:
                    continue
                if isinstance(prompt_dict, dict):
                    merged_prompts[f"prompt_{n}"] = prompt_dict

            payload = {
                "character_name": character_name,
                "image_generation_prompts": merged_prompts,
                "updated_at": datetime.now().isoformat(),
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"이미지 프롬프트 파일 저장 오류 ({character_name}): {e}")
            return False

    def load_character_image_prompts(self, character_name: str, character_index: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        캐릭터 이미지 프롬프트 파일 로드 (02_characters/image_prompts/)
        Returns:
            {"character_name": str, "image_generation_prompts": {prompt_1: {...}, ...}} 또는 None
        """
        try:
            if not character_name:
                return None
            prompts_dir = self.get_character_image_prompts_dir()

            if character_index is None:
                characters = self.load_characters()
                name_to_index = self._build_character_index_map(characters)
                norm_name = normalize_character_name(character_name)
                character_index = name_to_index.get(norm_name, 1)

            filename = get_numbered_character_image_prompts_filename(character_index, character_name)
            file_path = prompts_dir / filename
            if not file_path.exists():
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else None
        except Exception as e:
            print(f"이미지 프롬프트 파일 로드 오류 ({character_name}): {e}")
            return None

    def _build_character_index_map(self, characters: List[Dict[str, Any]]) -> Dict[str, int]:
        """name(공백 정리) -> 1-based index 매핑"""
        def _norm(n: str) -> str:
            return normalize_character_name(n or "")

        name_to_index: Dict[str, int] = {}
        for idx, c in enumerate(characters, start=1):
            name = _norm(c.get("name", ""))
            if name:
                name_to_index[name] = idx
        return name_to_index

    def _sync_image_prompts_into_profile_from_file(self, profile: Dict[str, Any], character_index: int) -> None:
        """
        image_prompts 폴더 파일을 읽어, 프로필의 image_generation_prompts에 누락된 prompt만 복원.
        - 프로필 저장 형식은 "JSON 문자열"이므로 dict -> json.dumps로 변환해 넣는다.
        """
        if not isinstance(profile, dict):
            return
        name = profile.get("name", "")
        if not isinstance(name, str) or not name.strip():
            return
        # 공백 제거 정규화(김회장 == 김 회장)
        profile["name"] = normalize_character_name(name)
        name = profile["name"]

        data = self.load_character_image_prompts(name, character_index=character_index)
        if not data or not isinstance(data, dict):
            return

        prompts_from_file = data.get("image_generation_prompts", {})
        if not isinstance(prompts_from_file, dict):
            return

        prompts_obj = profile.get("image_generation_prompts", {})
        if not isinstance(prompts_obj, dict):
            prompts_obj = {}
            profile["image_generation_prompts"] = prompts_obj

        for n in range(1, 9):
            key = f"prompt_{n}"
            existing = prompts_obj.get(key, "")
            # 프로필이 비어있을 때만 파일 값으로 채움
            if isinstance(existing, str) and existing.strip():
                continue
            file_val = prompts_from_file.get(key)
            if isinstance(file_val, dict):
                prompts_obj[key] = json.dumps(file_val, ensure_ascii=False)

        # prompt_1이 있고 image_generation_prompt가 비어있으면 동기화
        if not (isinstance(profile.get("image_generation_prompt"), str) and profile.get("image_generation_prompt").strip()):
            p1 = prompts_obj.get("prompt_1", "")
            if isinstance(p1, str) and p1.strip():
                profile["image_generation_prompt"] = p1

    def _sync_image_prompts_from_profiles(self, characters: List[Dict[str, Any]]) -> None:
        """
        프로필의 image_generation_prompts(JSON 문자열) -> image_prompts 파일(dict)로 저장
        """
        if not isinstance(characters, list) or not characters:
            return

        for idx, c in enumerate(characters, start=1):
            if not isinstance(c, dict):
                continue
            name = c.get("name", "")
            if not isinstance(name, str) or not name.strip():
                continue
            c["name"] = normalize_character_name(name)
            name = c["name"]

            prompts_obj = c.get("image_generation_prompts", {})
            if isinstance(prompts_obj, str):
                try:
                    parsed = json.loads(prompts_obj)
                    prompts_obj = parsed if isinstance(parsed, dict) else {}
                except Exception:
                    prompts_obj = {}
            if not isinstance(prompts_obj, dict):
                prompts_obj = {}

            prompts_by_number: Dict[int, Dict[str, Any]] = {}
            for n in range(1, 9):
                key = f"prompt_{n}"
                val = prompts_obj.get(key, "")
                if isinstance(val, dict):
                    prompts_by_number[n] = val
                elif isinstance(val, str) and val.strip():
                    try:
                        parsed = json.loads(val)
                        if isinstance(parsed, dict):
                            prompts_by_number[n] = parsed
                    except Exception:
                        # JSON 문자열이 아니면 무시
                        pass

            if prompts_by_number:
                self.save_character_image_prompts(
                    character_name=name,
                    prompts_by_number=prompts_by_number,
                    character_index=idx,
                )

        # (정리) image_prompts 폴더 정리: 현재 캐릭터 목록 기준 예상 파일 외 삭제
        try:
            prompts_dir = self.get_character_image_prompts_dir()
            expected = set()
            for idx, c in enumerate(characters, start=1):
                nm = c.get("name", "")
                if isinstance(nm, str) and nm.strip():
                    expected.add(get_numbered_character_image_prompts_filename(idx, nm))
            for f in prompts_dir.glob("*.json"):
                if f.name not in expected:
                    try:
                        f.unlink()
                    except Exception as e:
                        print(f"이미지 프롬프트 파일 삭제 오류 ({f.name}): {e}")
        except Exception as e:
            print(f"이미지 프롬프트 폴더 정리 중 오류: {e}")

    def _sync_details_into_profiles(self, details: List[Dict[str, Any]]) -> bool:
        """
        details 폴더의 내용을 캐릭터 프로필 파일에도 추가로 기록(동기화)
        - 프로필 dict에 character_detail 키로 묶어 저장하여 필드 충돌을 방지
        """
        try:
            if not isinstance(details, list) or not details:
                return True

            def _norm(n: str) -> str:
                return normalize_character_name(n or "")

            # name -> detail(내부키 제거, name 제외) 매핑
            detail_by_name: Dict[str, Dict[str, Any]] = {}
            for d in details:
                if not isinstance(d, dict):
                    continue
                name = _norm(d.get("name", ""))
                if not name:
                    continue
                # profile에 넣을 detail payload (name/_detail_filename 제외)
                payload = {k: v for k, v in d.items() if k not in ["name", "_detail_filename"]}
                detail_by_name[name] = payload

            if not detail_by_name:
                return True

            characters = self.load_characters()
            changed = False
            for c in characters:
                if not isinstance(c, dict):
                    continue
                name = _norm(c.get("name", ""))
                if not name:
                    continue
                if name in detail_by_name:
                    c["character_detail"] = detail_by_name[name]
                    changed = True

            if changed:
                return self.save_characters(characters)
            return True
        except Exception as e:
            print(f"캐릭터 디테일 → 프로필 동기화 오류: {e}")
            return False

    def save_character_details(self, details: List[Dict[str, Any]]) -> bool:
        """캐릭터 디테일 파일들 저장 (02_characters/details/)"""
        details_dir = self.project_path / "02_characters" / "details"
        details_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 프로필(인포) 순서에 맞춰 디테일도 동일 번호로 맞춤
            try:
                characters = self.load_characters()
            except Exception:
                characters = []
            name_to_index = self._build_character_index_map(characters)

            for detail in details:
                # 저장 시 항상 넘버링된 파일명 부여(가능하면 프로필과 동일 번호)
                if isinstance(detail.get("name"), str):
                    detail["name"] = normalize_character_name(detail.get("name"))
                char_name = detail.get("name", "character")
                norm_name = normalize_character_name(char_name)
                idx = name_to_index.get(norm_name)
                if idx is None:
                    # 프로필에 없으면 디테일 리스트 순서대로 번호 부여(뒤로 밀림)
                    idx = len(name_to_index) + 1
                    name_to_index[norm_name] = idx
                filename = get_numbered_character_detail_filename(idx, char_name)
                detail["_detail_filename"] = filename

                detail_path = details_dir / filename

                # 내부 키 제거 후 저장
                save_data = {k: v for k, v in detail.items() if k not in ["_detail_filename"]}
                with open(detail_path, "w", encoding="utf-8") as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)

            # (정리) details 폴더 정리: 현재 details 목록 기준 예상 파일 외 삭제
            try:
                expected = {d.get("_detail_filename") for d in details if isinstance(d, dict) and d.get("_detail_filename")}
                for f in details_dir.glob("*.json"):
                    if f.name not in expected:
                        try:
                            f.unlink()
                        except Exception as e:
                            print(f"디테일 파일 삭제 오류 ({f.name}): {e}")
            except Exception as e:
                print(f"디테일 폴더 정리 중 오류: {e}")

            # 저장 후 프로필 파일에도 디테일을 추가로 기록
            self._sync_details_into_profiles(details)
            return True
        except Exception as e:
            print(f"캐릭터 디테일 저장 오류: {e}")
            return False

    def save_character_detail(self, detail: Dict[str, Any], character_index: Optional[int] = None) -> bool:
        """단일 캐릭터 디테일 저장"""
        if not isinstance(detail, dict):
            return False

        details_dir = self.project_path / "02_characters" / "details"
        details_dir.mkdir(parents=True, exist_ok=True)

        try:
            if isinstance(detail.get("name"), str):
                detail["name"] = normalize_character_name(detail.get("name"))
            char_name = detail.get("name", "character")
            if character_index is None:
                # 프로필(인포) 기준 인덱스 매칭 시도
                characters = self.load_characters()
                name_to_index = self._build_character_index_map(characters)
                norm_name = normalize_character_name(char_name)
                character_index = name_to_index.get(norm_name, 1)

            filename = get_numbered_character_detail_filename(character_index, char_name)
            detail["_detail_filename"] = filename

            detail_path = details_dir / filename
            save_data = {k: v for k, v in detail.items() if k not in ["_detail_filename"]}
            with open(detail_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            # 저장 후 프로필 파일에도 디테일을 추가로 기록
            try:
                self._sync_details_into_profiles([detail])
            except Exception as e:
                print(f"프로필 동기화 오류: {e}")
            return True
        except Exception as e:
            print(f"캐릭터 디테일 저장 오류: {e}")
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
