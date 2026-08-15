# Déploiement production — TAXI SENIRAN AIBD

## 1. Infrastructure
- Ubuntu Server LTS
- Python 3.13
- PostgreSQL
- Nginx
- Gunicorn
- HTTPS/TLS
- sauvegardes quotidiennes
- supervision CPU/RAM/disque/API
- journalisation centralisée

## 2. Variables d'environnement
```text
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=<secret-long-et-aleatoire>
FLASK_ENV=production
```

## 3. Mobile
Android :
```bash
flutter pub get
flutter build appbundle --release
```

iOS :
```bash
flutter pub get
flutter build ipa --release
```

Les signatures et certificats doivent être fournis/configurés dans les comptes développeur.

## 4. GPS et carte
Le service de localisation est déjà prévu dans le projet. Pour une carte complète :
- Google Maps ou Mapbox;
- clé API séparée Android/iOS;
- restrictions par application;
- géofencing de l'aéroport;
- conservation minimale des données de localisation.

## 5. Sécurité avant production
- remplacer les secrets de démonstration;
- HTTPS obligatoire;
- mots de passe forts;
- rotation des secrets;
- limitation de débit;
- validation stricte des entrées;
- sauvegardes;
- tests d'intrusion;
- journalisation des opérations sensibles;
- politique de confidentialité.

## 6. Stores
Préparer :
- nom et description;
- icône;
- captures d'écran;
- politique de confidentialité;
- coordonnées du support;
- classification d'âge;
- comptes développeur;
- signature Android;
- certificats Apple;
- environnement de test;
- validation finale.
