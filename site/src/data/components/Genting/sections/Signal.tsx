'use client';

import { SignalChart } from '@/data/components/Genting/charts/SignalChart';
import { Section } from '@/data/components/Genting/SectionShell';

export function SignalSection() {
  return (
    <Section
      id="signal"
      accent
      kicker="01 — The signal"
      title="The crowd followed the price."
    >
      <p className="max-w-2xl text-lg leading-relaxed text-black/55">
        Retail did not call the top. Sentiment stayed positive through the first
        year of the decline, peaked near +0.19 in July 2025, and was still +0.13
        after the privatisation bid failed. It moved with the price — not ahead
        of it.
      </p>
      <div className="mt-8">
        <SignalChart />
      </div>
      <div className="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-[10px] uppercase tracking-[0.16em] text-black/35">
        <span className="text-[#ED1C24]">Sentiment (left)</span>
        <span>GENM price (right)</span>
        <span>Same-month correlation 0.62</span>
        <span>Bearish share 16% → 27.5%</span>
      </div>
    </Section>
  );
}
