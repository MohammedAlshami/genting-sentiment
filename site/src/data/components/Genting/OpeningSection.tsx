'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, useMotionValueEvent, useScroll, useTransform } from 'framer-motion';
import { corpusStats, historySeries } from '@/data/gentingHistory';
import { opinionSentences } from '@/data/opinions';

const RED = '#ED1C24';
const BLUE = '#2563EB';
const INK = '#3F3F46';

const TONE_COLOR = { pos: BLUE, neg: RED, neutral: INK } as const;

const N = historySeries.length;

// Plot frame in the 1000 x 1000 viewBox that is stretched over the viewport.
const X0 = 58;
const X1 = 948;
const P_TOP = 300;
const P_BOT = 620;
const S_TOP = 670;
const S_BOT = 780;

const xAt = (i: number) => X0 + (i / (N - 1)) * (X1 - X0);
const priceY = (v: number) => P_BOT - ((v - 1.0) / (6.2 - 1.0)) * (P_BOT - P_TOP);
const sentimentY = (v: number) => S_BOT - ((v - 0.3) / 0.45) * (S_BOT - S_TOP);

const priceD = historySeries
  .map((p, i) => `${i === 0 ? 'M' : 'L'}${xAt(i).toFixed(1)},${priceY(p.genm).toFixed(1)}`)
  .join(' ');

const priceArea = `${priceD} L${X1},${P_BOT} L${X0},${P_BOT} Z`;

const sentimentD = historySeries
  .map((p, i) => `${i === 0 ? 'M' : 'L'}${xAt(i).toFixed(1)},${sentimentY(p.sentiment).toFixed(1)}`)
  .join(' ');

const idx = (month: string) => historySeries.findIndex((p) => p.month === month);

type EventMark = {
  month: string;
  label: string;
  detail: string;
  align?: 'center' | 'right';
  top?: string;
};

const EVENTS: EventMark[] = [
  { month: '2018-05', label: 'May 2018', detail: 'GE14, BN loses' },
  { month: '2019-08', label: 'Aug 2019', detail: 'Empire deal' },
  { month: '2020-03', label: 'Mar 2020', detail: 'Casinos shut', top: '22.2%' },
  { month: '2025-10', label: 'Oct 2025', detail: 'RM2.35 bid fails', top: '22.2%' },
  { month: '2026-10', label: 'Oct 2026', detail: 'RM1.25b rights issue', align: 'right' },
];

const PRICE_TICKS = [6.0, 4.5, 3.0, 1.5];
const SENT_TICKS = [0.7, 0.6, 0.5, 0.4];
const YEARS = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026];

const yearIndex = (year: number) => (year - 2016) * 12 - 10;

type Pt = { x: number; y: number };
type Source = { x: number; y: number };

type Placed = {
  text: string;
  tone: keyof typeof TONE_COLOR;
  color: string;
  size: number;
  x: number;
  y: number;
  w: number;
  h: number;
};

type Particle = {
  sx: number;
  sy: number;
  tx: number;
  ty: number;
  delay: number;
  arc: number;
};

type Group = { color: string; items: Particle[] };

function clamp(v: number, min = 0, max = 1) {
  return Math.max(min, Math.min(max, v));
}

function ease(t: number) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function samplePrice(count: number): Pt[] {
  const source = historySeries.map((p, i) => ({ x: xAt(i), y: priceY(p.genm) }));
  const lengths: number[] = [0];
  for (let i = 1; i < source.length; i++) {
    lengths.push(
      lengths[i - 1] +
        Math.hypot(source[i].x - source[i - 1].x, source[i].y - source[i - 1].y),
    );
  }
  const total = lengths[lengths.length - 1];
  const out: Pt[] = [];
  for (let i = 0; i < count; i++) {
    const target = (i / (count - 1)) * total;
    let j = 1;
    while (j < lengths.length - 1 && lengths[j] < target) j++;
    const t = (target - lengths[j - 1]) / (lengths[j] - lengths[j - 1] || 1);
    out.push({
      x: source[j - 1].x + (source[j].x - source[j - 1].x) * t,
      y: source[j - 1].y + (source[j].y - source[j - 1].y) * t,
    });
  }
  return out;
}

