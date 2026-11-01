'use client';

import React, { useRef, useEffect } from 'react';
import {
  motion,
  useMotionTemplate,
  useScroll,
  useTransform,
} from 'framer-motion';

const SECTION_HEIGHT = 1500;

const MAIN_IMAGE_URL =
  '/landing/images/genting-hero.svg';

const PARALLAX_HERO_IMAGES = [
  { src: '/landing/images/genting-a.svg', alt: 'Corpus' },
  { src: '/landing/images/genting-b.svg', alt: 'Rights issue' },
];

/** Very high grain overlay for the center hero image */
function HighGrainOverlay({ containerRef }: { containerRef: React.RefObject<HTMLDivElement | null> }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    const resize = () => {
      if (!container || !canvas) return;
      const rect = container.getBoundingClientRect();
      const dpr = typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1;
      const w = Math.ceil(rect.width * dpr);
      const h = Math.ceil(rect.height * dpr);
      if (w <= 0 || h <= 0) return;
      canvas.width = w;
      canvas.height = h;
      canvas.style.width = '100%';
      canvas.style.height = '100%';
      const imageData = ctx.createImageData(w, h);
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        const v = Math.random() * 255;
        data[i] = data[i + 1] = data[i + 2] = v;
        data[i + 3] = 45;
      }
      ctx.putImageData(imageData, 0, 0);
    };

    const ro = typeof window !== 'undefined' ? new ResizeObserver(resize) : null;
    if (ro) {
      ro.observe(container);
      resize();
    }
    return () => ro?.disconnect();
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 h-full w-full z-[1]"
      style={{
        imageRendering: 'pixelated',
        mixBlendMode: 'overlay',
        maskImage: 'linear-gradient(to bottom, transparent 0%, black 30%, black 50%, transparent 100%)',
        WebkitMaskImage: 'linear-gradient(to bottom, transparent 0%, black 30%, black 50%, transparent 100%)',
      }}
      aria-hidden
    />
  );
}

export function SmoothScrollHeroContent() {
  return (
    <>
      <Hero />
    </>
  );
}

const Hero = () => {
  const { scrollY } = useScroll();
  const textScale = useTransform(scrollY, [0, 1200], [0.28, 1]);

  return (
    <div
      style={{ height: `calc(${SECTION_HEIGHT}px + 100vh)` }}
      className="relative w-full"
    >
      <CenterImage />
      {/* GENTING text centered over the main image – starts very small, grows with scroll */}
      <div className="pointer-events-none absolute inset-0 z-10 flex justify-center">
        <div className="sticky top-0 h-screen flex items-center justify-center px-6">
          <motion.div className="text-right w-fit" style={{ scale: textScale }}>
            <h1
              className="font-bold tracking-tight leading-none mb-1 sm:mb-2 whitespace-nowrap select-none"
              style={{
                fontFamily: '"Mori", sans-serif',
                fontSize: 'clamp(40px, 10vw, 190px)',
                color: '#FFF7DD',
              }}
            >
              GENTING
            </h1>
            <p
              className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl 2xl:text-3xl font-medium tracking-wide whitespace-nowrap uppercase"
              style={{ fontFamily: '"Mori", sans-serif', color: '#FFF7DD' }}
            >
              Retail sentiment · Malaysia · 2016—2026
            </p>
          </motion.div>
        </div>
      </div>
      <ParallaxImages />
      <div className="absolute bottom-0 left-0 right-0 h-96 bg-gradient-to-b from-[#0E100F]/0 to-[#0E100F]" />
    </div>
  );
};

const CenterImage = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollY } = useScroll();

  const clip1 = useTransform(scrollY, [0, 1500], [25, 0]);
  const clip2 = useTransform(scrollY, [0, 1500], [75, 100]);

  const clipPath = useMotionTemplate`polygon(${clip1}% ${clip1}%, ${clip2}% ${clip1}%, ${clip2}% ${clip2}%, ${clip1}% ${clip2}%)`;

  const backgroundSize = useTransform(
    scrollY,
    [0, 1200],
    ['55%', '100%']
  );
  const grainScale = useTransform(scrollY, [0, 1200], [0.55, 1]);
  const opacity = useTransform(
    scrollY,
    [SECTION_HEIGHT, SECTION_HEIGHT + 500],
    [1, 0]
  );

  return (
    <motion.div
      ref={containerRef}
      className="sticky top-0 h-screen w-full relative"
      style={{
        clipPath,
        backgroundSize,
        opacity,
        backgroundImage: `url(${MAIN_IMAGE_URL})`,
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        maskImage: 'linear-gradient(to bottom, transparent 0%, black 30%, black 50%, transparent 100%)',
        WebkitMaskImage: 'linear-gradient(to bottom, transparent 0%, black 30%, black 50%, transparent 100%)',
      }}
    >
      <div className="absolute inset-0 bg-[#0E100F]/60" aria-hidden />
      <motion.div
        className="absolute inset-0 origin-center"
        style={{ scale: grainScale }}
      >
        <HighGrainOverlay containerRef={containerRef} />
      </motion.div>
    </motion.div>
  );
};

interface ParallaxImgWithGrainProps {
  src: string;
  alt: string;
  start: number;
  end: number;
  containerClassName: string;
  imgClassName: string;
}

const ParallaxImgWithGrain = ({
  src,
  alt,
  start,
  end,
  containerClassName,
  imgClassName,
}: ParallaxImgWithGrainProps) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: [`${start}px end`, `end ${end * -1}px`],
  });

  const opacity = useTransform(scrollYProgress, [0.75, 1], [1, 0]);
  const scale = useTransform(scrollYProgress, [0.75, 1], [1, 0.85]);
  const y = useTransform(scrollYProgress, [0, 1], [start, end]);
  const transform = useMotionTemplate`translateY(${y}px) scale(${scale})`;

  return (
    <motion.div
      ref={containerRef}
      className={`relative overflow-hidden ${containerClassName}`}
      style={{ transform, opacity }}
    >
      <img src={src} alt={alt} className={imgClassName} />
      <HighGrainOverlay containerRef={containerRef} />
    </motion.div>
  );
};

const ParallaxImages = () => {
  return (
    <div className="mx-auto max-w-5xl px-4 pt-[200px] flex justify-between gap-4">
      <ParallaxImgWithGrain
        src={PARALLAX_HERO_IMAGES[0].src}
        alt={PARALLAX_HERO_IMAGES[0].alt}
        start={-200}
        end={200}
        containerClassName="w-1/3"
        imgClassName="block w-full h-auto"
      />
      <ParallaxImgWithGrain
        src={PARALLAX_HERO_IMAGES[1].src}
        alt={PARALLAX_HERO_IMAGES[1].alt}
        start={-200}
        end={200}
        containerClassName="w-1/3"
        imgClassName="block w-full h-auto"
      />
    </div>
  );
};
