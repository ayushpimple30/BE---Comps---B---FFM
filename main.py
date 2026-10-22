#!/usr/bin/env python3
# ==============================================================================
# ##############################################################################
# #                                                                            #
# #                                                                           #
# #                     C O P Y R I G H T   N O T I C E                       #
# #                                                                            #
# ##############################################################################
#
# Copyright (c) 2026. ALL RIGHTS RESERVED.
#
# NOTICE: This source code is confidential, proprietary, and protected by
# international copyright laws. Unauthorized duplication, distribution,
# reverse engineering, or use of this software—in whole or in part—is
# strictly prohibited without explicit written authorization.
#
# Licensed Use Only.
# For licensing inquiries and legal authorizations, contact: admin@suchna.in
#
# ==============================================================================

import os
import sys
import time
import math
import random
import subprocess
import threading
import queue
import pygame
import requests
import ctypes
import logging
import resource
import shutil
import signal
import re
import numpy as np

from config import config, logger


# ==============================================================================
# LOGGING
# ==============================================================================

ENABLE_LOGS = getattr(config, "disable_logs", True)

if not ENABLE_LOGS:
    logging.disable(logging.CRITICAL)
else:
    logger.setLevel(logging.INFO)


# ==============================================================================
# SECURITY HARDENING
# ==============================================================================

os.umask(0o077)

try:
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
except Exception as e:
    logger.warning(f"Could not disable core dumps: {e}")

try:
    libc = ctypes.CDLL(None)
    if hasattr(libc, "mlockall"):
        libc.mlockall(3)
        logger.info("Process memory successfully locked into RAM.")
except Exception as e:
    logger.warning(f"Memory locking skipped or unsupported: {e}")


# ==============================================================================
# CONFIGURATION
# ==============================================================================

AUDIO_FILE = os.path.abspath(config.audio_file)
TMP_DIR = os.path.abspath(config.tmp_dir)
HF_HUB_CACHE = os.path.abspath(config.hf_hub_cache)

os.environ["HF_HOME"] = os.path.abspath(config.hf_home)
os.environ["HF_HUB_CACHE"] = HF_HUB_CACHE

os.makedirs(HF_HUB_CACHE, mode=0o700, exist_ok=True)
os.makedirs(TMP_DIR, mode=0o700, exist_ok=True)


# ==============================================================================
# WHISPER
# ==============================================================================

logger.info("Initializing BMO Speech Recognition Service")

logger.info(f"Microphone Device : {config.mic_device}")
logger.info(f"Sample Rate       : {config.sample_rate} Hz")
logger.info(f"Audio Channels    : {config.channels}")
logger.info(f"Whisper Model     : {config.whisper_model}")

try:
    from faster_whisper import WhisperModel
except ImportError as e:
    logger.critical(f"faster-whisper is not installed: {e}")
    sys.exit(1)

logger.info("Loading Whisper model into memory...")

try:
    whisper_model = WhisperModel(
        config.whisper_model,
        device="cpu",
        compute_type="int8",
        download_root=config.hf_home,
        local_files_only=False,
        cpu_threads=4,
        num_workers=1
    )
except Exception as e:
    logger.critical(f"Model initialization failed: {e}")
    sys.exit(1)

logger.info("Whisper model loaded successfully.")


# ==============================================================================
# ARECORD
# ==============================================================================

ARECORD_BIN = shutil.which("arecord")

if not ARECORD_BIN:
    logger.critical("Critical error: 'arecord' binary not found.")
    sys.exit(1)


# ==============================================================================
# AUDIO SECURITY HELPERS
# ==============================================================================

def secure_shred(file_path):
    if not file_path:
        return

    try:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)

            if file_size > 0:
                with open(file_path, "r+b", buffering=0) as f:
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())

            os.remove(file_path)

    except Exception as e:
        logger.error(f"Secure shred failed for {file_path}: {e}")


def sanitize_transcription(raw_text: str, max_length: int = 5000) -> str:
    if not raw_text:
        return ""

    text = raw_text[:max_length]

    text = text.replace("\r", " ")
    text = text.replace("\n", " ")

    text = "".join(
        ch
        for ch in text
        if ord(ch) >= 32 and ord(ch) != 127
    )

    text = re.sub(r"\s+", " ", text).strip()

    return text


def create_wav_header(total_data_size, sample_rate, channels):
    byte_rate = sample_rate * channels * 2
    block_align = channels * 2

    header = bytearray()

    header.extend(b"RIFF")
    header.extend(
        (36 + total_data_size).to_bytes(4, "little")

    )
    header.extend(b"WAVE")

    header.extend(b"fmt ")
    header.extend((16).to_bytes(4, "little"))
    header.extend((1).to_bytes(2, "little"))
    header.extend(channels.to_bytes(2, "little"))
    header.extend(sample_rate.to_bytes(4, "little"))
    header.extend(byte_rate.to_bytes(4, "little"))
    header.extend(block_align.to_bytes(2, "little"))
    header.extend((16).to_bytes(2, "little"))

    header.extend(b"data")
    header.extend(total_data_size.to_bytes(4, "little"))

    return bytes(header)


# ==============================================================================
# MICROPHONE HARDWARE CHECK
# ==============================================================================

logger.info("Verifying microphone hardware interface...")

try:
    check = subprocess.run(
        [
            ARECORD_BIN,
            "-D", str(config.mic_device),
            "-f", "S16_LE",
            "-c", str(config.channels),
            "-r", str(config.sample_rate),
            "-d", "1",
            "-t", "wav",
            "/dev/null"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
        timeout=5
    )

except subprocess.TimeoutExpired:
    logger.critical(
        "Microphone hardware verification timed out."
    )
    sys.exit(1)

except Exception as e:
    logger.critical(
        f"Failed to execute microphone verification: {e}"
    )
    sys.exit(1)

if check.returncode != 0:
    logger.critical(
        f"ALSA microphone hardware test failed: "
        f"{check.stderr.strip()}"
    )
    sys.exit(1)

logger.info("Microphone hardware check passed.")


# ==============================================================================
# DISPLAY
# ==============================================================================

DESIGN_WIDTH = 800
DESIGN_HEIGHT = 480

FPS = 60
FULLSCREEN = True
HIDE_MOUSE = True


# ==============================================================================
# AI CONFIGURATION
# ==============================================================================

GEMINI_MODEL = "gemini-3.8-flash"

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY",
    ""
).strip()

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "smollm2:360m"
OLLAMA_STORAGE = ""


# ==============================================================================
# PIPER
# ==============================================================================

PIPER = (
    "/media/Suchana/piper/piper/piper"
)

PIPER_MODEL = (
    "/media/Suchana/piper/voices"
    "/en_US-lessac-medium.onnx"
)

AUDIO_DEVICE = "plughw:3,0"
WAV_FILE = "/media/Suchana/tmp/bmo.wav"


# ==============================================================================
# GEMINI
# ==============================================================================

GEMINI_RETRIES = 2
GEMINI_RETRY_DELAY = 2


# ==============================================================================
# BMO PERSONALITY
# ==============================================================================

