"""YoutubeOff — télécharge des vidéos et regarde-les hors ligne.

Lancer avec :  python app.py   puis ouvrir http://localhost:8756
"""
import io
import json
import os
import queue
import re
import socket
import subprocess
import threading
import uuid
from pathlib import Path

import imageio_ffmpeg
import yt_dlp
from flask import Flask, jsonify, request, send_from_directory, render_template

BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = BASE_DIR / "videos"
VIDEOS_DIR.mkdir(exist_ok=True)
LIBRARY_FILE = VIDEOS_DIR / "library.json"

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

app = Flask(__name__)

_lock = threading.Lock()
jobs = {}  # job_id -> {status, progress, title, error}


def load_library():
    if LIBRARY_FILE.exists():
        try:
            return json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_library(items):
    LIBRARY_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


FORMATS = {
    "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    "1080": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "720": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "480": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "audio": "bestaudio/best",
}


def _progress_hook(job_id):
    def hook(d):
        with _lock:
            job = jobs.get(job_id)
            if not job:
                return
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                if total:
                    job["progress"] = round(d.get("downloaded_bytes", 0) / total * 100, 1)
                inf = d.get("info_dict") or {}
                idx, cnt = inf.get("playlist_index"), inf.get("n_entries")
                job["status"] = (
                    f"téléchargement {idx}/{cnt}"
                    if idx and cnt and cnt > 1
                    else "téléchargement"
                )
            elif d["status"] == "finished":
                job["progress"] = 100
                job["status"] = "conversion"
    return hook


def make_entry(info, audio_only, url):
    """Construit l'entrée de bibliothèque à partir des métadonnées yt-dlp."""
    ext = "mp3" if audio_only else "mp4"
    vid_id = info.get("id", "")
    media_file = thumb_file = None
    for f in VIDEOS_DIR.iterdir():
        if f"[{vid_id}]" not in f.name:
            continue
        if media_file is None and f.suffix.lstrip(".") in (ext, "mkv", "webm", "m4a"):
            media_file = f
        if thumb_file is None and f.suffix in (".jpg", ".png", ".webp"):
            thumb_file = f
    if not media_file:
        return None
    return {
        "id": str(uuid.uuid4()),
        "video_id": vid_id,
        "title": info.get("title") or media_file.stem,
        "uploader": info.get("uploader") or info.get("channel") or "",
        "duration": info.get("duration") or 0,
        "source": info.get("webpage_url") or url,
        "site": info.get("extractor_key", ""),
        "file": media_file.name,
        "thumbnail": thumb_file.name if thumb_file else None,
        "audio_only": audio_only,
        "date": info.get("upload_date", ""),
        "size": media_file.stat().st_size,
    }


def download_worker(job_id, url, quality):
    audio_only = quality == "audio"
    is_playlist = "list=" in url or "/playlist" in url
    with _lock:
        jobs[job_id]["status"] = "démarrage"
    outtmpl = str(VIDEOS_DIR / "%(title).150s [%(id)s].%(ext)s")
    opts = {
        "format": FORMATS.get(quality, FORMATS["best"]),
        "outtmpl": outtmpl,
        "ffmpeg_location": FFMPEG_EXE,
        # YouTube renvoie souvent des 403 avec le client web par défaut ;
        # le client Android reste fiable (cf. yt-dlp issue #12482)
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "writethumbnail": True,
        "noplaylist": not is_playlist,
        "ignoreerrors": is_playlist,  # une vidéo cassée n'annule pas toute la playlist
        "progress_hooks": [_progress_hook(job_id)],
        "postprocessors": [],
        "quiet": True,
        "no_warnings": True,
    }
    if audio_only:
        opts["postprocessors"].append(
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
        )
    else:
        opts["merge_output_format"] = "mp4"
    opts["postprocessors"].append({"key": "FFmpegThumbnailsConvertor", "format": "jpg"})

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        if not info:
            raise RuntimeError("Téléchargement impossible (lien invalide ou vidéo indisponible)")
        infos = [i for i in (info.get("entries") or [info]) if i]

        entries = []
        with _lock:
            lib = load_library()
            for inf in infos:
                entry = make_entry(inf, audio_only, url)
                if not entry:
                    continue
                # Si la même vidéo est retéléchargée : on remplace l'entrée mais on
                # garde son id, pour ne pas casser les copies déjà sur les appareils
                existing = next(
                    (e for e in lib
                     if e.get("video_id") == entry["video_id"]
                     and e.get("audio_only") == audio_only),
                    None,
                )
                if existing:
                    entry["id"] = existing["id"]
                lib = [
                    e for e in lib
                    if not (e.get("video_id") == entry["video_id"]
                            and e.get("audio_only") == audio_only)
                ]
                lib.insert(0, entry)
                entries.append(entry)
            if entries:
                save_library(lib)

        if not entries:
            raise RuntimeError("Aucune vidéo téléchargée (lien invalide ou vidéos indisponibles)")

        title = entries[0]["title"]
        if len(entries) > 1:
            title = f"{info.get('title') or 'Playlist'} ({len(entries)} vidéos)"
        with _lock:
            jobs[job_id].update(
                status="terminé", progress=100, title=title,
                entry_id=entries[0]["id"], entry_ids=[e["id"] for e in entries],
            )
    except Exception as e:
        msg = re.sub(r"\x1b\[[0-9;]*m", "", str(e))
        with _lock:
            jobs[job_id].update(status="erreur", error=msg)


