'use client';

import { DebtChart } from '@/data/components/Genting/charts/DebtChart';
import { Section } from '@/data/components/Genting/SectionShell';

export function DebtSection() {
  return (
    <Section
      id="debt"
      kicker="05 — August to September 2026"
      title="The debt wall."
    >
      <p className="max-w-2xl text-lg leading-relaxed text-black/55">
        Debt rose from RM39.0b to RM45.3b while profit swung to a loss. Moody’s,
        Fitch and S&amp;P all moved. The forums understood the arithmetic before
        the price did.
      </p>
      <div className="mt-8">
        <DebtChart />
      </div>
      <div className="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-[10px] uppercase tracking-[0.16em] text-black/35">
        <span>GENTING debt</span>
        <span>GENM debt</span>
        <span>Net debt</span>
        <span>Debt topic peak: 8.3% of replies, Sep 2026</span>
      </div>
    </Section>
  );
}
