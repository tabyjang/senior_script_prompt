"""
TTS Service
Multi-engine Text-to-Speech service.
Supports: Chatterbox, Edge TTS, gTTS, OpenAI TTS, ElevenLabs
"""

import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from abc import ABC, abstractmethod


class BaseTTSEngine(ABC):
    """Base class for TTS engines."""

    name: str = "Base"
    description: str = ""
    requires_internet: bool = True
    requires_api_key: bool = False
    supports_voice_cloning: bool = False  # 음성 복제 지원 여부

    @abstractmethod
    def get_voices(self) -> Dict[str, str]:
        """Get available voices. Returns {display_name: voice_id}"""
        pass

    @abstractmethod
    def generate(self, text: str, output_path: str, voice: str,
                 rate: int = 0, volume: int = 0, pitch: int = 0,
                 speaker_wav: str = None) -> bool:
        """Generate speech from text.
        Args:
            speaker_wav: 참조 음성 파일 경로 (음성 복제용)
        """
        pass


class EdgeTTSEngine(BaseTTSEngine):
    """Microsoft Edge TTS (Cloud, Free)"""

    name = "Edge TTS"
    description = "Microsoft Edge 클라우드 TTS (무료, 인터넷 필요)"
    requires_internet = True

    # 실제 사용 가능한 한국어 음성 (2024년 기준)
    KOREAN_VOICES = {
        "선희 (여성)": "ko-KR-SunHiNeural",
        "인준 (남성)": "ko-KR-InJoonNeural",
        "현수 (다국어)": "ko-KR-HyunsuMultilingualNeural",
    }

    # 영어 음성도 추가 (다양한 선택을 위해)
    ENGLISH_VOICES = {
        "Jenny (미국 여성)": "en-US-JennyNeural",
        "Guy (미국 남성)": "en-US-GuyNeural",
        "Aria (미국 여성)": "en-US-AriaNeural",
        "Davis (미국 남성)": "en-US-DavisNeural",
        "Sonia (영국 여성)": "en-GB-SoniaNeural",
        "Ryan (영국 남성)": "en-GB-RyanNeural",
    }

    # 일본어 음성
    JAPANESE_VOICES = {
        "나나미 (일본 여성)": "ja-JP-NanamiNeural",
        "켄지 (일본 남성)": "ja-JP-KeitaNeural",
    }

    # 중국어 음성
    CHINESE_VOICES = {
        "샤오샤오 (중국 여성)": "zh-CN-XiaoxiaoNeural",
        "윈양 (중국 남성)": "zh-CN-YunyangNeural",
    }

    def __init__(self):
        import edge_tts  # Check availability
        self._edge_tts = edge_tts

    def get_voices(self) -> Dict[str, str]:
        """Get all available voices grouped by language."""
        voices = {}
        # 한국어 우선
        voices.update({f"[한국어] {k}": v for k, v in self.KOREAN_VOICES.items()})
        voices.update({f"[영어] {k}": v for k, v in self.ENGLISH_VOICES.items()})
        voices.update({f"[일본어] {k}": v for k, v in self.JAPANESE_VOICES.items()})
        voices.update({f"[중국어] {k}": v for k, v in self.CHINESE_VOICES.items()})
        return voices

    def generate(self, text: str, output_path: str, voice: str,
                 rate: int = 0, volume: int = 0, pitch: int = 0,
                 speaker_wav: str = None) -> bool:
        try:
            async def _generate():
                communicate = self._edge_tts.Communicate(
                    text, voice,
                    rate=f"{rate:+d}%",
                    volume=f"{volume:+d}%",
                    pitch=f"{pitch:+d}Hz"
                )
                await communicate.save(output_path)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_generate())
            loop.close()
            return True
        except Exception as e:
            print(f"Edge TTS Error: {e}")
            return False


