# Déployer TAXI SENIRAN AIBD sur Render via GitHub

Le dépôt contient déjà `render.yaml`. Render peut donc créer le service Flask et la base PostgreSQL depuis un Blueprint.

## 1. Mettre le projet sur GitHub

Depuis le dossier du projet :

```bash
git init
git add .
git commit -m "TAXI SENIRAN AIBD - Render ready"
git branch -M main
git remote add origin https://github.com/VOTRE_COMPTE/taxi-seniran-aibd.git
git push -u origin main
```

## 2. Connecter GitHub à Render

Dans Render :
1. New → Blueprint
2. Connect GitHub
3. sélectionner `taxi-seniran-aibd`
4. sélectionner `main`
5. vérifier le Blueprint
6. Deploy Blueprint

Render lit `render.yaml` à la racine et crée les ressources déclarées.

## 3. Ressources créées

- Web Service : `taxi-seniran-aibd-api`
- PostgreSQL : `taxi-seniran-db`

Le service utilise :
- Python 3.13.5
- Gunicorn + Eventlet
- Flask
- PostgreSQL
- WebSocket/Socket.IO

## 4. Variables

`DATABASE_URL` est fourni automatiquement par la base Render.
`JWT_SECRET_KEY` est généré automatiquement.

Avant production, remplacer :
- `SMS_PROVIDER=demo`
- `PAYMENT_MODE=sandbox`
- `PAYMENT_WEBHOOK_VERIFY=false`

par les paramètres des prestataires réellement contractualisés.

## 5. URL

Après déploiement, Render fournit une URL de type :

`https://taxi-seniran-aibd-api.onrender.com`

Tester :

`GET /api/health`

Réponse attendue :

```json
{"status":"ok","service":"taxi-seniran-aibd"}
```

## 6. Déploiements automatiques

Une fois GitHub connecté, chaque push sur `main` peut déclencher automatiquement un nouveau déploiement.

## 7. Attention

La publication des applications mobiles sur Google Play et Apple App Store est distincte du déploiement du backend Render.
