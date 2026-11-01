'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { sentimentSeries } from '@/data/genting';

const W = 1000;
const H = 160;
const MIN = 0.03;
const MAX = 0.21;

const points = sentimentSeries.map((point, index) => {
  const x = (index / (sentimentSeries.length - 1)) * W;
  const y = H - ((point.sentiment - MIN) / (MAX - MIN)) * (H - 20) - 10;
  return `${index === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
});

const path = points.join(' ');

export function TransitionThread() {
  const { scrollY } = useScroll();
  const draw = useTransform(scrollY, [300, 650], [0, 1]);
  const offset = useTransform(draw, [0, 1], [1, 0]);
  const opacity = useTransform(
    scrollY,
    [280, 420, 820, 980],
    [0, 1, 1, 0],
  );
  const y = useTransform(scrollY, [700, 980], [0, 90]);

  return (
    <motion.div
      style={{ opacity, y }}
      className="pointer-events-none fixed inset-x-0 top-1/2 z-40 flex -translate-y-1/2 justify-center"
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="h-[150px] w-[82vw] max-w-[1600px] overflow-visible"
        preserveAspectRatio="none"
        aria-hidden
      >
        <motion.path
          d={path}
          fill="none"
          stroke="#ED1C24"
          strokeWidth={2.4}
          strokeLinecap="round"
          strokeLinejoin="round"
          pathLength={1}
          strokeDasharray="1"
          style={{ strokeDashoffset: offset }}
        />
      </svg>
    </motion.div>
  );
}
