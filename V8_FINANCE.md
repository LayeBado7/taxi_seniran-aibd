# TAXI SENIRAN AIBD — V8 FINANCE

## Fonctionnalités
- paiement associé à une course;
- statut pending/paid;
- référence transaction;
- commission configurable;
- portefeuille chauffeur;
- revenu brut;
- revenu net;
- facture interne;
- dashboard financier.

## Exemple
Course : 10 000 FCFA
Commission 10 % : 1 000 FCFA
Net chauffeur : 9 000 FCFA

Le taux de commission doit être défini contractuellement par l'opérateur.

## Paiements réels
Les routes constituent une couche métier. Avant production :
- brancher l'API officielle du prestataire;
- vérifier les signatures webhook;
- gérer idempotence;
- gérer remboursements;
- conserver les références;
- rapprocher les transactions.
