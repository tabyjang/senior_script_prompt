# 캐릭터 프롬프트 생성 가이드

시니어 스토리 대본에서 캐릭터와 장면을 분석하여 ComfyUI 이미지 프롬프트를 체계적으로 생성하는 가이드.

**중요: 포지티브 프롬프트만 생성한다. 네거티브 프롬프트는 생성하지 않는다.**
(네거티브는 ComfyUI 워크플로우에서 고정값으로 설정됨)

---

# Part 1: 대본 분석 및 캐릭터 추출

## 1.1 대본에서 캐릭터 정보 추출하기

대본 MD 파일을 받으면 **반드시 아래 순서로 분석**한다:

### Step 1: 캐릭터 목록 작성

대본에서 등장인물을 찾아 다음 표를 작성:

```
| 이름 | 실제나이 | 프롬프트나이(-15) | 성별 | 역할 | 성격키워드 | 외모특징 | 상징물 |
|------|---------|-----------------|------|------|-----------|---------|--------|
| 예시 | 72세    | 57세            | 여성 | 주인공 | 단단함, 인내 | 진주목걸이 | 진주 |
```

### Step 2: 대본 내 캐릭터 정보 우선 참조

**중요**: 대본에 캐릭터 설명이 있으면 해당 정보를 최우선으로 사용한다.

대본에서 찾아야 할 정보:
- 나이 (명시된 경우)
- 외모 묘사 (머리색, 체형, 특징)
- 습관적 행동 (무심코 만지는 물건, 버릇)
- 직업/과거 경력
- 상징적 소품 (목걸이, 안경, 휠체어 등)
- 성격 묘사 (대사와 행동에서 유추)

### Step 3: 캐릭터 관계도 파악

```
주인공 ─┬─ 적대자 (갈등 관계)
        ├─ 조력자 (협력 관계)
        ├─ 가족 (혈연 관계)
        └─ 중립자 (변화 가능)
```

---

## 1.2 역할 유형별 기본 프롬프트

### 주인공 (Protagonist)

```
# 기본 특성
determined eyes, inner strength visible in posture,
sympathetic appearance, relatable look,
central focus, protagonist presence

# 고난 중
resilient expression despite hardship,
tired but unbroken spirit, dignified suffering,
quiet determination in eyes

# 승리/성장 후
confident posture, triumphant yet humble,
peaceful strength, earned wisdom in eyes,
serene victorious expression
```

### 적대자 (Antagonist)

```
# 기본 특성
calculating eyes, composed exterior,
hidden intentions, polished appearance,
deceptively charming, cold undertone

# 우위에 있을 때
smug expression, confident smirk,
superior posture, condescending look,
satisfied smile, dominant presence

# 패배/폭로 시
desperate expression, cornered look,
crumbling composure, panic in eyes,
disheveled appearance, losing control
```

### 조력자 (Helper/Ally)

```
# 기본 특성
trustworthy appearance, loyal expression,
supportive presence, reliable look,
warm encouraging eyes, steady demeanor

# 지원할 때
protective stance, encouraging expression,
ready to help posture, solidarity in eyes,
determined to assist, unified presence
```

### 중립자/변화하는 캐릭터

```
# 갈등 전
uncertain expression, conflicted eyes,
hesitant posture, torn between choices,
ambiguous stance, wavering loyalty

# 깨달음 후
remorseful expression, awakened eyes,
humble posture, seeking forgiveness,
changed person, redemption in face
```

---

## 1.3 성격 유형별 프롬프트

### 강인한/단단한 성격

```
firm jaw, steady gaze, unwavering eyes,
straight posture, squared shoulders,
resolute expression, inner steel visible,
dignified bearing, unshakeable presence
```

### 온화한/자애로운 성격

```
soft eyes, gentle smile, warm expression,
relaxed posture, open body language,
nurturing presence, maternal/paternal warmth,
kind face, approachable demeanor
```

### 활발한/적극적인 성격

```
bright eyes, animated expression,
energetic posture, expressive gestures,
lively presence, enthusiastic demeanor,
dynamic personality visible
```

### 신중한/분석적인 성격

```
observant eyes, thoughtful expression,
composed posture, calculating gaze,
intelligent appearance, perceptive look,
careful demeanor, analytical presence
```

