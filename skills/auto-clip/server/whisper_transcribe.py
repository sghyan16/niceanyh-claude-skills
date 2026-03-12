"""
Whisper Transcription Script
Usage: python whisper_transcribe.py <video_path> [--model medium] [--language zh] [--format compact|json]

Compact format (default, token-efficient):
  Line 1:  lang|duration
  Lines 2+: start|end|word1(ws,we) word2(ws,we) ...

  Example:
    zh|187.40
    0.00|3.20|好(0.00,0.30) 那个(0.40,0.80) 今天(1.10,1.50) 我们来聊聊(1.50,3.20)
    3.20|7.80|就是说(3.20,3.80) 内容创作(3.80,5.20) 这件事情(5.20,7.80)

JSON format (--format json):
  Full nested JSON with words array (verbose, for debugging).
"""

import sys
import json
import argparse
from faster_whisper import WhisperModel


def transcribe_raw(file_path: str, model_size: str = "medium", language: str = None):
    """Returns (segments_list, info) where each segment has start/end/text/words."""
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
        words = []
        if seg.words:
            for w in seg.words:
                words.append((w.word.strip(), round(w.start, 2), round(w.end, 2)))
        segments.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
            "words": words,  # list of (word, start, end)
        })

    return segments, info


def format_compact(segments, info) -> str:
    """
    Compact line-per-segment format. ~77% fewer tokens than nested JSON.
    Header: lang|duration
    Segments: start|end|word(ws,we) word(ws,we) ...
    Falls back to plain text if no word timestamps.
    """
    lines = [f"{info.language}|{round(info.duration, 2)}"]
    for seg in segments:
        prefix = f"{seg['start']:.2f}|{seg['end']:.2f}|"
        if seg["words"]:
            words_inline = " ".join(f"{w}({ws:.2f},{we:.2f})" for w, ws, we in seg["words"])
            lines.append(prefix + words_inline)
        else:
            # No word timestamps: fall back to plain text marker
            lines.append(prefix + f"[{seg['text']}]")
    return "\n".join(lines)


def format_json(segments, info) -> str:
    result = {
        "segments": [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "words": [
                    {"word": w, "start": ws, "end": we}
                    for w, ws, we in seg["words"]
                ],
            }
            for seg in segments
        ],
        "language": info.language,
        "duration": round(info.duration, 2),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Path to video/audio file")
    parser.add_argument("--model", default="medium", help="Whisper model size (tiny/base/small/medium/large-v3)")
    parser.add_argument("--language", default=None, help="Language code e.g. zh, en. Default: auto-detect")
    parser.add_argument("--format", default="compact", choices=["compact", "json"],
                        help="Output format: compact (default, token-efficient) or json (verbose, for debugging)")
    args = parser.parse_args()

    segments, info = transcribe_raw(args.file_path, model_size=args.model, language=args.language)

    if args.format == "compact":
        print(format_compact(segments, info))
    else:
        print(format_json(segments, info))
