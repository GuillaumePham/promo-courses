# Promo Courses

Mini app web pour préparer ses courses et calculer les remises : promos magasin, coupons, cagnotte,
cashback (Coupon Network, iGraal, eBuyClub, Shopmium…), bons d'achat, import de tickets PDF Carrefour.

- `index.html` : l'app (un seul fichier, sans dépendance ; PDF.js est chargé à la demande pour lire les tickets).
- `offres.js` : catalogue des offres Coupon Network, mis à jour chaque mercredi par la tâche GitHub
  `.github/workflows/offres.yml` (script `recuperer_offres.py`).

Les données (courses, prix, réglages) restent dans le navigateur de chaque appareil.
Pour les passer d'un appareil à l'autre : ⚙ Sources → Exporter, puis Importer sur l'autre appareil.
