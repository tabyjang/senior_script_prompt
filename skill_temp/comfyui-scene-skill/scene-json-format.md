# Scene JSON Standard Format

Standard JSON structure for scene prompts with character reference system.

---

## Complete JSON Structure

```json
{
  "metadata": {
    "work_title": "Work_English_Title",
    "act": "act1",
    "act_title": "Act_Title",
    "chapter": 1,
    "chapter_title": "Chapter_Title",
    "created_at": "YYYY-MM-DD",
    "total_scenes": 10
  },
  "chapter_info": {
    "main_location": "Primary Location",
    "time_period": "daytime",
    "characters": ["Character_A", "Character_B"],
    "main_emotion": "emotion keywords"
  },
  "scenes": []
}
```

---

## Scene Object Structure

```json
{
  "scene_id": "s01",
  "scene_name": "scene_name_english",
  "description": "Brief scene description for reference",
  "beat_type": "confrontation",
  "shot_type": "medium shot",
  "camera_angle": "eye level",
  "location": "Specific Location",
  "time": "daytime",
  "lighting": "dramatic side lighting",
  "mood": "tense uncomfortable atmosphere",
  "main_prompt": "[Full 7-section main prompt]",
  "characters": [],
  "regional_settings": {
    "overlap": "none",
    "overlap_ratio": 0
  },
  "output": {
    "folder": "scenes/act1/ch01/s01_scene_name",
    "filename_prefix": "act1_ch01_s01"
  }
}
```

---

## Character Object Structure

```json
{
  "character_ref": "char_01",
  "name": "Character Name",
  "region": "0-50%",
  "position": "left",
  "expression": "angry fierce expression, furrowed brows",
  "action": "pointing finger accusingly, confrontational stance",
  "direction": "facing right",
  "full_prompt": "[Generated at runtime: base_prompt + expression + action + direction]"
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `character_ref` | ✅ | ID from character JSON (e.g., "char_01") |
| `name` | ✅ | Character name for reference |
| `region` | ✅ | Percentage range for regional prompt |
| `position` | ✅ | "left", "right", "center" |
| `expression` | ✅ | Scene-specific facial expression |
| `action` | ✅ | Scene-specific pose/action |
| `direction` | ✅ | "facing left", "facing right", "facing camera" |
| `full_prompt` | Generated | Merged prompt (base + scene specifics) |

---

## Beat Type Values

| Value | Description |
|-------|-------------|
| `inciting` | Event occurrence, story trigger |
| `confrontation` | Conflict, argument, clash |
| `revelation` | Truth exposed, secret revealed |
| `turning_point` | Decision moment, realization |
| `reconciliation` | Forgiveness, reunion, healing |
| `climax` | Peak tension, final showdown |
| `resolution` | Peaceful ending, conclusion |
| `transition` | Scene/location change |
| `daily` | Everyday moment, calm scene |
| `flashback` | Memory, dream sequence |

---

## Shot Type Values

| Value | Description |
|-------|-------------|
| `extreme close-up` | Detail shot (eyes, hands) |
| `close-up` | Face only |
| `medium close-up` | Head and shoulders |
| `medium shot` | Waist up |
| `medium wide shot` | Full body with space |
| `wide shot` | Full environment |
| `extreme wide shot` | Landscape/establishing |

---

## Camera Angle Values

| Value | Description |
|-------|-------------|
| `eye level` | Neutral, standard |
| `low angle` | Looking up (power) |
| `high angle` | Looking down (vulnerability) |
| `dutch angle` | Tilted (tension) |
| `over the shoulder` | Behind one character |
| `bird's eye view` | Directly above |

---

## Regional Settings

### For 2 Characters (No Overlap)
```json
{
  "overlap": "none",
  "overlap_ratio": 0
}
```
- Character A: `"region": "0-50%"`
- Character B: `"region": "50-100%"`

### For 2 Characters (Conversation - 10% Overlap)
```json
{
  "overlap": "slight",
  "overlap_ratio": 0.1
}
```
- Character A: `"region": "0-55%"`
- Character B: `"region": "45-100%"`

### For 2 Characters (Holding Hands - 25% Overlap)
```json
{
  "overlap": "moderate",
  "overlap_ratio": 0.25
}
```
- Character A: `"region": "0-55%"`
- Character B: `"region": "45-100%"`

### For 2 Characters (Embrace - 40% Overlap)
```json
{
  "overlap": "significant",
  "overlap_ratio": 0.4
}
```
- Character A: `"region": "0-60%"`
- Character B: `"region": "40-100%"`

### For 3 Characters
```json
{
  "overlap": "slight",
  "overlap_ratio": 0.1
}
```
- Character A: `"region": "0-40%"`
- Character B: `"region": "30-70%"`
- Character C: `"region": "60-100%"`

---

## Complete Example: Confrontation Scene

