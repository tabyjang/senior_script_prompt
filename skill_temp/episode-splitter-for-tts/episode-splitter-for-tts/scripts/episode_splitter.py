#!/usr/bin/env python3
"""
episode_splitter.py
시니어 스토리/오디오북 대본 MD 파일을 Act별 폴더와 에피소드별 MD 파일로 분리
TTS에 바로 넣을 수 있도록 마크다운 특수문자 제거 및 순수 대본만 추출

사용법:
    python3 episode_splitter.py <input.md> <project_name> [output_dir] [--keep-effects] [--with-header]
    
옵션:
    --keep-effects : 효과음/OST 표시 유지 (기본: 제거)
    --with-header  : 에피소드 파일에 제목 헤더 포함 (기본: 순수 텍스트만)

지원하는 에피소드 패턴:
    - __제X화. 제목__  (백슬래시 이스케이프 포함)
    - ## 제X화: 제목
    - ## X화: 제목
    - # 제X화
"""

import os
import re
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def convert_docx_to_md(docx_path: str, output_dir: str = "/home/claude") -> str:
    """Word 파일을 MD로 변환"""
    md_path = f"{output_dir}/converted_temp.md"
    
    try:
        result = subprocess.run(
            ['pandoc', docx_path, '-o', md_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Word 파일을 MD로 변환 완료: {md_path}")
        return md_path
    except subprocess.CalledProcessError as e:
        print(f"❌ 변환 실패: {e.stderr}")
        raise
    except FileNotFoundError:
        print("❌ pandoc이 설치되어 있지 않습니다.")
        raise


def get_act_info(episode_num: int, total_episodes: int) -> tuple:
    """에피소드 번호에 따른 Act 정보 반환
    
    Returns:
        (act_code, act_name) 튜플
    """
    
    if total_episodes <= 4:
        # 4화 이하: 단순 구조
        if episode_num == 1:
            return ("Act1", "시작")
        elif episode_num <= total_episodes - 1:
            return ("Act2", "전개")
        else:
            return ("Act3", "결말")
    
    elif total_episodes <= 8:
        # 5-8화: 3막 구조
        ratio = episode_num / total_episodes
        if ratio <= 0.25:
            return ("Act1", "설정과시작")
        elif ratio <= 0.625:
            return ("Act2", "전개와갈등")
        else:
            return ("Act3", "절정과해결")
    
    else:
        # 9화 이상: 4막 구조 (Act2 분할)
        ratio = episode_num / total_episodes
        if ratio <= 0.25:
            return ("Act1", "설정과시작")
        elif ratio <= 0.5:
            return ("Act2-1", "전개와갈등")
        elif ratio <= 0.75:
            return ("Act2-2", "심화와위기")
        else:
            return ("Act3", "절정과해결")


def clean_for_tts(text: str, keep_effects: bool = False) -> str:
    """TTS용 텍스트 클린업
    
    Args:
        text: 원본 텍스트
        keep_effects: True면 효과음/OST 유지, False면 제거
    
    Returns:
        정제된 텍스트
    """
    
    # 백슬래시 이스케이프 제거 (일부 MD 파일에서 사용)
    text = text.replace('\\. ', '. ')
    text = text.replace('\\.', '.')
    text = text.replace('\\,', ',')
    text = text.replace('\\-', '-')
    text = text.replace('\\!', '!')
    text = text.replace('\\?', '?')
    text = text.replace("\\'", "'")
    text = text.replace('\\"', '"')
    text = text.replace('\\(', '(')
    text = text.replace('\\)', ')')
    text = text.replace('\\[', '[')
    text = text.replace('\\]', ']')
    text = text.replace('\\*', '*')
    
    # 코드 블록 제거
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # __텍스트__ 형식 제거 (텍스트만 유지)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # 마크다운 헤딩 제거 (# 만 제거, 텍스트 유지)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # 굵은 글씨 마커 제거 (텍스트 유지)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # 이탤릭 마커 제거 (텍스트 유지)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'\1', text)
    
    # 인라인 코드 마커 제거
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # 링크 → 텍스트만 추출
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # 이미지 제거
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
    
    # 인용문 마커 제거 (텍스트 유지)
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    
    # 가로선 제거
    text = re.sub(r'^[-*]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # 리스트 마커 제거 (텍스트 유지)
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 테이블 마커 제거
    text = re.sub(r'\|', ' ', text)
    text = re.sub(r'^[\s]*[-:]+[\s]*$', '', text, flags=re.MULTILINE)
    
    # 효과음/설정 처리
    if not keep_effects:
        # [효과음: XXX], [BGM], (OST: XXX) 등 제거
        text = re.sub(r'\[효과음[^\]]*\]', '', text)
        text = re.sub(r'\[BGM[^\]]*\]', '', text)
        text = re.sub(r'\[음악[^\]]*\]', '', text)
        text = re.sub(r'\(OST[^)]*\)', '', text)
        text = re.sub(r'\(BGM[^)]*\)', '', text)
        text = re.sub(r'\{[^}]*\}', '', text)  # {설정} 등
    
    # 특수 마커 제거
    text = re.sub(r'^\s*\*\s*$', '', text, flags=re.MULTILINE)  # 단독 *
    
    # 연속 공백 정리
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 연속 빈 줄 정리 (2줄 이상 → 1줄)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 줄 시작/끝 공백 제거
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def extract_episodes(content: str) -> list:
    """MD 콘텐츠에서 에피소드 추출
    
    지원 패턴:
    - __제X화. 제목__  (백슬래시 이스케이프 포함)
    - ## 제X화: 제목
    - ## X화: 제목
    - # 제X화
    
    Returns:
        [{'number': int, 'title': str, 'content': str}, ...]
    """
    
    episodes = []
    
    # 에피소드 패턴들 (우선순위순)
    patterns = [
        # __제X화\. 제목__ 형식 (백슬래시 이스케이프 포함) - 우선순위 최고
        (r'__제(\d+)화\\*\.\s*(.*?)__\s*\n(.*?)(?=__제\d+화|$)', True),
        
        # ## 제1화: 제목 또는 ## 제1화 - 제목 (가장 일반적)
        (r'(?:^|\n)#{1,2}\s*제\s*(\d+)\s*화\s*[:\-–]\s*(.*?)\n(.*?)(?=\n#{1,2}\s*제\s*\d+\s*화|\Z)', True),
        
        # ## 제1화 (제목 없음)
        (r'(?:^|\n)#{1,2}\s*제\s*(\d+)\s*화\s*\n(.*?)(?=\n#{1,2}\s*제\s*\d+\s*화|\Z)', False),
        
        # ## 1화: 제목
        (r'(?:^|\n)#{1,2}\s*(\d+)\s*화\s*[:\-–]\s*(.*?)\n(.*?)(?=\n#{1,2}\s*\d+\s*화|\Z)', True),
        
        # ## 1화
        (r'(?:^|\n)#{1,2}\s*(\d+)\s*화\s*\n(.*?)(?=\n#{1,2}\s*\d+\s*화|\Z)', False),
        
        # 에피소드 N: 제목
        (r'(?:^|\n)#{1,2}\s*에피소드\s*(\d+)\s*[:\-–]\s*(.*?)\n(.*?)(?=\n#{1,2}\s*에피소드\s*\d+|\Z)', True),
        
        # Episode N: Title
        (r'(?:^|\n)#{1,2}\s*Episode\s*(\d+)\s*[:\-–]\s*(.*?)\n(.*?)(?=\n#{1,2}\s*Episode\s*\d+|\Z)', True),
    ]
    
    for pattern, has_title in patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f"패턴 매칭: {len(matches)}개 에피소드 발견")
            for match in matches:
                if has_title:
                    ep_num = int(match[0])
                    title = match[1].strip()
                    body = match[2].strip()
                else:
                    ep_num = int(match[0])
                    title = ""
                    body = match[1].strip()
                
                # 메타 정보 제거 - [X화 끝] 이후 내용 제거
                end_marker = re.search(r'\[.*?화\s*끝\]', body)
                if end_marker:
                    body = body[:end_marker.start()]
                
                # 제목이 없으면 본문에서 추출 시도
                if not title and body:
                    first_line = body.split('\n')[0].strip()
                    # 첫 줄이 짧고 대사가 아니면 제목으로 사용
                    if len(first_line) < 50 and not first_line.startswith('"') and ':' not in first_line:
                        title = first_line
                        body = '\n'.join(body.split('\n')[1:]).strip()
                
                episodes.append({
                    'number': ep_num,
                    'title': title or f"에피소드{ep_num}",
                    'content': body.strip()
                })
            break
    
    # 중복 제거 및 정렬
    seen = set()
    unique_episodes = []
    for ep in episodes:
        if ep['number'] not in seen:
            seen.add(ep['number'])
            unique_episodes.append(ep)
    
    return sorted(unique_episodes, key=lambda x: x['number'])


def create_episode_files(
    input_file: str, 
    project_name: str, 
    output_dir: str = "/home/claude",
    keep_effects: bool = True,
    with_header: bool = False,
    custom_act_names: dict = None
) -> str:
    """에피소드 분리 및 파일 생성
    
    Args:
        input_file: 입력 MD 또는 DOCX 파일 경로
        project_name: 프로젝트명 (출력 폴더명에 사용)
        output_dir: 출력 기본 디렉토리
        keep_effects: 효과음/OST 유지 여부
        with_header: 에피소드 파일에 제목 헤더 포함 여부
        custom_act_names: 커스텀 Act 이름 딕셔너리 {"Act1": "커스텀이름", ...}
    
    Returns:
        생성된 프로젝트 폴더 경로
    """
    
    # 파일 확장자 확인
    file_ext = Path(input_file).suffix.lower()
    temp_md_file = None
    
    if file_ext == '.docx':
        print(f"📄 Word 파일 감지: {input_file}")
        temp_md_file = convert_docx_to_md(input_file, output_dir)
        md_file = temp_md_file
    elif file_ext == '.md':
        md_file = input_file
    else:
        raise ValueError(f"지원하지 않는 파일 형식: {file_ext} (지원: .md, .docx)")
    
    # MD 파일 읽기
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 에피소드 추출
    episodes = extract_episodes(content)
    
    if not episodes:
        raise ValueError(
            "에피소드를 찾을 수 없습니다.\n"
            "지원 형식: '## 제1화: 제목', '## 1화', '## Episode 1' 등"
        )
    
    total_eps = len(episodes)
    
    # 프로젝트명 정리 (공백 → 언더스코어, 특수문자 제거)
    safe_project_name = re.sub(r'[\\/:*?"<>|]', '', project_name)
    safe_project_name = safe_project_name.replace(' ', '_')
    
    base_path = f"{output_dir}/{safe_project_name}_episodes"
    
    # 기존 폴더 정리
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    
    # 메타데이터 폴더
    os.makedirs(f"{base_path}/_metadata", exist_ok=True)
    
    # Act별 에피소드 분류
    act_episodes = {}
    episode_list = []
    
    for ep in episodes:
        act_code, act_name = get_act_info(ep['number'], total_eps)
        
        # 커스텀 Act 이름 적용
        if custom_act_names and act_code in custom_act_names:
            act_name = custom_act_names[act_code]
        
        act_folder = f"{act_code}_{act_name}"
        
        if act_folder not in act_episodes:
            act_episodes[act_folder] = []
        
        # 파일명 생성
        safe_title = re.sub(r'[\\/:*?"<>|\s]', '_', ep['title'])
        safe_title = re.sub(r'_+', '_', safe_title).strip('_')
        
        if safe_title:
            filename = f"EP{ep['number']:02d}_{safe_title}.md"
        else:
            filename = f"EP{ep['number']:02d}.md"
        
        # TTS 클린업
        clean_content = clean_for_tts(ep['content'], keep_effects)
        
        act_episodes[act_folder].append({
            'filename': filename,
            'number': ep['number'],
            'title': ep['title'],
            'content': clean_content,
            'original_length': len(ep['content']),
            'clean_length': len(clean_content)
        })
        
        episode_list.append({
            'episode': ep['number'],
            'title': ep['title'],
            'act': act_code,
            'act_name': act_name,
            'filename': f"{act_folder}/{filename}",
            'char_count': len(clean_content)
        })
    
    # 폴더 및 파일 생성
    for act_folder, eps in sorted(act_episodes.items()):
        act_path = f"{base_path}/{act_folder}"
        os.makedirs(act_path, exist_ok=True)
        
        for ep_data in eps:
            filepath = f"{act_path}/{ep_data['filename']}"
            with open(filepath, 'w', encoding='utf-8') as f:
                if with_header:
                    # 제목 헤더 포함
                    f.write(f"# 제{ep_data['number']}화: {ep_data['title']}\n\n")
                    f.write(ep_data['content'])
                else:
                    # TTS용 순수 텍스트만
                    f.write(ep_data['content'])
    
    # 메타데이터 저장
    act_structure = {
        'project_name': project_name,
        'total_episodes': total_eps,
        'acts': list(sorted(act_episodes.keys())),
        'episodes_per_act': {k: len(v) for k, v in sorted(act_episodes.items())},
        'settings': {
            'keep_effects': keep_effects,
            'with_header': with_header
        }
    }
    
    with open(f"{base_path}/_metadata/act_structure.json", 'w', encoding='utf-8') as f:
        json.dump(act_structure, f, ensure_ascii=False, indent=2)
    
    with open(f"{base_path}/_metadata/episode_list.json", 'w', encoding='utf-8') as f:
        json.dump(episode_list, f, ensure_ascii=False, indent=2)
    
    # 임시 파일 정리
    if temp_md_file and os.path.exists(temp_md_file):
        os.remove(temp_md_file)
    
    # 결과 출력
    print(f"\n✅ 에피소드 분리 완료!")
    print(f"📁 출력 경로: {base_path}")
    print(f"\n📊 요약:")
    print(f"   - 총 에피소드: {total_eps}개")
    print(f"   - Act 구분: {len(act_episodes)}개")
    for act, eps in sorted(act_episodes.items()):
        print(f"      • {act}: {len(eps)}개 에피소드")
    
    total_chars = sum(ep['char_count'] for ep in episode_list)
    print(f"   - 총 글자수: {total_chars:,}자")
    print(f"   - 예상 TTS 시간: 약 {total_chars // 200}분 (200자/분 기준)")
    
    return base_path


def print_tree(path: str, prefix: str = "") -> None:
    """폴더 구조 트리 출력"""
    items = sorted(Path(path).iterdir())
    dirs = [i for i in items if i.is_dir()]
    files = [i for i in items if i.is_file()]
    
    all_items = dirs + files
    
    for i, item in enumerate(all_items):
        is_last = i == len(all_items) - 1
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{item.name}")
        
        if item.is_dir():
            extension = "    " if is_last else "│   "
            print_tree(str(item), prefix + extension)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    project_name = sys.argv[2]
    output_dir = "/home/claude"
    keep_effects = False
    with_header = False
    
    # 인자 파싱
    for arg in sys.argv[3:]:
        if arg.startswith('/') or arg.startswith('.'):
            output_dir = arg
        elif arg == '--keep-effects':
            keep_effects = True
        elif arg == '--with-header':
            with_header = True
    
    try:
        result_path = create_episode_files(
            input_file,
            project_name,
            output_dir,
            keep_effects=keep_effects,
            with_header=with_header
        )
        
        print(f"\n📂 생성된 폴더 구조:")
        print_tree(result_path)
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        sys.exit(1)
