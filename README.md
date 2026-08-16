# 🚕 TAXI SENIRAN AIBD

Plateforme de mobilité AIBD : passager, chauffeur, supervision, file taxi, réservations, partenaires et finance.

## Déploiement Render + GitHub

Le projet est **Render-ready**.

➡️ Voir **[RENDER_DEPLOY.md](RENDER_DEPLOY.md)**.

Le fichier `render.yaml` est à la racine du dépôt et décrit :
- API Flask;
- PostgreSQL;
- variables d'environnement;
- health check;
- déploiement automatique.

## Architecture

```text
Passager Flutter ─┐
Chauffeur Flutter ├── HTTPS/WebSocket ──> Flask API ──> PostgreSQL
Admin Web ─────────┘                         │
                                            ├── SMS
                                            ├── Paiement
                                            └── Notifications
```

## Démonstration locale

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
python run.py
```

Health check :

```text
http://127.0.0.1:5000/api/health
```

## Important

Les comptes, clés SMS, clés de paiement, Firebase, domaine et certificats mobiles ne doivent jamais être placés dans Git.

## 🔐 Administrateur unique
Aucune inscription publique. Seul le compte administrateur principal crée les comptes Passager et Chauffeur. L'OTP ne crée jamais de compte.
