# ComfyUI Regional Prompt 설정 가이드

다중 캐릭터 이미지 생성을 위한 Regional Prompt 상세 설정 방법

## 필수 커스텀 노드

### 설치 방법

ComfyUI Manager에서 설치하거나 수동 설치:

```bash
# ComfyUI 폴더의 custom_nodes로 이동
cd ComfyUI/custom_nodes

# 1. Attention Couple (cgem156) - 권장
git clone https://github.com/laksjdjf/cgem156-ComfyUI

# 2. Comfy Couple - 간편 버전
git clone https://github.com/Danand/ComfyUI-ComfyCouple

# 3. Impact Pack - 얼굴 보정용
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack

# pandas 오류 시
pip install pandas
```

### 노드별 특징

| 노드 | 장점 | 단점 |
|------|------|------|
| AttentionCouple | 정밀한 영역 제어, 3인 이상 가능 | 설정 복잡 |
| ComfyCouple | 간단한 좌/우 분할 | 2인 제한 |
| Dense Diffusion | 세밀한 마스크 | 토큰 수 민감 |

## 마스크 설정

### 기본 2인 구성

```
┌─────────────────────────────────┐
│                                 │
│   캐릭터 A    │   캐릭터 B      │
│   (0-55%)    │   (45-100%)     │
│              │                  │
│         오버랩 영역             │
│         (45-55%)               │
└─────────────────────────────────┘
```

**ComfyUI 설정:**
- Mask 1: 검은색(캐릭터 A) 왼쪽 55%
- Mask 2: 검은색(캐릭터 B) 오른쪽 55%
- 중앙 10% 오버랩

### 상호작용별 오버랩 비율

| 상호작용 유형 | 오버랩 비율 | 설명 |
|-------------|-----------|------|
| 대화 (거리 있음) | 10-20% | 캐릭터 분리 유지 |
| 손잡기 | 20-30% | 손 부분만 겹침 |
| 어깨동무 | 30-40% | 옆면 겹침 |
| 포옹 | 40-50% | 상체 상당 부분 겹침 |
| 밀착 | 50%+ | 거의 전체 겹침 |

### 3인 이상 구성

```
3인 가로 배열:
┌─────────┬─────────┬─────────┐
│    A    │    B    │    C    │
│ (0-40%) │(30-70%) │(60-100%)│
└─────────┴─────────┴─────────┘

3인 삼각 배열 (한 명 뒤):
┌─────────────────────────────┐
│         C (뒷줄)             │
│        (25-75%)             │
├─────────────┬───────────────┤
│      A      │       B       │
│   (0-55%)   │   (45-100%)   │
└─────────────┴───────────────┘
```

## Attention Couple 노드 설정

### 기본 연결 구조

```
[Load Checkpoint] 
    ↓
[CLIP Text Encode - Main Prompt]
    ↓
[AttentionCouple]
    ├── cond_1 ← [CLIP Text Encode - 캐릭터 A]
    ├── cond_2 ← [CLIP Text Encode - 캐릭터 B]
    ├── mask_1 ← [Load Image - 마스크 A]
    └── mask_2 ← [Load Image - 마스크 B]
    ↓
[KSampler]
```

### 파라미터 설정

```yaml
AttentionCouple:
  mode: "Attention"  # 또는 "Latent"
  
# 각 Conditioning 연결:
  cond_1:
    weight: 1.0  # 캐릭터 A 강도
    start_at: 0.0
    end_at: 1.0
    
  cond_2:
    weight: 1.0  # 캐릭터 B 강도
    start_at: 0.0
    end_at: 1.0
```

### 마스크 준비

**권장 방법: ComfyUI 내 Mask Editor 사용**

1. `Load Image` 노드에 빈 흰색 이미지 로드
2. 노드 우클릭 → `Open in MaskEditor`
3. 검은색으로 캐릭터 영역 칠하기
4. 저장하여 마스크로 사용

