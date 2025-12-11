# 프로젝트 저장 구조 및 형식 정의

## 목표

프로젝트의 저장 폴더 구조와 각 데이터 타입의 저장 형식을 명확히 정의합니다.

## 결정 사항

1. **프로젝트 폴더 구조**: 프로젝트 번호 + 제목 형식
2. **이미지 프롬프트**: 캐릭터 정보 JSON에 포함
3. **대본(스크립트)**: 챕터 정보 JSON에 포함

## 폴더 구조

```
senior_contents/
└── senior_project_manager/
    └── 01_man/                          # 카테고리 (예: 남성향)
        └── 001_사돈_그_선을_넘어도_되겠습니까/  # 프로젝트 번호_제목
            ├── synopsis.json            # 시놉시스
            ├── 02_characters/           # 인물 정보
            │   ├── 김태주_profile.json
            │   ├── 이영숙_profile.json
            │   └── images/              # 이미지 파일 (선택사항)
            │       ├── 김태주/
            │       │   ├── prompt_1.jpg
            │       │   └── prompt_2.jpg
            │       └── 이영숙/
            │           └── ...
            └── 03_chapters/             # 챕터 정보
                ├── chapter_01.json
                ├── chapter_02.json
                └── ...
```

## 저장 형식 정의

### 1. 시놉시스 (`synopsis.json`)

**위치**: 프로젝트 루트 디렉토리

**구조**:
```json
{
  "title": "제목",
  "synopsis": "시놉시스 내용",
  "full_story": "전체 줄거리",
  "characters": [
    {
      "name": "이름",
      "age": 60,
      "occupation": "직업",
      "personality": "성격",
      "appearance": "외모",
      "traits": "특징",
      "desire": "욕망",
      "role": "역할"
    }
  ],
  "chapters": {
    "chapter_1": "챕터 1 내용",
    "chapter_2": "챕터 2 내용"
  },
  "main_events": "주요 사건 전개",
  "touching_events": "감동을 주는 사건",
  "joyful_events": "기쁨을 주는 사건",
  "shocking_events": "충격을 주는 사건",
  "key_objects": "키 오브젝트",
  "success_strategy": "성공 전략",
  "audiobook_script_example": "오디오북 대본 예시"
}
```

**필드 설명**:
- `title`: 프로젝트 제목
- `synopsis`: 시놉시스 요약
- `full_story`: 전체 줄거리
- `characters`: 등장인물 배열 (기본 정보)
- `chapters`: 챕터 구성 (딕셔너리)
- `main_events`: 주요 사건 전개
- `touching_events`: 감동을 주는 사건
- `joyful_events`: 기쁨을 주는 사건
- `shocking_events`: 충격을 주는 사건
- `key_objects`: 키 오브젝트
- `success_strategy`: 성공 전략
- `audiobook_script_example`: 오디오북 대본 예시

### 2. 캐릭터 정보 (`02_characters/{name}_profile.json`)

**위치**: `02_characters/` 폴더

**구조**:
```json
{
  "name": "김태주",
  "age": 60,
  "occupation": "재벌가 수행기사 (전직 북파공작원)",
  "personality": "강철같은 충성심과 무거운 입을 가졌습니다.",
  "appearance": "180cm, 정장 핏이 완벽한 다부진 체격.",
  "traits": "백미러를 통해 상황을 파악하는 능력이 탁월하며",
  "desire": "자신의 주군인 사모님을 지키고",
  "role": "남주인공, 우직한 영웅",
  
  "id": "char_male_01",
  "role_type": "Main_Male (Protagonist)",
  "relation_to_protagonist": "본인 (화자)",
  "appearance_visual": "180cm, 90kg. 낡은 정장이 터질듯한 근육질.",
  "sensory_scent": "오래된 가죽 냄새, 독한 스킨 향",
  "sensory_touch": "거칠고 투박하다. 굳은살이 박혀 있어",
  "fashion_style": "유행 지난 검은 정장, 하얀 장갑",
  "personality_surface": "감정이 없는 기계 같음",
  "personality_deep": "가슴속에 억눌린 야수와 폭력성이 있음",
  "trauma_or_lack": "과거 임무 중 동료를 지키지 못했다는 부채감",
  "desire_conscious": "사모님의 명령을 완수하고",
  "desire_unconscious": "백미러 속의 훔쳐보기를 멈추고",
  "voice_tone": "동굴처럼 울리는 초저음",
  "speech_habit": "말끝을 짧게 끊음",
  "breathing_sound": "평소엔 들리지 않으나, 흥분하면 코로 거칠게 몰아쉬는 숨소리가 맹수 같음",
  
  "image_generation_prompts": {
    "prompt_1": "전신샷 프롬프트 (JSON 문자열)",
    "prompt_2": "사이드샷 프롬프트 (JSON 문자열)",
    "prompt_3": "클로즈업 프롬프트 (JSON 문자열)",
    "prompt_4": "프롬프트 4 (JSON 문자열)",
    "prompt_5": "프롬프트 5 (JSON 문자열)",
    "prompt_6": "프롬프트 6 (JSON 문자열)",
    "prompt_7": "프롬프트 7 (JSON 문자열)"
  }
}
```

