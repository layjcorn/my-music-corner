#!/usr/bin/env python3
"""Scan a music folder and write library.json for the player.

Usage:
    python build_library.py /path/to/music                 # audio hosted next to the site (audio/ folder)
    python build_library.py /path/to/music --base https://your-bucket.example.com/music/

Optional: pip install mutagen   (reads artist/album/title tags; otherwise folder names are used)
Playlists: any .m3u / .m3u8 file inside the music folder becomes a playlist.
"""
import argparse, json, os, sys
from pathlib import Path

EXTS = {".flac", ".wav", ".mp3", ".m4a", ".ogg", ".opus", ".aac"}

try:
    import mutagen
except ImportError:
    mutagen = None


def tags(path: Path, root: Path):
    rel = path.relative_to(root)
    parts = rel.parts
    title = path.stem
    album = parts[-2] if len(parts) >= 2 else ""
    artist = parts[-3] if len(parts) >= 3 else ""
    if mutagen:
        try:
            m = mutagen.File(path, easy=True)
            if m:
                g = lambda k: (m.get(k) or [""])[0]
                title = g("title") or title
                album = g("album") or album
                artist = g("artist") or g("albumartist") or artist
                tn = g("tracknumber").split("/")[0]
                return title, artist, album, int(tn) if tn.isdigit() else 0
        except Exception:
            pass
    return title, artist, album, 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("music_dir")
    ap.add_argument("--base", default="audio/", help="URL prefix where audio files are served from")
    ap.add_argument("--out", default="library.json")
    args = ap.parse_args()

    root = Path(args.music_dir).resolve()
    files = sorted(p for p in root.rglob("*") if p.suffix.lower() in EXTS)
    if not files:
        sys.exit("No audio files found.")

    entries = []
    for p in files:
        title, artist, album, tn = tags(p, root)
        entries.append((album, tn, p.name.lower(), {"t": title, "a": artist, "al": album, "f": p.relative_to(root).as_posix()}))
    entries.sort(key=lambda e: (e[0].lower(), e[1], e[2]))
    tracks = [e[3] for e in entries]
    index = {t["f"]: i for i, t in enumerate(tracks)}

    playlists = []
    for pl in sorted(list(root.rglob("*.m3u")) + list(root.rglob("*.m3u8"))):
        ids = []
        for line in pl.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                rel = (pl.parent / line.replace("\\", "/")).resolve().relative_to(root).as_posix()
            except ValueError:
                continue
            if rel in index:
                ids.append(index[rel])
        if ids:
            playlists.append({"name": pl.stem, "tracks": ids})

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"base": args.base, "tracks": tracks, "playlists": playlists}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(tracks)} tracks, {len(playlists)} playlists -> {args.out} ({os.path.getsize(args.out)//1024} KB)")


if __name__ == "__main__":
    main()
