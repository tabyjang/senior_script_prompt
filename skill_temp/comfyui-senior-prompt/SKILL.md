---
name: comfyui-senior-prompt
description: >
  시니어 스토리 유튜브용 ComfyUI 이미지 프롬프트 생성 스킬.
  대본 MD 파일을 분석하여 캐릭터별 다양한 이미지 프롬프트(10개+)와
  챕터별 장면 프롬프트(10-20개/챕터)를 체계적으로 생성한다.
  사용 시점: (1) 대본 MD 파일 기반 캐릭터 이미지 프롬프트 생성 시,
  (2) 챕터별 장면 이미지 프롬프트 생성 시,
  (3) 시니어 스토리 이미지컷 프롬프트 요청 시,
  (4) ComfyUI Regional Prompt 설정이 필요할 때
---

# ComfyUI 시니어 스토리 프롬프트 생성 스킬

시니어 타겟 유튜브 콘텐츠용 ComfyUI 이미지 프롬프트를 생성한다.
**대본 MD 파일을 입력받아** 캐릭터와 장면을 분석하고, 다양한 버전의 프롬프트를 체계적으로 생성한다.

---

## 사용 방법

### 1. 대본 기반 캐릭터 프롬프트 생성

사용자가 대본 MD 파일을 제공하면:

```
1. 대본에서 등장인물 정보 추출 (나이, 외모, 성격, 상징물 등)
2. 캐릭터별로 최소 10개 이상의 프롬프트 버전 생성
   - 의상 변형 3개+
   - 표정 변형 4개+
   - 동작/자세 변형 3개+
3. 캐릭터 간 상호작용 프롬프트 생성
```

**중요**: 대본에 캐릭터 정보가 명시되어 있으면 해당 정보를 최우선으로 참조한다.

### 2. 대본 기반 장면 프롬프트 생성

```
1. 각 챕터에서 10-20개의 핵심 장면 추출
2. 장면별 프롬프트 생성 (장소, 시간, 인물, 감정, 행동 분석)
3. Regional Prompt 설정 포함 (다중 캐릭터 장면)
```

---

## 핵심 원칙

### 0. 프롬프트 언어 규칙

**프롬프트는 반드시 영어로 작성한다.** ComfyUI/Stable Diffusion은 한글을 제대로 인식하지 못한다.

```
✅ 올바른 예시:
"positive": "57 year old Korean woman, gentle face..."
"description": "정숙이 상주석에서 조문객을 맞이하는 장면"  // 한글 설명 OK

❌ 잘못된 예시:
"positive": "57세 한국 여성, 부드러운 얼굴..."  // 한글 프롬프트 금지
```

**구조:**
- `positive`, `main_prompt`, `character_prompts` → **영어 필수**
- `description`, `scene_name`, `emotion` → 한글 설명 OK (메타데이터)

### 1. 나이 표현의 황금률: "실제 나이 - 15세"

AI 이미지 생성에서 나이를 정확히 표현하려면 **실제 나이보다 15세 젊게** 프롬프트를 작성해야 한다.

| 캐릭터 실제 나이 | 프롬프트 나이 | 프롬프트 표현 |
|-----------------|-------------|--------------|
| 50세 | 35세 | `35 year old Korean woman` |
| 55세 | 40세 | `40 year old Korean woman, early middle-aged` |
| 60세 | 45세 | `45 year old Korean woman, middle-aged` |
| 65세 | 50세 | `50 year old Korean woman, mature` |
| 70세 | 55세 | `55 year old Korean woman, graceful aging` |
| 75세 | 60세 | `60 year old Korean woman, wise elder` |

### 2. 한국인 시니어 특화 키워드

```
# 필수 포함
Korean, East Asian features, natural skin texture, warm expression

# 나이별 세부 표현
50대: subtle smile lines, healthy complexion, elegant demeanor
60대: gentle wrinkles, silver-streaked hair, wise eyes, dignified
70대: silver hair, soft wrinkles, kind eyes, warm grandmother appearance

# 피해야 할 표현
❌ old, elderly, aged, wrinkled (과도하게 늙어 보임)
❌ young, youthful (나이 불일치)
❌ anime, cartoon (실사 스타일과 충돌)
❌ white hair (나이를 15세 적게 해도 백발 쓰면 늙어 보임 → silver hair 사용)
```

---

## 대본 분석 워크플로우

### Step 1: 캐릭터 목록 작성

대본에서 등장인물을 찾아 다음 정보를 추출:

```
| 이름 | 실제나이 | 프롬프트나이 | 성별 | 역할 | 성격 | 외모특징 | 상징물 |
|------|---------|-------------|------|------|------|---------|--------|
```

추출할 정보:
- 나이 (명시된 경우)
- 외모 묘사 (머리색, 체형, 특징)
- 습관적 행동 (무심코 만지는 물건, 버릇)
- 직업/과거 경력
- 상징적 소품 (목걸이, 안경, 휠체어 등)
- 성격 묘사 (대사와 행동에서 유추)

