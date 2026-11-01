'use client';

import React from 'react';
import { SocialLogos } from '@/data/components/Genting/SocialLogos';

export default function Footer() {
  return (
    <div
      id="footer"
      className="px-4 py-4 font-sf-pro-display sm:px-6 sm:py-6 md:px-8 md:py-8 lg:px-10 lg:py-10"
      style={{ backgroundColor: '#FFFFFF' }}
    >
      <footer
        className="relative flex w-full flex-col overflow-hidden rounded-xl border border-black/10 bg-white"
        style={{ fontFamily: '"Mori", sans-serif' }}
      >
        <div className="flex flex-1 items-center justify-center px-4 py-20 sm:px-6 md:py-28">
          <h2
            className="text-center text-[clamp(60px,15vw,300px)] font-bold leading-none tracking-tight text-[#0E100F]"
            style={{ fontFamily: '"Mori", sans-serif' }}
          >
            Genting
          </h2>
        </div>

        <div className="mt-auto w-full px-6 pb-8 sm:px-12 md:px-16 lg:px-24">
          <div className="mb-10 flex flex-col gap-8 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h4 className="text-lg font-bold uppercase tracking-wide text-[#0E100F] md:text-xl">
                Retail sentiment research
              </h4>
              <p className="mt-2 max-w-md text-sm leading-relaxed text-[#0E100F]/50">
                A two-year read of Malaysian public conversation about Genting
                Berhad and Genting Malaysia. Public data only. Not investment
                advice.
              </p>
              <SocialLogos className="mt-5" />
            </div>
            <div className="flex flex-col items-start gap-2 sm:items-end">
              <a href="#signal" className="text-sm text-[#0E100F]/60 hover:text-[#0E100F]">
                The signal
              </a>
              <a href="#company" className="text-sm text-[#0E100F]/60 hover:text-[#0E100F]">
                The company
              </a>
              <a href="#method" className="text-sm text-[#0E100F]/60 hover:text-[#0E100F]">
                Method
              </a>
            </div>
          </div>

          <div className="flex flex-col items-center justify-between gap-4 border-t border-black/10 pt-6 text-xs text-[#0E100F]/40 md:flex-row">
            <p>© {new Date().getFullYear()} Genting / Sentiment · Prototype</p>
            <p>GENTING 3182 · GENM 4715 · 2 Nov 2024 — 2 Nov 2026</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
