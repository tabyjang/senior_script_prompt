"""
콘텐츠 생성 서비스
LLM을 사용하여 대본, 장면, 프로필 등을 생성합니다.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class ContentGenerator:
    """콘텐츠 생성 서비스 클래스"""

    def __init__(self, llm_service):
        """
        Args:
            llm_service: LLMService 인스턴스
        """
        self.llm = llm_service

    def generate_character_profile(self, synopsis: Dict, char_name: str, char_info: Dict) -> Optional[Dict]:
        """
        캐릭터 프로필 생성

        Args:
            synopsis: 시놉시스 데이터
            char_name: 캐릭터 이름
            char_info: 캐릭터 기본 정보

        Returns:
            생성된 프로필 데이터 또는 None
        """
        full_story = synopsis.get('full_story', synopsis.get('synopsis', ''))

        system_prompt = """당신은 소설/드라마 캐릭터 개발 전문가입니다.
시놉시스와 캐릭터 기본 정보를 바탕으로 상세한 캐릭터 프로필을 작성해주세요.

**중요 원칙**:
1. 시놉시스의 스토리와 인물 관계를 정확히 반영해야 합니다
2. 50-70대 시니어 남성 독자를 위한 콘텐츠이므로 품격 있고 세련된 표현을 사용하세요
3. 외모 묘사는 구체적이고 상세해야 합니다
4. 성격은 복합적이고 입체적으로 표현하세요
5. 반드시 JSON 형식으로만 응답해주세요"""

        user_prompt = f"""다음 정보를 바탕으로 캐릭터의 상세 프로필을 작성해주세요:

## 전체 스토리
{full_story}

## 캐릭터 기본 정보
- 이름: {char_name}
- 나이: {char_info.get('age', '')}세
- 직업: {char_info.get('occupation', '')}
- 역할: {char_info.get('role', '')}
- 성격 (개요): {char_info.get('personality', '')}
- 외모 (개요): {char_info.get('appearance', '')}
- 특성: {char_info.get('traits', '')}
- 욕구/동기: {char_info.get('desire', '')}

## 요청사항
위 정보를 바탕으로 다음 항목을 **상세하게** 작성해주세요:

1. **외모 (appearance)**:
   - face: 얼굴 특징 (얼굴형, 눈, 코, 입, 피부톤 등을 구체적으로)
   - body: 체형 (키, 체격, 자세, 걸음걸이 등)
   - clothing: 평소 복장 스타일 (선호하는 옷 스타일, 색상, 액세서리 등)
   - features: 눈에 띄는 특징들 (배열로, 3-5개)

2. **성격 (personality)**:
   - traits: 성격 특성 (배열로, 5-7개의 구체적인 특성)
   - speech_style: 말투와 대화 스타일 (어떻게 말하는지, 자주 쓰는 표현 등)

3. **background**: 배경 스토리 (과거 경험, 현재 상황, 내적 갈등 등을 2-3문장으로)

4. **visual_reference**: 시각적 참고 설명 (이 인물의 전체적인 인상과 분위기를 1-2문장으로)

**반드시 다음 JSON 형식으로만 응답하세요. 다른 설명은 포함하지 마세요:**

```json
{{
  "appearance": {{
    "face": "상세한 얼굴 특징 설명",
    "body": "상세한 체형 설명",
    "clothing": "복장 스타일 설명",
    "features": ["특징1", "특징2", "특징3"]
  }},
  "personality": {{
    "traits": ["특성1", "특성2", "특성3", "특성4", "특성5"],
    "speech_style": "말투와 대화 스타일 설명"
  }},
  "background": "배경 스토리",
  "visual_reference": "시각적 참고 설명"
}}
```"""

        try:
            response = self.llm.call(user_prompt, system_prompt)
            if response:
                # JSON 추출
                from utils.json_utils import extract_json_from_text, safe_json_loads
                json_text = extract_json_from_text(response)
                return safe_json_loads(json_text)
        except Exception as e:
            print(f"프로필 생성 오류 ({char_name}): {e}")

        return None

    def generate_script(self, chapter: Dict, synopsis: Dict, characters_info: str, previous_script: str = "") -> Optional[str]:
        """
        챕터 대본 생성

        Args:
            chapter: 챕터 데이터
            synopsis: 시놉시스 데이터
            characters_info: 인물 정보 (포맷팅된 문자열)
            previous_script: 이전 챕터 대본 (연속성 유지용)

        Returns:
            생성된 대본 텍스트 또는 None
        """
        full_story = synopsis.get('full_story', synopsis.get('synopsis', ''))
        chapter_num = chapter.get('chapter_number', 0)

        system_prompt = """당신은 50-70대 시니어 남성 독자를 위한 오디오북 대본 작가입니다.
