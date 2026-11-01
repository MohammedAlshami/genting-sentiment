'use client';

import React from 'react';
import { createPortal } from 'react-dom';
import { Link } from '@tanstack/react-router';
import { ArrowUpRight } from 'lucide-react';
import type { Project } from '@/data/projects';
import { PROJECT_ILLUSTRATION } from '@/data/components/project-illustrations';

type HoverState = { src: string; caption: string; x: number; y: number } | null;

const PREVIEW_W = 288;
const PREVIEW_H = 196;
const OFFSET = 16;

/** Single-column list of project links with a cursor-following preview (portaled to <body>). */
export default function ProjectGrid({ projects }: { projects: Project[] }) {
  const [hover, setHover] = React.useState<HoverState>(null);
  const [mounted, setMounted] = React.useState(false);
  const fine = React.useRef(false);

  React.useEffect(() => {
    setMounted(true);
    fine.current = !window.matchMedia('(pointer: coarse)').matches;
  }, []);

  const show = (project: Project, e: React.MouseEvent) => {
    if (!fine.current) return;
    const shot = project.screenshots[0];
    if (!shot) return;
    setHover({ src: shot.src, caption: shot.caption, x: e.clientX, y: e.clientY });
  };
  const move = (e: React.MouseEvent) => {
    if (!fine.current) return;
    setHover((h) => (h ? { ...h, x: e.clientX, y: e.clientY } : h));
  };
  const hide = () => setHover(null);

  const vw = typeof window !== 'undefined' ? window.innerWidth : 1280;
  const vh = typeof window !== 'undefined' ? window.innerHeight : 800;
  const pos = hover
    ? {
        x: hover.x + OFFSET + PREVIEW_W > vw - 8 ? hover.x - PREVIEW_W - OFFSET : hover.x + OFFSET,
        y: hover.y + OFFSET + PREVIEW_H > vh - 8 ? hover.y - PREVIEW_H - OFFSET : hover.y + OFFSET,
      }
    : { x: 0, y: 0 };

  return (
    <>
      <div className="border-t border-dashed border-white/25">
        {projects.map((project) => {
          const Illustration = PROJECT_ILLUSTRATION[project.id];
          const Icon = project.icon;
          return (
            <Link
              key={project.id}
              to="/projects/$id"
              params={{ id: project.id }}
              onMouseEnter={(e) => show(project, e)}
              onMouseMove={move}
              onMouseLeave={hide}
              className="group flex flex-col gap-4 border-b border-dashed border-white/25 px-5 py-8 transition-colors hover:bg-white/[0.03] md:flex-row md:items-center md:gap-10 md:px-10 md:py-12"
            >
              <div className="flex min-w-0 flex-1 items-center gap-4">
                {Illustration ? (
                  <Illustration className="h-24 w-24 shrink-0 object-contain transition-transform duration-300 group-hover:scale-[1.06]" />
                ) : (
                  <Icon className="size-6 shrink-0 text-[#FFF7DD]" />
                )}
                <div className="min-w-0">
                  <h3
                    className="text-2xl font-semibold tracking-tight text-[#FFF7DD] md:text-3xl"
                    style={{ fontFamily: '"Mori", sans-serif' }}
                  >
                    {project.title}
                  </h3>
                  <p className="mt-1.5 text-xs uppercase tracking-wider text-[#FFF7DD]/50">
                    {project.category}
                    {project.date ? ` · ${project.date}` : ''}
                  </p>
                </div>
              </div>
              <p className="text-base leading-relaxed text-[#FFF7DD]/70 md:max-w-2xl md:text-lg">
                {project.summary}
              </p>
              <ArrowUpRight className="hidden size-5 shrink-0 text-[#FFF7DD]/40 transition-all group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-[#FFF7DD] md:block" />
            </Link>
          );
        })}
      </div>

      {mounted &&
        hover &&
        createPortal(
          <div className="pointer-events-none fixed inset-0 z-[9999] hidden md:block" aria-hidden>
            <div
              className="absolute w-72 overflow-hidden rounded-xl border border-white/15 bg-[#141816] shadow-2xl shadow-black/60 will-change-transform"
              style={{ transform: `translate3d(${pos.x}px, ${pos.y}px, 0)` }}
            >
              <img src={hover.src} alt="" className="aspect-[16/10] w-full object-cover object-top" />
              <div className="truncate px-3 py-2 text-[11px] uppercase tracking-wider text-[#FFF7DD]/60">
                {hover.caption}
              </div>
            </div>
          </div>,
          document.body,
        )}
    </>
  );
}
