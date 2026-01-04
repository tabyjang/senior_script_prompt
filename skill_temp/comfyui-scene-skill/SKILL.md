# ComfyUI Scene Prompt Generation Skill

Generate scene prompts for senior story YouTube content.
Combines cinematic shot techniques with story beat structure.
Ensures character consistency by referencing character JSON data.

---

## Required Workflow

### Phase 1: Character JSON Creation (One-time)
```
Input:  Script or character descriptions
Output: characters.json (all characters for the work)
Skill:  comfyui-character-prompt
```

### Phase 2: Scene Prompt Generation (Per Chapter)
```
Input:  1. characters.json (from Phase 1)
        2. Chapter script (one chapter only)
Output: chapter_XX_scenes.json
Skill:  comfyui-scene-prompt (this skill)
```

### Why This Workflow?
- Context limit management (chapter-by-chapter)
- Character consistency (same base_prompt across all scenes)
- Accurate scene extraction (direct script reference)

---

## Absolute Rules

### 1. No Text/Letter - Always Include at End
**Every main_prompt must end with:**
```
no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### 2. No Separate Negative Prompt
- Do NOT create negative prompts
- All restrictions go in positive prompt with `no [element]` format

### 3. Age Rule: "Actual Age - 15"
| Actual Age | Prompt Age | Expression |
|------------|------------|------------|
| 50 | 35 | `35 year old Korean woman` |
| 60 | 45 | `45 year old Korean woman` |
| 65 | 50 | `50 year old Korean woman` |
| 70 | 55 | `55 year old Korean woman` |

### 4. Character Consistency
**Always read base_prompt from character JSON and merge with scene-specific elements.**

---

## Fixed Output Format

### File Naming
```
characters.json          # Character master data
chapter_01_scenes.json   # Chapter 1 scenes
chapter_02_scenes.json   # Chapter 2 scenes
...
```

---

## CHARACTER JSON FORMAT (Input)

**File: characters.json**

All keys are FIXED. Do not change key names.

```json
{
  "metadata": {
    "work_title": "string",
    "created_at": "YYYY-MM-DD",
    "total_characters": 0
  },
  "characters": [
    {
      "character_id": "char_01",
      "name_kr": "string",
      "name_en": "string",
      "actual_age": 0,
      "prompt_age": 0,
      "gender": "female|male",
      "role": "protagonist|antagonist|supporting",
      "base_prompt": "string",
      "fixed_traits": "string"
    }
  ]
}
```

### Character Object Keys (FIXED)

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `character_id` | string | ✅ | Unique ID: char_01, char_02... |
| `name_kr` | string | ✅ | Korean name |
| `name_en` | string | ✅ | English name (no spaces, use underscore) |
| `actual_age` | integer | ✅ | Real character age |
| `prompt_age` | integer | ✅ | actual_age - 15 |
| `gender` | string | ✅ | "female" or "male" |
| `role` | string | ✅ | "protagonist", "antagonist", "supporting" |
| `base_prompt` | string | ✅ | Fixed appearance prompt (English) |
| `fixed_traits` | string | ✅ | Key visual traits summary |

---

## SCENE JSON FORMAT (Output)

**File: chapter_XX_scenes.json**

All keys are FIXED. Do not change key names.

```json
{
  "metadata": {
    "work_title": "string",
    "act": "string",
    "act_title": "string",
    "chapter": 0,
    "chapter_title": "string",
    "created_at": "YYYY-MM-DD",
    "total_scenes": 0
  },
  "chapter_info": {
    "main_location": "string",
    "time_period": "string",
    "character_ids": ["char_01", "char_02"],
    "main_emotion": "string"
  },
  "scenes": []
}
```

### Metadata Keys (FIXED)

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `work_title` | string | ✅ | Work title in English |
| `act` | string | ✅ | Act identifier: act1, act2, act3 |
| `act_title` | string | ✅ | Act title in English |
| `chapter` | integer | ✅ | Chapter number |
| `chapter_title` | string | ✅ | Chapter title in English |
| `created_at` | string | ✅ | Creation date YYYY-MM-DD |
| `total_scenes` | integer | ✅ | Number of scenes in this chapter |

### Chapter Info Keys (FIXED)

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `main_location` | string | ✅ | Primary location |
| `time_period` | string | ✅ | daytime, evening, night, dawn |
| `character_ids` | array | ✅ | List of character_id appearing |
| `main_emotion` | string | ✅ | Dominant emotional tone |

---

## SCENE OBJECT FORMAT (FIXED)

```json
{
  "scene_id": "s01",
  "scene_name": "string",
  "description": "string",
  "beat_type": "string",
  "shot_type": "string",
  "camera_angle": "string",
  "location": "string",
  "time": "string",
  "lighting": "string",
  "mood": "string",
  "main_prompt": "string",
  "characters": [],
  "regional_settings": {
    "overlap": "string",
    "overlap_ratio": 0.0
  },
  "output": {
    "folder": "string",
    "filename_prefix": "string"
  }
}
```

### Scene Object Keys (FIXED)

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `scene_id` | string | ✅ | Scene ID: s01, s02, s03... |
| `scene_name` | string | ✅ | English name with underscore |
| `description` | string | ✅ | Brief description (can be Korean) |
| `beat_type` | string | ✅ | Story beat type (see Beat Types) |
| `shot_type` | string | ✅ | Camera shot type (see Shot Types) |
| `camera_angle` | string | ✅ | Camera angle (see Angles) |
| `location` | string | ✅ | Specific location in English |
| `time` | string | ✅ | daytime, evening, night, dawn, flashback |
| `lighting` | string | ✅ | Lighting technique in English |
| `mood` | string | ✅ | Atmosphere keywords in English |
| `main_prompt` | string | ✅ | Complete 7-section prompt |
| `characters` | array | ✅ | Character objects in scene |
| `regional_settings` | object | ✅ | Overlap configuration |
| `output` | object | ✅ | Output path configuration |

---

## CHARACTER IN SCENE FORMAT (FIXED)

```json
{
  "character_id": "char_01",
  "name": "string",
  "region_start": 0,
  "region_end": 50,
  "position": "string",
  "expression": "string",
  "action": "string",
  "direction": "string",
  "full_prompt": "string"
}
```

### Character in Scene Keys (FIXED)

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `character_id` | string | ✅ | Reference to characters.json |
| `name` | string | ✅ | Character name for readability |
| `region_start` | integer | ✅ | Region start percentage (0-100) |
| `region_end` | integer | ✅ | Region end percentage (0-100) |
| `position` | string | ✅ | "left", "center", "right" |
| `expression` | string | ✅ | Facial expression keywords |
| `action` | string | ✅ | Pose/action keywords |
| `direction` | string | ✅ | "facing_left", "facing_right", "facing_camera" |
| `full_prompt` | string | ✅ | Merged: base_prompt + expression + action + direction |

---

## REGIONAL SETTINGS FORMAT (FIXED)

```json
{
  "overlap": "string",
  "overlap_ratio": 0.0
}
```

| Key | Type | Values |
|-----|------|--------|
| `overlap` | string | "none", "slight", "moderate", "significant" |
| `overlap_ratio` | float | 0.0, 0.1, 0.25, 0.4 |

### Overlap Values

| overlap | overlap_ratio | Use Case |
|---------|---------------|----------|
| "none" | 0.0 | Confrontation, separate |
| "slight" | 0.1 | Conversation |
| "moderate" | 0.25 | Holding hands |
| "significant" | 0.4 | Embrace, hug |

---

## OUTPUT FORMAT (FIXED)

```json
{
  "folder": "string",
  "filename_prefix": "string"
}
```

| Key | Type | Format |
|-----|------|--------|
| `folder` | string | scenes/{act}/ch{XX}/s{XX}_{scene_name} |
| `filename_prefix` | string | {act}_ch{XX}_s{XX} |

---

## FIXED VALUES

### Quality Tags (Section 1)
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus
```