다음 규칙을 **반드시** 준수하여 TTS(Text-to-Speech)용 나레이션 대본을 작성해주세요.

핵심 원칙:
1. 제공된 시놉시스의 전체 줄거리를 반드시 숙지할 것
2. 제공된 인물 프로필의 성격, 말투, 특징을 정확히 반영할 것
3. 해당 챕터의 내용과 분위기에 맞게 작성할 것
4. 이전 챕터들의 흐름과 연속성을 유지할 것
5. 캐릭터와 줄거리의 일관성을 반드시 유지할 것

나레이션 형식:
- 전체 대본은 정중한 존댓말 사용 (예: "~습니다", "~였습니다")
- 나레이션이 인물의 심리, 행동, 대사를 모두 자연스럽게 포함
- 대사보다 나레이션의 비중이 훨씬 많아야 함 (나레이션 70-80% : 대사 20-30%)
- 인물의 대사를 나레이션이 전달: "김성민은 '안녕하세요'라고 인사를 건넸습니다"

TTS 최적화:
- 복사-붙여넣기로 바로 TTS에 입력 가능한 형태
- 대본 길이: **5000자 내외** (4500~5500자 권장)
- 문단 구분이 자연스럽고 호흡이 편안해야 함
- 특수문자, 괄호, 주석 등 불필요한 요소 제거

대상 독자:
- 50-70대 시니어 남성
- 영웅 서사, 성적 친밀감을 고조시켜주는 로맨스, 성적 긴장감 해설 중심, 성적인 특징에 대한 묘사와 두근두근 거리는 느낌의 긴장감 신비로움, 성적 가까워지는 기대감과 그것의 충족시켜가는 디테일한 과정이 핵심 포인트, 의리와 액션, 카타르시스, 디테일한 묘사
- 강렬한 로맨스와 성취감 높은 메시지, 성적 친밀감에 대한 치밀한 묘사 중심"""

        user_prompt = f"""다음 정보를 바탕으로 챕터 {chapter_num}의 TTS용 나레이션 대본을 작성해주세요.

1. 전체 시놉시스:
{full_story}

2. 등장인물 정보:
{characters_info}

3. 해당 챕터 정보:
- 챕터 번호: {chapter_num}
- 챕터 제목: {chapter.get('title', '')}
- 챕터 요약: {chapter.get('summary', '')}
- 주요 사건: {chr(10).join(chapter.get('key_events', []))}
- 등장 인물: {', '.join(chapter.get('characters_involved', []))}
- 분위기: {chapter.get('mood', '')}

4. 이전 챕터 대본 (연속성 참고):
{previous_script if previous_script else "없음 (첫 챕터)"}

작성 요구사항:
1. **반드시** 위의 시놉시스, 인물 정보, 챕터 정보를 숙지하고 일관성 있게 작성할 것
2. 대본 길이: **5000자 내외** (4500~5500자)
3. 정중한 존댓말 사용
4. 나레이션 중심 (대사는 최소화)
5. TTS에 바로 사용 가능하도록 순수 텍스트만 출력
6. 캐릭터의 성격, 말투, 관계가 정확히 반영되어야 함
7. 이전 챕터와의 연속성 유지
8. 50-70대 남성 독자에게 강렬한 로맨스와 성취감 높은 메시지, 성적 친밀감에 대한 치밀한 묘사 중심
9. 성적 친밀감을 고조시켜주는 로맨스, 성적 긴장감 해설 중심, 성적인 특징에 대한 묘사와 두근두근 거리는 느낌의 긴장감 신비로움, 성적 가까워지는 기대감과 그것의 충족시켜가는 디테일한 과정이 핵심 포인트, 의리와 액션, 카타르시스, 디테일한 묘사

