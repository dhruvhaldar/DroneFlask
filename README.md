# Drone Control Station (Glassmorphism)

This project has been fully rebuilt as a **Next.js + TypeScript** web app optimized for **Vercel serverless deployment**.

## Features

- Glassmorphism UI for flight controls
- Interactive throttle/pitch/roll/yaw sliders
- Flight mode switching and arm/disarm controls
- Serverless API route (`/api/state`) for reading/updating control state
- Ready to deploy on Vercel out of the box

## Run locally

```bash
npm install
npm run dev
```

## Production checks

```bash
npm run lint
npm run typecheck
npm run build
```

## Deploy to Vercel

1. Push this repo to GitHub.
2. Import into Vercel.
3. Use default Next.js settings and deploy.
