# 프롬프트 출력 형식 및 폴더 구조 가이드

대본에서 생성한 캐릭터/장면 프롬프트를 MD와 JSON 형식으로 저장하고,
n8n + ComfyUI 자동화를 위한 폴더 구조를 정의한다.

---

## 1. 폴더 구조

### 1.1 프롬프트 저장 폴더

```
프로젝트폴더/
├── prompts/                              # 프롬프트 저장 루트
│   └── [작품명]/                         # 대본별 폴더
│       ├── characters/                   # 캐릭터 프롬프트
│       │   ├── [캐릭터명].md             # 사람이 읽는 용도
│       │   └── [캐릭터명].json           # n8n 자동화 용도
│       ├── scenes/                       # 장면 프롬프트
│       │   ├── [막]_[제목]/              # 막별 폴더
│       │   │   ├── [화수]_[제목].md
│       │   │   └── [화수]_[제목].json
│       │   └── ...
│       ├── characters_all.md             # 전체 캐릭터 통합본
│       ├── characters_all.json           # 전체 캐릭터 JSON
│       ├── scenes_all.md                 # 전체 장면 통합본
│       └── scenes_all.json               # 전체 장면 JSON
```

### 1.2 이미지 출력 폴더 (ComfyUI)

```
output/                                   # ComfyUI 출력 루트
└── [작품명]/                             # 작품별 폴더
    ├── characters/                       # 캐릭터 이미지
    │   ├── [캐릭터명]/                   # 캐릭터별 폴더
    │   │   ├── v01_기본/                 # 버전별 폴더
    │   │   │   └── [캐릭터명]_v01_00001.png
    │   │   ├── v02_슬픔/
    │   │   ├── v03_분노/
    │   │   └── ...
    │   └── ...
    └── scenes/                           # 장면 이미지
        ├── [막]/                         # 막별 폴더
        │   ├── [화수]/                   # 화별 폴더
        │   │   ├── s01_[장면명]_00001.png
        │   │   ├── s02_[장면명]_00001.png
        │   │   └── ...
        │   └── ...
        └── ...
```

### 1.3 예시: 302호의여자들

```
editors_app/
├── prompts/
│   └── 302호의여자들/
│       ├── characters/
│       │   ├── 01_한정숙.md
│       │   ├── 01_한정숙.json
│       │   ├── 02_최영희.md
│       │   ├── 02_최영희.json
│       │   └── ...
│       ├── scenes/
│       │   ├── 1막_일상과균열/
│       │   │   ├── 01화_장례식장의낯선여자.md
│       │   │   ├── 01화_장례식장의낯선여자.json
│       │   │   └── ...
│       │   └── ...
│       ├── characters_all.json
│       └── scenes_all.json
│
└── output/
    └── 302호의여자들/
        ├── characters/
        │   ├── 한정숙/
        │   │   ├── v01_기본/
        │   │   ├── v02_슬픔/
        │   │   └── ...
        │   └── ...
        └── scenes/
            └── ...
```

---

## 2. MD 파일 형식

### 2.1 캐릭터 프롬프트 MD 형식

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

### 버전 2: 일상 의상 + 평온한 표정

**Positive:**
```
[프롬프트 내용]
```

**Negative:**
```
[네거티브 프롬프트]
```

**출력 경로:** `characters/[캐릭터명]/v02_일상/`

---

[... 버전 3-10 계속 ...]
```

### 2.2 장면 프롬프트 MD 형식

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

---

### 장면 2: [장면 설명]

[... 계속 ...]
```

---

## 3. JSON 파일 형식

### 3.1 캐릭터 프롬프트 JSON 형식

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
      "positive": "masterpiece, best quality, photorealistic, 8k uhd, medium shot, front view, 57 year old Korean woman, gentle face, subtle smile lines, warm brown eyes, shoulder-length black hair with gray streaks, serene expression, wearing elegant beige cardigan, pearl necklace, standing straight, hands clasped, neutral background, soft studio lighting",
      "negative": "worst quality, low quality, blurry, deformed, disfigured, bad anatomy, bad hands, extra fingers, missing fingers, ugly, duplicate, morbid, mutilated, out of frame, watermark, text, signature, anime, cartoon, 3d render, cgi",
      "output_folder": "characters/한정숙/v01_기본",
      "filename_prefix": "한정숙_v01_기본"
    },
    {
      "version_id": "v02",
      "version_name": "일상_평온",
      "description": "일상 의상, 평온한 표정",
      "positive": "...",
      "negative": "...",
      "output_folder": "characters/한정숙/v02_일상",
      "filename_prefix": "한정숙_v02_일상"
    }
  ]
}
```

### 3.2 장면 프롬프트 JSON 형식

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
      "main_prompt": "masterpiece, best quality, photorealistic, 1woman, funeral hall interior, Korean funeral setting, chrysanthemum flowers, solemn atmosphere, soft diffused lighting",
      "character_prompts": {
        "한정숙": "57 year old Korean woman, black mourning clothes, tearful but composed expression, touching pearl necklace, sitting in chief mourner position, dignified grief"
      },
      "negative": "worst quality, low quality, blurry, deformed...",
      "regional_settings": null,
      "output_folder": "scenes/1막/01화/s01_상주석",
      "filename_prefix": "1막_01화_s01"
    },
    {
      "scene_id": "s02",
      "scene_name": "낯선여자_등장",
      "description": "미라가 두 아이와 함께 장례식장에 등장",
      "location": "장례식장 입구",
      "time": "낮",
      "characters": ["한정숙", "윤미라", "강서연", "강서준"],
      "emotion": "충격, 혼란",
      "action": "미라 등장, 아이들이 영정 앞에 무릎 꿇음",
      "main_prompt": "masterpiece, best quality, photorealistic, 4people, funeral hall, tense atmosphere, dramatic moment, shocked onlookers",
      "character_prompts": {
        "한정숙": "57 year old Korean woman, shocked expression, frozen in place, wide eyes",
        "윤미라": "33 year old Korean woman, composed expression, black dress, pearl earrings, confident walk, holding children's hands"
      },
      "negative": "...",
      "regional_settings": {
        "한정숙": {"start": 0, "end": 30},
        "윤미라": {"start": 40, "end": 70},
        "children": {"start": 70, "end": 100}
      },
      "output_folder": "scenes/1막/01화/s02_낯선여자등장",
      "filename_prefix": "1막_01화_s02"
    }
  ]
}
```

