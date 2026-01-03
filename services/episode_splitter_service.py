"""
Episode Splitter Service
MD 파일을 ACT/에피소드별로 분리하는 서비스 (일반화 버전)
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class EpisodeSplitterService:
    """MD 파일을 에피소드별로 분리하는 서비스"""

    def __init__(self):
        pass

    def clean_text_for_tts(self, text: str) -> str:
        """TTS용으로 텍스트 정리"""
        # 마크다운 이스케이프 문자 제거
        text = text.replace("\\.", ".")
        text = text.replace("\\!", "!")
        text = text.replace("\\?", "?")
        text = text.replace("\\,", ",")
        text = text.replace("\\'", "'")
        text = text.replace('\\"', '"')
        text = text.replace("\\[", "[")
        text = text.replace("\\]", "]")
        text = text.replace("\\(", "(")
        text = text.replace("\\)", ")")
        text = text.replace("\\-", "-")
        text = text.replace("\\_", "_")
        text = text.replace("\\*", "*")

        # 마크다운 강조 제거
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)

        # 불필요한 메타 정보 제거
        text = re.sub(r'분량:\s*약\s*[\d,]+자', '', text)
        text = re.sub(r'\d+화\s*이어서\s*작성할까요\?', '', text)
        text = re.sub(r'좋아요!\s*\d+화\s*이어갑니다\.?', '', text)
        text = re.sub(r'좋아요\\!\s*\d+화\s*이어갑니다\\.?', '', text)

        # 여러 줄바꿈을 하나로
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 앞뒤 공백 제거
        text = text.strip()

        return text

    def clean_filename(self, text: str) -> str:
        """파일명에 사용할 수 없는 문자 제거"""
        # 파일명 금지 문자 제거
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # 공백을 언더스코어로
        text = re.sub(r'\s+', '_', text)
        # 연속된 언더스코어 정리
        text = re.sub(r'_+', '_', text)
        # 앞뒤 언더스코어 제거
        text = text.strip('_')
        return text

    def detect_act_structure(self, content: str) -> Dict[int, Tuple[str, str]]:
        """파일에서 ACT 구조 자동 감지"""
        act_mapping = {}

        # ACT/막 패턴 찾기
        # 예: __1막: 지옥의 시작 (1-3챕터, 25%)__
        # 예: __1막 (1-3챕터): 지옥의 시작__
        act_patterns = [
            r'(?:__|__)(\d)막[:\s]*([^(_\n]+?)[\s]*\((\d+)-(\d+)(?:챕터|화)',
            r'(?:__|__)(\d)막\s*\((\d+)-(\d+)(?:챕터|화)[^)]*\)[:\s]*([^_\n]+?)(?:__|__)',
            r'(\d)막[:\s]+([^(]+?)\s*\((\d+)-(\d+)',
        ]

        for pattern in act_patterns:
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    if len(match) == 4:
                        # 첫 번째 패턴: (막번호, 이름, 시작화, 끝화)
                        act_num, act_name, start_ep, end_ep = match
                    else:
                        continue

                    act_name = act_name.strip().replace("\\", "")
                    for ep in range(int(start_ep), int(end_ep) + 1):
                        act_mapping[ep] = (f"Act{act_num}", self.clean_filename(act_name))
                break

        return act_mapping

    def extract_episodes(self, content: str) -> Dict[int, Dict]:
        """MD 파일에서 에피소드 추출"""
        episodes = {}

        # ACT 구조 감지
        act_mapping = self.detect_act_structure(content)

        # 에피소드 패턴들 (다양한 형식 지원)
        episode_patterns = [
            r'(?:__|__)제(\d+)화[\.\s\\\.]+([^_\n]+?)(?:__|__)',  # __제N화. 제목__
            r'(?:__|__)(\d+)화[\.\s\\\.]+([^_\n]+?)(?:__|__)',   # __N화. 제목__
            r'#\s*제?(\d+)화[\.\s:]+(.+?)(?:\n|$)',              # # 제N화: 제목
            r'##\s*제?(\d+)화[\.\s:]+(.+?)(?:\n|$)',             # ## 제N화: 제목
        ]

        # 에피소드 끝 패턴
        end_patterns = [
            r'(?:__|__)\[(\d+)화\s*끝\](?:__|__)',
            r'\[(\d+)화\s*끝\]',
            r'---\s*(\d+)화\s*끝\s*---',
        ]

        # 모든 패턴으로 에피소드 찾기
        all_starts = []
        for pattern in episode_patterns:
            for match in re.finditer(pattern, content):
                ep_num = int(match.group(1))
                ep_title = match.group(2).strip().replace("\\", "").strip()
                all_starts.append((match.start(), match.end(), ep_num, ep_title))

        # 위치순 정렬 및 중복 제거
        all_starts = sorted(set(all_starts), key=lambda x: x[0])

        for i, (start_pos, title_end, ep_num, ep_title) in enumerate(all_starts):
            # 다음 에피소드 시작 또는 파일 끝까지
            if i + 1 < len(all_starts):
                end_pos = all_starts[i + 1][0]
            else:
                end_pos = len(content)

            # 에피소드 내용 추출
            ep_content = content[title_end:end_pos]

            # [N화 끝] 태그까지만 추출
            for end_pattern in end_patterns:
                end_match = re.search(end_pattern, ep_content)
                if end_match:
                    ep_content = ep_content[:end_match.end()]
                    break

            # TTS용으로 정리
            clean_content = self.clean_text_for_tts(ep_content)

            # 에피소드 끝 태그 제거
            clean_content = re.sub(r'\[\d+화\s*끝\]', '', clean_content)
            clean_content = clean_content.strip()

            # ACT 정보 가져오기 (없으면 자동 계산)
            if ep_num in act_mapping:
                act_id, act_name = act_mapping[ep_num]
            else:
                # 기본: 3화씩 한 막으로
                act_num = (ep_num - 1) // 3 + 1
                act_id = f"Act{act_num}"
                act_name = f"Part{act_num}"

            episodes[ep_num] = {
                "number": ep_num,
                "title": ep_title,
                "content": clean_content,
                "act_id": act_id,
                "act_name": act_name,
            }

        return episodes

    def split_to_files(self, md_file_path: str, output_dir: str = None) -> Dict[str, any]:
        """MD 파일을 에피소드별 파일로 분리"""
        md_path = Path(md_file_path)

        if not md_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {md_file_path}")

        # 출력 디렉토리 설정
        if output_dir is None:
            output_dir = md_path.parent / f"{md_path.stem}_episodes"
        else:
            output_dir = Path(output_dir)

        # MD 파일 읽기
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 에피소드 추출
        episodes = self.extract_episodes(content)

        if not episodes:
            raise ValueError("에피소드를 찾을 수 없습니다. 파일 형식을 확인하세요.\n"
                           "지원 형식: __제N화. 제목__, # 제N화: 제목 등")

        # ACT별로 그룹화
        created_files = {}

        for ep_num, ep_data in sorted(episodes.items()):
            act_folder = f"{ep_data['act_id']}_{ep_data['act_name']}"
            act_path = output_dir / act_folder
            act_path.mkdir(parents=True, exist_ok=True)

            # 파일명 생성
            ep_title_clean = self.clean_filename(ep_data['title'])
            filename = f"EP{ep_num:02d}_{ep_title_clean}.md"
            filepath = act_path / filename

            # 파일 내용 작성
            file_content = f"# 제{ep_num}화. {ep_data['title']}\n\n"
            file_content += ep_data['content']

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)

            # 결과 저장
            if act_folder not in created_files:
                created_files[act_folder] = []
            created_files[act_folder].append(str(filepath))

        return {
            "output_dir": str(output_dir),
            "episodes_count": len(episodes),
            "files": created_files,
            "episodes": episodes
        }

    def get_episode_list(self, md_file_path: str) -> List[Dict]:
        """에피소드 목록만 가져오기 (미리보기용)"""
        md_path = Path(md_file_path)

        if not md_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {md_file_path}")

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        episodes = self.extract_episodes(content)

        result = []
        for ep_num, ep_data in sorted(episodes.items()):
            result.append({
                "number": ep_num,
                "title": ep_data['title'],
                "act": f"{ep_data['act_id']}_{ep_data['act_name']}",
                "content_length": len(ep_data['content'])
            })

        return result


# 테스트
if __name__ == "__main__":
    service = EpisodeSplitterService()

    # 테스트 파일 경로
    test_file = r"C:\Newproject\senior-automation-project\senior-story-project\senior_script_prompt\prompts\1년동거5억조건\1년동거5억조건.md"

    print("=== 에피소드 목록 ===")
    try:
        episodes = service.get_episode_list(test_file)
        for ep in episodes:
            print(f"  EP{ep['number']:02d}: {ep['title']} ({ep['act']}) - {ep['content_length']}자")
    except Exception as e:
        print(f"에러: {e}")
