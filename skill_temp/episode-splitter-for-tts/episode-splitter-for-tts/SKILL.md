---
name: episode-splitter-for-tts
description: "시니어 스토리/오디오북 대본 MD 파일을 Act별 폴더와 에피소드별 MD 파일로 분리. TTS에 바로 넣을 수 있도록 마크다운 특수문자 제거 및 순수 대본만 추출. 사용 시점 - (1) 대본 파일을 에피소드별로 나눠줘 요청 시, (2) TTS용으로 정리해줘 요청 시, (3) Act/막 별로 폴더 구분해줘 요청 시"
---

# Episode Splitter for TTS

시니어 스토리/오디오북 대본 MD 파일을 Act(막)별 폴더 구조와 에피소드별 개별 MD 파일로 분리한다.
TTS 엔진에 바로 입력할 수 있도록 순수 대본만 추출하고 불필요한 마크다운 문법을 제거한다.

## 지원 입력 형식

| 형식 | 처리 방법 |
|------|-----------|
| `.md` | 직접 파싱 |
| `.docx` | pandoc으로 MD 변환 후 파싱 |

## 출력 폴더 구조

```
{project_name}_episodes/
├── Act1_설정과시작/
│   ├── EP01_제목.md
│   ├── EP02_제목.md
│   └── EP03_제목.md
├── Act2-1_전개와갈등/
│   ├── EP04_제목.md
│   ├── EP05_제목.md
│   └── EP06_제목.md
├── Act2-2_심화와위기/
│   ├── EP07_제목.md
│   ├── EP08_제목.md
│   └── EP09_제목.md
├── Act3_절정과해결/
│   ├── EP10_제목.md
│   ├── EP11_제목.md
│   └── EP12_제목.md
└── _metadata/
    ├── act_structure.json
    └── episode_list.json
```

## Act 분류 기준 (12화 기준)

| Act | 에피소드 | 설명 |
|-----|----------|------|
| Act1 | 1-3화 | 설정, 도입, 갈등 시작 |
| Act2-1 | 4-6화 | 전개, 충돌, 균열 |
| Act2-2 | 7-9화 | 심화, 이해, 위기 |
| Act3 | 10-12화 | 절정, 해결, 결말 |

> 에피소드 수에 따라 자동 조정됨

## 에피소드 식별 패턴

```
## 제1화: 제목
## 제1화 - 제목
## 1화: 제목
## 제 1 화: 제목
# 제1화
---제1화---
```

## TTS용 클린업 규칙

### 제거 항목
- 마크다운 헤딩 (`#`, `##`, `###`)
- 굵은 글씨 (`**텍스트**`, `__텍스트__`)
- 이탤릭 (`*텍스트*`, `_텍스트_`)
- 인라인 코드 (`` `텍스트` ``)
- 링크 (`[텍스트](url)`)
- 이미지 (`![alt](url)`)
- 코드 블록 (```...```)
- HTML 태그 (`<tag>`, `</tag>`)
- 콜아웃/인용 (`>`)
- 가로선 (`---`, `***`)
- 리스트 마커 (`-`, `*`, `1.`)

### 유지 항목
- 대사 (따옴표 안 내용)
- 나레이션/해설
- 줄바꿈 (문단 구분)
- 말줄임표 (`...`)
- 느낌표, 물음표

### 특수 처리
- `[효과음]`, `(OST)`, `{설정}` 등 메타정보 → 선택적 제거/유지
- 캐릭터명 콜론 형식 (`철수:`) → 유지 (TTS 캐릭터 분리용)

## 워크플로우

1. **MD 파일 로드**: 전체 내용 읽기
2. **대본 섹션 찾기**: `# 대본`, `## 대본`, 또는 `제1화` 시작점 찾기
3. **에피소드 분리**: 정규식으로 각 화 분리
4. **Act 분류**: 에피소드 번호에 따라 Act 결정
5. **TTS 클린업**: 각 에피소드 내용 정제
6. **폴더 생성**: Act별 폴더 생성
7. **파일 저장**: 각 에피소드를 개별 MD 파일로 저장
8. **메타데이터 생성**: JSON 형식으로 구조 정보 저장

## 구현 예시