### 3.3 전체 통합 JSON 형식

**characters_all.json:**
```json
{
  "metadata": {
    "work_title": "302호의여자들",
    "created_at": "2024-01-03",
    "total_characters": 6
  },
  "characters": [
    { /* 한정숙 전체 데이터 */ },
    { /* 최영희 전체 데이터 */ },
    { /* 이말자 전체 데이터 */ },
    { /* 강순덕 전체 데이터 */ },
    { /* 윤미라 전체 데이터 */ },
    { /* 오달수 전체 데이터 */ }
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

## 4. n8n + ComfyUI 자동화 설정

### 4.1 n8n 워크플로우 구조

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ JSON 파일    │ -> │ Split In     │ -> │ ComfyUI API  │ -> │ 완료 알림    │
│ 읽기         │    │ Batches      │    │ 호출         │    │ (Slack/etc)  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### 4.2 ComfyUI API 호출 예시

**HTTP Request 노드 설정:**

```json
{
  "method": "POST",
  "url": "http://localhost:8188/prompt",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "prompt": {
      "3": {
        "class_type": "KSampler",
        "inputs": {
          "seed": {{ Math.floor(Math.random() * 1000000) }},
          "steps": 20,
          "cfg": 7,
          "sampler_name": "euler",
          "scheduler": "normal",
          "denoise": 1,
          "model": ["4", 0],
          "positive": ["6", 0],
          "negative": ["7", 0],
          "latent_image": ["5", 0]
        }
      },
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

### 4.3 폴더 경로 동적 지정

ComfyUI SaveImage 노드에서 `filename_prefix`로 폴더 생성:

```
filename_prefix = "302호의여자들/characters/한정숙/v01_기본/한정숙_v01"
                   ↓
output/302호의여자들/characters/한정숙/v01_기본/한정숙_v01_00001.png
```

**n8n에서 동적 설정:**
```javascript
// Expression 노드에서
const outputPath = `${$json.metadata.work_title}/${$json.output_folder}/${$json.filename_prefix}`;
return { filename_prefix: outputPath };
```

### 4.4 배치 처리 설정

**Split In Batches 노드:**
- Batch Size: 1 (한 번에 1개씩 처리, GPU 메모리 관리)
- 또는 Batch Size: 4 (병렬 처리, 고성능 GPU)

**Wait 노드 (선택):**
- 각 이미지 생성 사이에 대기 시간 추가
- ComfyUI 부하 관리

---

## 5. 파일 명명 규칙

### 5.1 캐릭터 파일

```
[순번]_[캐릭터명].md
[순번]_[캐릭터명].json

예: 01_한정숙.md, 01_한정숙.json
```

### 5.2 장면 파일

```
[화수]화_[제목].md
[화수]화_[제목].json

예: 01화_장례식장의낯선여자.md
```

### 5.3 이미지 파일

```
[캐릭터명]_[버전ID]_[버전명]_[시퀀스].png
[막]_[화수]화_[장면ID]_[시퀀스].png

예: 한정숙_v01_기본_00001.png
예: 1막_01화_s01_00001.png
```

---

## 6. 체크리스트

### 프롬프트 파일 생성 시

```
□ prompts/[작품명]/ 폴더를 생성했는가?
□ characters/ 와 scenes/ 하위 폴더를 생성했는가?
□ 각 캐릭터별 MD와 JSON 파일을 생성했는가?
□ 각 챕터별 MD와 JSON 파일을 생성했는가?
□ 통합 JSON 파일(characters_all.json, scenes_all.json)을 생성했는가?
□ output_folder 경로가 올바르게 설정되어 있는가?
□ filename_prefix가 명명 규칙을 따르는가?
```

### n8n 자동화 설정 시

```
□ JSON 파일 경로가 올바른가?
□ ComfyUI API URL이 올바른가?
□ SaveImage 노드의 filename_prefix가 동적으로 설정되는가?
□ 배치 크기가 GPU 메모리에 적합한가?
□ 오류 처리 노드가 추가되어 있는가?
```
