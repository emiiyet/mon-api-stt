# 🎙️ Instructions de lancement - Speech to Text App

## ⚠️ Avant de commencer
- Ton Mac doit être connecté à Internet
- Docker Desktop doit être ouvert

---

## 🚀 Étape 1 : Ouvrir Docker Desktop
Clique sur l'icône Docker dans la barre des tâches et attends qu'il soit prêt (icône verte ✅)

---

## 🚀 Étape 2 : Lancer l'application (Terminal 1)
```bash
cd Desktop/mon-api-stt
docker-compose up
```
⏳ Attends de voir :
```
✅ Modèle Whisper prêt !
* Running on http://0.0.0.0:5000
```
(~2 minutes la première fois)

---

## 🚀 Étape 3 : Lancer ngrok (Terminal 2)
Ouvre un nouveau terminal (Ctrl + `)  puis :
```bash
ngrok http 5002
```
Tu verras :
```
Forwarding  https://XXXX.ngrok-free.app → localhost:5002
```

---

## 🚀 Étape 4 : Copier le lien
Copie le lien qui commence par **https://** et envoie-le à ton prof !

---

## 🚀 Étape 5 : Tester
Va sur le lien dans ton navigateur pour vérifier que tout marche avant d'envoyer !

---

## 🛑 Pour arrêter
Dans chaque terminal appuie sur :
```
Ctrl + C
```

---

## ⚠️ Points importants
- ✅ Garde ton Mac **allumé** pendant que ton prof teste
- ✅ Le lien **change** à chaque fois que tu relances ngrok
- ✅ Envoie le lien **juste avant** que ton prof teste
- ✅ Docker Desktop doit toujours être **ouvert**

---

## 🆘 Si ça ne marche pas
1. Arrête tout avec `Ctrl + C`
2. Relance Docker : `docker-compose up`
3. Relance ngrok : `ngrok http 5002`
4. Envoie le nouveau lien
