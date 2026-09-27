# YoutubeOff

Télécharge des vidéos (YouTube, Vimeo, Dailymotion… tout ce que gère [yt-dlp](https://github.com/yt-dlp/yt-dlp)) sur un serveur maison, puis regarde-les **hors ligne, directement dans l'appli**, sur téléphone, tablette ou PC.

L'appli est un lecteur à part entière : chaque vidéo a un état **« ✓ Disponible hors ligne »** (copiée dans l'appareil) ou **« ⤓ Rendre dispo hors ligne »**. Sans réseau, elle s'ouvre quand même et lit tout ce qui est marqué hors ligne.

## Fonctionnalités

- Téléchargement par lien (vidéo seule ou **playlist complète**), choix de la qualité (meilleure, 1080p, 720p, 480p, MP3 audio seul)
- **File d'attente** : plusieurs liens à la suite, traités l'un après l'autre
- Bibliothèque avec miniatures, **recherche**, tri (récentes, A→Z, durée, taille, non vues)
- **Hors ligne dans l'appli** : mise à disposition automatique sur téléphone après un téléchargement, bouton « Tout rendre dispo hors ligne », filtre ✈️ « Hors ligne seulement » (forcé sans réseau)
- Lecteur intégré : **reprise de lecture**, badge « vu », vitesses 1× / 1.25× / 1.5× / 2×, **lecture continue** (suivant / précédent)
- **PWA installable** (« Ajouter à l'écran d'accueil ») avec service worker
- Accès depuis les autres appareils : QR code Wi-Fi local + adresse [Tailscale](https://tailscale.com) (https privé via `tailscale serve`, nécessaire pour le hors ligne complet sur iPhone)
- Jauge de stockage utilisé sur l'appareil

## Installation (serveur)

Python 3.12+ requis. ffmpeg est fourni par `imageio-ffmpeg`, rien d'autre à installer.

```bash
pip install -r requirements.txt
python app.py
```

Puis ouvrir http://localhost:8756. Sous Windows, `Lancer YoutubeOff.bat` fait les deux.

Les vidéos et la bibliothèque (`videos/library.json`) sont stockées dans `videos/` (ignoré par git).

### Tourner 24/24 sur un serveur Linux

```bash
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
# service systemd utilisateur
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/youtubeoff.service <<'EOF'
[Unit]
Description=YoutubeOff
After=network-online.target
[Service]
WorkingDirectory=%h/youtubeoff
ExecStart=%h/youtubeoff/venv/bin/python app.py
Restart=always
RestartSec=5
[Install]
WantedBy=default.target
EOF
systemctl --user enable --now youtubeoff
loginctl enable-linger
```

Pour un accès https privé depuis n'importe où (et le hors ligne complet sur iPhone) :

```bash
sudo tailscale serve --bg --https=10000 8756
```

L'appli détecte l'adresse `tailscale serve` qui pointe vers son port et l'affiche avec un QR code.

## Utilisation sur téléphone

1. Ouvrir l'adresse affichée sur le PC (QR « Même Wi-Fi » ou « Partout (Tailscale) »).
2. Menu du navigateur → **Ajouter à l'écran d'accueil**.
3. Coller un lien : la vidéo arrive et devient automatiquement disponible hors ligne dans l'appli.
4. Sans réseau, ouvrir l'appli : les vidéos « ✓ Hors ligne » se lisent normalement.

> Sur iPhone, le mode hors ligne (service worker) exige une origine **https** — d'où Tailscale. Une adresse `http://192.168.x.x` fonctionne pour regarder en streaming, mais pas pour ouvrir l'appli sans réseau.

## Structure

```
app.py                  serveur Flask + yt-dlp (file d'attente, playlists, QR, détection Tailscale)
templates/index.html    l'application (bibliothèque, lecteur, stockage hors ligne IndexedDB)
static/                 manifest PWA, service worker, icônes
ios/                    variante iOS native SwiftUI (expérimentale) : liens directs + import Fichiers, lecture hors ligne
```

## Note

Outil d'usage personnel : respecte les conditions d'utilisation des plateformes et les droits des contenus que tu télécharges.
