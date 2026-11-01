'use client';

import { Section } from '@/data/components/Genting/SectionShell';

export function CashCallSection() {
  return (
    <Section
      id="cash-call"
      kicker="06 — October 2026"
      title="The cash call."
    >
      <div className="grid gap-10 lg:grid-cols-[0.95fr_1.05fr]">
        <div>
          <p className="max-w-lg text-lg leading-relaxed text-black/55">
            RM1.25b rights issue. Most of it goes to the banks: RM800m to repay
            loans, RM429.5m for working capital including RM280m of interest,
            RM20.5m for expenses.
          </p>
          <blockquote className="mt-8 max-w-md">
            <p className="text-2xl leading-snug tracking-tight text-[#0E100F]">
              “Why a rights issue when you can sell Miami land?”
            </p>
            <footer className="mt-3 text-[10px] uppercase tracking-[0.16em] text-black/35">
              KLSE Screener · Oct 2026
            </footer>
          </blockquote>
        </div>
        <div>
          <div className="flex h-3 w-full overflow-hidden rounded-full bg-black/[0.06]">
            <div className="h-full bg-[#0E100F]" style={{ width: '64%' }} />
            <div className="h-full bg-[#0E100F]/50" style={{ width: '34.4%' }} />
            <div className="h-full bg-[#0E100F]/20" style={{ width: '1.6%' }} />
          </div>
          <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-black/45">
            <span>RM800m debt</span>
            <span>RM429.5m working capital</span>
            <span>RM20.5m expenses</span>
          </div>
          <div className="mt-10 grid grid-cols-2 gap-8">
            {[
              ['−22.87%', 'GENTING, 12 Oct 2026'],
              ['RM1.45', 'close on the day'],
              ['RM1.49', 'Maybank target, Sell'],
              ['6m', 'GENT shares bought by Kien Huat at RM1.494'],
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
      </div>
    </Section>
  );
}
