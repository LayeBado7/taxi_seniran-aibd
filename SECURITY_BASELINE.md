# Baseline sécurité

## Obligatoire avant production
- HTTPS partout
- secret JWT aléatoire et rotation
- PostgreSQL sans exposition publique directe
- mots de passe de démonstration supprimés
- limitation de débit
- validation des entrées
- signature des webhooks de paiement
- journalisation des actions sensibles
- sauvegardes chiffrées
- restauration testée
- séparation admin/chauffeur/passager
- tests d'intrusion
- gestion des dépendances et CVE
- géofencing et accès opérateur validés

## Données GPS
Limiter la collecte à la durée/finalité nécessaire et documenter la conservation.
