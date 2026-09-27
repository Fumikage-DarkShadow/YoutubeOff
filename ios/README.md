# YoutubeOff pour iPhone

Cette version est une application iOS native : les vidéos importées ou téléchargées depuis un lien direct sont enregistrées dans le stockage de l'iPhone et restent lisibles sans réseau.

## Ouvrir sur Mac

1. Ouvrir `ios/YoutubeOff` dans Xcode et créer un projet iOS SwiftUI nommé `YoutubeOff` (iOS 17 minimum).
2. Remplacer les fichiers générés par les quatre fichiers Swift et `Info.plist` de ce dossier.
3. Dans *Signing & Capabilities*, choisir son compte Apple personnel, puis installer sur l'iPhone.

Le compte Apple gratuit permet les essais sur son propre iPhone. Une app personnelle signée avec un compte gratuit doit être renouvelée régulièrement ; un abonnement Apple Developer évite cette contrainte pour la distribution.

## Limite importante

L'app télécharge les liens directs vers des fichiers vidéo autorisés (MP4, MOV, etc.) et importe les fichiers depuis Fichiers. Une URL de page YouTube/TikTok n'est pas une URL de fichier vidéo : son traitement nécessite un moteur propre à chaque plateforme et doit respecter les règles de la plateforme ainsi que les droits du contenu.
