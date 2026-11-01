'use client';

import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

const morphVariants = {
  hidden: { opacity: 0, scale: 0.97, filter: 'blur(12px)' },
  visible: {
    opacity: 1,
    scale: 1,
    filter: 'blur(0px)',
    transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] as const },
  },
};

export default function CTASection() {
  const sectionRef = useRef<HTMLElement>(null);
  const isInView = useInView(sectionRef, { once: true, amount: 0.12 });

  return (
    <section
      id="cta"
      ref={sectionRef}
      className="relative w-full overflow-hidden bg-white py-24 font-sf-pro-display sm:py-28 md:py-32 lg:py-40"
    >
      <motion.div
        className="container mx-auto px-4 sm:px-6 lg:px-8"
        initial="hidden"
        animate={isInView ? 'visible' : 'hidden'}
        variants={morphVariants}
      >
        <div className="mx-auto max-w-6xl">
          <h2
            className="max-w-5xl text-4xl font-bold leading-[0.95] tracking-tight text-[#0E100F] sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl"
            style={{ fontFamily: '"Mori", sans-serif', letterSpacing: '-0.03em' }}
          >
            THE CROWD MOVED FIRST.
          </h2>

          <p className="mt-8 max-w-xl text-base leading-relaxed text-[#0E100F]/55">
            The price caught up a year later. The corpus, the price series and the
            filings are below.
          </p>

          <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:gap-5">
            <a
              href="#signal"
              className="inline-flex items-center justify-center rounded-lg bg-[#0E100F] px-8 py-4 text-base font-semibold text-white transition-colors hover:opacity-80"
              style={{ fontFamily: '"Mori", sans-serif' }}
            >
              READ THE EVIDENCE
            </a>
            <a
              href="#method"
              className="inline-flex items-center justify-center rounded-lg border border-black/15 px-8 py-4 text-base font-semibold text-[#0E100F] transition-colors hover:border-black/35"
              style={{ fontFamily: '"Mori", sans-serif' }}
            >
              METHOD
            </a>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