**기본 정보 필드**:
- `name`: 캐릭터 이름
- `age`: 나이
- `occupation`: 직업
- `personality`: 성격
- `appearance`: 외모
- `traits`: 특징
- `desire`: 욕망
- `role`: 역할

**세부 정보 필드**:
- `id`: 캐릭터 ID (예: "char_male_01")
- `role_type`: 역할 타입 (예: "Main_Male (Protagonist)")
- `relation_to_protagonist`: 주인공과의 관계
- `appearance_visual`: 시각적 외모 묘사
- `sensory_scent`: 향기/냄새
- `sensory_touch`: 촉감
- `fashion_style`: 패션 스타일
- `personality_surface`: 표면적 성격
- `personality_deep`: 깊은 성격
- `trauma_or_lack`: 트라우마 또는 부족함
- `desire_conscious`: 의식적 욕망
- `desire_unconscious`: 무의식적 욕망
- `voice_tone`: 목소리 톤
- `speech_habit`: 말투 습관
- `breathing_sound`: 호흡 소리

**이미지 프롬프트 필드**:
- `image_generation_prompts`: 이미지 생성 프롬프트 딕셔너리
  - `prompt_1` ~ `prompt_7`: 각 프롬프트 번호별 JSON 문자열

**이미지 프롬프트 형식** (각 `prompt_N`의 값):
```json
{
  "character": "Korean man, 40-year-old, elegant oval face...",
  "clothing": "Fitted navy suit, white gloves...",
  "pose": "Standing confidently, shoulders back...",
  "background": "Bright, minimalist office with soft natural light...",
  "situation": "Serene, confident, professional moment...",
  "combined": "Korean man, 40-year-old... Fitted navy suit... Standing confidently..."
}
```

### 3. 챕터 정보 (`03_chapters/chapter_{number:02d}.json`)

**위치**: `03_chapters/` 폴더

**구조**:
```json
{
  "chapter_number": 1,
  "title": "챕터 1 (도입)",
  "content": "챕터 내용...",
  "script": "대본 내용...",
  "script_length": 5234,
  "script_generated_at": "2024-01-15T10:30:00"
}
```

**필드 설명**:
- `chapter_number`: 챕터 번호 (숫자)
- `title`: 챕터 제목
- `content`: 챕터 내용
- `script`: 대본 텍스트 (문자열, 선택사항)
- `script_length`: 대본 글자 수 (숫자, 선택사항)
- `script_generated_at`: 대본 생성/수정 시간 (ISO 8601 형식, 선택사항)

**대본(스크립트) 필드**:
- `script`: 대본 텍스트 (문자열)
- `script_length`: 글자 수 (숫자, 선택사항)
- `script_generated_at`: 생성/수정 시간 (ISO 8601 형식, 선택사항)

## 파일 명명 규칙

### 프로젝트 폴더

- **형식**: `{번호:03d}_{제목}`
- **예**: `001_사돈_그_선을_넘어도_되겠습니까`
- **규칙**:
  - 번호는 3자리 숫자로 표시 (001, 002, ...)
  - 제목의 공백은 언더스코어(`_`)로 변환
  - 특수문자는 제거하거나 언더스코어로 변환
  - 파일 시스템에서 사용할 수 없는 문자는 제거

### 캐릭터 파일

- **형식**: `{이름}_profile.json`
- **예**: `김태주_profile.json`
- **규칙**:
  - 파일명에 사용할 수 없는 문자는 언더스코어로 변환
  - 파일명에 사용할 수 없는 문자: `<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, `*`

### 챕터 파일

- **형식**: `chapter_{번호:02d}.json`
- **예**: `chapter_01.json`, `chapter_02.json`
- **규칙**:
  - 번호는 2자리 숫자로 표시 (01, 02, ...)
  - 항상 `chapter_` 접두사 사용

## 이미지 파일 저장

**위치**: `02_characters/images/{character_name}/`

**파일명 형식**: `prompt_{번호}.{확장자}`

**예**:
- `02_characters/images/김태주/prompt_1.jpg`
- `02_characters/images/김태주/prompt_2.png`

**지원 확장자**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`

## 데이터 흐름

1. **시놉시스 입력** → `synopsis.json` 저장
2. **등장인물 파싱** → `02_characters/{name}_profile.json` 생성 (기본 정보)
3. **인물 세부정보 입력** → `02_characters/{name}_profile.json` 업데이트 (세부 정보 추가)
4. **이미지 프롬프트 생성** → `02_characters/{name}_profile.json` 업데이트 (`image_generation_prompts` 필드 추가)
5. **챕터 파싱** → `03_chapters/chapter_{number:02d}.json` 생성
6. **대본 생성** → `03_chapters/chapter_{number:02d}.json` 업데이트 (`script` 필드 추가)

## 구현 상태

- ✅ 프로젝트 번호 기반 폴더 구조
- ✅ 이미지 프롬프트를 캐릭터 JSON에 포함
- ✅ 대본을 챕터 JSON에 포함
- ✅ 파일명 정규화 함수
- ✅ 저장 형식 문서화

## 참고사항

- 모든 JSON 파일은 UTF-8 인코딩으로 저장됩니다.
- JSON 파일은 들여쓰기 2칸으로 포맷팅됩니다.
- 파일명에 사용되는 내부 메타데이터 필드 (`_filename`)는 저장 시 제거됩니다.