**매우 중요**:
- 대본 텍스트만 출력하세요
- 부가 설명, 주석, 메타 정보는 절대 포함하지 마세요
- "글자 수", "끝", "완료", "총 XXX자" 같은 문구를 절대 넣지 마세요
- 대본이 자연스럽게 끝나면 그대로 종료하세요"""

        try:
            script = self.llm.call(user_prompt, system_prompt)
            return script.strip() if script else None
        except Exception as e:
            print(f"대본 생성 오류 (챕터 {chapter_num}): {e}")
            return None

    def generate_scenes(self, chapter: Dict, synopsis: Dict, characters_info: str, character_prompts_info: str = "") -> Optional[List[Dict]]:
        """
        챕터의 10개 장면 생성

        Args:
            chapter: 챕터 데이터
            synopsis: 시놉시스 데이터
            characters_info: 인물 정보 (포맷팅된 문자열)
            character_prompts_info: 인물 이미지 프롬프트 참고 정보

        Returns:
            생성된 장면 리스트 또는 None
        """
        full_story = synopsis.get('full_story', synopsis.get('synopsis', ''))
        chapter_num = chapter.get('chapter_number', 0)
        script = chapter.get('script', '')

        system_prompt = """당신은 영상 제작을 위한 장면 분석 전문가입니다.
주어진 대본을 분석하여 10개의 핵심 장면을 추출하고, 각 장면에 맞는 이미지 프롬프트를 작성해주세요.

**중요 원칙**:
1. 대본의 흐름을 따라 자연스럽게 10개 장면으로 분할
2. 각 장면은 명확한 한글 제목을 가져야 함
3. 각 장면의 이미지 프롬프트는 등장인물, 배경, 동작 등을 포함할 것
4. 인물의 외모는 일관되게 유지 (이미지 프롬프트 참고)
5. **매우 중요: 각 캐릭터마다 다른 나이를 사용해야 합니다. 절대로 모든 캐릭터에 동일한 나이를 사용하지 마세요.**
6. **나이 표현 규칙**: "youthful 27-year-old appearance" 같은 고정 표현을 절대 사용하지 마세요.
   - 반드시 각 캐릭터의 실제 나이와 youth age를 사용하세요.
   - 형식: "[실제나이]-year-old (youth age: [youth나이])"
   - 예시: "Korean man, 35-year-old (youth age: 27), ..."
7. 반드시 JSON 형식으로만 응답"""

        user_prompt = f"""다음 정보를 바탕으로 챕터 {chapter_num}의 대본을 분석하여 10개의 장면을 생성해주세요:

## 전체 스토리
{full_story[:1000]}

## 등장인물 정보
{characters_info}

**중요**: 위 등장인물 정보에 각 캐릭터의 실제 나이와 Youth age가 명시되어 있습니다. 
각 캐릭터의 이미지 프롬프트를 작성할 때 반드시 해당 캐릭터의 실제 나이와 Youth age를 사용하세요.
절대로 모든 캐릭터에 동일한 나이(예: 27세)를 사용하지 마세요.

## 인물 이미지 프롬프트 참고
{character_prompts_info if character_prompts_info else "없음"}

## 챕터 정보
- 챕터 번호: {chapter_num}
- 챕터 제목: {chapter.get('title', '')}
- 챕터 요약: {chapter.get('summary', '')}

## 대본
{script}

## 요청사항
위 대본을 분석하여 다음 조건을 만족하는 10개의 장면을 생성해주세요:

1. **장면 분할**: 대본의 흐름에 따라 자연스럽게 10개로 분할
2. **장면 제목**: 각 장면에 명확하고 구체적인 한글 제목 부여
3. **이미지 프롬프트**: 각 장면을 상세한 영어 프롬프트 작성

**영어 프롬프트 작성 규칙 - 반드시 다음 구조를 따라야 합니다:**

이미지 프롬프트는 다음 순서로 작성하세요:

1. **배경 정보** (먼저 작성):
   - 장소: 헬스장, 요가 스튜디오, 거실 등 구체적인 장소
   - 물건: 데스크, 화분, 의자, 운동기구 등 장면에 있는 물건들
   - 바닥: 마루 바닥, 타일 바닥, 카펫 등
   - 조명: 밝은 조명, 부드러운 조명, 자연광 등

