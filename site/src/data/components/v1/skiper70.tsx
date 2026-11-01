'use client';

import React, { useRef, useMemo, ReactNode } from 'react';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { cn } from '~/lib/utils';

export interface HighlightConfig {
  word: string;
  textClass?: string;
  bgClass?: string;
}

export interface TextBoxRevealProps {
  children: ReactNode;
  /** Single word to highlight (legacy) */
  highlight?: string;
  /** Multiple words with different styles */
  highlights?: HighlightConfig[];
  /** Tailwind/custom classes for highlighted word text (legacy single highlight) */
  highlightTextClass?: string;
  /** Tailwind/custom classes for highlighted word background (legacy single highlight) */
  highlightBgClass?: string;
  /** When true, reveal is tied to scroll progress (scroll down = forward, scroll up = reverse) */
  scrollDrive?: boolean;
  /** Container className */
  className?: string;
  /** Optional callback ref per word: (word, element) when a word span mounts/unmounts. Use to anchor to a specific word (e.g. "Ready"). */
  wordRef?: (word: string, el: HTMLElement | null) => void;
}

/**
 * Text reveal: words appear one-by-one. Either on visible (once) or scroll-driven.
 * Use <br /> for line breaks.
 */
export function TextBoxReveal({
  children,
  highlight,
  highlights: highlightsProp,
  highlightTextClass = '!text-[#0E100F]',
  highlightBgClass = '!bg-amber-200/80',
  scrollDrive = false,
  className,
  wordRef,
}: TextBoxRevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.2 });

  const segments = useMemo(() => {
    const flat: Array<{ type: 'word'; text: string } | { type: 'br' }> = [];

    function walk(node: ReactNode): void {
      if (node == null) return;
      if (typeof node === 'string') {
        const words = node.split(/\s+/).filter(Boolean);
        words.forEach((w) => flat.push({ type: 'word', text: w }));
        return;
      }
      if (Array.isArray(node)) {
        node.forEach(walk);
        return;
      }
      if (React.isValidElement(node)) {
        if (node.type === 'br') {
          flat.push({ type: 'br' });
          return;
        }
        if (node.props?.children != null) {
          walk(node.props.children);
        }
        return;
      }
    }

    walk(children);
    return flat;
  }, [children]);

  const wordCount = useMemo(() => segments.filter((s) => s.type === 'word').length, [segments]);

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });

  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.04,
        delayChildren: 0.05,
      },
    },
  };

  const wordVariants = {
    hidden: {
      opacity: 0,
      scale: 0.95,
      filter: 'blur(4px)',
    },
    visible: {
      opacity: 1,
      scale: 1,
      filter: 'blur(0px)',
      transition: {
        duration: 0.35,
        ease: [0.25, 0.46, 0.45, 0.94],
      },
    },
  };

  const highlights: HighlightConfig[] = useMemo(() => {
    if (highlightsProp?.length) return highlightsProp;
    if (highlight != null) {
      return [{ word: highlight, textClass: highlightTextClass, bgClass: highlightBgClass }];
    }
    return [];
  }, [highlightsProp, highlight, highlightTextClass, highlightBgClass]);

  const getHighlightStyle = (word: string): { textClass: string; bgClass: string } | null => {
    const found = highlights.find(
      (h) => h.word.toLowerCase() === word.toLowerCase()
    );
    if (!found) return null;
    return {
      textClass: found.textClass ?? '!text-[#0E100F]',
      bgClass: found.bgClass ?? '!bg-amber-200/80',
    };
  };

  const useScrollReveal = scrollDrive && wordCount > 0;

  return (
    <motion.div
      ref={ref}
      className={cn('max-w-3xl', className)}
      initial="hidden"
      animate={!useScrollReveal && isInView ? 'visible' : 'hidden'}
      variants={containerVariants}
    >
      <span className="inline-block leading-relaxed">
        {segments.map((seg, i) => {
          if (seg.type === 'br') {
            return <br key={`br-${i}`} />;
          }
          const word = seg.text;
          const highlightStyle = getHighlightStyle(word);

          if (useScrollReveal) {
            const wordIndex = segments.slice(0, i).filter((s) => s.type === 'word').length;
            const start = (wordIndex / wordCount) * 0.55;
            const end = start + 0.06;
            const opacity = useTransform(scrollYProgress, [start, end], [0, 1]);
            const scale = useTransform(scrollYProgress, [start, end], [0.95, 1]);
            const filter = useTransform(
              scrollYProgress,
              [start, end],
              ['blur(4px)', 'blur(0px)']
            );

            return (
              <motion.span
                key={`${i}-${word}`}
                ref={(el) => wordRef?.(word, el)}
                className="relative inline-block whitespace-nowrap px-0.5 py-0.5"
                style={{ opacity, scale, filter }}
              >
                {highlightStyle ? (
                  <span
                    className={cn(
                      'relative z-[1] px-1 rounded font-semibold',
                      highlightStyle.textClass,
                      highlightStyle.bgClass
                    )}
                  >
                    {word}
                  </span>
                ) : (
                  <span className="relative z-[1]">{word}</span>
                )}
                {i < segments.length - 1 &&
                  segments[i + 1]?.type === 'word' &&
                  '\u00A0'}
              </motion.span>
            );
          }

          return (
            <motion.span
              key={`${i}-${word}`}
              ref={(el) => wordRef?.(word, el)}
              variants={wordVariants}
              className="relative inline-block whitespace-nowrap px-0.5 py-0.5"
            >
              {highlightStyle ? (
                <span
                  className={cn(
                    'relative z-[1] px-1 rounded',
                    highlightStyle.textClass,
                    highlightStyle.bgClass
                  )}
                >
                  {word}
                </span>
              ) : (
                <span className="relative z-[1]">{word}</span>
              )}
              {i < segments.length - 1 &&
                segments[i + 1]?.type === 'word' &&
                '\u00A0'}
            </motion.span>
          );
        })}
      </span>
    </motion.div>
  );
}

export default TextBoxReveal;
