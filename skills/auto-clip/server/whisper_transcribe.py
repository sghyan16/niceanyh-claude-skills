"""
Whisper Transcription Script
Usage: python whisper_transcribe.py <video_path> [--model medium] [--language zh]

Outputs JSON to stdout:
{
  "segments": [{"start": 0.0, "end": 2.5, "text": "...", "words": [...]}],
  "language": "zh",
  "duration": 120.4
}
"""

import sys
import json
import argparse
from faster_whisper import WhisperModel


def transcribe(file_path: str, model_size: str = "medium", language: str = None) -> dict:
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    kwargs = dict(
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=300, speech_pad_ms=200),
    )
    if language:
        kwargs["language"] = language

    segments_iter, info = model.transcribe(file_path, **kwargs)

    segments = []
    for seg in segments_iter:
        segment_data = {
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "words": [],
        }
        if seg.words:
            for w in seg.words:
                segment_data["words"].append({
                    "word": w.word,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3),
                })
        segments.append(segment_data)

    return {
        "segments": segments,
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "duration": round(info.duration, 3),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Path to video/audio file")
    parser.add_argument("--model", default="medium", help="Whisper model size (tiny/base/small/medium/large-v3)")
    parser.add_argument("--language", default=None, help="Language code e.g. zh, en. Default: auto-detect")
    args = parser.parse_args()

    result = transcribe(args.file_path, model_size=args.model, language=args.language)
    print(json.dumps(result, ensure_ascii=False, indent=2))
