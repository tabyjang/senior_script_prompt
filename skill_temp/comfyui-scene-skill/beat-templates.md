# Beat Type Templates

Complete prompt templates for each story beat type.
All values use FIXED keys from SKILL.md.

---

## Beat Type Quick Reference

| beat_type | shot_type | camera_angle | lighting |
|-----------|-----------|--------------|----------|
| `inciting` | `wide_shot` | `eye_level` | `soft_natural_lighting` |
| `confrontation` | `medium_shot` | `eye_level` | `dramatic_side_lighting` |
| `revelation` | `close_up` | `eye_level` | `chiaroscuro_lighting` |
| `turning_point` | `close_up` | `eye_level` | `chiaroscuro_lighting` |
| `reconciliation` | `medium_shot` | `eye_level` | `warm_golden_hour` |
| `climax` | `medium_shot` | `dutch_angle` | `dramatic_side_lighting` |
| `resolution` | `wide_shot` | `eye_level` | `warm_golden_hour` |
| `transition` | `wide_shot` | `eye_level` | `soft_natural_lighting` |
| `daily` | `medium_shot` | `eye_level` | `soft_natural_lighting` |
| `flashback` | `medium_shot` | `eye_level` | `soft_diffused_lighting` |

---

## inciting (Event Occurrence)

Introduces a new situation or event that starts the conflict.

