"""
FFmpeg Cut Script
Subcommands:
  probe    --input <video>
  cut      --input <video> --keep '<json>' --output <path>
  subtitle --input <cut_video> --transcript <compact_file> --cuts '<json>' --output <path>

--keep / --cuts: JSON array of {start, end} objects (seconds)
"""

import sys
import json
import re
import argparse
import os
import shutil
import subprocess
import tempfile
import ffmpeg


# ── ffmpeg path resolution ───────────────────────────────────────────────────

def _find_ffmpeg() -> str:
    """Find ffmpeg binary, preferring ffmpeg-full (has libass) over system ffmpeg."""
    full_path = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
    if os.path.isfile(full_path):
        return full_path
    return shutil.which("ffmpeg") or "ffmpeg"


def _find_ffprobe() -> str:
    """Find ffprobe binary, preferring ffmpeg-full over system ffprobe."""
    full_path = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"
    if os.path.isfile(full_path):
        return full_path
    return shutil.which("ffprobe") or "ffprobe"


FFMPEG = _find_ffmpeg()
FFPROBE = _find_ffprobe()


# ── cut ──────────────────────────────────────────────────────────────────────

def cut(input_path: str, keep_segments: list, output_path: str) -> dict:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not keep_segments:
        raise ValueError("keep_segments cannot be empty")

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    segments = sorted(keep_segments, key=lambda s: s["start"])
    inp = ffmpeg.input(input_path)

    interleaved = []
    for seg in segments:
        v = inp.video.filter("trim", start=seg["start"], end=seg["end"]).filter("setpts", "PTS-STARTPTS")
        a = inp.audio.filter("atrim", start=seg["start"], end=seg["end"]).filter("asetpts", "PTS-STARTPTS")
        interleaved.extend([v, a])

    joined = ffmpeg.concat(*interleaved, v=1, a=1)

    try:
        ffmpeg.output(joined, output_path).overwrite_output().run(
            cmd=FFMPEG, capture_stdout=True, capture_stderr=True
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr.decode()}")

    kept_duration = sum(s["end"] - s["start"] for s in segments)

    return {
        "output_path": output_path,
        "segments_kept": len(segments),
        "kept_duration_seconds": round(kept_duration, 2),
        "output_size_bytes": os.path.getsize(output_path),
    }


# ── probe ─────────────────────────────────────────────────────────────────────

def probe(file_path: str) -> dict:
    info = ffmpeg.probe(file_path, cmd=FFPROBE)
    fmt = info["format"]
    video_stream = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    return {
        "duration": float(fmt.get("duration", 0)),
        "size_bytes": int(fmt.get("size", 0)),
        "video": {
            "codec": video_stream.get("codec_name"),
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
        } if video_stream else None,
    }


# ── subtitle helpers ──────────────────────────────────────────────────────────

def parse_compact_transcript(content: str):
    """
    Parse compact transcript format produced by whisper_transcribe.py.
    Returns (language: str, segments: list[dict(start, end, text)])
    """
    lines = [l for l in content.strip().splitlines() if l and not l.startswith('#')]
    if not lines:
        raise ValueError("Empty transcript")

    header = lines[0].split('|')
    language = header[0].strip()

    word_re = re.compile(r'(.+?)\(([\d.]+),([\d.]+)\)')
    cjk_langs = {'zh', 'ja', 'ko'}

    segments = []
    for line in lines[1:]:
        parts = line.split('|', 2)
        if len(parts) < 3:
            continue
        start, end = float(parts[0]), float(parts[1])
        body = parts[2]

        if body.startswith('[') and body.endswith(']'):
            # Fallback: no word timestamps
            text = body[1:-1]
        else:
            words = word_re.findall(body)
            sep = '' if language in cjk_langs else ' '
            text = sep.join(w[0] for w in words)

        # Remove stray spaces (common in Whisper CJK output)
        text = text.replace(' ', '').strip() if language in cjk_langs else text.strip()

        segments.append({'start': start, 'end': end, 'text': text})

    return language, segments


def _remap(t: float, sorted_cuts: list) -> float:
    """Shift original timestamp t left by total duration of cuts that precede it."""
    removed = 0.0
    for c in sorted_cuts:
        if c['start'] >= t:
            break
        removed += min(c['end'], t) - c['start']
    return max(0.0, t - removed)


