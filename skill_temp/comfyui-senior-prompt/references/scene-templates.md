# 장면별 프롬프트 템플릿

시니어 스토리에서 자주 사용되는 장면 유형별 완성 프롬프트 템플릿

**중요: 포지티브 프롬프트만 생성한다. 네거티브 프롬프트는 생성하지 않는다.**
(네거티브는 ComfyUI 워크플로우에서 고정값으로 설정됨)

## 감동 장면

### 화해의 포옹

```yaml
scene: emotional_reconciliation
characters: 2 (mother 65, daughter 35)
emotion: touching, tearful

main_prompt: |
  masterpiece, best quality, photorealistic, cinematic lighting,
  2women emotional embrace, tearful reunion,
  warm indoor lighting, living room setting,
  heartwarming family moment, emotional scene

character_a_prompt: |  # 어머니 (왼쪽 0-60%)
  50 year old Korean woman, tears of joy streaming down,
  gray-streaked hair slightly disheveled from emotion,
  wearing simple home clothes, cardigan,
  embracing daughter tightly, eyes closed, relieved smile,
  arms wrapped around daughter protectively

character_b_prompt: |  # 딸 (오른쪽 40-100%)
  20 year old Korean woman, crying with emotion,
  long black hair, face pressed against mother shoulder,
  casual clothes, trembling with emotion,
  hugging mother desperately, tears visible

settings:
  aspect_ratio: 16:9
  overlap_ratio: 0.4
  recommended_steps: 30
  cfg_scale: 7
```

### 임종 장면

```yaml
scene: deathbed_farewell
characters: 2 (dying elder 75, family member)
emotion: sorrowful, peaceful

main_prompt: |
  masterpiece, best quality, photorealistic,
  hospital room scene, soft diffused lighting,
  emotional farewell moment, bittersweet atmosphere,
  warm but melancholic mood

character_a_prompt: |  # 환자 (침대 위)
  60 year old Korean woman, peaceful expression,
  white hair on pillow, pale but serene face,
  hospital gown, lying in bed,
  weak but loving smile, holding hand

character_b_prompt: |  # 가족 (침대 옆)
  50 year old Korean woman, tearful expression,
  holding elderly hand gently,
  sitting beside bed, leaning close,
  emotional face, trying to be strong

settings:
  aspect_ratio: 16:9
  lighting: soft hospital lighting
  mood: somber but peaceful
```

## 로맨틱 장면

### 첫사랑 재회

```yaml
scene: first_love_reunion
characters: 2 (both around 65)
emotion: nostalgic, romantic, bittersweet

main_prompt: |
  masterpiece, best quality, photorealistic,
  elderly couple reuniting, romantic nostalgic atmosphere,
  park setting, autumn season, golden hour lighting,
  emotional moment, destiny reunion

character_a_prompt: |  # 여성 (왼쪽)
  50 year old Korean woman, emotional recognition,
  elegant silver hair, tears forming in eyes,
  wearing autumn coat, scarf,
  hand reaching toward face, disbelief expression

character_b_prompt: |  # 남성 (오른쪽)
  52 year old Korean man, tender recognition,
  gray hair, aged but familiar face,
  neat casual coat, gentle smile,
  stepping forward, reaching out hand

settings:
  aspect_ratio: 16:9
  time: golden hour
  season: autumn with falling leaves
```

### 황혼 프로포즈

```yaml
scene: twilight_proposal
characters: 2 (couple in late 60s)
emotion: romantic, touching, hopeful

main_prompt: |
  masterpiece, best quality, photorealistic,
  elderly couple romantic moment, sunset beach,
  proposal scene, golden hour lighting,
  romantic atmosphere, emotional moment

character_a_prompt: |  # 남성 (무릎 꿇음)
  53 year old Korean man, sincere expression,
  gray hair, wearing neat casual clothes,
  kneeling on one knee, holding ring box,
  looking up with hope and love

character_b_prompt: |  # 여성 (서있음)
  50 year old Korean woman, surprised joyful expression,
  silver hair blowing in breeze, elegant dress,
  hands covering mouth in surprise,
  tears of joy forming, touched expression

settings:
  aspect_ratio: 16:9
  background: sunset beach, golden sky
  lighting: warm golden hour
```

## 갈등 장면

### 가족 대립

```yaml
scene: family_confrontation
characters: 2 (mother-in-law 65, daughter-in-law 35)
emotion: tense, frustrated

main_prompt: |
  masterpiece, best quality, photorealistic,
  2women tense confrontation, living room scene,
  dramatic lighting, emotional tension,
  family conflict moment

character_a_prompt: |  # 시어머니 (왼쪽)
  50 year old Korean woman, stern expression,
  neat gray hair in traditional style,
  wearing hanbok or traditional attire,
  arms crossed, disapproving posture,
  cold judging eyes, tight lips

character_b_prompt: |  # 며느리 (오른쪽)
  20 year old Korean woman, defensive posture,
  modern hairstyle, contemporary clothes,
  frustrated expression, looking away,
  tense shoulders, controlled anger

settings:
  aspect_ratio: 16:9
  overlap_ratio: 0.2  # 낮은 오버랩 - 거리감 표현
  lighting: dramatic side lighting
```

### 형제 유산 분쟁

