---
name: comfyui-output-format
description: >
  ComfyUI 이미지 프롬프트 출력 형식 및 폴더 구조 스킬.
  프롬프트 저장(MD/JSON), 이미지 출력 폴더 구조, 파일 명명 규칙,
  n8n 자동화 연동을 위한 JSON 형식을 정의한다.
  사용 시점: (1) 캐릭터/장면 프롬프트를 파일로 저장할 때,
  (2) ComfyUI 출력 폴더 구조 설정 시,
  (3) n8n 자동화용 JSON 형식이 필요할 때,
  (4) 파일 명명 규칙 확인 시
---

# ComfyUI 프롬프트 출력 형식 스킬

프롬프트 파일 저장 형식, 이미지 출력 폴더 구조, n8n 자동화를 위한 JSON 형식을 정의한다.

---

## 1. 폴더 구조

### 1.1 프롬프트 저장 폴더

```
프로젝트폴더/
├── prompts/                              # 프롬프트 저장 루트
│   └── [작품명]/                         # 대본별 폴더
│       ├── characters/                   # 캐릭터 프롬프트
│       │   ├── [순번]_[캐릭터명].md      # 사람이 읽는 용도
│       │   └── [순번]_[캐릭터명].json    # n8n 자동화 용도
│       ├── scenes/                       # 장면 프롬프트
│       │   ├── [막]_[제목]/              # 막별 폴더
│       │   │   ├── [화수]_[제목].md
│       │   │   └── [화수]_[제목].json
│       │   └── ...
│       ├── characters_all.json           # 전체 캐릭터 통합 JSON
│       └── scenes_all.json               # 전체 장면 통합 JSON
```

### 1.2 이미지 출력 폴더 (ComfyUI)

```
output/                                   # ComfyUI 출력 루트
└── [작품명]/                             # 작품별 폴더
    ├── characters/                       # 캐릭터 이미지
    │   └── [캐릭터명]/                   # 캐릭터별 폴더
    │       ├── v01_기본/                 # 버전별 폴더
    │       │   └── [캐릭터명]_v01_00001.png
    │       ├── v02_슬픔/
    │       ├── v03_분노/
    │       └── ...
    └── scenes/                           # 장면 이미지
        └── [막]/                         # 막별 폴더
            └── [화수]/                   # 화별 폴더
                ├── s01_[장면명]_00001.png
                └── s02_[장면명]_00001.png
```

---

## 2. 파일 명명 규칙

### 2.1 프롬프트 파일

| 유형 | 형식 | 예시 |
|------|------|------|
| 캐릭터 MD | `[순번]_[캐릭터명].md` | `01_한정숙.md` |
| 캐릭터 JSON | `[순번]_[캐릭터명].json` | `01_한정숙.json` |
| 장면 MD | `[화수]화_[제목].md` | `01화_장례식장의낯선여자.md` |
| 장면 JSON | `[화수]화_[제목].json` | `01화_장례식장의낯선여자.json` |

### 2.2 이미지 파일

| 유형 | 형식 | 예시 |
|------|------|------|
| 캐릭터 이미지 | `[캐릭터명]_[버전ID]_[버전명]_[시퀀스].png` | `한정숙_v01_기본_00001.png` |
| 장면 이미지 | `[막]_[화수]화_[장면ID]_[시퀀스].png` | `1막_01화_s01_00001.png` |

---

## 3. MD 파일 형식

### 3.1 캐릭터 프롬프트 MD

```markdown
# [캐릭터명] - 이미지 프롬프트

## 캐릭터 정보

| 항목 | 내용 |
|------|------|
| 이름 | [이름] |
| 실제 나이 | [나이]세 |
| 프롬프트 나이 | [나이-15]세 |
| 역할 | [주인공/적대자/조력자] |
| 성격 | [성격 키워드] |
| 외모 특징 | [특징] |
| 상징물 | [소품] |

---

## 버전별 프롬프트

### 버전 1: 기본 정면 (캐릭터 소개용)

**Positive:**
```
masterpiece, best quality, photorealistic, 8k uhd,
medium shot, front view,
[나이] year old Korean [성별], [얼굴특징],
[헤어스타일], [기본표정],
[기본의상], [악세서리],
standing straight, hands clasped,
neutral background, soft studio lighting
```

**Negative:**
```
worst quality, low quality, blurry, deformed, disfigured,
bad anatomy, bad hands, extra fingers, missing fingers,
ugly, duplicate, morbid, mutilated,
out of frame, watermark, text, signature,
anime, cartoon, 3d render, cgi
```

**출력 경로:** `characters/[캐릭터명]/v01_기본/`

---

### 버전 2-10: [의상/표정/동작 변형...]

[버전별 반복...]
```