### 교활한/이중적인 성격

```
shifting eyes, masked expression,
controlled body language, hidden agenda,
surface charm, underlying coldness,
two-faced appearance, deceptive smile
```

---

# Part 2: 캐릭터별 다양한 버전 생성

## 2.1 필수 생성 버전 (캐릭터당 최소 10개)

**각 캐릭터에 대해 다음 조합으로 최소 10개 이상의 프롬프트 버전을 생성한다:**

### 버전 생성 매트릭스

```
┌─────────────┬──────────────────────────────────────────────────────┐
│ 카테고리     │ 변형 옵션                                            │
├─────────────┼──────────────────────────────────────────────────────┤
│ 의상 (3+)   │ 일상복, 외출복, 정장, 요양원복, 잠옷, 한복, 운동복   │
│ 표정 (4+)   │ 평온, 기쁨, 슬픔, 분노, 결의, 놀람, 걱정, 사랑       │
│ 동작 (3+)   │ 서있기, 앉아있기, 걷기, 손잡기, 포옹, 대화, 작업     │
│ 악세서리    │ 기본, 안경, 목걸이, 귀걸이, 모자, 스카프, 가방       │
│ 시점/구도   │ 정면, 측면, 3/4뷰, 클로즈업, 미디엄샷, 풀샷         │
└─────────────┴──────────────────────────────────────────────────────┘
```

### 버전 생성 템플릿

캐릭터 1명당 다음 10개 버전을 기본으로 생성:

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

### 버전별 프롬프트 구조

```
[품질태그], [구도/시점],
[나이/성별/민족], [얼굴특징], [표정],
[헤어스타일], [의상상세], [악세서리],
[자세/동작], [손/팔 위치],
[배경], [조명]
```

---

## 2.2 의상 상세 프롬프트

### 일상복/집안복

```
# 여성
wearing comfortable home cardigan, soft knit sweater,
loose fitting clothes, cozy loungewear,
simple house dress, relaxed home attire

# 남성
wearing comfortable sweater, casual home clothes,
relaxed polo shirt, soft cotton shirt,
house slippers visible, cozy home attire
```

### 외출복

```
# 여성
wearing elegant blouse, stylish coat,
fashionable scarf, coordinated outfit,
leather handbag, polished appearance

# 남성
wearing neat jacket, buttoned shirt,
casual blazer, smart casual style,
leather belt, well-groomed appearance
```

### 정장/격식

```
# 여성
wearing formal dress suit, elegant two-piece,
silk blouse, pearl jewelry, refined makeup,
expensive-looking fabric, sophisticated style

# 남성
wearing tailored suit, silk tie,
polished dress shoes, cufflinks,
executive appearance, formal elegance
```

### 요양원/병원복

```
wearing simple patient gown, hospital clothes,
plain comfortable clothes, institutional attire,
slippers, minimal accessories,
subdued colors, practical garments
```

### 한복 (상세)

```
# 여성 한복
wearing traditional hanbok, silk jeogori jacket,
flowing chima skirt, delicate goreum ribbons,
embroidered details, pastel or vibrant colors,
traditional hairpin, elegant traditional beauty

# 남성 한복
wearing traditional hanbok, baji pants,
jeogori jacket, durumagi overcoat,
gat hat optional, dignified traditional look
```

---

## 2.3 동작/자세 상세 프롬프트

### 기본 자세

```
# 서있기
standing straight, upright posture,
hands clasped in front, dignified stance,
weight evenly distributed, stable position

# 앉아있기
sitting on sofa/chair, relaxed seated position,
hands on lap, comfortable sitting pose,
legs together, proper sitting posture

# 걷기
walking gracefully, mid-stride pose,
natural walking motion, purposeful gait,
one foot forward, balanced movement
```

### 감정적 동작

```
# 슬픔/우는 중
wiping tears, hands covering face,
shoulders shaking, hunched posture,
dabbing eyes with handkerchief,
bowed head, grief-stricken pose

# 분노
clenched fists, tense shoulders,
pointing finger, confrontational stance,
arms crossed defensively,
aggressive body language

# 기쁨
arms raised in joy, clapping hands,
jumping slightly, embracing gesture,
hands on heart, overwhelmed with happiness
```

### 상호작용 동작

