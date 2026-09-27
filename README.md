<div align="center">

<img src="static/icon-512.png" alt="YoutubeOff" width="120" height="120" />

# YoutubeOff

**Télécharge tes vidéos, regarde-les hors ligne — directement dans l'appli, sur téléphone, tablette ou PC**

[![Python](https://img.shields.io/badge/Python-3.12+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-serveur_local-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-moteur_de_t%C3%A9l%C3%A9chargement-ff0000?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![PWA](https://img.shields.io/badge/PWA-installable_offline-06b6d4?style=for-the-badge&logo=pwa&logoColor=white)](#-pwa-installable--multi-appareils)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge)](LICENSE)

</div>

---

## Aperçu

YoutubeOff est un **lecteur vidéo hors ligne** doublé d'un **serveur de téléchargement** maison. Tu colles un lien (YouTube, Vimeo, Dailymotion… tout ce que gère [yt-dlp](https://github.com/yt-dlp/yt-dlp)), le serveur récupère la vidéo, et elle rejoint une bibliothèque consultable depuis tous tes appareils.

La différence avec un simple téléchargeur : **l'appli est le lecteur**. Chaque vidéo a un état « ✓ Disponible hors ligne » (copiée dans l'appareil) ou « ⤓ Rendre dispo hors ligne ». Sans aucun réseau — mode avion, métro, train — l'appli s'ouvre quand même et lit tout ce qui est marqué hors ligne.

> **Le principe en une phrase** : avec du réseau tu remplis ta bibliothèque ; sans réseau tu regardes. Une vidéo doit entrer une fois dans l'appareil, ensuite elle est à toi.

<div align="center">

| 📥 Télécharger | ✈️ Hors ligne | ▶️ Regarder |
| :---: | :---: | :---: |
| Un lien, une playlist, une qualité | Copie dans l'appli, badge « ✓ Hors ligne » | Reprise, vitesse, lecture continue |

</div>

---

## Fonctionnalités clés

### ⬇️ Téléchargement par lien
Colle un lien de **vidéo** ou de **playlist complète**. Choix de la qualité : meilleure disponible, 1080p, 720p, 480p, ou **MP3 audio seul**. Barre de progression en direct, miniature et métadonnées (titre, chaîne, durée) récupérées automatiquement.

### 📋 File d'attente
Colle plusieurs liens à la suite : ils passent en « en attente » et se téléchargent **l'un après l'autre**. Dans une playlist, une vidéo indisponible n'annule pas les autres (compteur « 3/12 »).

### 📚 Bibliothèque
Grille de miniatures avec durée, chaîne et taille. **Recherche** (titre ou chaîne), **tri** (récentes, A→Z, durée, taille, non vues d'abord). Retélécharger une vidéo déjà présente ne crée pas de doublon.

### ✈️ Hors ligne dans l'appli
- Chaque vidéo porte son état : **✓ Disponible hors ligne** ou bouton **⤓ Rendre dispo hors ligne**
- Sur téléphone, une vidéo téléchargée devient **automatiquement** disponible hors ligne
- **⤓ Tout rendre dispo hors ligne** en un geste
- Filtre **✈️ Hors ligne seulement**, activé d'office quand le serveur est injoignable
- Stockage dans l'appareil (IndexedDB), avec demande de **stockage persistant** pour que le système ne l'efface pas
- Jauge : nombre de vidéos et espace occupé sur l'appareil

### ▶️ Lecteur intégré
**Reprise de lecture** là où tu t'étais arrêté (barre de progression sous la miniature), badge **👁 vu** à la fin, vitesses **1× / 1.25× / 1.5× / 2×**, **lecture continue** avec ⏮ ⏭ (la vidéo suivante s'enchaîne dans l'ordre affiché — ta recherche ou ton tri fait office de playlist).

### 📱 PWA installable & multi-appareils
Manifest + service worker : « Ajouter à l'écran d'accueil » et l'appli se comporte comme une app native, y compris **sans réseau**. Le serveur affiche un **QR code** pour ouvrir l'appli depuis un téléphone sur le même Wi-Fi.

### 🌍 Accès partout (optionnel)
Si [Tailscale](https://tailscale.com) est installé, l'appli détecte l'adresse **https privée** créée par `tailscale serve` et l'affiche avec un second QR code : accès depuis n'importe où (4G comprise), adresse fixe, rien d'exposé sur internet.

---

## ⚠️ Important — Hors ligne sur iPhone

Sur iPhone/iPad, Safari n'autorise le mode hors ligne complet (service worker) que depuis une origine **https**. Une adresse `http://192.168.x.x:8756` permet de regarder en streaming, mais **pas d'ouvrir l'appli sans réseau**.

Deux solutions :

- **Tailscale** (recommandé) : `tailscale serve` fournit une adresse https privée valide, sans certificat à installer — voir [Accès https partout](#accès-https-partout-tailscale).
- Un reverse proxy https maison (Caddy, nginx + certificat).

### 👉 Installe l'app sur l'écran d'accueil

- **iOS Safari** : bouton « Partager » → « Sur l'écran d'accueil »
- **Android Chrome** : menu ⋮ → « Ajouter à l'écran d'accueil »

Une fois installée, l'appli tourne en mode standalone et ses vidéos hors ligne sont protégées des nettoyages automatiques.

---

## Installation locale

Prérequis : **Python 3.12+**. ffmpeg est fourni par le paquet `imageio-ffmpeg`, rien d'autre à installer.

```bash
git clone https://github.com/Fumikage-DarkShadow/YoutubeOff.git
cd YoutubeOff
pip install -r requirements.txt
python app.py
```

L'appli est accessible sur http://localhost:8756. Sous Windows, `Lancer YoutubeOff.bat` lance le serveur et ouvre le navigateur.

Les vidéos et l'index de la bibliothèque (`videos/library.json`) sont stockés dans `videos/` (ignoré par git).

### Depuis un téléphone (même Wi-Fi)

Sur la page du PC, une carte « Sur ton téléphone » affiche l'adresse locale (`http://<ip-du-pc>:8756`) et un QR code. Cette adresse change si le PC change de réseau : il suffit de rescanner.

> Le pare-feu doit autoriser Python en entrée sur le port 8756 (Windows le propose au premier lancement).

### Tourner 24/24 sur un serveur Linux

```bash
git clone https://github.com/Fumikage-DarkShadow/YoutubeOff.git ~/youtubeoff
cd ~/youtubeoff
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt

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

systemctl --user daemon-reload
systemctl --user enable --now youtubeoff
loginctl enable-linger        # démarre au boot, sans session ouverte
```

### Accès https partout (Tailscale)

```bash
sudo tailscale serve --bg --https=443 8756
```

Tailscale n'autorise que les ports https **443, 8443 et 10000** : si 443 est déjà pris par un autre service, utilise `--https=8443` ou `--https=10000`. L'appli repère toute seule l'entrée `tailscale serve` qui pointe vers son port et l'affiche avec un QR code (« 🌍 Partout »).

> Utilise `tailscale serve` (privé, réservé à tes appareils), **pas** `tailscale funnel` (public).

---

## Architecture

```
app.py                     Serveur Flask
├── /api/download          Ajoute un lien à la file d'attente (yt-dlp, client Android pour éviter les 403)
├── /api/jobs              Progression des téléchargements
├── /api/videos            Bibliothèque (entrées dont le fichier existe encore)
├── /media/<fichier>       Vidéos et miniatures, avec support des requêtes Range
├── /api/info, /api/qr     Adresses locale / Tailscale et QR codes
└── /sw.js                 Service worker (en-tête Service-Worker-Allowed)

templates/index.html       L'application (une seule page, sans framework)
├── Bibliothèque           recherche, tri, filtre hors ligne, badges
├── Stockage hors ligne    IndexedDB (vidéo + miniature en blob), stockage persistant
├── Lecteur                reprise, vitesse, lecture continue
└── Téléchargements        file d'attente, mise à dispo automatique sur téléphone

static/                    manifest.json, sw.js, icônes PWA
tools/make_icons.py        Régénère les icônes (pip install pillow)
ios/                       Variante iOS native SwiftUI, expérimentale (liens directs + import Fichiers)
Lancer YoutubeOff.bat      Lanceur Windows
```

---

## Personnaliser

### Changer le port
`PORT = 8756` dans [`app.py`](app.py) (et dans `Lancer YoutubeOff.bat` / `.claude/launch.json` si tu les utilises).

### Ajouter un choix de qualité
Ajoute une entrée au dictionnaire `FORMATS` de [`app.py`](app.py) (syntaxe des [sélecteurs de format yt-dlp](https://github.com/yt-dlp/yt-dlp#format-selection)) et une `<option>` dans le `<select id="quality">` de [`templates/index.html`](templates/index.html).

### Régénérer les icônes

```bash
pip install pillow
python tools/make_icons.py
```

### Variante iOS native
Le dossier [`ios/`](ios/README.md) contient une petite app SwiftUI (iOS 17+) qui télécharge des **liens directs** vers des fichiers vidéo et importe depuis Fichiers, avec lecture hors ligne. Elle ne traite pas les pages YouTube : c'est le serveur Python qui s'en charge.

---

## Dépannage

| Symptôme | Cause probable | Solution |
| --- | --- | --- |
| « HTTP Error 403 » ou « Sign in to confirm » | YouTube a changé quelque chose | `pip install -U yt-dlp` puis relancer le serveur |
| Le téléphone n'atteint plus le PC | L'adresse Wi-Fi du PC a changé | Rescanner le QR code sur le PC, ou passer par Tailscale (adresse fixe) |
| Ancienne version affichée après une mise à jour | Cache du service worker | Recharger deux fois, ou désinstaller/réinstaller l'appli de l'écran d'accueil |
| Une vidéo n'apparaît plus | Son fichier a été supprimé de `videos/` | Normal : l'entrée est retirée automatiquement de la bibliothèque |
| Pas de mode hors ligne sur iPhone | Origine http | Ouvrir l'appli depuis une adresse https (voir plus haut) |

---

## Note

Outil d'usage personnel. Respecte les conditions d'utilisation des plateformes et les droits des contenus que tu télécharges.

## Licence

[MIT](LICENSE)