### Step 2: 캐릭터별 10개+ 버전 생성

각 캐릭터에 대해 다음 버전을 필수로 생성:

```
버전 1: 기본 정면 (캐릭터 소개용)
버전 2: 일상 의상 + 평온한 표정
버전 3: 외출 의상 + 밝은 표정
버전 4: 정장/격식 의상 + 단호한 표정
버전 5: 슬픈/감정적 표정 + 클로즈업
버전 6: 분노/결의 표정 + 강한 자세
버전 7: 동작 중 (걷기/작업 등)
버전 8: 다른 캐릭터와 상호작용 (대화)
버전 9: 다른 캐릭터와 상호작용 (신체 접촉)
버전 10: 상징적 소품과 함께
```

### Step 3: 챕터별 장면 프롬프트 생성

각 챕터에서 10-20개 핵심 장면 추출 기준:

```
1. 감정 전환점: 캐릭터의 감정이 크게 변하는 순간
2. 갈등 장면: 캐릭터 간 대립/충돌
3. 화해/연대 장면: 관계 변화
4. 상징적 장면: 스토리 테마를 보여주는 장면
5. 액션 장면: 중요한 행동/이벤트
6. 환경 전환: 새로운 장소로 이동
7. 오프닝/클로징: 챕터 시작과 끝
```

---

## 프롬프트 구조

### 기본 구조 (단일 캐릭터)

```
[품질 태그], [카메라/구도], [인물 설명], [표정/감정], [의상], [배경], [조명]
```

**예시: 72세 여성 주인공**
```
masterpiece, best quality, photorealistic, 8k uhd,
medium shot, eye level,
57 year old Korean woman, gentle face, subtle smile lines, warm brown eyes,
shoulder-length black hair with gray streaks, kind smile, soft expression,
wearing elegant beige cardigan, pearl necklace,
cozy living room background, natural window light,
soft lighting, warm color tone
```

### 버전별 프롬프트 구조

```
[품질태그], [구도/시점],
[나이/성별/민족], [얼굴특징], [표정],
[헤어스타일], [의상상세], [악세서리],
[자세/동작], [손/팔 위치],
[배경], [조명]
```

### 네거티브 프롬프트

**네거티브 프롬프트는 생성하지 않는다.** 포지티브 프롬프트만 작성한다.
(네거티브는 ComfyUI 워크플로우에서 고정값으로 설정됨)

---

## 다중 캐릭터 프롬프트 (2인 이상)

### 방법 1: ComfyUI Couple 노드 사용 (권장)

2인 캐릭터를 서로 다른 영역에 배치하여 특성 혼합을 방지한다.

**워크플로우 구성:**
1. `ComfyCouple` 또는 `AttentionCouple` 노드 설치
2. 이미지를 좌/우 영역으로 분할
3. 각 영역에 개별 프롬프트 적용

**메인 프롬프트 (전체 장면):**
```
masterpiece, best quality, photorealistic,
2women, indoor scene, warm lighting, living room,
mother and daughter conversation
```

**왼쪽 영역 프롬프트 (캐릭터 1 - 어머니 65세):**
```
50 year old Korean woman, gentle face, warm eyes,
gray-streaked hair in neat bun, wearing hanbok jeogori,
sitting on sofa, looking at daughter with love
```

**오른쪽 영역 프롬프트 (캐릭터 2 - 딸 40세):**
```
25 year old Korean woman, caring expression,
long black hair, wearing casual sweater,
sitting next to mother, holding her hand
```

### 방법 2: Regional Prompt + 마스크

**설정:**
- 마스크 1: 왼쪽 50% 영역 → 캐릭터 A
- 마스크 2: 오른쪽 50% 영역 → 캐릭터 B
- Overlap ratio: 0.3~0.5 (상호작용 시 높게)

**중요 규칙:**
```
✅ 메인 프롬프트에 총 인원수 명시: "2women", "1man 1woman", "3women"
✅ 각 영역 프롬프트는 해당 캐릭터만 설명
✅ 배경/조명은 메인 프롬프트에만 포함
❌ 각 영역에 "solo" 사용 금지
❌ 영역 프롬프트에 다른 캐릭터 언급 금지
```

---

## 캐릭터 상호작용 프롬프트

### 포옹 (Hug/Embrace)

상호작용이 있을 때는 **마스크 영역을 겹치게** 설정해야 한다.

**메인 프롬프트:**
```
masterpiece, best quality, photorealistic,
2women embracing, emotional reunion, warm lighting,
indoor setting, heartwarming scene
```

**캐릭터 A (왼쪽, 오버랩 30%):**
```
50 year old Korean woman, tearful smile,
gray hair, wearing cardigan,
hugging daughter, arms around her
```