```
# 대화 중
gesturing while speaking, leaning forward,
attentive listening pose, nodding,
making eye contact, engaged conversation

# 손잡기
holding hands tenderly, fingers intertwined,
reaching for hand, gentle hand grasp,
supportive hand holding, comforting touch

# 포옹
embracing warmly, arms wrapped around,
head on shoulder, tight hug,
comforting embrace, emotional reunion hug
```

---

## 2.4 악세서리 상세 프롬프트

### 목걸이/귀걸이

```
# 진주
wearing pearl necklace, single strand pearls,
pearl earrings, classic pearl set,
lustrous pearls, elegant pearl jewelry

# 금/은
wearing gold chain necklace, silver pendant,
delicate gold earrings, precious metal jewelry,
understated elegance, quality jewelry
```

### 안경

```
wearing reading glasses, elegant frames,
silver-rimmed glasses, intellectual appearance,
glasses perched on nose, looking over glasses,
bifocals, distinguished with spectacles
```

### 기타 악세서리

```
# 스카프/숄
silk scarf around neck, elegant shawl,
draped pashmina, colorful neck scarf,
warm wool shawl, stylish accessory

# 모자
wearing elegant hat, sun hat,
warm winter beanie, stylish beret,
traditional Korean gat, practical cap

# 가방
carrying leather handbag, elegant purse,
practical tote bag, classic clutch,
designer bag, everyday shoulder bag
```

---

# Part 3: 장면 분석 및 프롬프트 생성

## 3.1 챕터별 장면 분석 가이드

**각 챕터에서 10-20개의 핵심 장면을 추출하여 프롬프트를 생성한다.**

### 장면 추출 기준

```
1. 감정 전환점: 캐릭터의 감정이 크게 변하는 순간
2. 갈등 장면: 캐릭터 간 대립/충돌이 일어나는 장면
3. 화해/연대 장면: 관계 변화가 일어나는 장면
4. 상징적 장면: 스토리 테마를 보여주는 장면
5. 액션 장면: 중요한 행동/이벤트가 일어나는 장면
6. 환경 전환: 새로운 장소로 이동하는 장면
7. 오프닝/클로징: 챕터 시작과 끝 장면
```

### 장면 분석 템플릿

각 장면에 대해 다음을 분석:

```
┌─────────────────────────────────────────────────────────────┐
│ 장면 번호: [챕터]-[장면번호]                                 │
├─────────────────────────────────────────────────────────────┤
│ 장소: (어디서 일어나는가)                                    │
│ 시간: (낮/밤/새벽/저녁, 계절)                                │
│ 등장인물: (누가 나오는가)                                    │
│ 핵심 감정: (이 장면의 주요 감정)                             │
│ 핵심 행동: (무엇을 하고 있는가)                              │
│ 상징/소품: (중요한 물건이 있는가)                            │
│ 분위기: (전체적인 톤)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3.2 장면 유형별 프롬프트 템플릿

### 대화 장면 (2인)

```
메인 프롬프트:
masterpiece, best quality, photorealistic,
2people, [관계 설명], conversation scene,
[장소], [조명], [분위기]

캐릭터 A (왼쪽):
[나이] Korean [성별], [표정],
[헤어], [의상], speaking/listening,
[자세], facing right

캐릭터 B (오른쪽):
[나이] Korean [성별], [표정],
[헤어], [의상], listening/speaking,
[자세], facing left
```

### 갈등/대립 장면

```
메인 프롬프트:
masterpiece, best quality, photorealistic,
2people, tense confrontation, dramatic scene,
[장소], dramatic lighting, tension in air

캐릭터 A (공격적):
[캐릭터 설명], angry expression,
confrontational stance, pointing or gesturing,
aggressive body language

캐릭터 B (방어적/충격):
[캐릭터 설명], shocked/defensive expression,
stepped back posture, protective gesture,
vulnerable position
```

### 화해/포옹 장면

```
메인 프롬프트:
masterpiece, best quality, photorealistic,
2people embracing, emotional reunion,
[장소], warm lighting, touching moment

캐릭터 A:
[캐릭터 설명], tearful smile,
arms around other person, emotional expression,
relieved face, loving gesture