```json
{
  "metadata": {
    "work_title": "5_Billion_Inheritance",
    "act": "act1",
    "act_title": "Hell_Begins",
    "chapter": 3,
    "chapter_title": "First_Clash",
    "created_at": "2026-01-04",
    "total_scenes": 12
  },
  "chapter_info": {
    "main_location": "Living Room",
    "time_period": "afternoon",
    "characters": ["Kim_Soonja", "Yoon_Mira"],
    "main_emotion": "tension, hostility, power struggle"
  },
  "scenes": [
    {
      "scene_id": "s05",
      "scene_name": "living_room_confrontation",
      "description": "Soonja confronts Mira about her intentions",
      "beat_type": "confrontation",
      "shot_type": "medium shot",
      "camera_angle": "eye level",
      "location": "elegant living room interior",
      "time": "afternoon",
      "lighting": "dramatic side lighting",
      "mood": "tense hostile atmosphere",
      "main_prompt": "masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, tense confrontation scene, heated argument between women, 2women facing each other, elegant living room interior, dramatic side lighting, tense hostile atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration",
      "characters": [
        {
          "character_ref": "char_01",
          "name": "Kim_Soonja",
          "region": "0-50%",
          "position": "left",
          "expression": "angry fierce expression, furrowed brows, cold demanding eyes",
          "action": "pointing finger accusingly, confrontational stance, tense shoulders",
          "direction": "facing right",
          "full_prompt": "49 year old Korean woman, round gentle face, warm brown eyes, shoulder-length black hair with subtle gray, simple gold earrings, angry fierce expression, furrowed brows, cold demanding eyes, pointing finger accusingly, confrontational stance, tense shoulders, facing right"
        },
        {
          "character_ref": "char_02",
          "name": "Yoon_Mira",
          "region": "50-100%",
          "position": "right",
          "expression": "defiant smirk, calculating eyes, false innocence",
          "action": "arms crossed, confident posture, chin raised",
          "direction": "facing left",
          "full_prompt": "33 year old Korean woman, sharp attractive features, sleek black hair, pearl earrings, designer dress, defiant smirk, calculating eyes, false innocence, arms crossed, confident posture, chin raised, facing left"
        }
      ],
      "regional_settings": {
        "overlap": "none",
        "overlap_ratio": 0
      },
      "output": {
        "folder": "scenes/act1/ch03/s05_confrontation",
        "filename_prefix": "act1_ch03_s05"
      }
    }
  ]
}
```

---

## Complete Example: Reconciliation Scene

```json
{
  "scene_id": "s12",
  "scene_name": "mother_daughter_embrace",
  "description": "Soonja and her daughter reconcile after years of misunderstanding",
  "beat_type": "reconciliation",
  "shot_type": "medium shot",
  "camera_angle": "eye level",
  "location": "warm living room interior",
  "time": "evening",
  "lighting": "warm soft golden lighting",
  "mood": "emotional touching heartwarming atmosphere",
  "main_prompt": "masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, emotional reconciliation scene, tearful mother daughter embrace, 2women hugging emotionally, warm living room interior, warm soft golden lighting, emotional touching heartwarming atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration",
  "characters": [
    {
      "character_ref": "char_01",
      "name": "Kim_Soonja",
      "region": "0-60%",
      "position": "left",
      "expression": "tearful relieved smile, eyes glistening with happy tears",
      "action": "embracing daughter tightly, arms wrapped around, eyes closed",
      "direction": "facing right",
      "full_prompt": "49 year old Korean woman, round gentle face, warm brown eyes, shoulder-length black hair with subtle gray, simple gold earrings, tearful relieved smile, eyes glistening with happy tears, embracing daughter tightly, arms wrapped around, eyes closed, facing right"
    },
    {
      "character_ref": "char_05",
      "name": "Kim_Jiyoung",
      "region": "40-100%",
      "position": "right",
      "expression": "crying emotional expression, tears streaming down",
      "action": "being hugged, face pressed against mother shoulder, trembling",
      "direction": "facing left",
      "full_prompt": "20 year old Korean woman, soft features, long black hair, casual sweater, crying emotional expression, tears streaming down, being hugged, face pressed against mother shoulder, trembling, facing left"
    }
  ],
  "regional_settings": {
    "overlap": "significant",
    "overlap_ratio": 0.4
  },
  "output": {
    "folder": "scenes/act3/ch12/s12_reconciliation",
    "filename_prefix": "act3_ch12_s12"
  }
}
```

---

## n8n Integration Notes

### Loading Character Base Prompt

```javascript
// In n8n Function node
const characterData = await loadJSON(`characters/${scene.characters[0].character_ref}.json`);
const basePrompt = characterData.base_prompt;

// Merge with scene-specific elements
const fullPrompt = `${basePrompt}, ${char.expression}, ${char.action}, ${char.direction}`;
```

### Output Path Generation

```javascript
// Dynamic path for ComfyUI SaveImage
const outputPath = `${metadata.work_title}/${scene.output.folder}/${scene.output.filename_prefix}`;
```
