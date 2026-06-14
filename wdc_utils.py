"""
Core utility functions ported from WhatDreamsCost's ComfyUI nodes.
All ComfyUI-specific APIs (folder_paths, comfy.*, PromptServer) have been
replaced with standard Python / PyTorch / PIL equivalents.
"""

from __future__ import annotations

import math
import os
import re
import io as _io
import logging
from typing import Optional

import numpy as np
import torch
from PIL import Image

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Speech Length Calculator  (from speech_length_calculator.py)
# ---------------------------------------------------------------------------

def calculate_speech_frames(text: str, fps: int, additional_time: float = 0.0) -> dict:
    """
    Given a script (with spoken dialogue inside quotes) calculate how many
    video frames are needed at slow / average / fast speaking speed.

    Returns a dict with keys: word_count, slow_frames, avg_frames, fast_frames,
    slow_seconds, avg_seconds, fast_seconds.
    """
    # Find words inside double/single/smart quotes
    # Patterns: "...", '...', \u201c...\u201d, \u2018...\u2019
    pattern = (
        r'"([^"]*)"'           # ASCII double quotes
        r"|'([^']*)'"          # ASCII single quotes
        r"|\u201c([^\u201d]*)\u201d"  # Unicode left/right double quotes
        r"|\u2018([^\u2019]*)\u2019"  # Unicode left/right single quotes
    )
    matches = re.findall(pattern, text)
    quoted_text = " ".join(next((g for g in m if g), "") for m in matches)
    words = quoted_text.split()
    word_count = len(words)

    def calc_frames(wpm: int) -> int:
        if word_count == 0 and additional_time == 0:
            return 0
        minutes = word_count / wpm
        seconds = (minutes * 60) + additional_time
        return math.ceil(seconds * fps)

    slow_frames = calc_frames(100)
    avg_frames  = calc_frames(130)
    fast_frames = calc_frames(160)

    def to_secs(frames: int) -> float:
        return round(frames / fps, 2) if fps > 0 else 0.0

    return {
        "word_count":    word_count,
        "slow_frames":   slow_frames,
        "avg_frames":    avg_frames,
        "fast_frames":   fast_frames,
        "slow_seconds":  to_secs(slow_frames),
        "avg_seconds":   to_secs(avg_frames),
        "fast_seconds":  to_secs(fast_frames),
    }


# ---------------------------------------------------------------------------
# Image resize  (from multi_image_loader.py)
# ---------------------------------------------------------------------------