2. **캐릭터 1** (등장하는 첫 번째 캐릭터):
   - Korean man/woman, [youth나이]-year-old ([실제나이]-year-old)
   - 복장: 구체적인 옷차림 (예: 검은색 운동복, 편안한 요가복 등)
   - 표정: 감정이 드러나는 표정 (예: 집중된 표정, 따뜻한 미소, 걱정스러운 표정 등)
   - 동작: 구체적인 행동 (예: 요가 매트를 들고 있다, 손목을 살펴보고 있다 등)
   - 화면 위치 및 행동: 화면 어디에 위치해 있고 무엇을 하고 있는지 (예: 화면 중앙에서 요가 매트를 옮기고 있다, 왼쪽에서 손목을 살펴보고 있다 등)

3. **캐릭터 2** (등장하는 두 번째 캐릭터가 있는 경우):
   - Korean man/woman, [youth나이]-year-old ([실제나이]-year-old)
   - 복장: 구체적인 옷차림
   - 표정: 감정이 드러나는 표정
   - 동작: 구체적인 행동
   - 화면 위치 및 행동: 화면 어디에 위치해 있고 무엇을 하고 있는지

**매우 중요: 나이 표현**
- 절대로 "youthful 27-year-old appearance" 같은 고정 표현을 사용하지 마세요.
- 각 캐릭터의 실제 나이와 youth age를 위의 등장인물 정보에서 확인하여 사용하세요.
- **형식: "[youth나이]-year-old ([실제나이]-year-old)" - Youth age를 기본 표현으로 사용하고, 실제 나이는 괄호 안에 넣으세요.**
- 예시: "Korean man, 27-year-old (35-year-old), ..." 또는 "Korean woman, 25-year-old (28-year-old), ..."
- **중요**: 이미지 생성 시 youth age가 우선 적용되므로, youth age를 기본 표현으로 사용하세요.

**추가 규칙**:
- 인물의 외모는 위의 이미지 프롬프트 참고 정보를 기반으로 일관되게 유지
- 한국인 명시: "Korean man/woman" 명시
- 카메라 각도: 위에서 아래, 옆에서 앞, 옆에서 뒤, 초상화, 옆모습, 대각선 옆모습, 전신샷, 액션

**반드시 다음 JSON 형식으로만 응답하세요. 다른 설명은 포함하지 마세요:**

