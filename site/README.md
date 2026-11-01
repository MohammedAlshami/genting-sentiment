# Genting — retail sentiment landing page

A one-page, light-theme research story built from the portfolio design system:
same typography, spacing and motion, with the Genting retail-sentiment dataset.

## Run

```bash
npm install
npm run dev -- --port 3100 --host 0.0.0.0
```

Under pm2:

```bash
pm2 start ecosystem.config.cjs
pm2 save
```

Process: `genting-sentiment`, port **3100**.

## Structure

- `src/pages/public/LandingPage.tsx` — page composition, normal vertical scroll
- `src/data/components/Genting/OpeningSection.tsx` — full-screen opening
- `src/data/components/Genting/StorySections.tsx` — just imports the section files
- `src/data/components/Genting/SectionShell.tsx` — shared full-screen shell
- `src/data/components/Genting/sections/`
  - `Signal.tsx` — the crowd followed the price
  - `Offer.tsx` — the RM2.35 bid
  - `NewYork.tsx` — licence and capex
  - `Debt.tsx` — the debt wall
  - `CashCall.tsx` — the rights issue
  - `Company.tsx` — four numbers
  - `Ahead.tsx` — scenarios
  - `Method.tsx` — caveats
- `src/data/components/Genting/charts/`
  - `SignalChart.tsx` — sentiment vs GENM price
  - `DebtChart.tsx` — GENTING / GENM / net debt
  - `ProjectionChart.tsx` — illustrative scenario fan
  - `theme.ts` — axis/tooltip styles
- `src/data/genting.ts` — real monthly sentiment/prices, real quarterly debt,
  illustrative scenarios
- `src/data/components/Genting/SocialLogos.tsx` — source logos
- `public/logos/genting-dark.png` — Genting mark
- `public/logos/social/` — monochrome social logos

## Notes

- Each section is `100vh` on desktop and at least `100vh` on mobile.
- No navbar, no footer, no arrow navigation.
- One typeface across the page (Plus Jakarta Sans), matching the portfolio stack.
- `react-grab` is enabled in development.
- Mock data only; replace `src/data/genting.ts` with the live collector output.
