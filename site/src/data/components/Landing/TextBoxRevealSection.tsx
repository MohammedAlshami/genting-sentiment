'use client';

import React from 'react';
import { TextBoxReveal } from '@/data/components/v1/skiper70';

const HIGHLIGHTS = [
  { word: 'forums', textClass: '!text-[#0E100F]', bgClass: '!bg-amber-200/90' },
  { word: 'moomoo', textClass: '!text-[#0E100F]', bgClass: '!bg-rose-200/90' },
  { word: 'Reddit', textClass: '!text-[#0E100F]', bgClass: '!bg-sky-200/90' },
  { word: 'YouTube', textClass: '!text-[#0E100F]', bgClass: '!bg-violet-200/90' },
  { word: 'TikTok', textClass: '!text-[#0E100F]', bgClass: '!bg-emerald-200/90' },
  { word: 'debt', textClass: '!text-[#0E100F]', bgClass: '!bg-orange-200/90' },
  { word: 'rights issue', textClass: '!text-[#0E100F]', bgClass: '!bg-lime-200/90' },
  { word: 'sentiment', textClass: '!text-[#0E100F]', bgClass: '!bg-amber-200/90' },
];

export default function TextBoxRevealSection() {
  return (
    <section className="pt-24 md:pt-32 pb-0 bg-white font-sf-pro-text">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-[1.7fr_1fr] lg:gap-16">
          <div className="relative z-10 text-2xl leading-relaxed text-[#0E100F] md:text-3xl lg:text-4xl xl:text-5xl">
            <TextBoxReveal
              highlights={HIGHLIGHTS}
              scrollDrive
              className="max-w-none w-full"
            >
              Two years of Malaysian retail conversation, gathered from
              forums, moomoo, Reddit, YouTube, TikTok, Telegram, Facebook and
              the news.
            </TextBoxReveal>

            <div className="mt-10">
              <TextBoxReveal
                highlights={HIGHLIGHTS}
                scrollDrive
                className="max-w-none w-full"
              >
                The crowd turned on the debt before the market did. Then the
                rights issue made it official.
              </TextBoxReveal>
            </div>
          </div>

          <div className="hidden justify-center lg:flex" aria-hidden>
            <img
              src="/illustrations/landing/work.svg"
              alt=""
              draggable={false}
              className="h-72 w-72 object-contain xl:h-80 xl:w-80"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
