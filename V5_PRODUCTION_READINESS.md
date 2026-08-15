# TAXI SENIRAN AIBD — V5 Production Readiness

## Architecture
Mobile Flutter → HTTPS API Flask → PostgreSQL
                      ↘ WebSocket → supervision temps réel

## V5 ajoutée
- endpoint de santé `/api/health`
- serveur Gunicorn
- PostgreSQL driver
- Docker production
- permissions Android GPS/Internet
- modèle de politique de confidentialité
- checklists Google Play / Apple App Store
- baseline sécurité
- CI GitHub
- audit API
- webhook paiement préparé

## Services externes restant à contractualiser/configurer
1. fournisseur SMS OTP;
2. cartographie/navigation;
3. Firebase Cloud Messaging;
4. Wave;
5. Orange Money;
6. éventuellement paiement carte;
7. hébergement et domaine HTTPS;
8. comptes stores.

## Ordre recommandé
1. environnement de recette;
2. 5–10 taxis pilotes;
3. tests sécurité;
4. tests GPS/réseau;
5. validation exploitation AIBD;
6. contractualisation paiements/SMS;
7. bêta fermée;
8. publication Android;
9. publication iOS;
10. extension progressive.
