'use client';

import { Section } from '@/data/components/Genting/SectionShell';

export function NewYorkSection() {
  return (
    <Section
      id="new-york"
      kicker="04 — December 2025 to May 2026"
      title="The New York bill."
    >
      <div className="grid gap-10 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <p className="max-w-lg text-lg leading-relaxed text-black/55">
            The licence was the good news the bull case had waited years for.
            The market treated it as a capex bill.
          </p>
          <div className="mt-10 grid gap-8 sm:grid-cols-3">
            {[
              ['US$5.5b', 'capex'],
              ['US$600m', 'upfront licence commitment'],
              ['>US$500m', 'racing-support tax dispute'],
            ].map(([value, label]) => (
              <div key={label}>
                <div className="text-2xl font-semibold tracking-tight text-[#0E100F] sm:text-3xl">
                  {value}
                </div>
                <div className="mt-2 text-[10px] uppercase tracking-[0.15em] text-black/35">
                  {label}
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-6">
          {[
            ['16 Dec 2025', 'RWNYC awarded the full New York licence'],
            ['1 May 2026', 'Casino opens as a full integrated resort'],
            ['−10.5%', 'GENTING, 20 days after opening'],
          ].map(([date, body]) => (
            <div key={date} className="flex gap-6">
              <div className="w-24 shrink-0 text-[10px] uppercase tracking-[0.14em] text-black/35">
                {date}
              </div>
              <p className="max-w-md text-base leading-relaxed text-black/55">
                {body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