### No Elements Tags (Section 7)
```
no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

### Beat Types (FIXED VALUES)
| Value | Description |
|-------|-------------|
| `inciting` | Event triggers story |
| `confrontation` | Conflict/clash |
| `revelation` | Truth exposed |
| `turning_point` | Decision moment |
| `reconciliation` | Forgiveness/reunion |
| `climax` | Peak tension |
| `resolution` | Peaceful ending |
| `transition` | Scene change |
| `daily` | Everyday moment |
| `flashback` | Memory/past |

### Shot Types (FIXED VALUES)
| Value | Description |
|-------|-------------|
| `extreme_close_up` | Detail (eyes, hands) |
| `close_up` | Face only |
| `medium_close_up` | Head and shoulders |
| `medium_shot` | Waist up |
| `medium_wide_shot` | Full body with space |
| `wide_shot` | Full environment |
| `extreme_wide_shot` | Landscape |

### Camera Angles (FIXED VALUES)
| Value | Description |
|-------|-------------|
| `eye_level` | Neutral |
| `low_angle` | Power/dominance |
| `high_angle` | Vulnerability |
| `dutch_angle` | Tension |
| `over_the_shoulder` | Dialogue |
| `birds_eye_view` | Overview |

### Lighting (FIXED VALUES)
| Value | Description |
|-------|-------------|
| `soft_natural_lighting` | Calm, daily |
| `warm_golden_hour` | Romantic |
| `dramatic_side_lighting` | Tension |
| `chiaroscuro_lighting` | Mystery |
| `high_key_lighting` | Happy |
| `low_key_lighting` | Dark |
| `backlit_silhouette` | Dramatic |
| `soft_diffused_lighting` | Dreamy |

### Direction (FIXED VALUES)
| Value | Description |
|-------|-------------|
| `facing_left` | Looking left |
| `facing_right` | Looking right |
| `facing_camera` | Looking at viewer |

### Position (FIXED VALUES)
| Value | Description |
|-------|-------------|
| `left` | Left side of frame |
| `center` | Center of frame |
| `right` | Right side of frame |

---

## MAIN PROMPT STRUCTURE (7 Sections)

```
[1.Quality] [2.Shot/Angle] [3.Beat/Action] [4.People] [5.Location] [6.Lighting/Mood] [7.NoElements]
```

### Template
```
masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, {shot_type}, {camera_angle}, {beat_type} scene, {key_action}, {people_count}, {location}, {lighting}, {mood}, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration
```

---

## CHARACTER PROMPT STRUCTURE (4 Sections)

```
[1.Base Prompt] [2.Expression] [3.Action] [4.Direction]
```

### Merge Formula
```
full_prompt = base_prompt + ", " + expression + ", " + action + ", " + direction
```

---

## COMPLETE EXAMPLE

### Input: characters.json (excerpt)

```json
{
  "metadata": {
    "work_title": "5_Billion_Inheritance",
    "created_at": "2026-01-04",
    "total_characters": 2
  },
  "characters": [
    {
      "character_id": "char_01",
      "name_kr": "김순자",
      "name_en": "Kim_Soonja",
      "actual_age": 64,
      "prompt_age": 49,
      "gender": "female",
      "role": "protagonist",
      "base_prompt": "49 year old Korean woman, round gentle face, warm brown eyes, shoulder-length black hair with subtle gray, simple gold earrings",
      "fixed_traits": "round gentle face, warm brown eyes, black hair with gray, gold earrings"
    },
    {
      "character_id": "char_02",
      "name_kr": "박영숙",
      "name_en": "Park_Youngsook",
      "actual_age": 67,
      "prompt_age": 52,
      "gender": "female",
      "role": "antagonist",
      "base_prompt": "52 year old Korean woman, sharp angular face, cold piercing eyes, short permed gray hair, expensive pearl jewelry",
      "fixed_traits": "sharp angular face, cold eyes, short permed gray hair, pearl jewelry"
    }
  ]
}
```

### Output: chapter_01_scenes.json

```json
{
  "metadata": {
    "work_title": "5_Billion_Inheritance",
    "act": "act1",
    "act_title": "Hell_Begins",
    "chapter": 1,
    "chapter_title": "Enemys_Funeral",
    "created_at": "2026-01-04",
    "total_scenes": 8
  },
  "chapter_info": {
    "main_location": "Funeral Hall",
    "time_period": "daytime",
    "character_ids": ["char_01", "char_02"],
    "main_emotion": "bitterness, complexity, tension"
  },
  "scenes": [
    {
      "scene_id": "s01",
      "scene_name": "funeral_hall_arrival",
      "description": "순자가 장례식장에 도착하는 장면",
      "beat_type": "inciting",
      "shot_type": "wide_shot",
      "camera_angle": "eye_level",
      "location": "funeral hall entrance exterior",
      "time": "daytime",
      "lighting": "soft_natural_lighting",
      "mood": "solemn heavy atmosphere",
      "main_prompt": "masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, wide shot, eye level, inciting scene, woman arriving at funeral, 1woman, funeral hall entrance exterior, soft natural lighting, solemn heavy atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration",
      "characters": [
        {
          "character_id": "char_01",
          "name": "Kim_Soonja",
          "region_start": 0,
          "region_end": 100,
          "position": "center",
          "expression": "complicated mixed emotions, hesitant look",
          "action": "walking slowly, cautious steps",
          "direction": "facing_camera",
          "full_prompt": "49 year old Korean woman, round gentle face, warm brown eyes, shoulder-length black hair with subtle gray, simple gold earrings, complicated mixed emotions, hesitant look, walking slowly, cautious steps, facing camera"
        }
      ],
      "regional_settings": {
        "overlap": "none",
        "overlap_ratio": 0.0
      },
      "output": {
        "folder": "scenes/act1/ch01/s01_funeral_hall_arrival",
        "filename_prefix": "act1_ch01_s01"
      }
    },
    {
      "scene_id": "s02",
      "scene_name": "portrait_gazing",
      "description": "순자가 영숙의 영정 사진을 바라보는 장면",
      "beat_type": "daily",
      "shot_type": "medium_shot",
      "camera_angle": "eye_level",
      "location": "funeral hall memorial room interior",
      "time": "daytime",
      "lighting": "soft_diffused_lighting",
      "mood": "contemplative somber atmosphere",
      "main_prompt": "masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, daily scene, woman gazing at funeral portrait, 1woman, funeral hall memorial room interior, soft diffused lighting, contemplative somber atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration",
      "characters": [
        {
          "character_id": "char_01",
          "name": "Kim_Soonja",
          "region_start": 0,
          "region_end": 100,
          "position": "center",
          "expression": "complex reminiscent expression, distant gaze",
          "action": "standing still, looking at portrait",
          "direction": "facing_right",
          "full_prompt": "49 year old Korean woman, round gentle face, warm brown eyes, shoulder-length black hair with subtle gray, simple gold earrings, complex reminiscent expression, distant gaze, standing still, looking at portrait, facing right"
        }
      ],
      "regional_settings": {
        "overlap": "none",
        "overlap_ratio": 0.0
      },
      "output": {
        "folder": "scenes/act1/ch01/s02_portrait_gazing",
        "filename_prefix": "act1_ch01_s02"
      }
    },
    {
      "scene_id": "s03",
      "scene_name": "wedding_flashback",
      "description": "40년 전 결혼식에서 영숙을 처음 만난 회상",
      "beat_type": "flashback",
      "shot_type": "medium_shot",
      "camera_angle": "eye_level",
      "location": "1980s Korean wedding hall interior",
      "time": "flashback",
      "lighting": "soft_diffused_lighting",
      "mood": "dreamy nostalgic sepia atmosphere",
      "main_prompt": "masterpiece, best quality, photorealistic, 8k uhd, highly detailed, sharp focus, medium shot, eye level, flashback scene, two women meeting at wedding, 2women, 1980s Korean wedding hall interior, soft diffused lighting, dreamy nostalgic sepia atmosphere, no text, no letters, no words, no writing, no captions, no subtitles, no watermark, no signature, no logo, no anime, no cartoon, no 3d render, no illustration",
      "characters": [
        {
          "character_id": "char_01",
          "name": "Kim_Soonja_young",
          "region_start": 0,
          "region_end": 50,
          "position": "left",
          "expression": "innocent hopeful expression, nervous smile",
          "action": "standing in wedding dress, hands clasped",
          "direction": "facing_right",
          "full_prompt": "24 year old Korean woman, round gentle face, warm brown eyes, long black hair in bridal updo, wedding dress, innocent hopeful expression, nervous smile, standing in wedding dress, hands clasped, facing right"
        },
        {
          "character_id": "char_02",
          "name": "Park_Youngsook_young",
          "region_start": 50,
          "region_end": 100,
          "position": "right",
          "expression": "sharp critical expression, dismissive look",
          "action": "arms crossed, judging posture",
          "direction": "facing_left",
          "full_prompt": "27 year old Korean woman, sharp angular face, cold piercing eyes, neat black hair, elegant hanbok, sharp critical expression, dismissive look, arms crossed, judging posture, facing left"
        }
      ],
      "regional_settings": {
        "overlap": "none",
        "overlap_ratio": 0.0
      },
      "output": {
        "folder": "scenes/act1/ch01/s03_wedding_flashback",
        "filename_prefix": "act1_ch01_s03"
      }
    }
  ]
}
```

---

## CHECKLIST

### Before Generation
```
□ characters.json uploaded?
□ Chapter script uploaded?
□ Character base_prompt values confirmed?
```

### During Generation
```
□ All keys exactly match FIXED format?
□ main_prompt has all 7 sections?
□ full_prompt = base_prompt + expression + action + direction?
□ region_start and region_end are integers (0-100)?
□ overlap_ratio matches overlap type?
□ All enum values from FIXED VALUES list?
```

### After Generation
```
□ JSON is valid (no syntax errors)?
□ All character_id references exist in characters.json?
□ scene_id is sequential (s01, s02, s03...)?
□ output folder/filename follows naming convention?
```