class GTTSEngine(BaseTTSEngine):
    """Google TTS (Cloud, Free)"""

    name = "Google TTS"
    description = "Google 클라우드 TTS (무료, 인터넷 필요)"
    requires_internet = True

    VOICES = {
        "한국어 (기본)": "ko",
        "영어 (미국)": "en",
        "영어 (영국)": "en-uk",
        "일본어": "ja",
        "중국어": "zh-CN",
    }

    def __init__(self):
        from gtts import gTTS  # Check availability
        self._gtts = gTTS

    def get_voices(self) -> Dict[str, str]:
        return self.VOICES.copy()

    def generate(self, text: str, output_path: str, voice: str,
                 rate: int = 0, volume: int = 0, pitch: int = 0,
                 speaker_wav: str = None) -> bool:
        try:
            # gTTS doesn't support rate/volume/pitch directly
            slow = rate < -20
            tts = self._gtts(text=text, lang=voice, slow=slow)
            tts.save(output_path)
            return True
        except Exception as e:
            print(f"gTTS Error: {e}")
            return False


class Pyttsx3Engine(BaseTTSEngine):
    """pyttsx3 - Local Windows SAPI TTS"""

    name = "Windows TTS"
    description = "Windows 로컬 TTS (오프라인, SAPI)"
    requires_internet = False

    def __init__(self):
        import pyttsx3  # Check availability
        self._engine = pyttsx3.init()
        self._voices = {}
        for v in self._engine.getProperty('voices'):
            # Filter Korean voices or show all
            name = v.name
            if 'Korean' in name or 'ko-KR' in v.id or 'ko_KR' in v.id:
                self._voices[f"{name} (한국어)"] = v.id
            elif len(self._voices) < 5:  # Add some other voices
                self._voices[name] = v.id

        # If no Korean voices, add all available
        if not self._voices:
            for v in self._engine.getProperty('voices'):
                self._voices[v.name] = v.id

    def get_voices(self) -> Dict[str, str]:
        return self._voices.copy()

    def generate(self, text: str, output_path: str, voice: str,
                 rate: int = 0, volume: int = 0, pitch: int = 0,
                 speaker_wav: str = None) -> bool:
        try:
            import pyttsx3
            engine = pyttsx3.init()

            # Set voice
            engine.setProperty('voice', voice)

            # Set rate (default ~200, range 50-400)
            base_rate = 200
            new_rate = base_rate + (rate * 2)  # rate -50~+100 -> 100~400
            engine.setProperty('rate', max(50, min(400, new_rate)))

            # Set volume (0.0 to 1.0)
            vol = 0.5 + (volume / 200)  # volume -50~+100 -> 0.25~1.0
            engine.setProperty('volume', max(0.0, min(1.0, vol)))

            # Save to file
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            return True
        except Exception as e:
            print(f"pyttsx3 Error: {e}")
            return False


class OpenAITTSEngine(BaseTTSEngine):
    """OpenAI TTS API"""

    name = "OpenAI TTS"
    description = "OpenAI TTS API (유료, API 키 필요)"
    requires_internet = True
    requires_api_key = True

    VOICES = {
        "Alloy (중성)": "alloy",
        "Echo (남성)": "echo",
        "Fable (영국 남성)": "fable",
        "Onyx (깊은 남성)": "onyx",
        "Nova (여성)": "nova",
        "Shimmer (여성)": "shimmer",
    }

    def __init__(self, api_key: str = None):
        from openai import OpenAI  # Check availability
        import os
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("OpenAI API key required")
        self._client = OpenAI(api_key=self._api_key)

    def get_voices(self) -> Dict[str, str]:
        return self.VOICES.copy()

    def generate(self, text: str, output_path: str, voice: str,
                 rate: int = 0, volume: int = 0, pitch: int = 0,
                 speaker_wav: str = None) -> bool:
        try:
            # Map rate to speed (0.25 to 4.0, default 1.0)
            speed = 1.0 + (rate / 100)  # rate -50~+100 -> 0.5~2.0
            speed = max(0.25, min(4.0, speed))

            response = self._client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )
            response.stream_to_file(output_path)
            return True
        except Exception as e:
            print(f"OpenAI TTS Error: {e}")
            return False


