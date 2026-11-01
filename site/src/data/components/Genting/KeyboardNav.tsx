'use client';

import { useEffect, useRef } from 'react';
import { useLenis } from 'lenis/react';

export function KeyboardNav() {
  const lenis = useLenis();
  const locked = useRef(false);
  const unlockTimer = useRef<number | null>(null);

  useEffect(() => {
    const collectStops = () =>
      Array.from(
        document.querySelectorAll<HTMLElement>('[data-scroll-stop], [data-section-stop]'),
      )
        .map((el) => Math.round(el.getBoundingClientRect().top + window.scrollY))
        .sort((a, b) => a - b)
        .filter((value, index, all) => index === 0 || value !== all[index - 1]);

    const onKey = (event: KeyboardEvent) => {
      if (
        event.repeat ||
        event.metaKey ||
        event.ctrlKey ||
        event.altKey ||
        locked.current
      ) {
        return;
      }

      const backward = event.key === 'ArrowLeft' || event.key === 'ArrowUp';
      const forward = event.key === 'ArrowRight' || event.key === 'ArrowDown';
      if (!backward && !forward) return;

      const stops = collectStops();
      if (stops.length < 2) return;

      const pos = window.scrollY;
      let index = 0;
      stops.forEach((stop, i) => {
        if (stop <= pos + 8) index = i;
      });

      const atStop = Math.abs(pos - stops[index]) < 30;
      const target = backward ? (atStop ? index - 1 : index) : index + 1;
      if (target < 0 || target >= stops.length) return;

      event.preventDefault();

      const distance = Math.abs(stops[target] - pos);
      const duration = Math.min(2.6, Math.max(1.0, distance / 1250));

      locked.current = true;
      if (unlockTimer.current) window.clearTimeout(unlockTimer.current);
      unlockTimer.current = window.setTimeout(() => {
        locked.current = false;
      }, duration * 1000 + 220);

      if (lenis) {
        lenis.scrollTo(stops[target], {
          duration,
          easing: (t) => 1 - Math.pow(1 - t, 3),
        });
      } else {
        window.scrollTo({ top: stops[target], behavior: 'smooth' });
      }
    };

    window.addEventListener('keydown', onKey);
    return () => {
      window.removeEventListener('keydown', onKey);
      if (unlockTimer.current) window.clearTimeout(unlockTimer.current);
    };
  }, [lenis]);

  return null;
}
