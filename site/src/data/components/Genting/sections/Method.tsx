'use client';

import { Section } from '@/data/components/Genting/SectionShell';
import { corpusStats, historySeries } from '@/data/gentingHistory';

const EVENTS = [
  ['13 Oct 2025', 'Genting offers RM2.35 for GENM'],
  ['1 Dec 2025', 'Bid closes at 73.13% — below 75%'],
  ['16 Dec 2025', 'Resorts World NYC licence awarded'],
  ['1 May 2026', 'NYC casino opens'],
  ['9 Oct 2026', 'RM1.25b rights issue'],
  ['12 Oct 2026', 'GENTING falls 22.87% to RM1.45'],
];

const tone = (value: number) => {
  if (value > 0.505) return 'text-[#2563EB]';
  if (value < 0.495) return 'text-[#ED1C24]';
  return 'text-black/45';
};

export function MethodSection() {
  return (
    <Section id="data" kicker="09 — The data" title="Every month behind the story.">
      <div className="grid grid-cols-2 gap-5 sm:grid-cols-5">
        {[
          ['Replies in corpus', corpusStats.replies.toLocaleString()],
          ['LLM classified', corpusStats.classified.toLocaleString()],
          ['News articles', corpusStats.articles.toLocaleString()],
          ['Months measured', `${corpusStats.measuredMonths} / ${corpusStats.months}`],
          ['Same-month corr.', corpusStats.sameMonthCorrelation.toFixed(2)],
        ].map(([label, value]) => (
          <div key={label}>
            <div className="text-[26px] font-semibold leading-none tracking-tight tabular-nums text-[#0E100F]">
              {value}
            </div>
            <div className="mt-2 text-[10px] uppercase tracking-[0.16em] text-black/35">
              {label}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-7 grid gap-6 lg:grid-cols-[1.45fr_0.55fr]">
        <div className="max-h-[52vh] overflow-auto rounded-md border border-black/10">
          <table className="w-full border-collapse text-left text-[12px] tabular-nums">
            <thead className="sticky top-0 z-10 bg-white">
              <tr className="text-[9px] uppercase tracking-[0.14em] text-black/35">
                <th className="px-3 py-2 font-medium">Month</th>
                <th className="px-3 py-2 text-right font-medium">GENM</th>
                <th className="px-3 py-2 text-right font-medium">GENTING</th>
                <th className="px-3 py-2 text-right font-medium">Sent.</th>
                <th className="px-3 py-2 text-right font-medium">n</th>
                <th className="px-3 py-2 text-right font-medium">Bull</th>
                <th className="px-3 py-2 text-right font-medium">Bear</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/5">
              {historySeries.map((row) => (
                <tr key={row.month} className="text-[#0E100F]/75">
                  <td className="px-3 py-1.5 text-black/55">{row.month}</td>
                  <td className="px-3 py-1.5 text-right text-[#ED1C24]">
                    {row.genm.toFixed(2)}
                  </td>
                  <td className="px-3 py-1.5 text-right">{row.genting.toFixed(2)}</td>
                  <td className={`px-3 py-1.5 text-right font-medium ${tone(row.sentiment)}`}>
                    {row.sentiment.toFixed(2)}
                    {row.modelled ? <span className="text-black/25">*</span> : null}
                  </td>
                  <td className="px-3 py-1.5 text-right text-black/40">
                    {row.n || '—'}
                  </td>
                  <td className="px-3 py-1.5 text-right text-[#2563EB]">
                    {row.n ? `${Math.round(row.bull * 100)}%` : '—'}
                  </td>
                  <td className="px-3 py-1.5 text-right text-[#ED1C24]">
                    {row.n ? `${Math.round(row.bear * 100)}%` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="space-y-6">
          <div>
            <div className="text-[10px] uppercase tracking-[0.18em] text-black/35">
              How to read it
            </div>
            <p className="mt-2 text-[13px] leading-relaxed text-black/55">
              Sentiment is a monthly mean on a 0–1 scale: 0 is maximally bearish,
              0.5 neutral, 1 maximally bullish. Each reply was scored 0–10 with the
              rubric in <code className="text-[12px]">scripts/llm_classify.py</code>,
              then divided by 10. An asterisk marks a month interpolated because no
              replies were sampled yet.
            </p>
          </div>

          <div>
            <div className="text-[10px] uppercase tracking-[0.18em] text-black/35">
              Events in the chart
            </div>
            <ul className="mt-2 space-y-1.5 text-[12px] leading-snug text-black/50">
              {EVENTS.map(([date, text]) => (
                <li key={date}>
                  <span className="text-[#ED1C24]">{date}</span> — {text}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="text-[10px] uppercase tracking-[0.18em] text-black/35">
              Sources classified
            </div>
            <p className="mt-2 text-[12px] leading-relaxed text-black/45">
              {corpusStats.sources.join(' · ')}
            </p>
          </div>

          <div>
            <div className="text-[10px] uppercase tracking-[0.18em] text-black/35">
              Caveats
            </div>
            <p className="mt-2 text-[12px] leading-relaxed text-black/45">
              LLM sample, not the full {corpusStats.replies.toLocaleString()} replies.
              The corpus also holds {corpusStats.articles.toLocaleString()} full news
              articles (2016–2024 backfill included). i3investor 2016–2024 is the full
              crawl (124,062 replies, absolute timestamps). YouTube timestamps are
              month-level. Not investment advice.
            </p>
          </div>
        </div>
      </div>
    </Section>
  );
}
