'use client';

import React from 'react';
import { ArrowUpRight } from 'lucide-react';

const CHAPTERS = [
  {
    n: '01',
    id: 'signal',
    title: 'The signal',
    meta: '24 months · sentiment vs price',
    summary:
      'Retail turned in October 2025, a year before the rights issue. The price kept falling.',
  },
  {
    n: '02',
    id: 'crowd',
    title: 'The crowd',
    meta: '9 sources · 75,629 posts and comments',
    summary:
      'KLSE Screener and i3investor dominate. Moomoo, YouTube and TikTok add reach beyond the forums.',
  },
  {
    n: '03',
    id: 'narrative',
    title: 'The narrative',
    meta: '7 topics · debt, dilution, New York',
    summary:
      'Two-thirds of the conversation is about leverage, the cash call or dividends.',
  },
  {
    n: '04',
    id: 'breaking',
    title: 'The breaking point',
    meta: '8 events · Oct 2025 → Oct 2026',
    summary:
      'From the RM2.35 privatisation bid to the 22.87% single-day fall.',
  },
  {
    n: '05',
    id: 'company',
    title: 'The company',
    meta: 'RM45.3b debt · 73.888% stake',
    summary:
      'The balance sheet and ownership structure behind the retail anxiety.',
  },
  {
    n: '06',
    id: 'ahead',
    title: 'The road ahead',
    meta: '3 scenarios · 6 months',
    summary:
      'Bear, base and bull paths — presented as a range, not a prophecy.',
  },
  {
    n: '07',
    id: 'method',
    title: 'Method',
    meta: 'Coverage · caveats',
    summary:
      'What was collected, how timestamps were handled, and what the data cannot say.',
  },
];

export default function SelectedProjects() {
  return (
    <section id="chapters" className="bg-white font-sf-pro-display">
      <div className="py-24">
        <div className="container mx-auto w-full px-4 sm:px-6 lg:px-8">
          <div className="mb-10 flex items-end justify-between gap-6 md:mb-12">
            <h2
              className="text-balance text-2xl font-semibold text-[#0E100F] md:text-3xl lg:text-4xl"
              style={{ fontFamily: '"Mori", sans-serif' }}
            >
              Seven chapters
            </h2>
            <span className="shrink-0 font-mono text-[10px] uppercase tracking-[0.18em] text-[#0E100F]/40">
              Scroll ↓
            </span>
          </div>

          <div className="border-t border-dashed border-black/15">
            {CHAPTERS.map((chapter) => (
              <a
                key={chapter.id}
                href={`#${chapter.id}`}
                className="group flex flex-col gap-4 border-b border-dashed border-black/15 px-5 py-8 transition-colors hover:bg-black/[0.03] md:flex-row md:items-center md:gap-10 md:px-10 md:py-10"
              >
                <div className="flex min-w-0 flex-1 items-center gap-5">
                  <span className="font-mono text-[10px] text-[#0E100F]/30">
                    {chapter.n}
                  </span>
                  <div className="min-w-0">
                    <h3
                      className="text-2xl font-semibold tracking-tight text-[#0E100F] md:text-3xl"
                      style={{ fontFamily: '"Mori", sans-serif' }}
                    >
                      {chapter.title}
                    </h3>
                    <p className="mt-1.5 text-xs uppercase tracking-wider text-[#0E100F]/40">
                      {chapter.meta}
                    </p>
                  </div>
                </div>

                <p className="text-base leading-relaxed text-[#0E100F]/60 md:max-w-2xl md:text-lg">
                  {chapter.summary}
                </p>

                <ArrowUpRight className="hidden size-5 shrink-0 text-[#0E100F]/30 transition-all group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-[#0E100F] md:block" />
              </a>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
