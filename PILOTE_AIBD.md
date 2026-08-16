# PILOTE TERRAIN — TAXI SENIRAN AIBD

## Objectif
Tester la plateforme avec un petit groupe de taxis avant généralisation.

## Pré-requis
- liste des chauffeurs autorisés;
- liste des véhicules;
- numéros de téléphone vérifiés;
- tarifs validés;
- zones de prise en charge;
- procédure de gestion des incidents;
- téléphone Android/iOS par chauffeur;
- compte administrateur AIBD.

## Test de bout en bout
1. Chauffeur demande/active son statut.
2. GPS chauffeur est enregistré.
3. Passager demande une course.
4. Superviseur voit la demande.
5. Attribution par file ou proximité.
6. Chauffeur accepte.
7. Chauffeur démarre.
8. Passager suit la course.
9. Chauffeur termine.
10. Paiement est enregistré.
11. Passager note.
12. Incident/SOS est testé.
13. Rapport est vérifié.

## KPI pilote
- temps moyen d'attribution;
- temps moyen d'attente;
- taux d'acceptation;
- taux d'annulation;
- courses terminées;
- incidents;
- satisfaction passager;
- disponibilité flotte.

## Règle de déploiement
Ne pas activer les paiements réels, les SMS OTP ou le trafic public avant validation des contrats, clés API, procédures de sécurité, politique de confidentialité et autorisations nécessaires.