캐릭터 B:
[캐릭터 설명], crying with joy,
being held, face against shoulder,
emotional release, grateful expression
```

### 그룹 장면 (3-4인)

```
메인 프롬프트:
masterpiece, best quality, photorealistic,
[N]people, group scene, [활동 설명],
[장소], [조명], [분위기]

Regional Prompt 설정:
- 왼쪽 25%: 캐릭터 A
- 중앙 왼쪽 25%: 캐릭터 B
- 중앙 오른쪽 25%: 캐릭터 C
- 오른쪽 25%: 캐릭터 D
```

### 독백/회상 장면

```
masterpiece, best quality, photorealistic,
single person, contemplative moment,
[캐릭터 설명], pensive expression,
looking at [상징물/창밖/사진],
[장소], soft lighting, melancholic atmosphere,
nostalgic mood, introspective scene
```

### 전환점/깨달음 장면

```
masterpiece, best quality, photorealistic,
[캐릭터 설명], moment of realization,
eyes widening, dawning understanding,
[장소], dramatic lighting,
pivotal moment, emotional breakthrough
```

---

## 3.3 장소별 상세 프롬프트

### 요양원

```
# 복도
nursing home hallway, institutional corridor,
fluorescent lighting, handrails on walls,
clean linoleum floor, sterile atmosphere

# 방 (다인실)
nursing home room, multiple beds,
simple furniture, window with curtains,
personal items on nightstands,
institutional but lived-in atmosphere

# 휴게실
nursing home common area, TV on wall,
plastic chairs, vending machines,
elderly residents, communal space

# 독방
small isolation room, single bed,
barred window, sparse furniture,
confined space, oppressive atmosphere
```

### 법원/공식 장소

```
# 법정
courtroom interior, wooden benches,
judge's bench, witness stand,
formal legal setting, serious atmosphere,
fluorescent lighting, official environment

# 기자회견장
press conference room, podium with microphones,
camera flashes, journalists seated,
bright media lighting, formal setting
```

### 집/거실

```
# 따뜻한 거실
cozy Korean living room, warm lighting,
family photos on wall, comfortable sofa,
traditional decorations, homey atmosphere,
afternoon sunlight through window

# 고급 거실
luxurious living room, expensive furniture,
modern Korean interior, designer decor,
cold elegance, wealth displayed
```

### 제주도/자연

```
# 해변 펜션
Jeju island pension, ocean view,
wooden deck, outdoor terrace,
blue sea in background, peaceful setting,
warm sunlight, vacation atmosphere

# 마당/정원
Korean garden, chrysanthemum flowers,
stone path, traditional elements,
natural greenery, peaceful outdoor space
```

---

## 3.4 시간/조명별 프롬프트

### 시간대

```
# 아침
morning light, soft dawn glow,
golden sunrise, fresh atmosphere,
new day beginning, hopeful lighting

# 낮
bright daylight, natural sunlight,
clear visibility, neutral lighting,
everyday atmosphere

# 저녁/석양
golden hour, warm sunset glow,
orange and pink sky, nostalgic atmosphere,
long shadows, romantic lighting

# 밤
nighttime, artificial lighting,
dark background, lamp light,
intimate atmosphere, quiet night

# 새벽 (비밀 행동)
pre-dawn darkness, dim lighting,
secretive atmosphere, hushed moment,
shadows prominent, covert feeling
```

### 감정적 조명

```
# 희망적
bright warm lighting, golden glow,
uplifting atmosphere, optimistic mood

# 우울/슬픔
dim muted lighting, gray tones,
subdued atmosphere, melancholic mood

# 긴장/위험
harsh dramatic lighting, strong shadows,
high contrast, ominous atmosphere

# 평화/해결
soft diffused lighting, gentle warmth,
calm atmosphere, resolution mood
```

---

# Part 4: 프롬프트 생성 체크리스트

## 캐릭터 프롬프트 생성 시

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

## 장면 프롬프트 생성 시

```
□ 챕터당 10-20개 장면을 추출했는가?
□ 각 장면의 장소/시간/인물을 분석했는가?
□ 핵심 감정과 행동을 파악했는가?
□ 적절한 장면 유형 템플릿을 선택했는가?
□ 다중 캐릭터 장면에서 Regional Prompt 설정을 포함했는가?
□ 조명/분위기가 장면 감정과 일치하는가?
□ 상징적 소품이 필요한 장면에 포함했는가?
```

---

# Part 5: 기존 프롬프트 사전 (레퍼런스)

## 나이별 기본 프롬프트

### 50대 여성 (프롬프트 나이: 35-40세)

```
# 기본형
35 year old Korean woman, natural beauty, healthy complexion,
subtle smile lines, warm brown eyes,
shoulder-length black hair, elegant appearance

