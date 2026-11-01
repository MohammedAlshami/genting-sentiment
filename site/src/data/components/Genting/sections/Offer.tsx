'use client';

import { Section } from '@/data/components/Genting/SectionShell';

export function OfferSection() {
  return (
    <Section
      id="offer"
      kicker="03 — October 2025"
      title="The offer that wasn’t."
    >
      <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr]">
        <div>
          <p className="max-w-lg text-lg leading-relaxed text-black/55">
            On 13 October, Genting offered RM2.35 a share for the GENM minority
            — RM6.7b, aiming past the 75% delisting line. The market read it as
            a floor. The forums read it as a lowball.
          </p>
          <blockquote className="mt-8 max-w-md">
            <p className="text-2xl leading-snug tracking-tight text-[#0E100F]">
              “2.35 is not fair value. Don’t sell.”
            </p>
            <footer className="mt-3 text-[10px] uppercase tracking-[0.16em] text-black/35">
              KLSE Screener · Oct 2025
            </footer>
          </blockquote>
        </div>
        <div className="grid gap-8 sm:grid-cols-2">
          {[
            ['13 Oct 2025', 'Offer launched at RM2.35'],
            ['1 Dec 2025', 'Closes at 73.13% — below 75%'],
            ['+17.8%', 'GENTING, 5 days after the offer'],
            ['−12.3%', 'GENM, 20 days after the bid failed'],
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
          <p className="text-sm leading-relaxed text-black/45 sm:col-span-2">
            The stake later rose to 73.888%. Privatisation reached 14.6% of all
            forum replies in November 2025 — the loudest topic of the period.
          </p>
        </div>
      </div>
    </Section>
  );
}