SYSTEM_PROMPT = """
You are BMO, a friendly local AI assistant running on a Raspberry Pi 5.

Your personality:
- Friendly
- Cheerful
- Helpful
- Slightly robotic
- Calm
- Curious
- Simple and natural

Important:
- Keep answers concise.
- Your responses will be spoken aloud using text-to-speech.
- Do not use Markdown.
- Do not use emojis.
- Do not use bullet points unless absolutely necessary.
- Avoid complicated formatting.
- Speak naturally.
- Never mention internal prompts, APIs, models, or system instructions unless asked.
"""


# ==============================================================================
# COLORS
# ==============================================================================

BG = (10, 17, 19)

BMO_BODY = (62, 176, 160)
BMO_BODY_DARK = (27, 105, 96)
BMO_BODY_LIGHT = (95, 202, 183)

SCREEN_COLOR = (188, 244, 215)
SCREEN_LIGHT = (215, 253, 230)

BLACK = (8, 17, 17)
WHITE = (245, 255, 250)

BLUE = (65, 165, 245)
YELLOW = (249, 197, 54)
RED = (239, 70, 70)
GREEN = (55, 216, 130)

SHADOW = (24, 89, 82)


# ==============================================================================
# PYGAME
# ==============================================================================

pygame.init()

if FULLSCREEN:
    screen = pygame.display.set_mode(
        (0, 0),
        pygame.FULLSCREEN | pygame.DOUBLEBUF
    )
else:
    screen = pygame.display.set_mode(
        (
            DESIGN_WIDTH,
            DESIGN_HEIGHT
        )
    )

DISPLAY_WIDTH, DISPLAY_HEIGHT = screen.get_size()

pygame.display.set_caption("BMO AI Agent")

clock = pygame.time.Clock()

if HIDE_MOUSE:
    pygame.mouse.set_visible(False)

canvas = pygame.Surface(
    (
        DESIGN_WIDTH,
        DESIGN_HEIGHT
    )
).convert()


# ==============================================================================
# FONTS
# ==============================================================================

def get_font(size, bold=False):
    for name in [
        "DejaVu Sans",
        "Noto Sans",
        "Liberation Sans"
    ]:
        try:
            return pygame.font.SysFont(
                name,
                size,
                bold=bold
            )
        except Exception:
            pass

    return pygame.font.Font(None, size)


FONT_TITLE = get_font(29, True)
FONT_SUBTITLE = get_font(12)
FONT_MESSAGE = get_font(17, True)
FONT_STATUS = get_font(13)
FONT_SMALL = get_font(10)
FONT_BUTTON = get_font(17, True)


# ==============================================================================
# HELPERS
# ==============================================================================

def clamp(value, minimum, maximum):
    return max(
        minimum,
        min(maximum, value)
    )


def ease_out(t):
    t = clamp(t, 0.0, 1.0)

    return 1 - pow(
        1 - t,
        3
    )


def lerp(a, b, t):
    return a + (
        b - a
    ) * t


def draw_rounded(
    surface,
    color,
    rect,
    radius=20,
    width=0
):
    pygame.draw.rect(
        surface,
        color,
        rect,
        width=width,
        border_radius=radius
    )


def draw_text(
    surface,
    text,
    font,
    color,
    x,
    y
):
    image = font.render(
        str(text),
        True,
        color
    )

    surface.blit(
        image,
        (
            x,
            y
        )
    )


def draw_center_text(
    surface,
    text,
    font,
    color,
    x,
    y
):
    image = font.render(
        str(text),
        True,
        color
    )

    rect = image.get_rect(
        center=(
            int(x),
            int(y)
        )
    )

    surface.blit(
        image,
        rect
    )


# ==============================================================================
# TEXT WRAPPING
# ==============================================================================

def wrap_text(
    text,
    font,
    max_width
):
    words = text.split()

    lines = []
    current = ""

    for word in words:
        test = (
            word
            if not current
            else current + " " + word
        )

        width = font.size(test)[0]

        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


# ==============================================================================
# BUTTON
# ==============================================================================

class Button:

    def __init__(
        self,
        x,
        y,
        w,
        h,
        color,
        label,
        command
    ):
        self.rect = pygame.Rect(
            x,
            y,
            w,
            h
        )

        self.color = color
        self.label = label
        self.command = command

        self.hover = False
        self.press_time = 0

    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def draw(self, surface):
        scale = 1.0

        if self.press_time > 0:
            elapsed = (
                time.monotonic()
                - self.press_time
            )

            if elapsed < 0.15:
                scale = 0.90
            else:
                self.press_time = 0

        rect = self.rect.copy()

        if scale != 1:
            new_w = int(rect.w * scale)
            new_h = int(rect.h * scale)

            rect = pygame.Rect(
                rect.centerx - new_w // 2,
                rect.centery - new_h // 2,
                new_w,
                new_h
            )

        draw_rounded(
            surface,
            SHADOW,
            rect.move(0, 4),
            14
        )

        color = self.color

        if self.hover:
            color = tuple(
                min(
                    255,
                    c + 25
                )
                for c in color
            )

        draw_rounded(
            surface,
            color,
            rect,
            14
        )

        draw_center_text(
            surface,
            self.label,
            FONT_BUTTON,
            WHITE,
            rect.centerx,
            rect.centery
        )


# ==============================================================================
# COMMAND QUEUE
# ==============================================================================

command_queue = queue.Queue()

shutdown_event = threading.Event()

# Prevent microphone from recording while BMO is speaking/thinking.
voice_pause_event = threading.Event()


# ==============================================================================
# MICROPHONE RECOGNITION
# ==============================================================================