```python
import os
import re
import json

def get_act_info(episode_num: int, total_episodes: int) -> dict:
    """에피소드 번호에 따른 Act 정보 반환"""
    
    if total_episodes <= 4:
        # 4화 이하: 단순 구조
        acts = {
            1: ("Act1", "시작"),
            2: ("Act2", "전개"),
            3: ("Act3", "절정"),
            4: ("Act3", "결말")
        }
        return acts.get(episode_num, ("Act1", "시작"))
    
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
    """TTS용 텍스트 클린업"""
    
    # 코드 블록 제거
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 마크다운 헤딩 제거 (# 만 제거, 텍스트 유지)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # 굵은 글씨/이탤릭 마커 제거 (텍스트 유지)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # 인라인 코드 마커 제거
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # 링크 → 텍스트만 추출
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # 이미지 제거
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
    
    # 인용문 마커 제거
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    
    # 가로선 제거
    text = re.sub(r'^[-*]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # 리스트 마커 제거
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 효과음/설정 처리
    if not keep_effects:
        text = re.sub(r'\[효과음[^\]]*\]', '', text)
        text = re.sub(r'\(OST[^)]*\)', '', text)
        text = re.sub(r'\{[^}]*\}', '', text)
    
    # 연속 빈 줄 정리
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def extract_episodes(content: str) -> list:
    """MD 콘텐츠에서 에피소드 추출"""
    
    episodes = []
    
    # 에피소드 패턴들
    patterns = [
        # ## 제1화: 제목 또는 ## 제1화 - 제목
        r'(?:^|\n)#{1,2}\s*제\s*(\d+)\s*화\s*[:\-]\s*(.*?)\n(.*?)(?=\n#{1,2}\s*제\s*\d+\s*화|\Z)',
        # ## 1화: 제목
        r'(?:^|\n)#{1,2}\s*(\d+)\s*화\s*[:\-]\s*(.*?)\n(.*?)(?=\n#{1,2}\s*\d+\s*화|\Z)',
        # # 제1화
        r'(?:^|\n)#{1,2}\s*제\s*(\d+)\s*화\s*\n(.*?)\n(.*?)(?=\n#{1,2}\s*제\s*\d+\s*화|\Z)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            for match in matches:
                ep_num = int(match[0])
                title = match[1].strip() if len(match) > 2 else f"제{ep_num}화"
                body = match[2].strip() if len(match) > 2 else match[1].strip()
                
                # 제목이 없으면 본문에서 첫 줄 추출
                if not title and body:
                    first_line = body.split('\n')[0]
                    if len(first_line) < 50:
                        title = first_line
                
                episodes.append({
                    'number': ep_num,
                    'title': title or f"에피소드{ep_num}",
                    'content': body
                })
            break
    
    return sorted(episodes, key=lambda x: x['number'])


def create_episode_files(
    input_file: str, 
    project_name: str, 
    output_dir: str = "/home/claude",
    keep_effects: bool = True,
    custom_act_names: dict = None
) -> str:
    """에피소드 분리 및 파일 생성"""
    
    # MD 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 에피소드 추출
    episodes = extract_episodes(content)
    
    if not episodes:
        raise ValueError("에피소드를 찾을 수 없습니다. 제X화 형식인지 확인해주세요.")
    
    total_eps = len(episodes)
    base_path = f"{output_dir}/{project_name}_episodes"
    
    # 기존 폴더 정리
    if os.path.exists(base_path):
        import shutil
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
        
        # 파일명 생성 (공백 → 언더스코어)
        safe_title = re.sub(r'[\\/:*?"<>|]', '', ep['title'])
        safe_title = safe_title.replace(' ', '_')
        filename = f"EP{ep['number']:02d}_{safe_title}.md"
        
        # TTS 클린업
        clean_content = clean_for_tts(ep['content'], keep_effects)
        
        act_episodes[act_folder].append({
            'filename': filename,
            'number': ep['number'],
            'title': ep['title'],
            'content': clean_content
        })
        
        episode_list.append({
            'episode': ep['number'],
            'title': ep['title'],
            'act': act_code,
            'filename': f"{act_folder}/{filename}"
        })
    
    # 폴더 및 파일 생성
    for act_folder, eps in act_episodes.items():
        act_path = f"{base_path}/{act_folder}"
        os.makedirs(act_path, exist_ok=True)
        
        for ep_data in eps:
            filepath = f"{act_path}/{ep_data['filename']}"
            with open(filepath, 'w', encoding='utf-8') as f:
                # TTS용이므로 마크다운 헤더 없이 순수 텍스트만
                f.write(ep_data['content'])
    
    # 메타데이터 저장
    with open(f"{base_path}/_metadata/act_structure.json", 'w', encoding='utf-8') as f:
        json.dump({
            'total_episodes': total_eps,
            'acts': list(act_episodes.keys()),
            'episodes_per_act': {k: len(v) for k, v in act_episodes.items()}
        }, f, ensure_ascii=False, indent=2)
    
    with open(f"{base_path}/_metadata/episode_list.json", 'w', encoding='utf-8') as f:
        json.dump(episode_list, f, ensure_ascii=False, indent=2)
    
    return base_path
```

## 사용 예시

### 기본 사용
```bash
python3 episode_splitter.py input.md 1년동거5억조건
```

### 커스텀 Act 이름 지정
```python
custom_acts = {
    "Act1": "지옥의시작",
    "Act2-1": "충돌과균열",
    "Act2-2": "이해와위기",
    "Act3": "진짜유산"
}
create_episode_files("input.md", "project", custom_act_names=custom_acts)
```

### 효과음 제거
```python
create_episode_files("input.md", "project", keep_effects=False)
```

## 출력 후 작업

1. 폴더 구조 트리 출력
2. 총 에피소드 수 및 Act별 분포 요약
3. `/mnt/user-data/outputs/`에 전체 프로젝트 복사
4. present_files로 주요 에피소드 파일 공유

## 트러블슈팅

### 에피소드가 0개인 경우
- 원본 파일에서 `제X화` 패턴 확인
- `## 1화`, `# 제1화: 제목` 등 형식 확인
- 대본 섹션이 별도로 있는지 확인

### Act 분류가 맞지 않는 경우
- `custom_act_names` 파라미터로 직접 지정
- 또는 파일 기반 config 사용