**Photoshop/GIMP 사용 시:**
- 이미지 크기: 생성할 이미지와 동일
- 캐릭터 영역: 검은색 (#000000)
- 나머지 영역: 흰색 (#FFFFFF)
- 저장 형식: PNG (투명도 없이)

## Comfy Couple 노드 설정 (간편)

### 기본 구조

```
[Load Checkpoint]
    ↓
[Comfy Couple]
    ├── positive_1: "캐릭터 A 프롬프트"
    ├── positive_2: "캐릭터 B 프롬프트"
    ├── negative: "공통 네거티브"
    └── direction: "horizontal"  # 또는 "vertical"
    ↓
[KSampler]
```

### 파라미터

```yaml
ComfyCouple:
  direction: "horizontal"  # 좌우 분할
  # 또는 "vertical"  # 상하 분할
  
  background_weight: 0.5  # 배경 영향력
  character_weight: 1.0   # 캐릭터 영향력
```

## 상호작용 시 특수 설정

### 포옹 장면

```yaml
# 마스크 설정
mask_a: 0% ~ 60%   # 왼쪽 캐릭터 (오른쪽으로 확장)
mask_b: 40% ~ 100% # 오른쪽 캐릭터 (왼쪽으로 확장)
overlap: 40-60% 영역

# 프롬프트 팁
main_prompt: "2women embracing, hug, close contact"
char_a: "hugging, arms around [상대방 위치]"
char_b: "being hugged, face against shoulder"

# KSampler 설정
steps: 30-40  # 복잡한 상호작용은 더 많은 스텝
cfg_scale: 7-8
```

### 손잡기 장면

```yaml
# 마스크 설정
mask_a: 0% ~ 55%
mask_b: 45% ~ 100%
overlap: 45-55% (손 부분만)

# 프롬프트 팁
main_prompt: "couple holding hands, romantic"
char_a: "hand extended toward [방향], fingers intertwined"
char_b: "holding partner hand, tender gesture"

# 손 품질 향상
negative_prompt += ", bad hands, extra fingers, fused fingers"
```

### 대화/마주보기 장면

```yaml
# 마스크 설정 (거리 있음)
mask_a: 0% ~ 45%
mask_b: 55% ~ 100%
overlap: 최소화 또는 없음

# 프롬프트 팁
main_prompt: "2women conversation, facing each other"
char_a: "looking at [오른쪽/상대방], speaking gesture"
char_b: "looking at [왼쪽/상대방], listening expression"

# 얼굴 방향 명시
char_a: "..., face turned right, profile view"
char_b: "..., face turned left, three-quarter view"
```

## 문제 해결

### 캐릭터 특성이 섞일 때

```
원인: 오버랩 영역에서 프롬프트 혼합
해결:
1. 오버랩 비율 줄이기 (20% 이하)
2. 각 캐릭터 특성을 더 강하게 명시
3. 구분되는 색상/의상 사용
4. img2img로 영역별 보정
```

### 손/팔이 이상할 때

```
원인: 상호작용 영역의 해부학적 혼란
해결:
1. ControlNet OpenPose 추가
2. 네거티브에 손 관련 키워드 강화
3. 2단계 생성 후 Inpaint로 수정
4. Face/Hand Detailer 노드 사용
```

### 나이가 균일하지 않을 때

```
원인: 각 영역에서 나이 인식 다름
해결:
1. 메인 프롬프트에도 나이 관련 키워드 포함
2. 모든 영역에 나이 명시
3. Face Detailer로 얼굴별 프롬프트 적용
```

### "tensor size mismatch" 오류

```
원인: Dense Diffusion 사용 시 토큰 수 불일치
해결:
1. 각 영역 프롬프트 길이 비슷하게 조정
2. 임베딩(embedding) 사용 줄이기
3. cgem156 대신 ComfyCouple 사용
```

## 권장 워크플로우

### 기본 2인 캐릭터 워크플로우

```
1. Load Checkpoint (realistic 모델)
2. Load/Create Masks (캐릭터별)
3. CLIP Text Encode × 3 (메인, 캐릭터A, 캐릭터B)
4. AttentionCouple 노드
5. KSampler (steps: 30, cfg: 7)
6. VAE Decode
7. (선택) Face Detailer
8. Save Image
```

### 상호작용 장면 권장 워크플로우

```
1단계: 기본 구도 생성
- 낮은 디테일로 포즈/구도 확정
- Steps: 15-20

2단계: Regional Prompt로 디테일
- 1단계 결과를 img2img 입력
- Regional Prompt 적용
- Denoise: 0.5-0.6

3단계: 얼굴 보정
- Face Detailer 적용
- 각 얼굴에 나이별 프롬프트

4단계: (필요시) 손 보정
- Inpaint로 손 영역 선택
- 손 전용 프롬프트로 재생성
```

## 추천 모델 & 설정

### Checkpoint 모델

```
# 실사 한국인용
- Realistic Vision V5.1
- ChilloutMix
- majicMIX realistic

# 설정
VAE: vae-ft-mse-840000-ema-pruned
Sampler: DPM++ 2M Karras
Steps: 25-35
CFG Scale: 7-8
```

### LoRA (선택사항)

```
# 한국인 얼굴 개선
- Korean Doll Likeness
- KoreanStyle

# 나이 조절
- Age Slider embeddings
- AS-MidAged, AS-Elderly
```
