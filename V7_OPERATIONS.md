# TAXI SENIRAN AIBD — V7 OPERATIONS

## Nouveautés
- gestion des zones AIBD;
- gestion de la file des chauffeurs;
- vue flotte administrateur;
- annulation de course;
- KPI opérationnels;
- suivi de flotte actualisé;
- point de configuration domaine/HTTPS.

## Règles d'exploitation
### File
Le superviseur peut corriger le rang en cas d'incident opérationnel, avec traçabilité à ajouter en production.

### Annulation
Une annulation doit avoir un motif. Les statistiques distinguent courses terminées et annulées.

### Géofencing
La zone AIBD est configurée comme point de départ de référence. Les coordonnées/rayon doivent être validés avec l'exploitant avant activation terrain.

## KPI minimum
- courses demandées;
- courses attribuées;
- courses terminées;
- annulations;
- taux de réalisation;
- taux d'annulation;
- taxis disponibles;
- temps d'attente moyen;
- satisfaction moyenne.

## Go-Live
Le passage en production doit être précédé par un test avec données réelles limitées, un plan de sauvegarde et une procédure d'incident.