class ElevenLabsTTSEngine(BaseTTSEngine):
    """ElevenLabs TTS - High Quality AI Voice"""

    name = "ElevenLabs"
    description = "ElevenLabs AI 음성 (고품질, API 키 필요)"
    requires_internet = True
    requires_api_key = True

    # 기본 제공 음성
    VOICES = {
        "Rachel (여성, 미국)": "21m00Tcm4TlvDq8ikWAM",
        "Drew (남성, 미국)": "29vD33N1CtxCmqQRPOHJ",
        "Clyde (남성, 미국)": "2EiwWnXFnvU5JabPnv8n",
        "Paul (남성, 미국)": "5Q0t7uMcjvnagumLfvZi",
        "Domi (여성, 미국)": "AZnzlk1XvdvUeBnXmlld",
        "Dave (남성, 영국)": "CYw3kZ02Hs0563khs1Fj",
        "Fin (남성, 아일랜드)": "D38z5RcWu1voky8WS1ja",
        "Sarah (여성, 미국, 부드러움)": "EXAVITQu4vr4xnSDxMaL",
        "Antoni (남성, 미국)": "ErXwobaYiN019PkySvjV",
        "Elli (여성, 미국)": "MF3mGyEYCl7XYWbV9V6O",
        "Josh (남성, 미국, 젊음)": "TxGEqnHWrfWFTfGW9XjX",
        "Arnold (남성, 미국)": "VR6AewLTigWG4xSOukaG",
        "Adam (남성, 미국, 깊은)": "pNInz6obpgDQGcFmaJgB",
        "Sam (남성, 미국)": "yoZ06aMxZJJ28mfd3POQ",
    }

    def __init__(self, api_key: str = None):
        from elevenlabs.client import ElevenLabs
        import os
        self._api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        if not self._api_key:
            raise ValueError("ElevenLabs API key required")
        self._client = ElevenLabs(api_key=self._api_key)

    def get_voices(self) -> Dict[str, str]:
        return self.VOICES.copy()

    def generate(self, text: str, output_path: str, voice: str,
                 rate: int = 0, volume: int = 0, pitch: int = 0,
                 speaker_wav: str = None) -> bool:
        try:
            # ElevenLabs stability/similarity settings
            # rate를 stability에 매핑 (높을수록 안정적)
            stability = 0.5 + (rate / 200)  # -50~+100 -> 0.25~1.0
            stability = max(0.0, min(1.0, stability))

            audio = self._client.generate(
                text=text,
                voice=voice,
                model="eleven_multilingual_v2"  # 다국어 지원 모델
            )

            # Save audio to file
            with open(output_path, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)

            return True
        except Exception as e:
            print(f"ElevenLabs TTS Error: {e}")
            return False


