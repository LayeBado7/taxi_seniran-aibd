# API V1.2

## Passager
- `POST /auth/login`
- `GET /me`
- `POST /rides`
- `GET /rides`
- `GET /rides/<id>`
- `POST /rides/<id>/rating`
- `GET /tariffs`

## Chauffeur
- `GET /drivers/me`
- `GET /rides`
- `POST /drivers/status`
- `POST /drivers/location`
- `POST /rides/<id>/accept`
- `POST /rides/<id>/start`
- `POST /rides/<id>/complete`

## Administration
- `GET /admin/dashboard`
- `POST /admin/tariffs`
- `POST /admin/assign-next/<ride_id>`

Toutes les routes protégées utilisent JWT.
