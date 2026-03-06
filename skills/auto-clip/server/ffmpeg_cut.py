"""
FFmpeg Cut Script
Usage: python ffmpeg_cut.py --input <video_path> --keep '<json>' --output <output_path>

--keep: JSON array of segments to KEEP, e.g. '[{"start":0,"end":12.3},{"start":15.7,"end":60}]'

Outputs JSON to stdout:
{
  "output_path": "...",
  "segments_kept": 3,
  "kept_duration_seconds": 87.4,
  "output_size_bytes": 12345678
}
"""

import sys
import json
import argparse
import os
import ffmpeg


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
            capture_stdout=True, capture_stderr=True
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


def probe(file_path: str) -> dict:
    info = ffmpeg.probe(file_path)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # cut subcommand
    cut_parser = subparsers.add_parser("cut")
    cut_parser.add_argument("--input", required=True, help="Input video path")
    cut_parser.add_argument("--keep", required=True, help="JSON array of {start, end} segments to keep")
    cut_parser.add_argument("--output", required=True, help="Output video path")

    # probe subcommand
    probe_parser = subparsers.add_parser("probe")
    probe_parser.add_argument("--input", required=True, help="Video file to probe")

    args = parser.parse_args()

    if args.command == "cut":
        keep_segments = json.loads(args.keep)
        result = cut(args.input, keep_segments, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "probe":
        result = probe(args.input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()
        sys.exit(1)