class ChatterboxTTSEngine(BaseTTSEngine):
    """Chatterbox TTS - Local Neural TTS (Resemble AI)"""

    name = "Chatterbox"
    description = "Chatterbox 로컬 AI TTS (오프라인, 23개 언어, 음성복제)"
    requires_internet = False
    supports_voice_cloning = True  # 음성 복제 지원

    # 지원 언어
    LANGUAGES = {
        "[한국어] 기본": "ko",
        "[영어] English": "en",
        "[일본어] 日本語": "ja",
        "[중국어] 中文": "zh",
        "[독일어] Deutsch": "de",
        "[프랑스어] Français": "fr",
        "[스페인어] Español": "es",
        "[이탈리아어] Italiano": "it",
        "[포르투갈어] Português": "pt",
        "[러시아어] Русский": "ru",
    }

    # Conda 환경 Python 경로
    CONDA_PYTHON = r"C:\Users\USER\Miniconda3\envs\chatterbox\python.exe"

    def __init__(self):
        import os
        if not os.path.exists(self.CONDA_PYTHON):
            raise FileNotFoundError(f"Chatterbox environment not found: {self.CONDA_PYTHON}")

    def get_voices(self) -> Dict[str, str]:
        return self.LANGUAGES.copy()

    def generate(self, text: str, output_path: str, voice: str,
                 rate: int = 0, volume: int = 0, pitch: int = 0,
                 speaker_wav: str = None) -> bool:
        import subprocess
        import tempfile
        import os

        try:
            # WAV로 생성 (Chatterbox는 WAV 출력)
            wav_path = output_path.replace('.mp3', '.wav')

            # 텍스트를 별도 파일로 저장 (인코딩 문제 방지)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tf:
                tf.write(text)
                text_path = tf.name

            # 참조 음성 경로 처리
            speaker_wav_line = ""
            if speaker_wav and os.path.exists(speaker_wav):
                speaker_wav_line = f'audio_prompt_path = r"{speaker_wav}"'
            else:
                speaker_wav_line = "audio_prompt_path = None"

            # Python 스크립트
            script = f'''
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

wav_path = r"{wav_path}"
text_path = r"{text_path}"
lang = "{voice}"
{speaker_wav_line}

os.makedirs(os.path.dirname(wav_path) if os.path.dirname(wav_path) else ".", exist_ok=True)

# 텍스트 파일에서 읽기
with open(text_path, 'r', encoding='utf-8') as f:
    text = f.read()

# torch.load CPU 패치
import torch
_original_load = torch.load
def patched_load(f, *args, **kwargs):
    kwargs['map_location'] = 'cpu'
    return _original_load(f, *args, **kwargs)
torch.load = patched_load

from chatterbox import ChatterboxMultilingualTTS
import torchaudio

print("Loading model...")
model = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
print("Generating...")
if audio_prompt_path:
    print(f"Using voice clone from: {{audio_prompt_path}}")
wav = model.generate(text=text, language_id=lang, audio_prompt_path=audio_prompt_path)
torchaudio.save(wav_path, wav.cpu(), model.sr)
print("SUCCESS")
'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(script)
                script_path = f.name

            try:
                result = subprocess.run(
                    [self.CONDA_PYTHON, script_path],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    encoding='utf-8',
                    errors='replace'
                )

                print(f"Chatterbox stdout: {result.stdout}")
                if result.stderr:
                    # 경고만 필터링
                    errors = [l for l in result.stderr.split('\n')
                              if 'error' in l.lower() and 'warning' not in l.lower()]
                    if errors:
                        print(f"Chatterbox stderr: {errors}")

                if "SUCCESS" in result.stdout:
                    if os.path.exists(wav_path):
                        # MP3로 변환 시도 (ffmpeg)
                        if output_path.endswith('.mp3'):
                            try:
                                subprocess.run(
                                    ['ffmpeg', '-y', '-i', wav_path, '-q:a', '2', output_path],
                                    capture_output=True, timeout=30
                                )
                                os.remove(wav_path)
                            except:
                                import shutil
                                shutil.move(wav_path, output_path.replace('.mp3', '.wav'))
                        return True
                else:
                    print(f"Chatterbox Error: {result.stderr}")
                    return False
            finally:
                os.unlink(script_path)
                if os.path.exists(text_path):
                    os.unlink(text_path)

        except subprocess.TimeoutExpired:
            print("Chatterbox Error: Timeout")
            return False
        except Exception as e:
            print(f"Chatterbox Error: {e}")
            return False


# Engine registry
TTS_ENGINES = {
    "chatterbox": ChatterboxTTSEngine,
    "edge_tts": EdgeTTSEngine,
    "gtts": GTTSEngine,
    "openai": OpenAITTSEngine,
    "elevenlabs": ElevenLabsTTSEngine,
}


class TTSService:
    """Multi-engine TTS Service."""

    def __init__(self):
        self.engines: Dict[str, BaseTTSEngine] = {}
        self.current_engine: Optional[BaseTTSEngine] = None
        self.current_engine_name: str = ""
        self.rate = 0
        self.volume = 0
        self.pitch = 0

        # Auto-detect available engines
        self._detect_engines()

    def _detect_engines(self):
        """Detect and initialize available TTS engines."""
        for name, engine_class in TTS_ENGINES.items():
            try:
                import os
                # Skip API-required engines if no API key
                if name == "openai" and not os.environ.get("OPENAI_API_KEY"):
                    continue
                if name == "elevenlabs" and not os.environ.get("ELEVENLABS_API_KEY"):
                    continue

                engine = engine_class()
                self.engines[name] = engine
                print(f"TTS Engine loaded: {engine.name}")

                # Set first available engine as default
                if self.current_engine is None:
                    self.current_engine = engine
                    self.current_engine_name = name

            except ImportError as e:
                print(f"TTS Engine '{name}' not available: {e}")
            except Exception as e:
                print(f"TTS Engine '{name}' failed to initialize: {e}")

    def get_available_engines(self) -> List[Tuple[str, str, str]]:
        """Get list of available engines.
        Returns: [(engine_id, display_name, description), ...]
        """
        result = []
        for name, engine in self.engines.items():
            result.append((name, engine.name, engine.description))
        return result

    def set_engine(self, engine_name: str) -> bool:
        """Set current TTS engine."""
        if engine_name in self.engines:
            self.current_engine = self.engines[engine_name]
            self.current_engine_name = engine_name
            return True
        return False

    def get_voice_names(self) -> List[str]:
        """Get list of available voice names for current engine."""
        if self.current_engine:
            return list(self.current_engine.get_voices().keys())
        return []

    def get_voice_id(self, voice_name: str) -> str:
        """Get voice ID from display name."""
        if self.current_engine:
            voices = self.current_engine.get_voices()
            return voices.get(voice_name, list(voices.values())[0] if voices else "")
        return ""

    def set_rate(self, rate: int):
        """Set speech rate (-50 to +100)."""
        self.rate = rate

    def set_volume(self, volume: int):
        """Set volume (-50 to +100)."""
        self.volume = volume

    def set_pitch(self, pitch: int):
        """Set pitch (-50 to +50)."""
        self.pitch = pitch

    def supports_voice_cloning(self) -> bool:
        """Check if current engine supports voice cloning."""
        if self.current_engine:
            return getattr(self.current_engine, 'supports_voice_cloning', False)
        return False

    def generate(self, text: str, output_path: str, voice_name: str = None,
                 speaker_wav: str = None) -> bool:
        """Generate speech from text.
        Args:
            speaker_wav: 참조 음성 파일 경로 (음성 복제용, Chatterbox만 지원)
        """
        if not self.current_engine:
            print("No TTS engine available")
            return False

        voice = self.get_voice_id(voice_name) if voice_name else ""
        if not voice:
            voices = self.current_engine.get_voices()
            voice = list(voices.values())[0] if voices else ""

        return self.current_engine.generate(
            text, output_path, voice,
            self.rate, self.volume, self.pitch,
            speaker_wav=speaker_wav
        )

    def generate_batch(
        self,
        items: List[Dict],
        output_dir: str,
        voice_name: str = None,
        progress_callback=None
    ) -> List[str]:
        """Generate multiple audio files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        generated_files = []
        total = len(items)

        for i, item in enumerate(items):
            text = item.get('text', '')
            filename = item.get('filename', f'audio_{i+1}.mp3')

            if not filename.endswith('.mp3'):
                filename += '.mp3'

            file_path = str(output_path / filename)

            if text.strip():
                success = self.generate(text, file_path, voice_name)
                if success:
                    generated_files.append(file_path)

            if progress_callback:
                progress_callback(i + 1, total)

        return generated_files


# Test
if __name__ == "__main__":
    tts = TTSService()

    print("\n=== Available TTS Engines ===")
    for engine_id, name, desc in tts.get_available_engines():
        print(f"  - {name}: {desc}")

    if tts.current_engine:
        print(f"\nCurrent engine: {tts.current_engine.name}")
        print(f"Available voices: {tts.get_voice_names()}")

        # Test generation
        tts.generate(
            "안녕하세요. TTS 테스트입니다.",
            "test_output.mp3"
        )
        print("\nGenerated: test_output.mp3")