function densify(points: Source[], step: number): Source[] {
  const out: Source[] = [];
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1];
    const b = points[i];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    const n = Math.max(1, Math.ceil(len / step));
    for (let k = 0; k < n; k++) {
      out.push({ x: a.x + ((b.x - a.x) * k) / n, y: a.y + ((b.y - a.y) * k) / n });
    }
  }
  return out;
}

function layoutSentences(width: number, height: number): Placed[] {
  const scale = clamp(Math.min(width / 1920, height / 1080), 0.55, 1.15);
  const measure = document.createElement('canvas').getContext('2d');
  if (!measure) return [];

  const items = opinionSentences
    .map((sentence) => ({
      ...sentence,
      size: (26 + ((sentence.weight - 26) / (56 - 26)) * 46) * scale,
    }))
    .sort((a, b) => b.size - a.size)
    .map((sentence) => {
      measure.font = `600 ${sentence.size}px "Plus Jakarta Sans", sans-serif`;
      measure.letterSpacing = `${-0.03 * sentence.size}px`;
      return { ...sentence, w: measure.measureText(sentence.text).width };
    });

  const gapX = 44 * scale;
  const maxW = width * 0.92;
  const rows: { items: typeof items; width: number; h: number }[] = [];

  let row = { items: [] as typeof items, width: 0, h: 0 };
  for (const item of items) {
    const extra = row.items.length ? gapX : 0;
    if (row.items.length && row.width + extra + item.w > maxW) {
      rows.push(row);
      row = { items: [], width: 0, h: 0 };
    }
    const add = row.items.length ? gapX : 0;
    row.width += add + item.w;
    row.h = Math.max(row.h, item.size);
    row.items.push(item);
  }
  if (row.items.length) rows.push(row);

  const sumH = rows.reduce((total, r) => total + r.h, 0);
  const targetH = height * 0.8;
  const gapY = clamp(
    rows.length > 1 ? (targetH - sumH) / (rows.length - 1) : 0,
    18 * scale,
    62 * scale,
  );
  const totalH = sumH + gapY * (rows.length - 1);
  let y = (height - totalH) / 2 - height * 0.012;

  const placed: Placed[] = [];
  rows.forEach((r, rowIndex) => {
    const offset = Math.sin(rowIndex * 1.7) * 12 * scale;
    let x = (width - r.width) / 2 + offset;
    for (const item of r.items) {
      placed.push({
        text: item.text,
        tone: item.tone,
        color: TONE_COLOR[item.tone],
        size: item.size,
        x: x + item.w / 2,
        y: y + r.h / 2,
        w: item.w,
        h: item.size * 1.05,
      });
      x += item.w + gapX;
    }
    y += r.h + gapY;
  });

  return placed;
}