# 활발한 타입
38 year old Korean woman, energetic expression,
bright eyes, modern short haircut,
confident posture, stylish casual wear

# 전통적 타입
40 year old Korean woman, graceful demeanor,
neat hair bun, traditional elegance,
serene expression, hanbok or classic attire
```

### 60대 여성 (프롬프트 나이: 45-50세)

```
# 기본형
45 year old Korean woman, mature elegance,
gentle wrinkles around eyes, silver-streaked hair,
warm maternal expression, dignified posture

# 당당한 타입
48 year old Korean woman, confident expression,
short gray-streaked hair, wise eyes,
strong presence, well-dressed professional look

# 자애로운 타입
50 year old Korean woman, kind face,
soft permed hair with gray, warm smile,
motherly aura, comfortable cardigan style
```

### 70대 여성 (프롬프트 나이: 55세)

```
# 기본형
55 year old Korean woman, graceful aging,
white hair in neat style, soft wrinkles,
wise kind eyes, warm grandmother appearance

# 건강한 타입
55 year old Korean woman, vital appearance,
silver white hair, healthy skin tone,
bright eyes, active grandmother look

# 전통적 타입
55 year old Korean woman, traditional elegance,
white hair in bun, dignified expression,
wearing hanbok, serene composure
```

### 50대 남성 (프롬프트 나이: 35-40세)

```
# 기본형
38 year old Korean man, mature appearance,
neat short hair with some gray, defined features,
confident expression, business casual attire

# 다정한 타입
40 year old Korean man, warm expression,
gentle eyes, salt-and-pepper hair,
kind smile, comfortable sweater style
```

### 60대 남성 (프롬프트 나이: 45-50세)

```
# 기본형
48 year old Korean man, distinguished look,
gray hair neatly combed, dignified expression,
wise eyes, suit or smart casual

# 신사 타입
50 year old Korean man, gentleman appearance,
silver gray hair, warm paternal expression,
elegant posture, classic coat style
```

### 70대 남성 (프롬프트 나이: 55세)

```
# 기본형
55 year old Korean man, elderly gentleman,
white gray hair, gentle wrinkles,
kind grandfather expression, comfortable attire

# 당당한 타입
55 year old Korean man, dignified elder,
neat white hair, wise experienced eyes,
authoritative but warm presence
```

---

## 관계별 프롬프트 조합

### 모녀 (어머니 65세 + 딸 35세)

**메인:** `2women, mother and daughter, indoor family scene`

**어머니:**
```
50 year old Korean woman, maternal warmth,
gray-streaked hair, gentle expression,
looking at daughter with love and pride,
wearing comfortable home clothes
```

**딸:**
```
20 year old Korean woman, caring expression,
long black hair, modern casual style,
looking at mother with respect and affection
```

### 황혼 부부 (아내 65세 + 남편 68세)

**메인:** `elderly couple, romantic atmosphere, warm lighting`

**아내:**
```
50 year old Korean woman, serene beauty,
elegant silver hair, peaceful expression,
wearing pearl accessories, refined style
```

**남편:**
```
53 year old Korean man, gentle husband,
gray hair, warm protective expression,
neat casual attire, dependable presence
```

### 시어머니와 며느리 (시어머니 65세 + 며느리 35세)

**메인:** `2women, Korean family scene, living room setting`

**시어머니:**
```
50 year old Korean woman, traditional dignity,
neat gray hair, evaluating yet kind expression,
wearing hanbok or elegant traditional style
```

**며느리:**
```
20 year old Korean woman, respectful demeanor,
neat appearance, modest expression,
wearing conservative modern clothes
```

### 오랜 친구들 (모두 60대)

**메인:** `2women, old friends chatting, cafe or park setting`

**친구 A:**
```
45 year old Korean woman, animated expression,
permed hair, colorful outfit,
gesturing while talking, lively personality
```

**친구 B:**
```
45 year old Korean woman, attentive listener,
straight hair with gray, subtle makeup,
nodding with interest, warm smile
```

### 동맹/공모자들 (3-4인 그룹)

**메인:** `group of elderly women, conspiratorial atmosphere, united front`

```
# 리더 타입
determined expression, central position,
commanding presence, organizing gesture,
rallying the group, strong leadership

