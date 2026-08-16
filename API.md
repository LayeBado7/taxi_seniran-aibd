# API MVP

Base URL : `/api`

| Méthode | Route | Fonction |
|---|---|---|
| POST | `/auth/login` | Connexion |
| GET | `/me` | Profil |
| GET | `/drivers/available` | Taxis disponibles |
| POST | `/rides` | Commander un taxi |
| GET | `/rides/<id>` | Suivre une course |
| GET | `/admin/dashboard` | KPI administrateur |

Authentification : `Authorization: Bearer <JWT>`.