```yaml
scene: sibling_inheritance_dispute
characters: 2-3 siblings (50s-60s)
emotion: angry, hurt, betrayed

main_prompt: |
  masterpiece, best quality, photorealistic,
  3women heated argument, formal room setting,
  inheritance dispute scene, tense atmosphere,
  dramatic lighting, emotional confrontation

character_a_prompt: |  # 큰언니 (왼쪽)
  48 year old Korean woman, angry expression,
  neat hair, formal attire,
  pointing accusingly, raised voice posture

character_b_prompt: |  # 둘째 (중앙)
  45 year old Korean woman, hurt expression,
  crying while arguing, documents in hand,
  defensive posture, tearful eyes

character_c_prompt: |  # 막내 (오른쪽)
  42 year old Korean woman, mediation attempt,
  worried expression, hands raised calmingly,
  trying to intervene, stressed face

settings:
  aspect_ratio: 16:9
  mask_regions: 3 equal parts
  lighting: harsh overhead lighting
```

## 일상 장면

### 친구들 수다

```yaml
scene: friends_chatting
characters: 2-3 friends (all 60s)
emotion: warm, lively, comfortable

main_prompt: |
  masterpiece, best quality, photorealistic,
  elderly Korean women friends chatting,
  cozy cafe setting, warm afternoon light,
  comfortable friendship scene, lively conversation

character_a_prompt: |
  45 year old Korean woman, animated talker,
  short permed hair, colorful blouse,
  gesturing enthusiastically, wide smile,
  leaning forward engaged in story

character_b_prompt: |
  45 year old Korean woman, attentive listener,
  straight gray-streaked hair, cardigan,
  laughing at story, coffee cup in hand,
  nodding with amusement

settings:
  aspect_ratio: 16:9
  background: bright Korean cafe interior
  mood: warm, cheerful
```

### 손주와 함께

```yaml
scene: with_grandchild
characters: 2 (grandmother 65, grandchild 7)
emotion: loving, warm, playful

main_prompt: |
  masterpiece, best quality, photorealistic,
  grandmother and grandchild bonding,
  park setting, warm sunlight,
  heartwarming family moment, pure joy

character_a_prompt: |  # 할머니
  50 year old Korean woman, adoring expression,
  neat gray hair, comfortable outdoor clothes,
  crouching to child level, arms open,
  beaming smile, eyes full of love

character_b_prompt: |  # 손주
  7 year old Korean child, excited expression,
  running toward grandmother, arms outstretched,
  school uniform or casual clothes,
  pure happy smile, energetic pose

settings:
  aspect_ratio: 16:9
  background: sunny park with playground
  lighting: warm natural sunlight
```

## 극적 장면

### 진실 폭로

```yaml
scene: truth_revelation
characters: 3+ (revealer, accused, witnesses)
emotion: shock, vindication, shame

main_prompt: |
  masterpiece, best quality, photorealistic,
  dramatic revelation scene, family gathering,
  tense atmosphere, multiple emotional reactions,
  dramatic lighting, pivotal moment

character_a_prompt: |  # 진실 폭로자
  50 year old Korean woman, determined expression,
  holding evidence documents or phone,
  standing firm, righteous anger,
  finally speaking truth posture

character_b_prompt: |  # 폭로 대상
  45 year old Korean woman, caught expression,
  panic in eyes, pale face,
  shrinking back, guilty posture,
  exposed and ashamed look

character_c_prompt: |  # 목격자들
  shocked expressions, covering mouths,
  disbelief on faces, gasping reactions

settings:
  aspect_ratio: 16:9
  lighting: dramatic spotlight effect
  mood: climactic, justice moment
```

### 복수 성공

```yaml
scene: revenge_success
characters: 2 (victor, defeated)
emotion: triumphant, humiliated

main_prompt: |
  masterpiece, best quality, photorealistic,
  triumph over adversary scene,
  formal setting like courtroom or office,
  dramatic lighting, power shift moment

character_a_prompt: |  # 승자
  50 year old Korean woman, dignified triumph,
  elegant attire, composed expression,
  standing tall, subtle satisfied smile,
  confidence radiating, vindicated posture

character_b_prompt: |  # 패자
  40 year old Korean woman, defeated expression,
  disheveled appearance, slumped posture,
  avoiding eye contact, humiliated face,
  surrounded by disapproving onlookers

settings:
  aspect_ratio: 16:9
  lighting: bright on winner, shadow on loser
  mood: satisfying justice
```

## 특수 장면

### 꿈/회상 시퀀스

```yaml
scene: dream_flashback
characters: same person young and old
emotion: nostalgic, bittersweet

main_prompt: |
  masterpiece, best quality, photorealistic,
  dream sequence, soft dreamy lighting,
  memory visualization, ethereal atmosphere,
  past and present blend, nostalgic mood

# 현재의 나 (선명)
current_prompt: |
  50 year old Korean woman, sleeping peacefully,
  or gazing into distance, nostalgic expression

# 과거의 나 (몽환적)
past_prompt: |
  20 year old Korean woman, soft focus effect,
  glowing ethereal appearance, young beauty,
  happy innocent expression, dreamlike quality

settings:
  style: soft focus, dreamy filter
  color_grade: warm sepia tones
  special_effect: gentle glow, vignette
```

### 영정 사진 / 제사 장면

```yaml
scene: memorial_scene
characters: photo + mourners
emotion: respectful, sorrowful, remembering

main_prompt: |
  masterpiece, best quality, photorealistic,
  Korean memorial service scene, solemn atmosphere,
  traditional setting, respectful mood,
  family remembrance moment

memorial_photo_prompt: |
  framed portrait photo of deceased,
  55 year old Korean person, peaceful smile,
  formal attire, dignified expression,
  surrounded by flowers and candles

mourners_prompt: |
  family members in mourning clothes,
  respectful bowing posture, tears,
  traditional Korean funeral attire,
  somber expressions, grief

settings:
  aspect_ratio: 4:3 or 16:9
  lighting: soft candlelight atmosphere
  background: traditional Korean memorial setup
```