```json
{{
  "scenes": [
    {{
      "scene_number": 1,
      "title": "헬스장 데스크에서의 만남",
      "image_prompt": "Yoga studio interior with reception desk, potted plants, wooden floor, bright natural lighting. Korean man (Seong-min), 27-year-old (35-year-old), wearing black athletic wear, focused determined expression, carrying heavy yoga mats across studio, positioned in center of frame moving mats. Korean woman (Ji-eun), 25-year-old (28-year-old), wearing comfortable yoga attire with wrist support band, warm bright smile, standing in background watching gratefully, positioned in right side of frame near doorway."
    }},
    {{
      "scene_number": 2,
      "title": "손목 부상 확인",
      "image_prompt": "Yoga studio interior with wooden floor, mirrors on walls, soft warm studio lighting. Korean man (Seong-min), 27-year-old (35-year-old), wearing black athletic wear, gentle caring expression, gently examining Korean woman's wrist with care, positioned on left side of frame in close-up. Korean woman (Ji-eun), 25-year-old (28-year-old), wearing comfortable yoga attire with wrist support band, grateful and trusting expression, standing close to Korean man, positioned on right side of frame, both facing each other."
    }},
    ...
    {{
      "scene_number": 10,
      "title": "한글 제목",
      "image_prompt": "[배경 정보: 장소, 물건, 바닥, 조명]. Korean man/woman, [youth나이]-year-old ([실제나이]-year-old), [복장], [표정], [동작], [화면 위치 및 행동]. Korean man/woman, [youth나이]-year-old ([실제나이]-year-old), [복장], [표정], [동작], [화면 위치 및 행동]."
    }}
  ]
}}
```"""

        try:
            response = self.llm.call(user_prompt, system_prompt)
            if response:
                from utils.json_utils import extract_json_from_text, safe_json_loads
                json_text = extract_json_from_text(response)
                data = safe_json_loads(json_text)
                if data:
                    return data.get('scenes', [])
        except Exception as e:
            print(f"장면 생성 오류 (챕터 {chapter_num}): {e}")

        return None

    def generate_image_prompts(self, character: Dict, synopsis: Dict, visual_age: int) -> Optional[Dict]:
        """
        캐릭터 이미지 프롬프트 7종류 생성 (JSON 구조)

        Args:
            character: 캐릭터 데이터
            synopsis: 시놉시스 데이터
            visual_age: 비주얼 나이 (실제 나이보다 젊게)

        Returns:
            생성된 프롬프트 딕셔너리 또는 None
        """
        char_name = character.get('name', '알 수 없음')
        synopsis_text = synopsis.get('synopsis', '') or synopsis.get('full_story', '')

        # 캐릭터 정보 수집
        syn_char = {}
        for sc in synopsis.get('characters', []):
            if sc.get('name') == char_name:
                syn_char = sc
                break

        # 나이 추출: 캐릭터 객체 우선, 없으면 시놉시스에서 가져오기
        char_age_raw = character.get('age') or syn_char.get('age', '')
        if not char_age_raw:
            char_age_raw = 35  # 기본값
        
        # 문자열인 경우 정수로 변환
        if isinstance(char_age_raw, str):
            try:
                char_age = int(char_age_raw)
            except:
                char_age = 35
        else:
            char_age = int(char_age_raw) if char_age_raw else 35
        
        # 비주얼 나이 계산 (나이대별 차감 규칙, 최소 25세)
        # 60세 이상: 20세 차감, 50세 이상: 15세 차감, 40세 이상: 10세 차감, 30세 이상: 7세 차감
        if char_age >= 60:
            age_deduction = 20
        elif char_age >= 50:
            age_deduction = 15
        elif char_age >= 40:
            age_deduction = 10
        elif char_age >= 30:
            age_deduction = 7
        else:
            # 30세 미만은 최소값 적용
            age_deduction = 0
        calculated_visual_age = max(25, char_age - age_deduction)
        
        # 파라미터로 받은 visual_age가 있으면 사용, 없으면 계산한 값 사용
        # 단, 파라미터로 받은 값이 잘못 계산되었을 수 있으므로 항상 내부 계산값을 사용
        final_visual_age = calculated_visual_age
        
        # 디버깅: 각 캐릭터의 나이 정보 출력
        print(f"[이미지 프롬프트 생성] 캐릭터: {char_name}, 실제 나이: {char_age}세, 차감: {age_deduction}세, Youth age: {final_visual_age}세")
        
        char_occupation = syn_char.get('occupation', '') or character.get('occupation', '')
        char_role = syn_char.get('role', '') or character.get('role', '')
        char_appearance_text = syn_char.get('appearance', '') or character.get('appearance_text', '')
        char_personality_text = syn_char.get('personality', '') or character.get('personality', '')

        char_appearance = character.get('appearance', {})
        char_visual_ref = character.get('visual_reference', '')

        system_prompt = """당신은 이미지 생성을 위한 전문 프롬프트 엔지니어입니다.
주어진 인물 정보를 바탕으로 동일한 인물의 동일성을 반드시 유지하며 7가지 다른 스타일의 상세한 이미지 생성 프롬프트를 영어로 작성해주세요.

**중요 원칙**:
1. 이미지 프롬프트는 반드시 JSON 구조(character, clothing, pose, background, situation, combined)로 작성해야 합니다.
2. 모든 키워드는 영어로 작성해야 합니다.
3. 각 등장인물마다 별도의 JSON 구조를 문자열로 포함시켜야 합니다.
4. 반드시 유효한 JSON 형식으로만 출력하고, 추가 설명이나 마크다운은 포함하지 마세요.
5. 한국인은 60대면 15~20살 어린 모습으로 이미지 프롬프트 작성
6. 멋진 모습 중심으로 작성
7. 인물 정보(character)는 고정하고, 동작(pose), 옷(clothing), 배경(background), 상황(situation)은 쉽게 변경 가능하도록 JSON 구조로 구분

