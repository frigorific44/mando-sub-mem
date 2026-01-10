import subprocess
import shutil
import pathlib


def get_subtitle_streams(input_path: pathlib.Path) -> dict:
    if not shutil.which("ffprobe"):
        print(
            "FFmpeg:ffprobe is not found in PATH. Install FFmpeg or use a separate utility to extract subtitles."
        )
    probe_args = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "s",
        "-show_entries",
        "stream=index:stream_tags=title",
        "-of",
        "csv=p=0",
        input_path,
    ]
    probe_p = subprocess.run(probe_args, encoding="utf-8", capture_output=True)
    # ffprobe does not respect argument order,
    # but the output ordering is hoped to be stable.
    sub_stream_dict = {
        line.split(",", maxsplit=1)[0]: line.split(",", maxsplit=1)[1]
        for line in probe_p.stdout.split("\n")
        if line != ""
    }
    return sub_stream_dict


def ext(input_path: pathlib.Path, stream_n: int) -> str:
    if not shutil.which("ffmpeg"):
        print(
            "FFmpeg is not found in PATH. Install FFmpeg or use a separate utility to extract subtitles."
        )
    ff_args = [
        "ffmpeg",
        "-i",
        input_path,
        "-map",
        f"0:s:{stream_n}",
        "-loglevel",
        "quiet",
        "-f",
        "srt",
        "-",
    ]
    ff_p = subprocess.run(ff_args, encoding="utf-8", capture_output=True)
    return ff_p.stdout
