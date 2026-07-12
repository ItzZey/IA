# Dividend AI Watcher

Application web d'aide a l'analyse des actions a dividendes.

## Version Vercel

La version principale est maintenant une application Next.js situee a la racine du depot. Elle est compatible avec Vercel.

- Framework Vercel : Next.js
- Root directory : racine du depot
- Build command : `next build`
- Donnees : Yahoo Finance public, recupere cote serveur
- Variables d'environnement : aucune obligatoire

## Lancer en local

```bash
pnpm install
pnpm dev
```

Puis ouvrir `http://localhost:3000`.

## Ancienne version Streamlit

L'ancienne version Python/Streamlit reste dans le dossier `app/` pour historique et tests metier.