def _fmt_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds % 1) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _wrap_subtitle_text(text: str, max_chars: int = 12) -> str:
    """Split subtitle text into multiple lines when it exceeds max_chars per line."""
    if len(text) <= max_chars:
        return text

    lines = []
    while text:
        if len(text) <= max_chars:
            lines.append(text)
            break
        # Find split point at max_chars boundary
        split_at = max_chars
        lines.append(text[:split_at])
        text = text[split_at:]

    return '\n'.join(lines)


def generate_srt(segments: list, cuts: list) -> str:
    """
    Build SRT content with timestamps remapped to the cut video timeline.
    Segments entirely removed by cuts are skipped.
    """
    sorted_cuts = sorted(cuts, key=lambda c: c['start'])
    lines = []
    idx = 1

    for seg in segments:
        new_start = _remap(seg['start'], sorted_cuts)
        new_end = _remap(seg['end'], sorted_cuts)

        if new_end - new_start < 0.05:   # segment was entirely cut
            continue

        wrapped_text = _wrap_subtitle_text(seg['text'])
        lines += [
            str(idx),
            f"{_fmt_srt_time(new_start)} --> {_fmt_srt_time(new_end)}",
            wrapped_text,
            '',
        ]
        idx += 1

    return '\n'.join(lines)


def subtitle(input_path: str, transcript_path: str, cuts: list, output_path: str) -> dict:
    """
    Burn subtitles into an already-cut video, remapping timestamps to match the edit.
    Uses libass via ffmpeg subtitles filter; audio stream is stream-copied (no re-encode).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(transcript_path, encoding='utf-8') as f:
        content = f.read()

    language, segments = parse_compact_transcript(content)
    srt_content = generate_srt(segments, cuts)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Write SRT to a temp file in /tmp (avoids path chars that confuse ffmpeg filter parser)
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.srt', delete=False, dir='/tmp', encoding='utf-8'
    ) as tmp:
        tmp.write(srt_content)
        srt_path = tmp.name

    try:
        # Escape for ffmpeg filter syntax: colons and backslashes need escaping
        escaped = srt_path.replace('\\', '\\\\').replace(':', '\\:')

        style = (
            'FontSize=12,'
            'Spacing=1.5,'
            'PrimaryColour=&H00FFFFFF,'
            'OutlineColour=&H00000000,'
            'Outline=2,'
            'Shadow=1,'
            'Alignment=2'
        )

        # Build filter string — single quotes are ffmpeg filter-level quoting
        vf = f"subtitles='{escaped}':force_style='{style}'"

        cmd = [
            FFMPEG, '-y',
            '-i', input_path,
            '-vf', vf,
            '-c:a', 'copy',
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg subtitle error:\n{result.stderr[-2000:]}")
    finally:
        os.unlink(srt_path)

    # Count subtitles from the SRT content
    subtitle_count = len([l for l in srt_content.split('\n') if ' --> ' in l])

    return {
        "output_path": output_path,
        "subtitle_count": subtitle_count,
        "output_size_bytes": os.path.getsize(output_path),
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # cut
    cut_parser = subparsers.add_parser("cut")
    cut_parser.add_argument("--input", required=True)
    cut_parser.add_argument("--keep", required=True, help="JSON array of {start,end} to keep")
    cut_parser.add_argument("--output", required=True)

    # probe
    probe_parser = subparsers.add_parser("probe")
    probe_parser.add_argument("--input", required=True)

    # subtitle
    sub_parser = subparsers.add_parser("subtitle")
    sub_parser.add_argument("--input", required=True, help="Already-cut video file")
    sub_parser.add_argument("--transcript", required=True, help="Compact transcript file path")
    sub_parser.add_argument("--cuts", required=True, help="JSON array of {start,end} cuts that were applied")
    sub_parser.add_argument("--output", required=True)

    # check
    subparsers.add_parser("check", help="Verify ffmpeg has required filters")

    args = parser.parse_args()

    if args.command == "cut":
        result = cut(args.input, json.loads(args.keep), args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "probe":
        result = probe(args.input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "subtitle":
        result = subtitle(args.input, args.transcript, json.loads(args.cuts), args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "check":
        print(f"ffmpeg:  {FFMPEG}")
        print(f"ffprobe: {FFPROBE}")
        check = subprocess.run(
            [FFMPEG, '-filters'], capture_output=True, text=True
        )
        filters = check.stderr + check.stdout
        for name in ['subtitles', 'drawtext', 'ass']:
            found = name in filters
            print(f"  filter '{name}': {'OK' if found else 'MISSING'}")

    else:
        parser.print_help()
        sys.exit(1)
