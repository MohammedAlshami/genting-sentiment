'use client';

import { ProjectionChart } from '@/data/components/Genting/charts/ProjectionChart';
import { Section } from '@/data/components/Genting/SectionShell';

export function AheadSection() {
  return (
    <Section
      id="ahead"
      kicker="08 — The road ahead"
      title="Three paths. Not a prophecy."
    >
      <p className="max-w-2xl text-lg leading-relaxed text-black/55">
        Sentiment does not tell you the price. At best it tells you which
        scenario the crowd is positioned for.
      </p>
      <div className="mt-8">
        <ProjectionChart />
      </div>
      <div className="mt-8 grid gap-8 sm:grid-cols-3">
        {[
          ['Bear', 'RM0.95', 'Undersubscribed cash call, another downgrade, New York slips.'],
          ['Base', 'RM1.32', 'Debt is paid down, the cash call clears, sentiment stabilises.'],
          ['Bull', 'RM1.55', 'RWNYC turns, asset sales land, a new bid returns.'],
        ].map(([name, price, body]) => (
          <div key={name}>
            <div className="flex items-baseline justify-between">
              <span className="text-[10px] uppercase tracking-[0.16em] text-black/35">
                {name}
              </span>
              <span className="text-xl font-semibold tracking-tight text-[#0E100F]">
                {price}
              </span>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-black/50">{body}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}