export function OpeningSection() {
  const ref = useRef<HTMLElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const linesRef = useRef<SVGSVGElement>(null);
  const progressRef = useRef(0);
  const [chartOn, setChartOn] = useState(false);
  const [sentencesOn, setSentencesOn] = useState(false);
  const [placed, setPlaced] = useState<Placed[]>([]);

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end end'],
  });

  const measured = historySeries.filter((p) => !p.modelled);
  const robust = measured.filter((p) => p.n >= 20);
  const peak = robust.reduce((a, b) => (b.sentiment > a.sentiment ? b : a), robust[0]);
  const low = robust.reduce((a, b) => (b.sentiment < a.sentiment ? b : a), robust[0]);
  const latest = measured[measured.length - 1];
  const mean = measured.reduce((sum, p) => sum + p.sentiment, 0) / measured.length;
  const monthLabel = (month: string) =>
    new Date(`${month}-01T00:00:00`).toLocaleString('en-MY', { month: 'long', year: 'numeric' });
  const { scrollY } = useScroll();
  const chrome = useTransform(scrollY, [0, 150], [1, 0]);
  const tagline = useTransform(scrollY, [40, 190], [1, 0]);

  useMotionValueEvent(scrollYProgress, 'change', (value) => {
    progressRef.current = value;

    const nextChart = value > 0.2 && value < 0.47;
    setChartOn((prev) => (prev === nextChart ? prev : nextChart));

    const nextSentences = value > 0.79;
    setSentencesOn((prev) => (prev === nextSentences ? prev : nextSentences));

    if (linesRef.current) {
      const opacity =
        clamp((value - 0.17) / 0.04) * (1 - clamp((value - 0.54) / 0.14));
      linesRef.current.style.opacity = String(opacity);
    }
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    const section = ref.current;
    if (!canvas || !section) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let fontSize = 0;
    let cx = 0;
    let cy = 0;
    let wordA: Pt[] = [];
    let targetA: Pt[] = [];
    let groupsB: Group[] = [];
    let raf = 0;

    const draw = () => {
      const p = progressRef.current;
      ctx.clearRect(0, 0, width, height);

      // 1. GENTING -> GENM price line.
      const alphaA = clamp((p - 0.045) / 0.03) * (1 - clamp((p - 0.185) / 0.035));
      if (alphaA > 0 && wordA.length) {
        ctx.globalAlpha = alphaA;
        ctx.fillStyle = RED;
        const morph = clamp((p - 0.055) / 0.115);
        const n = Math.min(wordA.length, targetA.length);
        for (let i = 0; i < n; i++) {
          const t = ease(clamp((morph - (i / n) * 0.14) / 0.86));
          const x = wordA[i].x + (targetA[i].x - wordA[i].x) * t;
          const y = wordA[i].y + (targetA[i].y - wordA[i].y) * t;
          ctx.fillRect(x - 1.15, y - 1.15, 2.3, 2.3);
        }
      }

      // 2. The same two lines -> opinion sentences.
      const alphaB = clamp((p - 0.505) / 0.03) * (1 - clamp((p - 0.78) / 0.04));
      if (alphaB > 0 && groupsB.length) {
        ctx.globalAlpha = alphaB;
        const morph = clamp((p - 0.515) / 0.245);
        for (const group of groupsB) {
          ctx.fillStyle = group.color;
          for (const q of group.items) {
            const t = ease(clamp((morph - q.delay) / (1 - q.delay)));
            const x = q.sx + (q.tx - q.sx) * t;
            const y = q.sy + (q.ty - q.sy) * t + Math.sin(t * Math.PI) * q.arc;
            ctx.fillRect(x - 1.5, y - 1.5, 3, 3);
          }
        }
      }

      // 3. The opening word, before it breaks apart.
      const solid = 1 - clamp((p - 0.05) / 0.05);
      if (solid > 0) {
        ctx.globalAlpha = solid;
        ctx.fillStyle = RED;
        ctx.font = `800 ${fontSize}px "Plus Jakarta Sans", sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.letterSpacing = `${-fontSize * 0.06}px`;
        ctx.fillText('GENTING', cx, cy);
      }

      ctx.globalAlpha = 1;
    };

    const build = async () => {
      await document.fonts.ready;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = section.clientWidth;
      height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);

      fontSize = Math.min(Math.max(72, width * 0.17), 240);
      cx = width / 2;
      cy = height * 0.46;

      // Word mask for the opening morph.
      const off = document.createElement('canvas');
      off.width = width;
      off.height = height;
      const octx = off.getContext('2d');
      if (!octx) return;
      octx.font = `800 ${fontSize}px "Plus Jakarta Sans", sans-serif`;
      octx.textAlign = 'center';
      octx.textBaseline = 'middle';
      octx.letterSpacing = `${-fontSize * 0.06}px`;
      octx.fillStyle = '#000';
      octx.fillText('GENTING', cx, cy);

      const data = octx.getImageData(0, 0, width, height).data;
      const points: Pt[] = [];
      const step = width > 1400 ? 4 : 3;
      for (let y = 0; y < height; y += step) {
        for (let x = 0; x < width; x += step) {
          if (data[(y * width + x) * 4 + 3] > 120) points.push({ x, y });
        }
      }
      points.sort((a, b) => a.x - b.x);

      const sampled = samplePrice(points.length).sort((a, b) => a.x - b.x);
      wordA = points;
      targetA = sampled.map((p) => ({
        x: (p.x / 1000) * width,
        y: (p.y / 1000) * height,
      }));

      // Sentence mask for the second morph.
      const cloud = layoutSentences(width, height);
      setPlaced(cloud);

      const off2 = document.createElement('canvas');
      off2.width = width;
      off2.height = height;
      const octx2 = off2.getContext('2d');
      if (!octx2) return;
      octx2.textAlign = 'center';
      octx2.textBaseline = 'middle';
      octx2.fillStyle = '#000';
      for (const sentence of cloud) {
        octx2.font = `600 ${sentence.size}px "Plus Jakarta Sans", sans-serif`;
        octx2.letterSpacing = `${-0.03 * sentence.size}px`;
        octx2.fillText(sentence.text, sentence.x, sentence.y);
      }

      const data2 = octx2.getImageData(0, 0, width, height).data;
      const targetPoints: { x: number; y: number; tone: keyof typeof TONE_COLOR }[] = [];
      const step2 = width > 1400 ? 4 : 3;

      for (const sentence of cloud) {
        const left = Math.max(0, Math.floor(sentence.x - sentence.w / 2));
        const right = Math.min(width, Math.ceil(sentence.x + sentence.w / 2));
        const top = Math.max(0, Math.floor(sentence.y - sentence.h / 2));
        const bottom = Math.min(height, Math.ceil(sentence.y + sentence.h / 2));
        for (let y = top; y < bottom; y += step2) {
          for (let x = left; x < right; x += step2) {
            if (data2[(y * width + x) * 4 + 3] > 140) {
              targetPoints.push({ x, y, tone: sentence.tone });
            }
          }
        }
      }

      const priceDense = densify(
        historySeries.map((p, i) => ({
          x: (xAt(i) / 1000) * width,
          y: (priceY(p.genm) / 1000) * height,
        })),
        6,
      );
      const sentimentDense = densify(
        historySeries.map((p, i) => ({
          x: (xAt(i) / 1000) * width,
          y: (sentimentY(p.sentiment) / 1000) * height,
        })),
        6,
      );

      const groups = new Map<string, Particle[]>();
      let seed = 3182;
      const rand = () => {
        seed = (seed * 16807) % 2147483647;
        return seed / 2147483647;
      };

      targetPoints.forEach((point, i) => {
        const priceSrc = priceDense[Math.floor((point.x / width) * (priceDense.length - 1))];
        const sentSrc =
          sentimentDense[Math.floor((point.x / width) * (sentimentDense.length - 1))];
        let source: Source;
        if (point.tone === 'neg') {
          source = { x: priceSrc.x, y: priceSrc.y };
        } else if (point.tone === 'pos') {
          source = { x: sentSrc.x, y: sentSrc.y };
        } else if (i % 2 === 0) {
          source = { x: priceSrc.x, y: priceSrc.y };
        } else {
          source = { x: sentSrc.x, y: sentSrc.y };
        }

        const color = TONE_COLOR[point.tone];
        if (!groups.has(color)) groups.set(color, []);
        groups.get(color)!.push({
          sx: source.x + (rand() - 0.5) * 4,
          sy: source.y + (rand() - 0.5) * 4,
          tx: point.x,
          ty: point.y,
          delay: (point.x / width) * 0.2 + rand() * 0.08,
          arc: (rand() - 0.5) * 54,
        });
      });

      groupsB = Array.from(groups.entries()).map(([color, items]) => ({ color, items }));
      if (linesRef.current) linesRef.current.style.opacity = '0';
      draw();
    };

    const onScroll = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(draw);
    };

    void build();
    const unsubscribe = scrollYProgress.on('change', onScroll);
    const ro = new ResizeObserver(() => void build());
    ro.observe(section);

    return () => {
      cancelAnimationFrame(raf);
      unsubscribe();
      ro.disconnect();
    };
  }, [scrollYProgress]);

  return (
    <section id="intro-signal" ref={ref} className="relative h-[700vh] w-full bg-white">
      <span data-scroll-stop aria-hidden className="pointer-events-none absolute left-0 top-0 h-px w-px" />
      <span
        data-scroll-stop
        aria-hidden
        style={{ top: '34.29%' }}
        className="pointer-events-none absolute left-0 h-px w-px"
      />
      <span
        data-scroll-stop
        aria-hidden
        style={{ top: '73.71%' }}
        className="pointer-events-none absolute left-0 h-px w-px"
      />

      <div className="sticky top-0 flex h-screen w-full items-center justify-center overflow-hidden px-6 font-sf-pro-display sm:px-10">
        <canvas ref={canvasRef} className="pointer-events-none absolute inset-0" />

        <motion.img
          src="/logos/genting.png"
          alt="Genting"
          style={{ opacity: chrome }}
          className="absolute left-1/2 top-8 h-8 w-auto -translate-x-1/2 sm:top-12 sm:h-10"
        />

        <motion.p
          style={{ opacity: tagline }}
          className="absolute left-1/2 top-[65%] w-full max-w-3xl -translate-x-1/2 text-center text-2xl font-medium tracking-[-0.02em] text-[#0E100F] sm:text-3xl md:text-4xl"
        >
          {corpusStats.replies.toLocaleString()} voices. One falling stock.
        </motion.p>

        <svg
          ref={linesRef}
          viewBox="0 0 1000 1000"
          preserveAspectRatio="none"
          className="pointer-events-none absolute inset-0 h-full w-full"
          style={{ opacity: 0 }}
          aria-hidden
        >
          <defs>
            <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={RED} stopOpacity="0.12" />
              <stop offset="100%" stopColor={RED} stopOpacity="0" />
            </linearGradient>
          </defs>

          {EVENTS.map((event) => {
            const i = idx(event.month);
            if (i < 0) return null;
            return (
              <line
                key={`${event.month}-line`}
                x1={xAt(i)}
                y1={P_TOP}
                x2={xAt(i)}
                y2={S_BOT}
                stroke="rgba(14,16,15,0.16)"
                strokeWidth={1}
                strokeDasharray="2 6"
                vectorEffect="non-scaling-stroke"
              />
            );
          })}

          <path d={priceArea} fill="url(#priceFill)" stroke="none" />
          <path
            d={priceD}
            fill="none"
            stroke={RED}
            strokeWidth={3}
            strokeLinecap="round"
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />

          {EVENTS.map((event) => {
            const i = idx(event.month);
            if (i < 0) return null;
            return (
              <circle
                key={`${event.month}-dot`}
                cx={xAt(i)}
                cy={priceY(historySeries[i].genm)}
                r={4}
                fill="#fff"
                stroke={RED}
                strokeWidth={2.4}
                vectorEffect="non-scaling-stroke"
              />
            );
          })}

          <line
            x1={X0}
            y1={S_BOT}
            x2={X1}
            y2={S_BOT}
            stroke="rgba(14,16,15,0.2)"
            strokeWidth={1}
            vectorEffect="non-scaling-stroke"
          />
          <path
            d={sentimentD}
            fill="none"
            stroke={BLUE}
            strokeWidth={2.4}
            strokeLinecap="round"
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />
          <circle
            cx={xAt(N - 1)}
            cy={sentimentY(historySeries[N - 1].sentiment)}
            r={4}
            fill={BLUE}
          />
          <circle cx={xAt(N - 1)} cy={priceY(historySeries[N - 1].genm)} r={5} fill={RED} />
        </svg>

        <div
          className="pointer-events-none absolute inset-0"
          style={{ opacity: chartOn ? 1 : 0, transition: 'opacity 420ms ease' }}
        >
          <div className="absolute left-6 top-10 max-w-4xl sm:left-10 md:top-12 lg:left-16">
            <h2 className="text-4xl font-semibold leading-[0.95] tracking-[-0.03em] text-[#0E100F] sm:text-5xl lg:text-6xl">
              The crowd followed the price.
            </h2>
            <p className="mt-4 max-w-3xl text-base leading-relaxed text-black/55">
              Over ten years GENM fell from RM6.00 to RM1.25. Retail sentiment
              averaged {mean.toFixed(2)}, peaked at {peak.sentiment.toFixed(2)} in{' '}
              {monthLabel(peak.month)} and was {latest.sentiment.toFixed(2)} in{' '}
              {monthLabel(latest.month)}. The link is weak — same-month correlation{' '}
              {corpusStats.sameMonthCorrelation.toFixed(2)} — but the crowd moved with
              the price, not ahead of it.
            </p>
          </div>

          {EVENTS.map((event) => {
            const i = idx(event.month);
            if (i < 0) return null;
            const right = event.align === 'right';
            return (
              <div
                key={`${event.month}-label`}
                style={{ left: `${(xAt(i) / 1000) * 100}%`, top: event.top ?? '25.2%' }}
                className={`absolute text-[15px] uppercase tracking-[0.1em] text-black/45 ${
                  right ? '-translate-x-full text-right' : '-translate-x-1/2 text-center'
                }`}
              >
                <div className="text-[#ED1C24]">{event.label}</div>
                <div className="mt-0.5 whitespace-nowrap text-[13px] normal-case tracking-normal text-black/45">
                  {event.detail}
                </div>
              </div>
            );
          })}

          {PRICE_TICKS.map((tick) => (
            <div
              key={tick}
              style={{ top: `${(priceY(tick) / 1000) * 100}%` }}
              className="absolute left-3 -translate-y-1/2 text-[21px] tabular-nums text-black/55"
            >
              RM{tick.toFixed(2)}
            </div>
          ))}

          <div className="absolute left-6 top-[65.4%] text-[15px] uppercase tracking-[0.14em] text-[#2563EB] sm:left-10 lg:left-16">
            Retail sentiment
          </div>

          {SENT_TICKS.map((tick) => (
            <div
              key={tick}
              style={{ top: `${(sentimentY(tick) / 1000) * 100}%` }}
              className="absolute left-3 -translate-y-1/2 text-[17px] tabular-nums text-[#2563EB]/80"
            >
              {tick.toFixed(2)}
            </div>
          ))}

          {YEARS.map((year) => (
            <div
              key={year}
              style={{ left: `${(xAt(yearIndex(year)) / 1000) * 100}%` }}
              className="absolute top-[81.2%] -translate-x-1/2 text-[15px] tabular-nums text-black/40"
            >
              {year}
            </div>
          ))}

          <div
            style={{ top: `${(priceY(1.25) / 1000) * 100}%` }}
            className="absolute right-3 -translate-y-1/2 rounded bg-white/90 px-1 text-[30px] font-semibold tabular-nums text-[#ED1C24]"
          >
            RM1.25
          </div>
          <div
            style={{ top: `${(sentimentY(latest.sentiment) / 1000) * 100}%` }}
            className="absolute right-3 -translate-y-1/2 rounded bg-white/90 px-1 text-[19px] tabular-nums text-[#2563EB]"
          >
            {latest.sentiment.toFixed(2)}
          </div>

          <div className="absolute bottom-4 left-6 right-6 flex flex-wrap items-center justify-between gap-3 text-[12px] uppercase tracking-[0.14em] text-black/40 sm:left-10 sm:right-10 lg:left-16 lg:right-16">
            <span className="text-[#ED1C24]">GENM price</span>
            <span className="text-[#2563EB]">Retail sentiment</span>
            <span>2016 → 2026</span>
            <span>Correlation {corpusStats.sameMonthCorrelation.toFixed(2)} · same month</span>
          </div>
        </div>

        <div
          className="pointer-events-none absolute inset-0"
          style={{ opacity: sentencesOn ? 1 : 0, transition: 'opacity 460ms ease' }}
        >
          {placed.map((sentence) => (
            <span
              key={sentence.text}
              style={{
                left: sentence.x,
                top: sentence.y,
                fontSize: sentence.size,
                color: sentence.color,
                letterSpacing: '-0.03em',
                lineHeight: 1,
              }}
              className="absolute -translate-x-1/2 -translate-y-1/2 whitespace-nowrap font-semibold"
            >
              {sentence.text}
            </span>
          ))}

          <div className="absolute left-6 top-8 text-[10px] uppercase tracking-[0.22em] text-black/35 sm:left-10">
            02 — What they said
          </div>
          <div className="absolute right-6 top-8 text-[10px] uppercase tracking-[0.18em] text-black/30 sm:right-10">
            {corpusStats.replies.toLocaleString()}+ replies · classified by tone
          </div>
          <div className="absolute bottom-16 left-1/2 flex -translate-x-1/2 flex-wrap items-center justify-center gap-x-8 gap-y-2 text-[11px] uppercase tracking-[0.14em] text-black/40">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#2563EB]" /> bullish
            </span>
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#ED1C24]" /> bearish
            </span>
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#3F3F46]" /> question
            </span>
            <span>size = mentions</span>
          </div>
        </div>
      </div>
    </section>
  );
}
