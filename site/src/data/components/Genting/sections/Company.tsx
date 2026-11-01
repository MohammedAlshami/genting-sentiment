'use client';

import { Section } from '@/data/components/Genting/SectionShell';

export function CompanySection() {
  return (
    <Section
      id="company"
      kicker="07 — The company"
      title="The numbers behind the noise."
    >
      <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ['73.888%', 'Genting stake in GENM'],
          ['RM45.3b', 'group debt'],
          ['RM2.1b', 'annual interest'],
          ['RM1.25b', 'rights issue'],
        ].map(([value, label]) => (
          <div key={label}>
            <div className="text-4xl font-semibold tracking-[-0.03em] text-[#0E100F] sm:text-5xl">
              {value}
            </div>
            <div className="mt-3 text-[10px] uppercase tracking-[0.16em] text-black/35">
              {label}
            </div>
          </div>
        ))}
      </div>
      <p className="mt-10 max-w-2xl text-lg leading-relaxed text-black/55">
        The Lim family’s deemed interest rose from 44.84% to 45.24%. Kien Huat
        bought 47.2m GENT shares over the period — including 6m on the day of
        the rights-issue crash.
      </p>
    </Section>
  );
}
