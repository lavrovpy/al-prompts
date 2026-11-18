"""Assemble scene videos, and optionally a full cut, from cards and raw clips.

Usage: python3 assemble.py <scenes.json> [scene ...|all]   (no scene: every scene, then the full cut)

Cards are PNGs held still; clips are trimmed, scaled to 1920x1080 and joined at 30 fps.
See examples/scenes.example.json for the format.
"""

import json
import subprocess
import sys
from pathlib import Path

NORM = "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p,setsar=1"
ENCODE = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart"]


def concat(inputs: list[str], count: int, out: Path, trim_pts: bool) -> Path:
    pts = "setpts=PTS-STARTPTS," if trim_pts else ""
    filters = [f"[{i}:v]{pts}{NORM}[v{i}]" for i in range(count)]
    graph = (
        ";".join(filters)
        + ";"
        + "".join(f"[v{i}]" for i in range(count))
        + f"concat=n={count}:v=1:a=0[out]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            *inputs,
            "-filter_complex",
            graph,
            "-map",
            "[out]",
            *ENCODE,
            str(out),
        ],
        check=True,
    )
    return out


def build_scene(cfg: dict, root: Path, key: str) -> Path:
    scene = cfg["scenes"][key]
    raw, cards = root / cfg.get("raw_dir", "raw"), root / cfg.get("cards_dir", "cards")
    inputs = []
    for part in scene["parts"]:
        if part[0] == "card":
            _, name, seconds = part
            inputs += ["-loop", "1", "-t", str(seconds), "-i", str(cards / f"{name}.png")]
        else:
            _, name, start, end = part
            inputs += (
                ["-ss", str(start)]
                + (["-to", str(end)] if end is not None else [])
                + ["-i", str(raw / f"{name}.mp4")]
            )
    return concat(inputs, len(scene["parts"]), root / f"{scene['name']}.mp4", trim_pts=True)


def build_full(cfg: dict, root: Path) -> Path:
    full, cards = cfg["full"], root / cfg.get("cards_dir", "cards")
    inputs = [
        "-loop",
        "1",
        "-t",
        str(full.get("card_seconds", 5)),
        "-i",
        str(cards / f"{full['open']}.png"),
    ]
    for key in cfg["scenes"]:
        inputs += ["-i", str(root / f"{cfg['scenes'][key]['name']}.mp4")]
    inputs += [
        "-loop",
        "1",
        "-t",
        str(full.get("card_seconds", 5)),
        "-i",
        str(cards / f"{full['close']}.png"),
    ]
    return concat(inputs, len(cfg["scenes"]) + 2, root / f"{full['name']}.mp4", trim_pts=False)


if __name__ == "__main__":
    path = Path(sys.argv[1]).expanduser()
    cfg = json.loads(path.read_text())
    root = Path(cfg.get("root", path.parent)).expanduser()
    wanted = sys.argv[2:] or [*cfg["scenes"], *(["all"] if "full" in cfg else [])]
    for key in wanted:
        print(build_full(cfg, root) if key == "all" else build_scene(cfg, root, key))