### 3.2 장면 프롬프트 MD

```markdown
# [화수]. [제목] - 장면 이미지 프롬프트

## 챕터 정보

| 항목 | 내용 |
|------|------|
| 막 | [1막/2막/3막] |
| 화수 | [N]화 |
| 제목 | [제목] |
| 주요 장소 | [장소들] |
| 등장인물 | [인물들] |

---

## 장면별 프롬프트

### 장면 1: [장면 설명]

**장면 정보:**
- 장소: [장소]
- 시간: [시간대]
- 등장인물: [인물]
- 핵심 감정: [감정]
- 핵심 행동: [행동]

**메인 프롬프트:**
```
masterpiece, best quality, photorealistic,
[인원수], [장면설명],
[장소], [조명], [분위기]
```

**캐릭터 A (왼쪽 영역):**
```
[캐릭터 프롬프트]
```

**캐릭터 B (오른쪽 영역):**
```
[캐릭터 프롬프트]
```

**Regional Prompt 설정:**
- 캐릭터 A: 0-50%
- 캐릭터 B: 50-100%
- 오버랩: [필요시 설정]

**Negative:**
```
[네거티브 프롬프트]
```

**출력 경로:** `scenes/[막]/[화수]/s01_[장면명]/`
```

---

## 4. JSON 파일 형식

### 4.1 캐릭터 프롬프트 JSON

```json
{
  "metadata": {
    "work_title": "302호의여자들",
    "character_name": "한정숙",
    "created_at": "2024-01-03",
    "total_versions": 10
  },
  "character_info": {
    "name": "한정숙",
    "real_age": 72,
    "prompt_age": 57,
    "gender": "female",
    "role": "protagonist",
    "personality": ["강인함", "인내", "단단함"],
    "appearance": ["진주목걸이", "회색 섞인 머리", "따뜻한 눈빛"],
    "symbolic_item": "진주목걸이"
  },
  "versions": [
    {
      "version_id": "v01",
      "version_name": "기본_정면",
      "description": "캐릭터 소개용 기본 이미지",
      "positive": "masterpiece, best quality, photorealistic, 8k uhd, medium shot, front view, 57 year old Korean woman...",
      "negative": "worst quality, low quality, blurry, deformed...",
      "output_folder": "characters/한정숙/v01_기본",
      "filename_prefix": "한정숙_v01_기본"
    }
  ]
}
```

**필수 필드:**
- `metadata.work_title`: 작품명
- `metadata.character_name`: 캐릭터명
- `versions[].positive`: 포지티브 프롬프트
- `versions[].negative`: 네거티브 프롬프트
- `versions[].output_folder`: 출력 폴더 경로
- `versions[].filename_prefix`: 파일명 접두사

### 4.2 장면 프롬프트 JSON

```json
{
  "metadata": {
    "work_title": "302호의여자들",
    "act": "1막",
    "act_title": "일상과균열",
    "chapter": 1,
    "chapter_title": "장례식장의낯선여자",
    "created_at": "2024-01-03",
    "total_scenes": 15
  },
  "chapter_info": {
    "main_location": "장례식장",
    "time_period": "낮",
    "characters": ["한정숙", "강민수", "윤미라"],
    "main_emotion": "충격, 배신감"
  },
  "scenes": [
    {
      "scene_id": "s01",
      "scene_name": "상주석의_정숙",
      "description": "정숙이 상주석에서 조문객을 맞이하는 장면",
      "location": "장례식장 빈소",
      "time": "낮",
      "characters": ["한정숙"],
      "emotion": "슬픔, 공허함",
      "action": "조문객 맞이, 목걸이 만지기",
      "main_prompt": "masterpiece, best quality, photorealistic, 1woman, funeral hall interior...",
      "character_prompts": {
        "한정숙": "57 year old Korean woman, black mourning clothes..."
      },
      "negative": "worst quality, low quality, blurry, deformed...",
      "regional_settings": null,
      "output_folder": "scenes/1막/01화/s01_상주석",
      "filename_prefix": "1막_01화_s01"
    }
  ]
}
```