### Fixed Settings
```json
{
  "beat_type": "inciting",
  "shot_type": "wide_shot",
  "camera_angle": "eye_level",
  "lighting": "soft_natural_lighting",
  "mood": "tense anticipation atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, wide shot, eye level, inciting scene, {key_action}, {people_count}, {location}, soft natural lighting, tense anticipation atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Example
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, wide shot, eye level, inciting scene, mysterious woman entering funeral hall, 1woman, Korean funeral hall entrance exterior, soft natural lighting, tense anticipation atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

---

## confrontation (Conflict/Clash)

Direct conflict between characters.

### Fixed Settings
```json
{
  "beat_type": "confrontation",
  "shot_type": "medium_shot",
  "camera_angle": "eye_level",
  "lighting": "dramatic_side_lighting",
  "mood": "hostile tense atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, confrontation scene, {key_action}, {people_count}, {location}, dramatic side lighting, hostile tense atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Example
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, confrontation scene, heated argument between women, 2women, elegant living room interior, dramatic side lighting, hostile tense atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Character Templates

**Aggressor (left):**
```json
{
  "position": "left",
  "region_start": 0,
  "region_end": 50,
  "expression": "angry fierce expression, furrowed brows",
  "action": "pointing finger accusingly, confrontational stance",
  "direction": "facing_right"
}
```

**Defender (right):**
```json
{
  "position": "right",
  "region_start": 50,
  "region_end": 100,
  "expression": "defensive expression, tense face",
  "action": "arms crossed, stepped back posture",
  "direction": "facing_left"
}
```

---

## revelation (Truth Exposed)

Moment when truth is revealed or secret is exposed.

### Fixed Settings
```json
{
  "beat_type": "revelation",
  "shot_type": "close_up",
  "camera_angle": "eye_level",
  "lighting": "chiaroscuro_lighting",
  "mood": "shocking climactic atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, close up, eye level, revelation scene, {key_action}, {people_count}, {location}, chiaroscuro lighting, shocking climactic atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Example
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, close up, eye level, revelation scene, will being read shocking inheritance, 3people, lawyer office interior, chiaroscuro lighting, shocking climactic atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Character Templates

**Revealer:**
```json
{
  "expression": "triumphant vindicated expression",
  "action": "holding documents, confident posture",
  "direction": "facing_camera"
}
```

**Shocked:**
```json
{
  "expression": "wide eyes shocked expression, pale face",
  "action": "frozen in disbelief, devastated look",
  "direction": "facing_camera"
}
```

---

## turning_point (Decision Moment)

Character makes crucial decision or realizes something important.

### Fixed Settings
```json
{
  "beat_type": "turning_point",
  "shot_type": "close_up",
  "camera_angle": "eye_level",
  "lighting": "chiaroscuro_lighting",
  "mood": "determined transformative atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, close up, eye level, turning point scene, {key_action}, 1woman, {location}, chiaroscuro lighting, determined transformative atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Example
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, close up, eye level, turning point scene, woman making determined choice, 1woman, dimly lit room interior, chiaroscuro lighting, determined transformative atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Character Template
```json
{
  "expression": "determined resolute expression, steely gaze",
  "action": "jaw set firmly, inner strength visible",
  "direction": "facing_camera"
}
```

---

## reconciliation (Forgiveness/Reunion)

Characters forgive each other or reunite emotionally.

### Fixed Settings
```json
{
  "beat_type": "reconciliation",
  "shot_type": "medium_shot",
  "camera_angle": "eye_level",
  "lighting": "warm_golden_hour",
  "mood": "touching heartwarming atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, reconciliation scene, {key_action}, {people_count}, {location}, warm golden hour lighting, touching heartwarming atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Example
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, reconciliation scene, tearful mother daughter embrace, 2women, warm living room interior, warm golden hour lighting, touching heartwarming atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Character Templates (Embrace)

**Initiator (left):**
```json
{
  "position": "left",
  "region_start": 0,
  "region_end": 60,
  "expression": "tearful relieved smile, eyes glistening",
  "action": "embracing tightly, arms wrapped around",
  "direction": "facing_right"
}
```

**Receiver (right):**
```json
{
  "position": "right",
  "region_start": 40,
  "region_end": 100,
  "expression": "emotional crying expression, tears streaming",
  "action": "being hugged, face against shoulder",
  "direction": "facing_left"
}
```

### Regional Settings for Embrace
```json
{
  "overlap": "significant",
  "overlap_ratio": 0.4
}
```

---

## climax (Peak Conflict)

Highest point of dramatic tension.

### Fixed Settings
```json
{
  "beat_type": "climax",
  "shot_type": "medium_shot",
  "camera_angle": "dutch_angle",
  "lighting": "dramatic_side_lighting",
  "mood": "intense peak tension atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, dutch angle, climax scene, {key_action}, {people_count}, {location}, dramatic side lighting, intense peak tension atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Example
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, dutch angle, climax scene, final showdown between rivals, 2women, courtroom interior, dramatic side lighting, intense peak tension atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

---

## resolution (Peaceful Ending)

Story concludes, peace is restored.

### Fixed Settings
```json
{
  "beat_type": "resolution",
  "shot_type": "wide_shot",
  "camera_angle": "eye_level",
  "lighting": "warm_golden_hour",
  "mood": "peaceful hopeful atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, wide shot, eye level, resolution scene, {key_action}, {people_count}, {location}, warm golden hour lighting, peaceful hopeful atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Example
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, wide shot, eye level, resolution scene, new chapter beginning peaceful life, 1woman, beautiful countryside house exterior, warm golden hour lighting, peaceful hopeful atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

---

## transition (Scene Change)

Moving between locations or time periods.

### Fixed Settings
```json
{
  "beat_type": "transition",
  "shot_type": "wide_shot",
  "camera_angle": "eye_level",
  "lighting": "soft_natural_lighting",
  "mood": "transitional neutral atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, wide shot, eye level, transition scene, {key_action}, {people_count}, {location}, soft natural lighting, transitional neutral atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

---

## daily (Everyday Scene)

Normal daily activities, calm moments.

### Fixed Settings
```json
{
  "beat_type": "daily",
  "shot_type": "medium_shot",
  "camera_angle": "eye_level",
  "lighting": "soft_natural_lighting",
  "mood": "calm comfortable atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, daily scene, {key_action}, {people_count}, {location}, soft natural lighting, calm comfortable atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Example
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, daily scene, peaceful morning coffee moment, 1woman, cozy kitchen interior, soft natural lighting, calm comfortable atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

---

## flashback (Memory Scene)

Past memory or dream sequence.

### Fixed Settings
```json
{
  "beat_type": "flashback",
  "shot_type": "medium_shot",
  "camera_angle": "eye_level",
  "lighting": "soft_diffused_lighting",
  "mood": "nostalgic ethereal atmosphere"
}
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, flashback scene, dreamy soft focus, {key_action}, {people_count}, {location}, soft diffused lighting, nostalgic ethereal atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Example
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, flashback scene, dreamy soft focus, wedding day first meeting, 2women, 1980s Korean wedding hall interior, soft diffused lighting, nostalgic ethereal atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Note for Flashback Characters
- Use younger prompt_age: (actual_age_at_that_time - 15)
- Example: Character was 24 at wedding → prompt_age = 24 (no -15 for young characters)
- For characters under 30 at flashback time, use actual age in prompt

---

## Expression Keywords Reference

### Positive Emotions
| Emotion | Expression Keywords |
|---------|-------------------|
| Happy | `bright joyful smile, sparkling eyes` |
| Relieved | `relieved expression, weight lifted` |
| Loving | `tender loving gaze, warm soft smile` |
| Triumphant | `victorious proud expression, satisfied smile` |
| Hopeful | `hopeful optimistic expression, bright eyes` |

### Negative Emotions
| Emotion | Expression Keywords |
|---------|-------------------|
| Angry | `angry fierce expression, furrowed brows` |
| Sad | `sorrowful tearful expression, glistening eyes` |
| Scared | `fearful wide eyes, trembling expression` |
| Shocked | `shocked wide eyes, pale face, frozen` |
| Hurt | `pained wounded expression, betrayed look` |

### Neutral/Complex Emotions
| Emotion | Expression Keywords |
|---------|-------------------|
| Determined | `resolute determined expression, steely gaze` |
| Contemplative | `thoughtful pensive expression, distant gaze` |
| Suspicious | `suspicious narrowed eyes, wary expression` |
| Conflicted | `conflicted torn expression, uncertain eyes` |
| Resigned | `resigned accepting expression, weary eyes` |

---

## Action Keywords Reference

### Standing Actions
| Action | Keywords |
|--------|----------|
| Neutral | `standing straight, hands at sides` |
| Defensive | `arms crossed, guarded stance` |
| Aggressive | `pointing finger, confrontational stance` |
| Confident | `hands on hips, confident posture` |
| Vulnerable | `hugging self, protective posture` |

### Seated Actions
| Action | Keywords |
|--------|----------|
| Relaxed | `sitting comfortably, relaxed posture` |
| Tense | `sitting stiffly, tense shoulders` |
| Engaged | `leaning forward, attentive posture` |
| Withdrawn | `hunched over, withdrawn posture` |

### Interactive Actions
| Action | Keywords |
|--------|----------|
| Embracing | `arms wrapped around, holding tightly` |
| Holding hands | `hands clasped together, fingers intertwined` |
| Comforting | `hand on shoulder, comforting gesture` |
| Pushing away | `hands pushing forward, rejecting gesture` |

