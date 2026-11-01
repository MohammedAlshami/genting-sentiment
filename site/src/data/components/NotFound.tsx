import type { ReactNode } from 'react';
import { Link } from '@tanstack/react-router';

/** Themed 404 — used for unmatched routes and missing projects. */
export function NotFound({ children }: { children?: ReactNode }) {
  return (
    <div className="text-[#FFF7DD]">
      <main className="mx-auto flex min-h-[70vh] max-w-3xl flex-col items-center justify-center px-4 py-24 text-center sm:px-6">
        <p className="text-xs uppercase tracking-[0.3em] text-[#FFF7DD]/50">Error 404</p>
        <h1
          className="mt-6 text-7xl font-extrabold leading-none tracking-tight sm:text-9xl"
          style={{ fontFamily: '"Mori", sans-serif' }}
        >
          404
        </h1>
        <p className="mt-6 max-w-md text-lg leading-relaxed text-[#FFF7DD]/60">
          {children ?? 'This page does not exist — or it moved somewhere else.'}
        </p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          <Link
            to="/"
            className="rounded-lg bg-[#FFF7DD] px-5 py-3 text-sm font-bold uppercase tracking-wider text-[#0E100F] transition-colors hover:bg-white"
          >
            Back home
          </Link>
          <Link
            to="/projects"
            className="rounded-lg border border-dashed border-white/25 px-5 py-3 text-sm font-bold uppercase tracking-wider text-[#FFF7DD]/80 transition-colors hover:border-[#FFF7DD]/60 hover:text-[#FFF7DD]"
          >
            Browse projects
          </Link>
          <a
            href="mailto:mshami2021@gmail.com"
            className="rounded-lg px-5 py-3 text-sm font-bold uppercase tracking-wider text-[#FFF7DD]/60 transition-colors hover:text-[#FFF7DD]"
          >
            Contact
          </a>
        </div>
      </main>
    </div>
  );
}
