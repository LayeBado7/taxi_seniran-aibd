# Administrateur unique — TAXI SENIRAN AIBD

- Aucun endpoint d'inscription publique.
- Le premier et unique compte `admin` est créé depuis `ADMIN_PHONE`, `ADMIN_NAME`, `ADMIN_PASSWORD`.
- Ces valeurs sont configurées dans Render et ne doivent jamais être commitées dans GitHub.
- Seul l'administrateur peut créer des comptes Passager ou Chauffeur.
- L'OTP authentifie uniquement un compte déjà existant.
- Aucun second administrateur n'est créé par l'application.
- Les comptes utilisateurs peuvent être désactivés par l'administrateur.
- Le compte administrateur principal ne peut pas être désactivé depuis l'interface.

Pour la production, activer une protection MFA/2FA pour le compte administrateur.