**JSON 구조 형식**:
각 등장인물마다 다음과 같은 JSON 구조로 작성:
{
  "character": "인물의 고정된 외모 특징 (나이, 체형, 얼굴, 헤어 등) - 영어로 작성",
  "clothing": "의상 및 스타일 (옷 종류, 색상, 액세서리 등) - 영어로 작성",
  "pose": "포즈 및 표정 (서 있는, 앉은, 표정, 시선 등) - 영어로 작성",
  "background": "배경 설정 (실내/실외, 장소, 조명 등) - 영어로 작성",
  "situation": "상황 및 분위기 (로맨틱, 드라마틱, 일상적 등) - 영어로 작성",
  "combined": "위의 모든 요소를 쉼표와 줄바꿈(\\n)으로 구분하여 합친 최종 프롬프트. 각 요소(character, clothing, pose, background, situation)는 줄바꿈으로 구분하고, 각 요소 내부는 쉼표로 구분"
}

**나이 표현 규칙**:
- 반드시 youth age를 먼저 표시하고, 실제 나이를 괄호 안에 표시해야 합니다
- 형식: "Korean man/woman, [youth나이]-year-old ([실제나이]-year-old), ..."
- 예시: "Korean man, 27-year-old (35-year-old), ..."
- Youth age는 건강하고 젊어보이고 세련된 외모를 표현하기 위한 나이입니다."""

        user_prompt = f"""다음 인물에 대한 상세 정보를 바탕으로 동일한 인물의 동일성을 유지하며 7가지 이미지 생성 프롬프트를 JSON 구조로 작성해주세요:

**중요: 이 캐릭터의 정보만 사용하세요. 다른 캐릭터의 정보를 혼용하지 마세요.**

## 시놉시스 정보
{synopsis_text[:500] if synopsis_text else '정보 없음'}

## 인물 상세 정보
**캐릭터 이름: {char_name}**
**이 캐릭터의 실제 나이: {char_age}세 (반드시 프롬프트에 포함해야 함)**
**이 캐릭터의 Youth age: {final_visual_age}세 (건강하고 젊어보이고 세련된 외모를 표현하기 위한 나이)**

**매우 중요**: 
- 이 캐릭터({char_name})의 실제 나이는 {char_age}세입니다.
- 이 캐릭터의 youth age는 {final_visual_age}세입니다.
- 절대로 다른 캐릭터의 나이를 사용하지 마세요.
- 모든 프롬프트에서 반드시 "{final_visual_age}-year-old ({char_age}-year-old)" 형식을 사용하세요.
- Youth age를 기본 표현으로 사용하고, 실제 나이는 괄호 안에 넣으세요.

- 직업: {char_occupation}
- 역할: {char_role}
- 외모 (시놉시스): {char_appearance_text}
- 외모 (상세):
  - 얼굴: {char_appearance.get('face', '정보 없음')}
  - 체형: {char_appearance.get('body', '정보 없음')}
  - 복장 스타일: {char_appearance.get('clothing', '정보 없음')}
  - 특징: {', '.join(char_appearance.get('features', [])) if char_appearance.get('features') else '정보 없음'}
- 성격: {char_personality_text}
- 시각적 참고: {char_visual_ref}

**7가지 스타일**:
1. **Full Body Shot** (전신샷)(자연스러운 배경)
2. **옆모습 전신샷** (Side Profile Full Body Shot)(자연스러운 배경)
3. **대각선 옆모습 전신샷** (Diagonal Side Profile Full Body Shot)(자연스러운 배경)
4. **Portrait** (초상화)(자연스러운 배경)
5. **Side Profile** (초상화 옆모습)(자연스러운 배경)
6. **Action** (액션)
7. **Natural Background** (자연스러운 배경)

**반드시 다음 JSON 형식으로만 응답하세요. 다른 설명이나 마크다운은 포함하지 마세요:**

