"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import ScrollAnimationWrapper from "@/data/components/Landing/ScrollAnimationWrapper";

const QUOTE_TEXT =
  "Two years of Malaysian retail conversation about Genting — gathered from forums, moomoo, Reddit, YouTube, TikTok, Telegram, Facebook and the news. The corpus follows the share price, the debt, the failed privatisation and the rights issue. It is not a poll. It is what people actually wrote, across 69,000 posts and comments, scored and aligned to the events that moved the stock.";

const SUBTITLE = "Two years of Malaysian retail conversation about Genting";

const ILLUSTRATIONS = [
  { src: "/illustrations/landing/launch.svg", label: "Debt" },
  { src: "/illustrations/landing/time.svg", label: "Dilution" },
  { src: "/illustrations/landing/key.svg", label: "New York" },
];

export default function ImageGridSection() {
  const sectionRef = useRef<HTMLElement>(null);

  const { scrollYProgress: sectionProgress } = useScroll({
    target: sectionRef,
    offset: ["start 1.05", "start 0"],
  });

  const contentOpacity = useTransform(sectionProgress, [0.2, 0.5], [0, 1]);
  const contentY = useTransform(sectionProgress, [0.2, 0.5], [20, 0]);

  return (
    <section
      ref={sectionRef}
      className="relative w-full min-w-0 pb-20 sm:pb-24 md:pb-28 lg:pb-32 overflow-hidden bg-white font-sf-pro-display"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <ScrollAnimationWrapper>
          <motion.div className="relative" style={{ opacity: contentOpacity, y: contentY }}>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center min-h-[60vh]">
              <div className="lg:border-r border-black/10 lg:pr-12">
                <p className="font-display-hero text-8xl sm:text-9xl lg:text-[10rem] font-extrabold tracking-tighter leading-[0.9] text-[#0E100F]">
                  The signal
                </p>
              </div>
              <div>
                <p className="font-sf-pro-text text-2xl text-[#0E100F]/90 mb-6">{SUBTITLE}</p>
                <p className="font-sf-pro-display text-lg text-[#0E100F]/60 leading-relaxed">
                  {QUOTE_TEXT}
                </p>
              </div>
            </div>

            <div className="mt-16 grid grid-cols-3 items-end gap-6 sm:mt-24 sm:gap-12 md:gap-16">
              {ILLUSTRATIONS.map((item) => (
                <figure key={item.src} className="text-center">
                  <img
                    src={item.src}
                    alt=""
                    aria-hidden
                    draggable={false}
                    className="mx-auto h-28 w-28 object-contain sm:h-40 sm:w-40 md:h-52 md:w-52 lg:h-64 lg:w-64"
                  />
                  <figcaption className="mt-5 text-sm font-medium uppercase tracking-[0.18em] text-[#0E100F]/60 sm:mt-6 sm:text-base md:text-lg">
                    {item.label}
                  </figcaption>
                </figure>
              ))}
            </div>
          </motion.div>
        </ScrollAnimationWrapper>
      </div>
    </section>
  );
}