# File d'attente : les téléchargements s'exécutent l'un après l'autre
_task_q = queue.Queue()


def _queue_worker():
    while True:
        job_id, url, quality = _task_q.get()
        try:
            download_worker(job_id, url, quality)
        finally:
            _task_q.task_done()


threading.Thread(target=_queue_worker, daemon=True).start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()
    quality = data.get("quality", "best")
    if not url.lower().startswith(("http://", "https://")):
        return jsonify({"error": "URL invalide"}), 400
    job_id = str(uuid.uuid4())
    with _lock:
        jobs[job_id] = {"status": "en attente", "progress": 0, "url": url, "title": "", "error": None}
    _task_q.put((job_id, url, quality))
    return jsonify({"job_id": job_id})


@app.route("/api/jobs")
def api_jobs():
    with _lock:
        return jsonify(jobs)


@app.route("/api/videos")
def api_videos():
    # Ne montre que les vidéos dont le fichier existe encore sur le disque
    lib = load_library()
    valid = [v for v in lib if (VIDEOS_DIR / v["file"]).exists()]
    if len(valid) != len(lib):
        with _lock:
            save_library(valid)
    return jsonify(valid)


@app.route("/api/videos/<item_id>", methods=["DELETE"])
def api_delete(item_id):
    with _lock:
        lib = load_library()
        keep, removed = [], None
        for it in lib:
            if it["id"] == item_id:
                removed = it
            else:
                keep.append(it)
        if not removed:
            return jsonify({"error": "introuvable"}), 404
        for key in ("file", "thumbnail"):
            name = removed.get(key)
            if name:
                p = VIDEOS_DIR / name
                if p.exists():
                    p.unlink()
        save_library(keep)
    return jsonify({"ok": True})


@app.route("/media/<path:filename>")
def media(filename):
    return send_from_directory(VIDEOS_DIR, filename, conditional=True)


def get_lan_ip():
    """IP locale du PC sur le réseau Wi-Fi/Ethernet."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def get_tailscale_ip():
    """Adresse Tailscale du PC (100.64.0.0/10), si le VPN est installé."""
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            parts = ip.split(".")
            if parts[0] == "100" and 64 <= int(parts[1]) <= 127:
                return ip
    except (OSError, ValueError):
        pass
    return None


def get_tailscale_https():
    """URL https privée (tailscale serve) qui pointe vers CETTE appli —
    indispensable pour que l'appli fonctionne 100% hors ligne sur iPhone/iPad.
    On cherche le bloc dont le proxy cible notre port, car la machine peut
    héberger d'autres services Tailscale."""
    try:
        out = subprocess.run(
            ["tailscale", "serve", "status"],
            capture_output=True, text=True, timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).stdout
        current = None
        for line in out.splitlines():
            m = re.match(r"(https://\S+)", line.strip())
            if m:
                current = m.group(1).rstrip("/")
            elif current and "proxy" in line and f":{PORT}" in line:
                return current
        return None
    except (OSError, subprocess.SubprocessError):
        return None


TS_HTTPS = None  # détecté au démarrage


def tailscale_url():
    global TS_HTTPS
    if not TS_HTTPS:
        TS_HTTPS = get_tailscale_https()
    if TS_HTTPS:
        return TS_HTTPS
    ts_ip = get_tailscale_ip()
    return f"http://{ts_ip}:{PORT}" if ts_ip else None


@app.route("/api/info")
def api_info():
    return jsonify({"ip": get_lan_ip(), "ts_url": tailscale_url(), "port": PORT})


@app.route("/api/qr")
def api_qr():
    import qrcode
    import qrcode.image.svg

    url = f"http://{get_lan_ip()}:{PORT}"
    if request.args.get("which") == "ts":
        url = tailscale_url() or url
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=14)
    buf = io.BytesIO()
    img.save(buf)
    return app.response_class(buf.getvalue(), mimetype="image/svg+xml")


@app.route("/sw.js")
def service_worker():
    resp = send_from_directory(BASE_DIR / "static", "sw.js")
    resp.headers["Service-Worker-Allowed"] = "/"
    resp.headers["Cache-Control"] = "no-cache"
    return resp


PORT = 8756

if __name__ == "__main__":
    TS_HTTPS = get_tailscale_https()
    ip = get_lan_ip()
    print(f"YoutubeOff -> sur ce PC : http://localhost:{PORT}")
    print(f"              sur ton téléphone (même Wi-Fi) : http://{ip}:{PORT}")
    if TS_HTTPS:
        print(f"              partout via Tailscale : {TS_HTTPS}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