**캐릭터 B (오른쪽, 오버랩 30%):**
```
25 year old Korean woman, emotional expression,
long black hair, casual clothes,
being hugged by mother, face against shoulder
```

**마스크 설정:**
- 캐릭터 A 마스크: 이미지 왼쪽 0~60%
- 캐릭터 B 마스크: 이미지 오른쪽 40~100%
- 중앙 20% 영역 오버랩

### 손잡기 (Holding Hands)

**메인 프롬프트:**
```
masterpiece, best quality, photorealistic,
elderly couple holding hands, romantic, park bench,
golden hour lighting, autumn leaves background
```

**캐릭터 A (왼쪽):**
```
55 year old Korean woman, gentle smile,
silver hair, elegant coat, pearl necklace,
sitting on bench, hand extended to partner
```

**캐릭터 B (오른쪽):**
```
57 year old Korean man, warm expression,
gray hair, neat suit, dignified appearance,
sitting beside wife, holding her hand tenderly
```

**팁:** 손이 겹치는 중앙 영역에는 두 캐릭터의 마스크가 모두 적용되도록 설정

### 대화/마주보기 (Conversation)

**메인 프롬프트:**
```
masterpiece, best quality, photorealistic,
2women having conversation, cafe interior,
warm afternoon light, coffee cups on table
```

**캐릭터 A:**
```
50 year old Korean woman, animated expression,
short permed hair, colorful blouse,
gesturing while talking, friendly smile
```

**캐릭터 B:**
```
50 year old Korean woman, listening attentively,
straight hair with gray streaks, cardigan,
nodding, interested expression, coffee cup in hand
```

---

## 고급 기법

### 1. ControlNet + Regional Prompt 조합

포즈 제어가 필요한 상호작용 장면에 사용:

```
1. OpenPose 이미지 준비 (2인 포즈)
2. ControlNet OpenPose 노드 연결
3. Regional Prompt로 각 캐릭터 외모 지정
4. Denoise: 0.7~0.8 권장
```

### 2. 2단계 생성 (권장)

복잡한 상호작용 장면:

```
Step 1: 전체 구도 생성
- 낮은 디테일, 포즈/구도 확정
- Steps: 15-20, Denoise: 1.0

Step 2: img2img로 디테일 보강
- Regional Prompt 적용
- 각 캐릭터 영역만 마스크
- Denoise: 0.5-0.6
```

### 3. 얼굴 보정 (Face Detailer)

생성 후 얼굴 품질 향상:

```
ADetailer 또는 Face Detailer 노드 사용
각 얼굴 영역에 개별 프롬프트 적용 가능
특히 나이 표현 세부 조정에 유용
```

---

## 참조 파일

- **캐릭터 프롬프트 생성 가이드**: references/character-prompts.md
  - 대본 분석 방법
  - 역할/성격별 프롬프트
  - 캐릭터별 10개+ 버전 생성 가이드
  - 장면 분석 및 프롬프트 생성 가이드
  - 장소/시간/조명별 상세 프롬프트
- **장면별 템플릿**: references/scene-templates.md
- **Regional Prompt 설정 가이드**: references/regional-settings.md
- **출력 형식 및 폴더 구조 가이드**: references/output-format.md
  - MD/JSON 파일 형식 정의
  - 폴더 구조 (prompts/, output/)
  - n8n + ComfyUI 자동화 설정
  - 파일 명명 규칙

---

## 체크리스트

### 캐릭터 프롬프트 생성 시

```
□ 대본의 캐릭터 정보를 먼저 확인했는가?
□ 실제 나이에서 15세를 뺐는가?
□ 성격 유형에 맞는 표정/자세를 적용했는가?
□ 역할(주인공/적대자/조력자)에 맞는 표현을 사용했는가?
□ 대본에 나온 상징적 소품을 포함했는가?
□ 최소 10개 이상의 버전을 생성했는가?
  □ 의상 변형 3개 이상
  □ 표정 변형 4개 이상
  □ 동작/자세 변형 3개 이상
□ 다른 캐릭터와의 상호작용 버전이 있는가?
```

### 장면 프롬프트 생성 시

```
□ 챕터당 10-20개 장면을 추출했는가?
□ 각 장면의 장소/시간/인물을 분석했는가?
□ 핵심 감정과 행동을 파악했는가?
□ 적절한 장면 유형 템플릿을 선택했는가?
□ 다중 캐릭터 장면에서 Regional Prompt 설정을 포함했는가?
□ 조명/분위기가 장면 감정과 일치하는가?
□ 상징적 소품이 필요한 장면에 포함했는가?
```

### 기본 체크

```
□ 다중 캐릭터 시 총 인원수 명시했는가?
□ 상호작용 장면에서 마스크 오버랩 설정했는가?
□ 한국인 특화 키워드 포함했는가?
□ 포지티브 프롬프트만 작성했는가? (네거티브는 생성하지 않음)
```
