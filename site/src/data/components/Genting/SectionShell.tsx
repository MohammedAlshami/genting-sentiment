'use client';

import React from 'react';
import { motion } from 'framer-motion';

export function Section({
  id,
  kicker,
  title,
  accent = false,
  children,
}: {
  id: string;
  kicker: string;
  title: string;
  accent?: boolean;
  children: React.ReactNode;
}) {
  return (
    <section
      id={id}
      data-section-stop
      className="flex min-h-screen w-full items-center bg-white font-sans md:h-screen"
    >
      <div className="w-full px-6 py-16 sm:px-10 md:py-20 lg:px-16">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.7 }}
          className="mb-10 max-w-3xl"
        >
          <div className={`text-[10px] uppercase tracking-[0.22em] ${accent ? 'text-[#ED1C24]' : 'text-black/35'}`}>
            {kicker}
          </div>
          <h2 className="mt-4 text-4xl font-semibold leading-[0.95] tracking-[-0.03em] text-[#0E100F] sm:text-5xl lg:text-6xl">
            {title}
          </h2>
        </motion.div>
        {children}
      </div>
    </section>
  );
}