**다중 캐릭터 장면의 regional_settings:**
```json
{
  "regional_settings": {
    "한정숙": {"start": 0, "end": 30},
    "윤미라": {"start": 40, "end": 70},
    "children": {"start": 70, "end": 100}
  }
}
```

### 4.3 통합 JSON 형식

**characters_all.json:**
```json
{
  "metadata": {
    "work_title": "302호의여자들",
    "created_at": "2024-01-03",
    "total_characters": 6
  },
  "characters": [
    { /* 캐릭터 1 전체 데이터 */ },
    { /* 캐릭터 2 전체 데이터 */ }
  ]
}
```

**scenes_all.json:**
```json
{
  "metadata": {
    "work_title": "302호의여자들",
    "created_at": "2024-01-03",
    "total_acts": 3,
    "total_chapters": 24,
    "total_scenes": 350
  },
  "acts": [
    {
      "act": "1막",
      "title": "일상과균열",
      "chapters": [
        { /* 1화 전체 장면 */ },
        { /* 2화 전체 장면 */ }
      ]
    }
  ]
}
```

---

## 5. n8n + ComfyUI 자동화

### 5.1 워크플로우 구조

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ JSON 파일    │ -> │ Split In     │ -> │ ComfyUI API  │ -> │ 완료 알림    │
│ 읽기         │    │ Batches      │    │ 호출         │    │ (Slack/etc)  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### 5.2 ComfyUI API 호출 (n8n HTTP Request)

```json
{
  "method": "POST",
  "url": "http://localhost:8188/prompt",
  "body": {
    "prompt": {
      "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
          "text": "{{ $json.positive }}",
          "clip": ["4", 1]
        }
      },
      "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
          "text": "{{ $json.negative }}",
          "clip": ["4", 1]
        }
      },
      "9": {
        "class_type": "SaveImage",
        "inputs": {
          "filename_prefix": "{{ $json.output_folder }}/{{ $json.filename_prefix }}",
          "images": ["8", 0]
        }
      }
    }
  }
}
```

### 5.3 폴더 경로 동적 생성

ComfyUI SaveImage의 `filename_prefix`로 자동 폴더 생성:

```
filename_prefix = "302호의여자들/characters/한정숙/v01_기본/한정숙_v01"
                   ↓
output/302호의여자들/characters/한정숙/v01_기본/한정숙_v01_00001.png
```

**n8n Expression:**
```javascript
const outputPath = `${$json.metadata.work_title}/${$json.output_folder}/${$json.filename_prefix}`;
return { filename_prefix: outputPath };
```

### 5.4 배치 처리 설정

| 설정 | 값 | 용도 |
|------|-----|------|
| Batch Size | 1 | 안정적, GPU 메모리 관리 |
| Batch Size | 4 | 고성능 GPU 병렬 처리 |
| Wait Time | 5초 | ComfyUI 부하 관리 |

---

## 6. 체크리스트

### 프롬프트 파일 생성 시

```
□ prompts/[작품명]/ 폴더 생성
□ characters/, scenes/ 하위 폴더 생성
□ 캐릭터별 MD + JSON 파일 생성
□ 챕터별 MD + JSON 파일 생성
□ 통합 JSON (characters_all.json, scenes_all.json) 생성
□ output_folder 경로 정확히 설정
□ filename_prefix 명명 규칙 준수
```

### JSON 필수 필드 확인

```
□ metadata.work_title 있음
□ versions[].positive / scenes[].main_prompt 있음
□ versions[].negative / scenes[].negative 있음
□ output_folder 경로 있음
□ filename_prefix 있음
□ 다중 캐릭터 시 regional_settings 있음
```

### n8n 자동화 설정 시

```
□ JSON 파일 경로 정확
□ ComfyUI API URL 정확 (기본: http://localhost:8188/prompt)
□ SaveImage filename_prefix 동적 설정
□ 배치 크기 GPU에 적합
□ 오류 처리 노드 추가
```