{{
  "character_name": "{char_name}",
  "prompts": {{
    "full_body_shot": "{{\\"character\\": \\"Korean man/woman, {final_visual_age}-year-old ({char_age}-year-old), [외모 특징 상세 설명 - 영어]\\", \\"clothing\\": \\"[의상 및 스타일 - 영어]\\", \\"pose\\": \\"[포즈 및 표정 - 영어]\\", \\"background\\": \\"[배경 설정 - 영어]\\", \\"situation\\": \\"[상황 및 분위기 - 영어]\\", \\"combined\\": \\"[character 내용]\\\\n[clothing 내용]\\\\n[pose 내용]\\\\n[background 내용]\\\\n[situation 내용]\\"}}",
    "side_profile_full_body_shot": "{{\\"character\\": \\"Korean man/woman, {final_visual_age}-year-old ({char_age}-year-old), [외모 특징 상세 설명 - 영어]\\", \\"clothing\\": \\"[의상 및 스타일 - 영어]\\", \\"pose\\": \\"[포즈 및 표정 - 영어]\\", \\"background\\": \\"[배경 설정 - 영어]\\", \\"situation\\": \\"[상황 및 분위기 - 영어]\\", \\"combined\\": \\"[character 내용]\\\\n[clothing 내용]\\\\n[pose 내용]\\\\n[background 내용]\\\\n[situation 내용]\\"}}",
    "diagonal_side_profile_full_body_shot": "{{\\"character\\": \\"Korean man/woman, {final_visual_age}-year-old ({char_age}-year-old), [외모 특징 상세 설명 - 영어]\\", \\"clothing\\": \\"[의상 및 스타일 - 영어]\\", \\"pose\\": \\"[포즈 및 표정 - 영어]\\", \\"background\\": \\"[배경 설정 - 영어]\\", \\"situation\\": \\"[상황 및 분위기 - 영어]\\", \\"combined\\": \\"[character 내용]\\\\n[clothing 내용]\\\\n[pose 내용]\\\\n[background 내용]\\\\n[situation 내용]\\"}}",
    "portrait": "{{\\"character\\": \\"Korean man/woman, {final_visual_age}-year-old ({char_age}-year-old), [외모 특징 상세 설명 - 영어]\\", \\"clothing\\": \\"[의상 및 스타일 - 영어]\\", \\"pose\\": \\"[포즈 및 표정 - 영어]\\", \\"background\\": \\"[배경 설정 - 영어]\\", \\"situation\\": \\"[상황 및 분위기 - 영어]\\", \\"combined\\": \\"[character 내용]\\\\n[clothing 내용]\\\\n[pose 내용]\\\\n[background 내용]\\\\n[situation 내용]\\"}}",
    "side_profile": "{{\\"character\\": \\"Korean man/woman, {final_visual_age}-year-old ({char_age}-year-old), [외모 특징 상세 설명 - 영어]\\", \\"clothing\\": \\"[의상 및 스타일 - 영어]\\", \\"pose\\": \\"[포즈 및 표정 - 영어]\\", \\"background\\": \\"[배경 설정 - 영어]\\", \\"situation\\": \\"[상황 및 분위기 - 영어]\\", \\"combined\\": \\"[character 내용]\\\\n[clothing 내용]\\\\n[pose 내용]\\\\n[background 내용]\\\\n[situation 내용]\\"}}",
    "action": "{{\\"character\\": \\"Korean man/woman, {final_visual_age}-year-old ({char_age}-year-old), [외모 특징 상세 설명 - 영어]\\", \\"clothing\\": \\"[의상 및 스타일 - 영어]\\", \\"pose\\": \\"[포즈 및 표정 - 영어]\\", \\"background\\": \\"[배경 설정 - 영어]\\", \\"situation\\": \\"[상황 및 분위기 - 영어]\\", \\"combined\\": \\"[character 내용]\\\\n[clothing 내용]\\\\n[pose 내용]\\\\n[background 내용]\\\\n[situation 내용]\\"}}",
    "natural_background": "{{\\"character\\": \\"Korean man/woman, {final_visual_age}-year-old ({char_age}-year-old), [외모 특징 상세 설명 - 영어]\\", \\"clothing\\": \\"[의상 및 스타일 - 영어]\\", \\"pose\\": \\"[포즈 및 표정 - 영어]\\", \\"background\\": \\"[배경 설정 - 영어]\\", \\"situation\\": \\"[상황 및 분위기 - 영어]\\", \\"combined\\": \\"[character 내용]\\\\n[clothing 내용]\\\\n[pose 내용]\\\\n[background 내용]\\\\n[situation 내용]\\"}}"
  }}
}}"""

        try:
            response = self.llm.call(user_prompt, system_prompt)
            if response:
                from utils.json_utils import extract_json_from_text, safe_json_loads
                json_text = extract_json_from_text(response)
                data = safe_json_loads(json_text)
                if data:
                    return data.get('prompts', {})
        except Exception as e:
            print(f"이미지 프롬프트 생성 오류 ({char_name}): {e}")

        return None
