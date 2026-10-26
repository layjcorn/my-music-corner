# My Music

A tiny static music player: one `index.html` (no frameworks, no build step) plus a `library.json` listing your tracks. Features: albums, playlists (.m3u), search, shuffle all, shuffle/play per album, repeat, lock-screen controls, and playback with the screen off.

## 1. Shrink your music first (important)

FLAC/WAV are too big for GitHub and slow on a phone connection. GitHub Pages sites are limited to ~1 GB, files to 100 MB, and GitHub discourages using it as a media host. Convert a copy of your library to Opus or MP3 (same folder structure):

**Opus** (smallest, great quality at 128 kbps; plays on current Chrome/Firefox/Android, and Safari 17+):
```bash
find "/path/to/music" -type f \( -iname '*.flac' -o -iname '*.wav' \) | while read -r f; do
  out="/path/to/music-small/${f#/path/to/music/}"; out="${out%.*}.opus"
  mkdir -p "$(dirname "$out")"; ffmpeg -n -i "$f" -vn -c:a libopus -b:a 128k "$out"
done
```
**MP3** (works on essentially every old phone, so choose this if Opus fails):
```bash
# same loop, replace the encode step with:  -c:a libmp3lame -q:a 2   and use .mp3
```
A 1,000-album library at 128 kbps is roughly 40–60 GB; a few hundred albums fit comfortably in a cheap bucket.

## 2. Where to put the audio

| Option | Cost | Notes |
|---|---|---|
| **Cloudflare R2** | Free up to 10 GB, no egress fees | Best fit. Enable a public bucket URL and add a CORS rule allowing GET from your site. |
| **Backblaze B2** + Cloudflare | Cheap, free egress via Cloudflare | Slightly more setup. |
| **In the GitHub repo** (`audio/` folder) | Free | Only for a small library (well under 1 GB), using the converted files. |

## 3. Build the library file

```bash
pip install mutagen          # optional: reads artist/album/title tags
python build_library.py "/path/to/music-small" --base https://YOUR-BUCKET-URL/
# or for audio inside the repo:
python build_library.py "/path/to/music-small"          # uses audio/
```
Any `.m3u`/`.m3u8` files in the music folder show up as playlists. Re-run the script whenever you add music, then commit the new `library.json`.

## 4. Publish on GitHub

1. Create a repo and add `index.html` and `library.json` (plus `audio/` if hosting there).
2. Settings → Pages → deploy from branch `main`, folder `/ (root)`.
3. Open `https://YOUR-USERNAME.github.io/REPO-NAME/` on your phone and use the browser's "Add to home screen".

If the repo is public, your library list (and any audio in it) is public. Use a private bucket URL you don't share, or keep the repo private if your plan supports private Pages.

## Screen-off tips
- Playback uses a single plain `<audio>` element and the Media Session API, which is what mobile browsers allow to keep running with the screen off.
- If a very old browser pauses when the screen locks, try Chrome or Firefox for Android; on iPhones, add the site to the home screen first.
- The next track's first chunk is pre-fetched so changes between songs are quick; unplayable files are skipped automatically.