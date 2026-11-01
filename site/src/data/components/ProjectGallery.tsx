'use client';

import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import type { Screenshot } from '@/data/projects';

/** Carousel of project screenshots with arrows, thumbnails, keyboard and swipe support. */
export default function ProjectGallery({ shots }: { shots: Screenshot[] }) {
  const n = shots.length;
  const [index, setIndex] = React.useState(0);
  const startX = React.useRef<number | null>(null);

  const go = React.useCallback(
    (delta: number) => setIndex((i) => (i + delta + n) % n),
    [n],
  );

  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') go(-1);
      else if (e.key === 'ArrowRight') go(1);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [go]);

  if (n === 0) return null;

  const current = shots[index];

  return (
    <div className="select-none">
      <div
        className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03]"
        onTouchStart={(e) => {
          startX.current = e.touches[0].clientX;
        }}
        onTouchEnd={(e) => {
          if (startX.current === null) return;
          const dx = e.changedTouches[0].clientX - startX.current;
          if (Math.abs(dx) > 40) go(dx < 0 ? 1 : -1);
          startX.current = null;
        }}
      >
        <div
          className="flex transition-transform duration-500 ease-out"
          style={{ transform: `translateX(-${index * 100}%)` }}
        >
          {shots.map((shot, i) => (
            <div key={shot.src} className="w-full shrink-0" aria-hidden={i !== index}>
              <img
                src={shot.src}
                alt={shot.caption}
                loading={i === 0 ? 'eager' : 'lazy'}
                draggable={false}
                className="aspect-[16/10] w-full object-cover object-top"
              />
            </div>
          ))}
        </div>

        <div
          className="pointer-events-none absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black/75 via-black/25 to-transparent"
          aria-hidden
        />

        <button
          type="button"
          aria-label="Previous image"
          onClick={() => go(-1)}
          className="absolute left-3 top-1/2 grid size-11 -translate-y-1/2 place-items-center rounded-full border border-white/20 bg-black/50 text-[#FFF7DD] opacity-0 backdrop-blur transition hover:bg-black/75 focus-visible:opacity-100 group-hover:opacity-100 max-md:opacity-100"
        >
          <ChevronLeft className="size-5" />
        </button>
        <button
          type="button"
          aria-label="Next image"
          onClick={() => go(1)}
          className="absolute right-3 top-1/2 grid size-11 -translate-y-1/2 place-items-center rounded-full border border-white/20 bg-black/50 text-[#FFF7DD] opacity-0 backdrop-blur transition hover:bg-black/75 focus-visible:opacity-100 group-hover:opacity-100 max-md:opacity-100"
        >
          <ChevronRight className="size-5" />
        </button>

        <div className="pointer-events-none absolute inset-x-0 bottom-0 flex items-end justify-between gap-4 p-4 md:p-5">
          <p className="max-w-[80%] text-xs uppercase tracking-wider text-[#FFF7DD]/85">
            {current.caption}
          </p>
          <span className="shrink-0 font-mono text-xs text-[#FFF7DD]/60">
            {String(index + 1).padStart(2, '0')} / {String(n).padStart(2, '0')}
          </span>
        </div>
      </div>

      <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
        {shots.map((shot, i) => (
          <button
            key={shot.src}
            type="button"
            onClick={() => setIndex(i)}
            aria-label={`Show image ${i + 1}: ${shot.caption}`}
            aria-current={i === index}
            className={`relative shrink-0 overflow-hidden rounded-lg border transition ${
              i === index
                ? 'border-[#FFF7DD]'
                : 'border-white/10 opacity-55 hover:opacity-100'
            }`}
          >
            <img
              src={shot.src}
              alt=""
              loading="lazy"
              draggable={false}
              className="h-14 w-24 object-cover object-top md:h-16 md:w-28"
            />
          </button>
        ))}
      </div>
    </div>
  );
}