def resize_pil_image(
    pil_img: Image.Image,
    width: int,
    height: int,
    resize_method: str = "keep proportion",
    interpolation=Image.LANCZOS,
    multiple_of: int = 32,
) -> Image.Image:
    """
    Resize a PIL image using the same logic as WhatDreamsCost's MultiImageLoader.

    resize_method: "keep proportion" | "stretch" | "pad" | "crop"
    multiple_of:   snap final dimensions to a multiple of this value (0 = no snap)
    """
    MAX_RESOLUTION = 8192
    ow, oh = pil_img.size

    def snap(v: int) -> int:
        if multiple_of < 2:
            return v
        return max(multiple_of, (v // multiple_of) * multiple_of)

    if resize_method in ("keep proportion", "pad"):
        if width == 0 and oh < height:
            width = MAX_RESOLUTION
        elif width == 0:
            width = ow
        if height == 0 and ow < width:
            height = MAX_RESOLUTION
        elif height == 0:
            height = oh

        ratio = min(width / ow, height / oh)
        new_w = snap(round(ow * ratio))
        new_h = snap(round(oh * ratio))

        resized = pil_img.resize((new_w, new_h), interpolation)

        if resize_method == "pad":
            canvas = Image.new("RGB", (snap(width), snap(height)), (0, 0, 0))
            pad_l = (snap(width) - new_w) // 2
            pad_t = (snap(height) - new_h) // 2
            canvas.paste(resized, (pad_l, pad_t))
            return canvas
        return resized

    elif resize_method == "stretch":
        return pil_img.resize((snap(width) or ow, snap(height) or oh), interpolation)

    elif resize_method == "crop":
        target_w = snap(width) if width > 0 else ow
        target_h = snap(height) if height > 0 else oh
        ratio = max(target_w / ow, target_h / oh)
        scaled_w = round(ow * ratio)
        scaled_h = round(oh * ratio)
        tmp = pil_img.resize((scaled_w, scaled_h), interpolation)
        x = (scaled_w - target_w) // 2
        y = (scaled_h - target_h) // 2
        return tmp.crop((x, y, x + target_w, y + target_h))

    return pil_img  # fallback


# ---------------------------------------------------------------------------
# Video frame extraction  (from load_video_ui.py — pure logic, no ComfyUI)
# ---------------------------------------------------------------------------

def extract_video_frames(
    video_path: str,
    start_time: float = 0.0,
    end_time: float = 0.0,
    target_fps: int = 24,
    resize_method: str = "maintain aspect ratio",
    custom_width: int = 0,
    custom_height: int = 0,
    crop_x: float = 0.0,
    crop_y: float = 0.0,
    crop_w: float = 1.0,
    crop_h: float = 1.0,
) -> tuple[list[Image.Image], int, float]:
    """
    Extract frames from a video file between start_time and end_time (seconds).
    Returns (frames_list, actual_fps, duration_seconds).

    Requires PyAV:  pip install av
    """
    try:
        import av
    except ImportError:
        raise ImportError("PyAV is required for video loading.  Run: pip install av")

    frames: list[Image.Image] = []
    actual_fps = target_fps
    duration = 0.0

    with av.open(video_path) as container:
        stream = container.streams.video[0]
        native_fps = float(stream.average_rate or target_fps)
        actual_fps = target_fps or int(native_fps)

        # Total duration
        if stream.duration and stream.time_base:
            duration = float(stream.duration * stream.time_base)
        elif container.duration:
            duration = container.duration / 1_000_000.0

        t_end = end_time if end_time > 0 else duration

        stream.codec_context.skip_frame = "NONKEY"

        frame_interval = native_fps / actual_fps if actual_fps > 0 else 1
        next_frame_idx = 0.0

        for packet in container.demux(stream):
            for frame in packet.decode():
                pts_sec = float(frame.pts * stream.time_base) if frame.pts is not None else 0.0
                if pts_sec < start_time:
                    continue
                if pts_sec > t_end:
                    break

                frame_no = (pts_sec - start_time) * native_fps
                if frame_no < next_frame_idx:
                    continue
                next_frame_idx = frame_no + frame_interval

                img = frame.to_image().convert("RGB")

                # Apply crop
                if not (crop_x == 0.0 and crop_y == 0.0 and crop_w == 1.0 and crop_h == 1.0):
                    w, h = img.size
                    left   = int(crop_x * w)
                    top    = int(crop_y * h)
                    right  = int((crop_x + crop_w) * w)
                    bottom = int((crop_y + crop_h) * h)
                    img = img.crop((left, top, right, bottom))

                # Apply resize
                if custom_width > 0 or custom_height > 0:
                    _method_map = {
                        "maintain aspect ratio": "keep proportion",
                        "stretch to fit":        "stretch",
                        "pad":                   "pad",
                        "crop":                  "crop",
                    }
                    m = _method_map.get(resize_method, "keep proportion")
                    img = resize_pil_image(img, custom_width, custom_height, m)

                frames.append(img)

    return frames, actual_fps, duration


# ---------------------------------------------------------------------------
# Audio loading  (from load_audio_ui.py — pure logic)
# ---------------------------------------------------------------------------

def load_audio_tensor(filepath: str) -> tuple[torch.Tensor, int]:
    """
    Load an audio file and return (waveform_tensor [channels, samples], sample_rate).
    Requires PyAV.
    """
    try:
        import av
    except ImportError:
        raise ImportError("PyAV is required for audio loading.  Run: pip install av")

    def f32_pcm(wav: torch.Tensor) -> torch.Tensor:
        if wav.dtype.is_floating_point:
            return wav
        if wav.dtype == torch.int16:
            return wav.float() / (2 ** 15)
        if wav.dtype == torch.int32:
            return wav.float() / (2 ** 31)
        raise ValueError(f"Unsupported wav dtype: {wav.dtype}")

    with av.open(filepath) as af:
        if not af.streams.audio:
            raise ValueError("No audio stream found in the file.")
        stream = af.streams.audio[0]
        sr = stream.codec_context.sample_rate
        n_channels = stream.channels
        frames = []
        for frame in af.decode(streams=stream.index):
            buf = torch.from_numpy(frame.to_ndarray())
            if buf.shape[0] != n_channels:
                buf = buf.view(-1, n_channels).t()
            frames.append(buf)
        if not frames:
            raise ValueError("No audio frames decoded.")
        wav = torch.cat(frames, dim=1)
        wav = f32_pcm(wav)
        return wav, sr


def trim_audio_tensor(
    wav: torch.Tensor,
    sr: int,
    start_sec: float = 0.0,
    end_sec: Optional[float] = None,
) -> torch.Tensor:
    """Trim a waveform tensor [channels, samples] to [start_sec, end_sec]."""
    start_sample = int(start_sec * sr)
    end_sample   = int(end_sec * sr) if end_sec is not None else wav.shape[1]
    return wav[:, start_sample:end_sample]