# 전략가 타입
thoughtful expression, analytical gaze,
planning demeanor, intelligent presence,
considering options, wise advisor

# 정보통 타입
alert expression, observant eyes,
aware of surroundings, knowing look,
street-smart appearance, resourceful

# 실행자 타입
ready for action, practical demeanor,
capable hands, determined expression,
prepared to act, loyal supporter
```

---

## 표정별 프롬프트

### 기쁨/행복

```
joyful expression, bright smile, sparkling eyes,
happy tears, laughing, beaming face,
radiant expression, content smile
```

### 슬픔/감동

```
tearful expression, glistening eyes, moved to tears,
emotional face, bittersweet smile,
touched expression, gentle sobbing
```

### 분노/불쾌

```
stern expression, furrowed brows, disapproving look,
tight lips, cold eyes, frustrated face,
annoyed expression, crossed arms
```

### 걱정/근심

```
worried expression, concerned eyes, anxious face,
furrowed forehead, troubled look,
pensive expression, thoughtful gaze
```

### 놀람

```
surprised expression, wide eyes, open mouth,
shocked face, raised eyebrows,
astonished look, startled expression
```

### 사랑/애정

```
loving gaze, tender expression, adoring eyes,
soft smile, gentle look, warmth in eyes,
affectionate expression, caring face
```

### 결의/각오

```
determined expression, steely gaze, set jaw,
resolute face, unwavering eyes,
committed expression, fierce determination
```

### 승리/만족

```
triumphant smile, victorious expression,
proud stance, satisfied look,
accomplished feeling, winning moment
```

---

## 의상별 프롬프트

### 한복

```
# 여성 한복
wearing elegant hanbok, jeogori and chima,
traditional Korean dress, silk fabric,
delicate embroidery, pastel colors

# 남성 한복
wearing traditional hanbok, durumagi coat,
Korean traditional attire, dignified appearance
```

### 캐주얼

```
# 여성 캐주얼
wearing comfortable cardigan, simple blouse,
casual pants, neat appearance,
practical yet elegant style

# 남성 캐주얼
wearing polo shirt, casual jacket,
comfortable slacks, neat casual look
```

### 포멀

```
# 여성 포멀
wearing elegant dress, pearl jewelry,
refined formal attire, sophisticated style

# 남성 포멀
wearing neat suit, tie,
formal business attire, polished appearance
```

---

## 배경별 프롬프트

### 실내

```
# 거실
cozy living room, warm lighting, family photos on wall,
comfortable sofa, traditional Korean decor

# 부엌
Korean kitchen, warm atmosphere, cooking scene,
homey environment, familiar domestic setting

# 병원
hospital room, clean white environment,
medical equipment, soft lighting
```

### 실외

```
# 공원
Korean park, autumn leaves, park bench,
golden hour lighting, peaceful atmosphere

# 시장
Korean traditional market, bustling atmosphere,
colorful produce, lively background

# 해변
Korean beach, sunset, peaceful waves,
golden light, romantic atmosphere
```

---

# 부록: 빠른 참조 가이드

## 나이 변환표

| 실제 나이 | 프롬프트 나이 | 권장 표현 |
|----------|-------------|----------|
| 45-50세 | 30-35세 | "30 year old", early middle-aged |
| 50-55세 | 35-40세 | "35-40 year old", middle-aged |
| 55-60세 | 40-45세 | "40-45 year old", mature |
| 60-65세 | 45-50세 | "45-50 year old", distinguished |
| 65-70세 | 50-55세 | "50-55 year old", graceful aging |
| 70-75세 | 55-60세 | "55-60 year old", elderly elegant |
| 75-80세 | 60-65세 | "60-65 year old", wise elder |

## 네거티브 프롬프트

**생성하지 않음** - 포지티브 프롬프트만 작성한다.
(네거티브는 ComfyUI 워크플로우에서 고정값으로 설정됨)