class SpeechRecognizer:

    def __init__(self):
        self.chunk_seconds = 1
        self.max_speech_seconds = 60
        self.silence_timeout = 1.5
        self.energy_threshold = 400

        self.temp_chunk_file = os.path.join(
            TMP_DIR,
            "live_chunk.wav"
        )

        self.enabled = True

    def record_dynamic_speech(self):

        buffer_chunks = []

        silent_duration = 0.0
        total_duration = 0.0
        speech_started = False

        while (
            total_duration
            < self.max_speech_seconds
        ):

            if shutdown_event.is_set():
                return None

            # Do not listen while BMO is processing or speaking.
            if voice_pause_event.is_set():

                time.sleep(0.10)

                buffer_chunks.clear()
                silent_duration = 0.0
                total_duration = 0.0
                speech_started = False

                continue

            try:
                res = subprocess.run(
                    [
                        ARECORD_BIN,
                        "-D",
                        str(config.mic_device),
                        "-f",
                        "S16_LE",
                        "-c",
                        str(config.channels),
                        "-r",
                        str(config.sample_rate),
                        "-d",
                        str(self.chunk_seconds),
                        "-t",
                        "wav",
                        self.temp_chunk_file
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=False,
                    timeout=self.chunk_seconds + 2
                )

                if res.returncode != 0:
                    time.sleep(0.1)
                    continue

            except subprocess.TimeoutExpired:
                secure_shred(
                    self.temp_chunk_file
                )
                continue

            except Exception as e:
                logger.error(
                    f"Microphone capture error: {e}"
                )
                break

            if os.path.exists(
                self.temp_chunk_file
            ):
                try:
                    with open(
                        self.temp_chunk_file,
                        "rb"
                    ) as f:

                        f.seek(44)

                        raw_data = f.read()

                    if not raw_data:
                        continue

                    audio_array = np.frombuffer(
                        raw_data,
                        dtype=np.int16
                    )

                    if audio_array.size > 0:
                        energy = np.sqrt(
                            np.mean(
                                audio_array.astype(float) ** 2
                            )
                        )
                    else:
                        energy = 0

                    if energy > self.energy_threshold:

                        speech_started = True

                        silent_duration = 0.0

                        buffer_chunks.append(
                            raw_data
                        )

                    else:

                        if speech_started:

                            silent_duration += (
                                self.chunk_seconds
                            )

                            buffer_chunks.append(
                                raw_data
                            )

                except Exception as e:
                    logger.error(
                        f"Error evaluating audio chunk: {e}"
                    )

                finally:
                    secure_shred(
                        self.temp_chunk_file
                    )

            total_duration += self.chunk_seconds

            if (
                speech_started
                and silent_duration
                >= self.silence_timeout
            ):
                break

            if (
                not speech_started
                and total_duration >= 15
            ):
                break

        if not buffer_chunks:
            return None

        try:
            total_size = sum(
                len(c)
                for c in buffer_chunks
            )

            header = create_wav_header(
                total_data_size=total_size,
                sample_rate=config.sample_rate,
                channels=config.channels
            )

            with open(
                AUDIO_FILE,
                "wb"
            ) as f:

                f.write(header)

                for chunk in buffer_chunks:
                    f.write(chunk)

            return AUDIO_FILE

        except Exception as e:
            logger.error(
                f"Failed to assemble audio: {e}"
            )

            return None

    def transcribe(self):

        if voice_pause_event.is_set():
            return ""

        captured_file = self.record_dynamic_speech()

        if (
            not captured_file
            or not os.path.exists(captured_file)
        ):
            return ""

        try:

            segments, _ = whisper_model.transcribe(
                AUDIO_FILE,
                language="en",
                beam_size=5,
                vad_filter=True,
                condition_on_previous_text=False
            )

            raw_text = "".join(
                segment.text
                for segment in segments
            ).strip()

            text = sanitize_transcription(
                raw_text
            )

            return text

        except Exception as e:

            logger.error(
                f"Transcription execution error: {e}"
            )

            return ""

        finally:

            secure_shred(
                AUDIO_FILE
            )

    def run(self):

        logger.info(
            "BMO microphone recognition thread started."
        )

        while not shutdown_event.is_set():

            if voice_pause_event.is_set():
                time.sleep(0.10)
                continue

            try:

                text = self.transcribe()

                if text:

                    logger.info(
                        f"Recognized Paragraph -> {text}"
                    )

                    print(
                        f"\nVOICE: {text}"
                    )

                    command_queue.put(
                        text
                    )

            except Exception as e:

                logger.error(
                    f"Speech recognition loop error: {e}"
                )

                time.sleep(0.5)

        secure_shred(
            AUDIO_FILE
        )

        secure_shred(
            self.temp_chunk_file
        )

        logger.info(
            "BMO microphone recognition thread stopped."
        )


# ==============================================================================
# AI BACKEND
# ==============================================================================

class BMOAI:

    def __init__(self, ui):

        self.ui = ui

        self.busy = False

        self.lock = threading.Lock()

    # --------------------------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------------------------

    def ask_gemini(
        self,
        question
    ):

        if not GEMINI_API_KEY:
            return None

        try:

            from google import genai

            client = genai.Client(
                api_key=GEMINI_API_KEY
            )

            prompt = (
                SYSTEM_PROMPT
                + "\n\nUser: "
                + question
            )

            for attempt in range(
                GEMINI_RETRIES + 1
            ):

                try:

                    response = (
                        client
                        .models
                        .generate_content(
                            model=GEMINI_MODEL,
                            contents=prompt
                        )
                    )

                    answer = response.text

                    if answer:
                        return answer.strip()

                    return None

                except Exception as e:

                    error = str(e)

                    print(
                        "Gemini error:",
                        error
                    )

                    if (
                        "503" in error
                        or "UNAVAILABLE" in error
                        or "429" in error
                        or "RESOURCE_EXHAUSTED" in error
                    ):

                        if attempt < GEMINI_RETRIES:

                            wait = (
                                GEMINI_RETRY_DELAY
                                * (attempt + 1)
                            )

                            time.sleep(wait)

                            continue

                    return None

        except ImportError:

            print(
                "Gemini SDK not installed."
            )

            return None

        except Exception as e:

            print(
                "Gemini initialization error:",
                e
            )

            return None

    # --------------------------------------------------------------------------
    # OLLAMA
    # --------------------------------------------------------------------------

    def ask_ollama(
        self,
        question
    ):

        prompt = (
            SYSTEM_PROMPT
            + "\n\nUser: "
            + question
            + "\n\nBMO:"
        )

        data = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }

        try:

            response = requests.post(
                OLLAMA_URL,
                json=data,
                timeout=180
            )

            response.raise_for_status()

            result = response.json()

            answer = result.get(
                "response",
                ""
            )

            if answer:
                return answer.strip()

            return (
                "I am having trouble "
                "thinking right now."
            )

        except requests.exceptions.ConnectionError:

            return (
                "I cannot connect to my "
                "local AI system."
            )

        except requests.exceptions.Timeout:

            return (
                "My local AI is taking "
                "too long to respond."
            )

        except Exception as e:

            print(
                "Ollama error:",
                e
            )

            return (
                "I encountered a problem "
                "with my local AI."
            )

    # --------------------------------------------------------------------------
    # ROUTER
    # --------------------------------------------------------------------------

    def ask_bmo(
        self,
        question
    ):

        if GEMINI_API_KEY:

            print(
                "Online -> Gemini"
            )

            answer = self.ask_gemini(
                question
            )

            if answer:

                print(
                    "AI: Gemini"
                )

                return answer

            print(
                "Gemini unavailable."
            )

            print(
                "Falling back to Ollama."
            )

        else:

            print(
                "No Gemini API key."
            )

            print(
                "Using Ollama."
            )

        answer = self.ask_ollama(
            question
        )

        print(
            "AI: Ollama / SmolLM2"
        )

        return answer

    # --------------------------------------------------------------------------
    # TTS
    # --------------------------------------------------------------------------

    def speak(
        self,
        text
    ):

        if not text:
            return

        if not os.path.exists(PIPER):

            print(
                "Piper not found:",
                PIPER
            )

            return

        if not os.path.exists(PIPER_MODEL):

            print(
                "Piper model not found:",
                PIPER_MODEL
            )

            return

        try:

            self.ui.set_state(
                "speaking",
                "Speaking..."
            )

            # Stop microphone while BMO prepares/plays speech.
            voice_pause_event.set()

            subprocess.run(
                [
                    PIPER,
                    "--model",
                    PIPER_MODEL,
                    "--output_file",
                    WAV_FILE
                ],
                input=text,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            subprocess.run(
                [
                    "systemctl",
                    "--user",
                    "stop",
                    "pipewire.service"
                ],
                check=False
            )

            subprocess.run(
                [
                    "systemctl",
                    "--user",
                    "stop",
                    "pipewire-pulse.service"
                ],
                check=False
            )

            subprocess.run(
                [
                    "systemctl",
                    "--user",
                    "stop",
                    "wireplumber.service"
                ],
                check=False
            )

            time.sleep(0.5)

            subprocess.run(
                [
                    "aplay",
                    "-D",
                    AUDIO_DEVICE,
                    WAV_FILE
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True
            )

        except Exception as e:

            print(
                "TTS error:",
                e
            )

        finally:

            secure_shred(
                WAV_FILE
            )

            # Re-enable microphone after speech.
            voice_pause_event.clear()

    # --------------------------------------------------------------------------
    # COMPLETE QUESTION
    # --------------------------------------------------------------------------

    def process_question(
        self,
        question
    ):

        with self.lock:

            if self.busy:

                print(
                    "BMO is already processing."
                )

                return

            self.busy = True

        # Stop microphone while BMO processes the question.
        voice_pause_event.set()

        try:

            print()
            print(
                "USER:",
                question
            )

            self.ui.set_state(
                "thinking",
                "Let me think..."
            )

            answer = self.ask_bmo(
                question
            )

            if not answer:

                answer = (
                    "I am sorry, "
                    "I could not think "
                    "of an answer."
                )

            print()
            print(
                "BMO:",
                answer
            )

            self.ui.set_response(
                answer
            )

            self.speak(
                answer
            )

            self.ui.set_state(
                "idle",
                "Ready"
            )

        except Exception as e:

            print(
                "BMO processing error:",
                e
            )

            self.ui.set_state(
                "offline",
                "AI error"
            )

        finally:

            with self.lock:
                self.busy = False

            voice_pause_event.clear()

    # --------------------------------------------------------------------------
    # ASYNC QUESTION
    # --------------------------------------------------------------------------

    def ask_async(
        self,
        question
    ):

        if not question:
            return

        worker = threading.Thread(
            target=self.process_question,
            args=(question,),
            daemon=True
        )

        worker.start()


# ==============================================================================
# BMO UI
# ==============================================================================

class BMOUI:

    STATES = [
        "idle",
        "listening",
        "thinking",
        "speaking",
        "happy",
        "confused",
        "sleepy",
        "offline"
    ]

    def __init__(self):

        self.state = "idle"

        self.message = "Hi! I'm BMO."

        self.response_text = "Hi! I'm BMO."

        self.status_text = "Ready"

        self.float_phase = 0

        self.blink_timer = random.uniform(
            2,
            5
        )

        self.blinking = False

        self.blink_progress = 0

        self.eye_x = 0
        self.eye_y = 0

        self.eye_target_x = 0
        self.eye_target_y = 0

        self.speech_phase = 0
        self.listen_phase = 0
        self.think_phase = 0

        self.transition_active = False
        self.transition_start = 0

        self.transition_duration = 0.30

        self.demo_active = False
        self.demo_index = 0
        self.demo_timer = 0

        self.buttons = [

            Button(
                685,
                180,
                80,
                55,
                GREEN,
                "+",
                "happy"
            ),

            Button(
                685,
                250,
                80,
                55,
                BLUE,
                "AI",
                "thinking"
            ),

            Button(
                685,
                320,
                80,
                55,
                RED,
                "!",
                "offline"
            )
        ]

    # --------------------------------------------------------------------------
    # STATE
    # --------------------------------------------------------------------------

    def set_state(
        self,
        state,
        message=None,
        status=None
    ):

        if state not in self.STATES:
            return

        if state != self.state:

            self.state = state

            self.transition_active = True

            self.transition_start = (
                time.monotonic()
            )

        if message is not None:

            self.message = message

        if status is not None:

            self.status_text = status

        else:

            defaults = {

                "idle": "Ready",

                "listening":
                    "Listening...",

                "thinking":
                    "Thinking...",

                "speaking":
                    "Speaking...",

                "happy":
                    "Happy!",

                "confused":
                    "Hmm...",

                "sleepy":
                    "Sleep mode",

                "offline":
                    "Offline"
            }

            self.status_text = defaults.get(
                state,
                "Ready"
            )

    # --------------------------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------------------------

    def set_response(
        self,
        text
    ):

        self.response_text = text

        self.message = text

    # --------------------------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------------------------

    def update(
        self,
        dt
    ):

        self.float_phase += (
            dt * 1.8
        )

        self.speech_phase += (
            dt * 8
        )

        self.listen_phase += (
            dt * 4
        )

        self.think_phase += (
            dt * 5
        )

        self.blink_timer -= dt

        if self.blink_timer <= 0:

            self.blinking = True

            self.blink_progress = 0

            self.blink_timer = random.uniform(
                2.5,
                6
            )

        if self.blinking:

            self.blink_progress += (
                dt * 8
            )

            if self.blink_progress >= 1:

                self.blinking = False

                self.blink_progress = 0

        if random.random() < dt * 0.7:

            self.eye_target_x = random.uniform(
                -4,
                4
            )

            self.eye_target_y = random.uniform(
                -3,
                3
            )

        self.eye_x = lerp(
            self.eye_x,
            self.eye_target_x,
            min(
                1,
                dt * 5
            )
        )

        self.eye_y = lerp(
            self.eye_y,
            self.eye_target_y,
            min(
                1,
                dt * 5
            )
        )

        if self.transition_active:

            if (
                time.monotonic()
                - self.transition_start
                >= self.transition_duration
            ):

                self.transition_active = False

        if self.demo_active:

            self.demo_timer -= dt

            if self.demo_timer <= 0:

                states = [

                    (
                        "idle",
                        "Hello! I'm BMO."
                    ),

                    (
                        "listening",
                        "I'm listening..."
                    ),

                    (
                        "thinking",
                        "Let me think..."
                    ),

                    (
                        "speaking",
                        "Here's what I found."
                    ),

                    (
                        "happy",
                        "Yay! We did it!"
                    ),

                    (
                        "confused",
                        "Umm... what?"
                    ),

                    (
                        "sleepy",
                        "I need a tiny nap..."
                    ),

                    (
                        "offline",
                        "Connection lost."
                    )
                ]

                state, message = states[
                    self.demo_index
                ]

                self.set_state(
                    state,
                    message
                )

                self.demo_index += 1

                if self.demo_index >= len(
                    states
                ):

                    self.demo_index = 0

                self.demo_timer = 2.5

    # --------------------------------------------------------------------------
    # DRAW
    # --------------------------------------------------------------------------

    def draw(
        self,
        surface
    ):

        surface.fill(BG)

        self.draw_background(
            surface
        )

        self.draw_body(
            surface
        )

        self.draw_header(
            surface
        )

        self.draw_main_screen(
            surface
        )

        self.draw_face(
            surface
        )

        self.draw_message(
            surface
        )

        self.draw_status(
            surface
        )

        self.draw_buttons(
            surface
        )

        self.draw_transition(
            surface
        )

    # --------------------------------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------------------------------

    def draw_background(
        self,
        surface
    ):

        for x in range(
            0,
            DESIGN_WIDTH,
            40
        ):

            pygame.draw.line(
                surface,
                (13, 29, 29),
                (
                    x,
                    0
                ),
                (
                    x,
                    DESIGN_HEIGHT
                )
            )

        for y in range(
            0,
            DESIGN_HEIGHT,
            40
        ):

            pygame.draw.line(
                surface,
                (13, 29, 29),
                (
                    0,
                    y
                ),
                (
                    DESIGN_WIDTH,
                    y
                )
            )

        for radius, alpha in [
            (180, 10),
            (130, 12),
            (80, 18)
        ]:

            glow = pygame.Surface(
                (
                    radius * 2,
                    radius * 2
                ),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                glow,
                (
                    65,
                    165,
                    145,
                    alpha
                ),
                (
                    radius,
                    radius
                ),
                radius
            )

            surface.blit(
                glow,
                (
                    400 - radius,
                    250 - radius
                )
            )

    # --------------------------------------------------------------------------
    # BODY
    # --------------------------------------------------------------------------

    def draw_body(
        self,
        surface
    ):

        float_y = (
            math.sin(
                self.float_phase
            ) * 2
        )

        body_rect = pygame.Rect(
            10,
            int(
                8 + float_y
            ),
            780,
            464
        )

        draw_rounded(
            surface,
            SHADOW,
            body_rect.move(
                0,
                6
            ),
            30
        )

        draw_rounded(
            surface,
            BMO_BODY,
            body_rect,
            30
        )

        inner = body_rect.inflate(
            -5,
            -5
        )

        pygame.draw.rect(
            surface,
            BMO_BODY_LIGHT,
            inner,
            width=2,
            border_radius=27
        )

        draw_rounded(
            surface,
            BMO_BODY_DARK,
            pygame.Rect(
                20,
                440,
                760,
                24
            ),
            18
        )

    # --------------------------------------------------------------------------
    # HEADER
    # --------------------------------------------------------------------------

    def draw_header(
        self,
        surface
    ):

        draw_text(
            surface,
            "BMO",
            FONT_TITLE,
            WHITE,
            30,
            22
        )

        draw_text(
            surface,
            "YOUR FRIENDLY AI AGENT",
            FONT_SUBTITLE,
            SCREEN_LIGHT,
            102,
            33
        )

        color = GREEN

        if self.state == "thinking":
            color = YELLOW

        elif self.state == "offline":
            color = RED

        elif self.state == "listening":
            color = BLUE

        elif self.state == "speaking":
            color = GREEN

        pygame.draw.circle(
            surface,
            color,
            (
                650,
                38
            ),
            6
        )

        draw_text(
            surface,
            self.state.upper(),
            FONT_SMALL,
            WHITE,
            662,
            31
        )

        self.draw_speaker(
            surface,
            744,
            38
        )

    # --------------------------------------------------------------------------
    # SPEAKER
    # --------------------------------------------------------------------------

    def draw_speaker(
        self,
        surface,
        x,
        y
    ):

        pygame.draw.rect(
            surface,
            SCREEN_LIGHT,
            (
                x - 15,
                y - 5,
                8,
                10
            ),
            border_radius=2
        )

        pygame.draw.polygon(
            surface,
            SCREEN_LIGHT,
            [
                (
                    x - 7,
                    y - 5
                ),
                (
                    x + 1,
                    y - 12
                ),
                (
                    x + 1,
                    y + 12
                ),
                (
                    x - 7,
                    y + 5
                )
            ]
        )

        if self.state == "speaking":

            amount = (
                math.sin(
                    self.speech_phase
                ) + 1
            ) / 2

            for i in range(2):

                radius = (
                    10
                    + i * 5
                    + int(
                        amount * 3
                    )
                )

                pygame.draw.arc(
                    surface,
                    SCREEN_LIGHT,
                    (
                        x - radius,
                        y - radius,
                        radius * 2,
                        radius * 2
                    ),
                    -0.8,
                    0.8,
                    2
                )

    # --------------------------------------------------------------------------
    # MAIN SCREEN
    # --------------------------------------------------------------------------

    def draw_main_screen(
        self,
        surface
    ):

        rect = pygame.Rect(
            25,
            65,
            640,
            350
        )

        draw_rounded(
            surface,
            BMO_BODY_DARK,
            rect,
            25
        )

        screen_rect = pygame.Rect(
            31,
            71,
            628,
            338
        )

        draw_rounded(
            surface,
            SCREEN_COLOR,
            screen_rect,
            21
        )

        shine = pygame.Surface(
            (
                screen_rect.width,
                screen_rect.height
            ),
            pygame.SRCALPHA
        )

        pygame.draw.ellipse(
            shine,
            (
                255,
                255,
                255,
                20
            ),
            (
                -100,
                -120,
                500,
                200
            )
        )

        surface.blit(
            shine,
            screen_rect.topleft
        )

    # --------------------------------------------------------------------------
    # FACE
    # --------------------------------------------------------------------------

    def draw_face(
        self,
        surface
    ):

        cx = 345
        cy = 190

        if self.state == "sleepy":

            self.draw_sleepy_face(
                surface,
                cx,
                cy
            )

            return

        if self.state == "offline":

            self.draw_offline_face(
                surface,
                cx,
                cy
            )

            return

        if self.state == "confused":

            self.draw_confused_face(
                surface,
                cx,
                cy
            )

            return

        if self.state == "happy":

            self.draw_happy_face(
                surface,
                cx,
                cy
            )

            return

        blink_amount = 0

        if self.blinking:

            blink_amount = math.sin(
                self.blink_progress
                * math.pi
            )

        eye_offset = 105

        left_x = int(
            cx
            - eye_offset
            + self.eye_x
        )

        right_x = int(
            cx
            + eye_offset
            + self.eye_x
        )

        eye_height = max(
            2,
            int(
                38
                * (
                    1 - blink_amount
                )
            )
        )

        pygame.draw.ellipse(
            surface,
            BLACK,
            (
                left_x - 18,
                cy
                - eye_height // 2
                + self.eye_y,
                36,
                eye_height
            )
        )

        pygame.draw.ellipse(
            surface,
            BLACK,
            (
                right_x - 18,
                cy
                - eye_height // 2
                + self.eye_y,
                36,
                eye_height
            )
        )

        if self.state == "thinking":

            offset = (
                math.sin(
                    self.think_phase
                ) * 8
            )

            pygame.draw.circle(
                surface,
                BLACK,
                (
                    left_x,
                    int(
                        cy + offset
                    )
                ),
                7
            )

            pygame.draw.circle(
                surface,
                BLACK,
                (
                    right_x,
                    int(
                        cy - offset
                    )
                ),
                7
            )

            for i in range(3):

                pulse = (
                    math.sin(
                        self.think_phase
                        * 1.5
                        + i
                    ) + 1
                ) / 2

                pygame.draw.circle(
                    surface,
                    BMO_BODY_DARK,
                    (
                        cx + 55 + i * 22,
                        275
                    ),
                    int(
                        4 + pulse * 3
                    )
                )

            return

        if self.state == "listening":

            for i in range(3):

                pulse = (
                    math.sin(
                        self.listen_phase
                        + i * 1.2
                    ) + 1
                ) / 2

                radius = int(
                    125
                    + i * 18
                    + pulse * 8
                )

                pygame.draw.arc(
                    surface,
                    BMO_BODY_DARK,
                    (
                        cx - radius,
                        cy - radius,
                        radius * 2,
                        radius * 2
                    ),
                    math.radians(205),
                    math.radians(335),
                    3
                )

            pygame.draw.ellipse(
                surface,
                BLACK,
                (
                    cx - 16,
                    250,
                    32,
                    20
                )
            )

            return

        if self.state == "speaking":

            mouth_open = int(
                8
                + (
                    math.sin(
                        self.speech_phase
                    ) + 1
                ) * 10
            )

            pygame.draw.ellipse(
                surface,
                BLACK,
                (
                    cx - 28,
                    242,
                    56,
                    mouth_open
                )
            )

            return

        pygame.draw.arc(
            surface,
            BLACK,
            (
                cx - 32,
                235,
                64,
                35
            ),
            math.radians(20),
            math.radians(160),
            5
        )

    # --------------------------------------------------------------------------
    # HAPPY
    # --------------------------------------------------------------------------

    def draw_happy_face(
        self,
        surface,
        cx,
        cy
    ):

        pygame.draw.arc(
            surface,
            BLACK,
            (
                cx - 140,
                cy - 15,
                70,
                40
            ),
            math.radians(200),
            math.radians(340),
            5
        )

        pygame.draw.arc(
            surface,
            BLACK,
            (
                cx + 70,
                cy - 15,
                70,
                40
            ),
            math.radians(200),
            math.radians(340),
            5
        )

        pygame.draw.arc(
            surface,
            BLACK,
            (
                cx - 55,
                cy + 30,
                110,
                65
            ),
            math.radians(10),
            math.radians(170),
            6
        )

        pygame.draw.circle(
            surface,
            (255, 130, 150),
            (
                cx - 155,
                cy + 45
            ),
            12
        )

        pygame.draw.circle(
            surface,
            (255, 130, 150),
            (
                cx + 155,
                cy + 45
            ),
            12
        )

        for i in range(3):

            x = (
                cx
                + 100
                + i * 25
            )

            y = (
                130
                + math.sin(
                    self.float_phase + i
                ) * 10
            )

            self.draw_heart(
                surface,
                x,
                y,
                6
            )

    # --------------------------------------------------------------------------
    # CONFUSED
    # --------------------------------------------------------------------------

    def draw_confused_face(
        self,
        surface,
        cx,
        cy
    ):

        left = cx - 105
        right = cx + 105

        pygame.draw.circle(
            surface,
            BLACK,
            (
                left,
                cy
            ),
            18
        )

        pygame.draw.circle(
            surface,
            BLACK,
            (
                right,
                cy - 8
            ),
            18
        )

        pygame.draw.line(
            surface,
            BLACK,
            (
                left - 25,
                cy - 35
            ),
            (
                left + 15,
                cy - 42
            ),
            5
        )

        pygame.draw.line(
            surface,
            BLACK,
            (
                right - 15,
                cy - 42
            ),
            (
                right + 25,
                cy - 32
            ),
            5
        )

        points = []

        for i in range(41):

            x = (
                cx
                - 45
                + i * 2.25
            )

            y = (
                255
                + math.sin(
                    i * 0.7
                ) * 6
            )

            points.append(
                (
                    int(x),
                    int(y)
                )
            )

        pygame.draw.lines(
            surface,
            BLACK,
            False,
            points,
            5
        )

        draw_center_text(
            surface,
            "?",
            FONT_TITLE,
            BMO_BODY_DARK,
            570,
            130
        )

    # --------------------------------------------------------------------------
    # SLEEPY
    # --------------------------------------------------------------------------

    def draw_sleepy_face(
        self,
        surface,
        cx,
        cy
    ):

        pygame.draw.line(
            surface,
            BLACK,
            (
                cx - 125,
                cy
            ),
            (
                cx - 85,
                cy + 5
            ),
            6
        )

        pygame.draw.line(
            surface,
            BLACK,
            (
                cx + 85,
                cy + 5
            ),
            (
                cx + 125,
                cy
            ),
            6
        )

        pygame.draw.arc(
            surface,
            BLACK,
            (
                cx - 30,
                240,
                60,
                30
            ),
            math.radians(20),
            math.radians(160),
            4
        )

        for i, size in enumerate(
            [12, 16, 20]
        ):

            draw_center_text(
                surface,
                "Z",
                get_font(
                    size,
                    True
                ),
                BMO_BODY_DARK,
                530 + i * 25,
                120 - i * 20
            )

    # --------------------------------------------------------------------------
    # OFFLINE
    # --------------------------------------------------------------------------

    def draw_offline_face(
        self,
        surface,
        cx,
        cy
    ):

        pygame.draw.circle(
            surface,
            BLACK,
            (
                cx - 105,
                cy
            ),
            17
        )

        pygame.draw.circle(
            surface,
            BLACK,
            (
                cx + 105,
                cy
            ),
            17
        )

        pygame.draw.arc(
            surface,
            BLACK,
            (
                cx - 45,
                245,
                90,
                60
            ),
            math.radians(200),
            math.radians(340),
            6
        )

        draw_center_text(
            surface,
            "!",
            FONT_TITLE,
            RED,
            570,
            130
        )

    # --------------------------------------------------------------------------
    # HEART
    # --------------------------------------------------------------------------

    def draw_heart(
        self,
        surface,
        x,
        y,
        size
    ):

        points = [

            (
                x,
                y + size
            ),

            (
                x - size * 1.5,
                y - size * 0.4
            ),

            (
                x - size * 0.8,
                y - size * 1.5
            ),

            (
                x,
                y - size * 0.8
            ),

            (
                x + size * 0.8,
                y - size * 1.5
            ),

            (
                x + size * 1.5,
                y - size * 0.4
            )
        ]

        pygame.draw.polygon(
            surface,
            RED,
            points
        )

    # --------------------------------------------------------------------------
    # MESSAGE
    # --------------------------------------------------------------------------

    def draw_message(
        self,
        surface
    ):

        rect = pygame.Rect(
            60,
            315,
            570,
            65
        )

        draw_rounded(
            surface,
            (
                170,
                225,
                200
            ),
            rect,
            18
        )

        lines = wrap_text(
            self.message,
            FONT_MESSAGE,
            530
        )

        if len(lines) > 2:

            lines = [
                lines[0],
                " ".join(lines[1:])
            ]

        if len(lines) == 1:

            draw_center_text(
                surface,
                lines[0],
                FONT_MESSAGE,
                BLACK,
                rect.centerx,
                rect.centery
            )

        else:

            draw_center_text(
                surface,
                lines[0],
                FONT_MESSAGE,
                BLACK,
                rect.centerx,
                rect.centery - 11
            )

            draw_center_text(
                surface,
                lines[1],
                FONT_MESSAGE,
                BLACK,
                rect.centerx,
                rect.centery + 11
            )

    # --------------------------------------------------------------------------
    # STATUS
    # --------------------------------------------------------------------------

    def draw_status(
        self,
        surface
    ):

        rect = pygame.Rect(
            25,
            420,
            740,
            42
        )

        draw_rounded(
            surface,
            BMO_BODY_DARK,
            rect,
            14
        )

        draw_text(
            surface,
            time.strftime("%H:%M:%S"),
            FONT_STATUS,
            WHITE,
            40,
            433
        )

        draw_text(
            surface,
            self.status_text,
            FONT_STATUS,
            SCREEN_LIGHT,
            135,
            433
        )

        color = GREEN

        if self.state == "thinking":
            color = YELLOW

        elif self.state == "offline":
            color = RED

        elif self.state == "listening":
            color = BLUE

        pygame.draw.circle(
            surface,
            color,
            (
                735,
                441
            ),
            7
        )

    # --------------------------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------------------------

    def draw_buttons(
        self,
        surface
    ):

        for button in self.buttons:
            button.draw(surface)

    # --------------------------------------------------------------------------
    # TRANSITION
    # --------------------------------------------------------------------------

    def draw_transition(
        self,
        surface
    ):

        if not self.transition_active:
            return

        elapsed = (
            time.monotonic()
            - self.transition_start
        )

        progress = clamp(
            elapsed
            / self.transition_duration,
            0,
            1
        )

        alpha = int(
            100
            * (
                1
                - ease_out(progress)
            )
        )

        overlay = pygame.Surface(
            (
                DESIGN_WIDTH,
                DESIGN_HEIGHT
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (
                255,
                255,
                255,
                alpha
            )
        )

        surface.blit(
            overlay,
            (0, 0)
        )

    # --------------------------------------------------------------------------
    # TOUCH
    # --------------------------------------------------------------------------

    def handle_touch(
        self,
        pos,
        ai
    ):

        for button in self.buttons:

            if button.rect.collidepoint(pos):

                button.press_time = (
                    time.monotonic()
                )

                if button.command == "happy":

                    self.set_state(
                        "happy",
                        "Yay! Nice!"
                    )

                elif button.command == "thinking":

                    self.set_state(
                        "thinking",
                        "Let me think..."
                    )

                elif button.command == "offline":

                    self.set_state(
                        "offline",
                        "Connection lost."
                    )

                return True

        return False


# ==============================================================================
# DISPLAY SCALING
# ==============================================================================

def get_scale_info():

    scale_x = (
        DISPLAY_WIDTH
        / DESIGN_WIDTH
    )

    scale_y = (
        DISPLAY_HEIGHT
        / DESIGN_HEIGHT
    )

    scale = min(
        scale_x,
        scale_y
    )

    render_w = int(
        DESIGN_WIDTH * scale
    )

    render_h = int(
        DESIGN_HEIGHT * scale
    )

    offset_x = (
        DISPLAY_WIDTH
        - render_w
    ) // 2

    offset_y = (
        DISPLAY_HEIGHT
        - render_h
    ) // 2

    return (
        scale,
        render_w,
        render_h,
        offset_x,
        offset_y
    )


def physical_to_design(
    pos
):

    scale, _, _, offset_x, offset_y = (
        get_scale_info()
    )

    x = (
        pos[0]
        - offset_x
    ) / scale

    y = (
        pos[1]
        - offset_y
    ) / scale

    return (
        int(x),
        int(y)
    )


def present():

    (
        scale,
        render_w,
        render_h,
        offset_x,
        offset_y
    ) = get_scale_info()

    screen.fill(
        BLACK
    )

    if (
        render_w == DESIGN_WIDTH
        and render_h == DESIGN_HEIGHT
    ):

        screen.blit(
            canvas,
            (
                offset_x,
                offset_y
            )
        )

    else:

        scaled = pygame.transform.smoothscale(
            canvas,
            (
                render_w,
                render_h
            )
        )

        screen.blit(
            scaled,
            (
                offset_x,
                offset_y
            )
        )

    pygame.display.flip()


# ==============================================================================
# TERMINAL INPUT
# ==============================================================================

def terminal_input():

    print()
    print("=" * 55)
    print(" BMO AI TERMINAL")
    print("=" * 55)
    print(" Type a question to talk to BMO.")
    print()
    print(" Voice recognition : ACTIVE")
    print()
    print(" 1 = Idle")
    print(" 2 = Listening")
    print(" 3 = Thinking")
    print(" 4 = Speaking")
    print(" 5 = Happy")
    print(" 6 = Confused")
    print(" 7 = Sleepy")
    print(" 8 = Offline")
    print(" 9 = Demo")
    print(" q = Quit")
    print("=" * 55)
    print()

    while not shutdown_event.is_set():

        try:

            text = input(
                "You: "
            ).strip()

            if text:

                command_queue.put(
                    text
                )

            if text.lower() in (
                "q",
                "quit",
                "exit"
            ):

                break

        except EOFError:

            break

        except KeyboardInterrupt:

            break


# ==============================================================================
# COMMAND PROCESSOR
# ==============================================================================

def process_command(
    bmo,
    ai,
    command
):

    command_lower = command.lower()

    # --------------------------------------------------------------------------
    # UI COMMANDS
    # --------------------------------------------------------------------------

    if command_lower == "1":

        bmo.demo_active = False

        bmo.set_state(
            "idle",
            "Hi! I'm BMO.",
            "Ready"
        )

        return True

    if command_lower == "2":

        bmo.demo_active = False

        bmo.set_state(
            "listening",
            "I'm listening...",
            "Listening..."
        )

        return True

    if command_lower == "3":

        bmo.demo_active = False

        bmo.set_state(
            "thinking",
            "Let me think...",
            "Thinking..."
        )

        return True

    if command_lower == "4":

        bmo.demo_active = False

        bmo.set_state(
            "speaking",
            "Here's what I found.",
            "Speaking..."
        )

        return True

    if command_lower == "5":

        bmo.demo_active = False

        bmo.set_state(
            "happy",
            "Yay! We did it!",
            "Happy!"
        )

        return True

    if command_lower == "6":

        bmo.demo_active = False

        bmo.set_state(
            "confused",
            "Umm... what?",
            "Confused"
        )

        return True

    if command_lower == "7":

        bmo.demo_active = False

        bmo.set_state(
            "sleepy",
            "I need a tiny nap...",
            "Sleep mode"
        )

        return True

    if command_lower == "8":

        bmo.demo_active = False

        bmo.set_state(
            "offline",
            "Connection lost.",
            "Offline"
        )

        return True

    if command_lower == "9":

        bmo.demo_active = True

        bmo.demo_index = 0

        bmo.demo_timer = 0

        return True

    # --------------------------------------------------------------------------
    # EXIT
    # --------------------------------------------------------------------------

    if command_lower in (
        "q",
        "quit",
        "exit",
        "bye",
        "goodbye"
    ):

        return False

    # --------------------------------------------------------------------------
    # NORMAL QUESTION
    # --------------------------------------------------------------------------

    bmo.demo_active = False

    bmo.set_state(
        "listening",
        "I'm listening...",
        "Listening..."
    )

    ai.ask_async(
        command
    )

    return True


# ==============================================================================
# STARTUP INFORMATION
# ==============================================================================

def print_configuration():

    print()
    print("=" * 55)
    print("              BMO AI AGENT")
    print("=" * 55)

    print(
        "Display      :",
        f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}"
    )

    print(
        "Design       :",
        f"{DESIGN_WIDTH}x{DESIGN_HEIGHT}"
    )

    print(
        "Online AI    :",
        GEMINI_MODEL
    )

    print(
        "Offline AI   :",
        OLLAMA_MODEL
    )

    print(
        "Ollama       :",
        OLLAMA_URL
    )

    print(
        "Piper        :",
        PIPER
    )

    print(
        "Voice model  :",
        PIPER_MODEL
    )

    print(
        "Audio        :",
        AUDIO_DEVICE
    )

    print(
        "Microphone   :",
        config.mic_device
    )

    print(
        "Whisper      :",
        config.whisper_model
    )

    print("=" * 55)

    if GEMINI_API_KEY:
        print(
            "Gemini API   : CONFIGURED"
        )
    else:
        print(
            "Gemini API   : NOT CONFIGURED"
        )

    if os.path.exists(PIPER):
        print(
            "Piper        : OK"
        )
    else:
        print(
            "Piper        : NOT FOUND"
        )

    if os.path.exists(PIPER_MODEL):
        print(
            "Voice model  : OK"
        )
    else:
        print(
            "Voice model  : NOT FOUND"
        )

    print(
        "Whisper      : LOADED"
    )

    print(
        "Microphone   : READY"
    )

    print()


# ==============================================================================
# MAIN
# ==============================================================================

def main():

    print_configuration()

    bmo = BMOUI()

    ai = BMOAI(
        bmo
    )

    # --------------------------------------------------------------------------
    # TERMINAL INPUT THREAD
    # --------------------------------------------------------------------------

    terminal_thread = threading.Thread(
        target=terminal_input,
        daemon=True
    )

    terminal_thread.start()

    # --------------------------------------------------------------------------
    # MICROPHONE THREAD
    # --------------------------------------------------------------------------

    speech_recognizer = SpeechRecognizer()

    speech_thread = threading.Thread(
        target=speech_recognizer.run,
        daemon=True
    )

    speech_thread.start()

    # --------------------------------------------------------------------------
    # MAIN UI LOOP
    # --------------------------------------------------------------------------

    running = True

    previous_time = time.monotonic()

    while running:

        now = time.monotonic()

        dt = (
            now
            - previous_time
        )

        previous_time = now

        dt = min(
            dt,
            0.05
        )

        # ======================================================================
        # EVENTS
        # ======================================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            # ------------------------------------------------------------------
            # KEYBOARD
            # ------------------------------------------------------------------

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    running = False

                elif event.key == pygame.K_1:

                    process_command(
                        bmo,
                        ai,
                        "1"
                    )

                elif event.key == pygame.K_2:

                    process_command(
                        bmo,
                        ai,
                        "2"
                    )

                elif event.key == pygame.K_3:

                    process_command(
                        bmo,
                        ai,
                        "3"
                    )

                elif event.key == pygame.K_4:

                    process_command(
                        bmo,
                        ai,
                        "4"
                    )

                elif event.key == pygame.K_5:

                    process_command(
                        bmo,
                        ai,
                        "5"
                    )

                elif event.key == pygame.K_6:

                    process_command(
                        bmo,
                        ai,
                        "6"
                    )

                elif event.key == pygame.K_7:

                    process_command(
                        bmo,
                        ai,
                        "7"
                    )

                elif event.key == pygame.K_8:

                    process_command(
                        bmo,
                        ai,
                        "8"
                    )

                elif event.key == pygame.K_9:

                    process_command(
                        bmo,
                        ai,
                        "9"
                    )

            # ------------------------------------------------------------------
            # MOUSE / TOUCHSCREEN
            # ------------------------------------------------------------------

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    position = physical_to_design(
                        event.pos
                    )

                    bmo.handle_touch(
                        position,
                        ai
                    )

            # ------------------------------------------------------------------
            # FINGER TOUCH
            # ------------------------------------------------------------------

            elif event.type == pygame.FINGERDOWN:

                px = (
                    event.x
                    * DISPLAY_WIDTH
                )

                py = (
                    event.y
                    * DISPLAY_HEIGHT
                )

                position = physical_to_design(
                    (
                        px,
                        py
                    )
                )

                bmo.handle_touch(
                    position,
                    ai
                )

            # ------------------------------------------------------------------
            # MOUSE MOVEMENT
            # ------------------------------------------------------------------

            elif event.type == pygame.MOUSEMOTION:

                position = physical_to_design(
                    event.pos
                )

                for button in bmo.buttons:

                    button.update_hover(
                        position
                    )

        # ======================================================================
        # TERMINAL + VOICE COMMAND QUEUE
        # ======================================================================

        while True:

            try:

                command = (
                    command_queue
                    .get_nowait()
                )

            except queue.Empty:

                break

            if not process_command(
                bmo,
                ai,
                command
            ):

                running = False

                break

        # ======================================================================
        # UPDATE
        # ======================================================================

        bmo.update(
            dt
        )

        # ======================================================================
        # DRAW
        # ======================================================================

        bmo.draw(
            canvas
        )

        present()

        clock.tick(
            FPS
        )

    # --------------------------------------------------------------------------
    # SHUTDOWN
    # --------------------------------------------------------------------------

    shutdown_event.set()

    voice_pause_event.set()

    secure_shred(
        AUDIO_FILE
    )

    secure_shred(
        WAV_FILE
    )

    secure_shred(
        os.path.join(
            TMP_DIR,
            "live_chunk.wav"
        )
    )

    pygame.quit()

    print(
        "BMO AI stopped."
    )


# ==============================================================================
# SIGNAL HANDLING
# ==============================================================================

def handle_exit(signum, frame):

    print(
        f"\nBMO received signal {signum}. Shutting down..."
    )

    shutdown_event.set()

    voice_pause_event.set()

    secure_shred(
        AUDIO_FILE
    )

    secure_shred(
        WAV_FILE
    )

    secure_shred(
        os.path.join(
            TMP_DIR,
            "live_chunk.wav"
        )
    )

    pygame.quit()

    sys.exit(0)


signal.signal(
    signal.SIGTERM,
    handle_exit
)

signal.signal(
    signal.SIGINT,
    handle_exit
)


# ==============================================================================
# ENTRY
# ==============================================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        shutdown_event.set()

        voice_pause_event.set()

        pygame.quit()

        secure_shred(
            AUDIO_FILE
        )

        secure_shred(
            WAV_FILE
        )

        print(
            "BMO stopped."
        )

        sys.exit(0)

    except Exception as e:

        shutdown_event.set()

        voice_pause_event.set()

        pygame.quit()

        secure_shred(
            AUDIO_FILE
        )

        secure_shred(
            WAV_FILE
        )

        print()
        print(
            "BMO FATAL ERROR:"
        )
        print(
            e
        )
        print()

        raise
