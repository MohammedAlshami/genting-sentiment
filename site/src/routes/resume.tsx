import type React from 'react';
import { createFileRoute, Link } from '@tanstack/react-router';
import { ArrowUpRight, Medal } from 'lucide-react';
import DownloadPdfButton from '@/data/components/resume/DownloadPdfButton';
import { PROJECTS as SITE_PROJECTS } from '@/data/projects';
import {
  ACHIEVEMENTS,
  EDUCATION,
  EMAIL,
  EXPERIENCE,
  LOCATION,
  NAME,
  PORTFOLIO,
  PORTFOLIO_URL,
  PROFILE,
  PROJECTS,
  RESEARCH,
  SKILLS,
  TITLE,
} from '@/data/resume-data';

export const Route = createFileRoute('/resume')({
  head: () => ({
    meta: [
      { title: `Résumé · ${NAME}` },
      {
        name: 'description',
        content:
          'AI engineer for agentic workflows and AI orchestration: multi-agent LangGraph systems, reference gathering, fact-checking and citation verification, RAG, evaluation and cost/latency tuning. Experience, projects, research and skills.',
      },
    ],
  }),
  component: ResumePage,
});

function ResumePage() {
  const onSite = new Set(SITE_PROJECTS.map((p) => p.id));

  return (
    <div className="resume-page text-[#FFF7DD]">
      <main className="mx-auto max-w-5xl px-4 pb-24 pt-16 sm:px-6 md:pt-24 lg:px-8">
        {/* Header */}
        <header className="border-b border-dashed border-white/20 pb-10">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-[#FFF7DD]/50">Résumé</p>
              <h1
                className="mt-4 text-4xl font-extrabold leading-[0.95] tracking-tight sm:text-5xl lg:text-6xl"
                style={{ fontFamily: '"Mori", sans-serif' }}
              >
                {NAME}
              </h1>
              <p className="mt-4 text-xl text-[#FFF7DD]/70">
                {TITLE}
              </p>
            </div>
            <DownloadPdfButton />
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-[#FFF7DD]/60">
            <span>{LOCATION}</span>
            <span aria-hidden>·</span>
            <a href={`mailto:${EMAIL}`} className="hover:text-[#FFF7DD]">
              {EMAIL}
            </a>
            <span aria-hidden>·</span>
            <a href={PORTFOLIO_URL} target="_blank" rel="noopener noreferrer" className="hover:text-[#FFF7DD]">
              {PORTFOLIO}
            </a>
          </div>
        </header>

        {/* Profile */}
        <Row heading="Profile">
          <p>{PROFILE}</p>
        </Row>

        {/* Experience first: the flagship agentic platform (IJO-BS / Imper) lives here */}
        <Row heading="Experience">
          <div className="space-y-9">
            {EXPERIENCE.map((job) => (
              <div key={`${job.org}-${job.role}`}>
                <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                  <h3 className="text-xl font-semibold text-[#FFF7DD]">
                    {job.org} · {job.role}
                  </h3>
                  <span className="text-sm uppercase tracking-wider text-[#FFF7DD]/50">{job.period}</span>
                </div>
                <p className="mt-1 text-xs uppercase tracking-wider text-[#FFF7DD]/45">{job.meta}</p>
                <ul className="mt-3 space-y-2">
                  {job.points.map((point) => (
                    <li key={point} className="flex gap-3">
                      <span className="mt-3 h-px w-4 shrink-0 bg-[#FFF7DD]/40" aria-hidden />
                      <span className="text-base leading-relaxed text-[#FFF7DD]/70">{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Row>

        {/* Supporting builds */}
        <Row heading="Projects">
          <div className="space-y-8">
            {PROJECTS.map((p) => {
              const linked = p.siteId && onSite.has(p.siteId);
              const head = (
                <span className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                  <span className="flex items-center gap-2 text-xl font-semibold text-[#FFF7DD]">
                    {p.title}
                    {linked && <ArrowUpRight className="size-4 shrink-0 text-[#FFF7DD]/40" aria-hidden />}
                  </span>
                  <span className="text-sm uppercase tracking-wider text-[#FFF7DD]/50">{p.tag}</span>
                </span>
              );
              return (
                <div key={p.title}>
                  {linked ? (
                    <Link to="/projects/$id" params={{ id: p.siteId! }} className="group block hover:text-white">
                      {head}
                    </Link>
                  ) : (
                    head
                  )}
                  {p.repo && (
                    <a
                      href={p.repo.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 inline-block text-sm text-[#FFF7DD]/50 hover:text-[#FFF7DD]"
                    >
                      {p.repo.label}
                    </a>
                  )}
                  <ul className="mt-3 space-y-2">
                    {p.points.map((point) => (
                      <li key={point} className="flex gap-3">
                        <span className="mt-3 h-px w-4 shrink-0 bg-[#FFF7DD]/40" aria-hidden />
                        <span className="text-base leading-relaxed text-[#FFF7DD]/70">{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
          <Link
            to="/projects"
            className="inline-block pt-2 text-sm uppercase tracking-wider text-[#FFF7DD]/60 hover:text-[#FFF7DD]"
          >
            All {SITE_PROJECTS.length} projects →
          </Link>
        </Row>

        {/* Research */}
        <Row heading="Research">
          <p>
            {RESEARCH.authors} <em>{RESEARCH.title}</em> {RESEARCH.venue}
          </p>
          <a
            href={RESEARCH.href}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm uppercase tracking-wider text-[#FFF7DD]/70 hover:text-[#FFF7DD]"
          >
            {RESEARCH.doi} <ArrowUpRight className="size-4" />
          </a>
        </Row>

        {/* Achievements */}
        <Row heading="Achievements">
          <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {ACHIEVEMENTS.map((item) => (
              <li key={item} className="flex items-start gap-3 rounded-xl border border-dashed border-white/20 p-4">
                <Medal className="mt-0.5 size-4 shrink-0 text-[#FFF7DD]/70" aria-hidden />
                <span className="text-base leading-snug text-[#FFF7DD]/80">{item}</span>
              </li>
            ))}
          </ul>
        </Row>

        {/* Education */}
        <Row heading="Education">
          <div>
            <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
              <h3 className="text-xl font-semibold text-[#FFF7DD]">{EDUCATION.school}</h3>
              <span className="text-sm uppercase tracking-wider text-[#FFF7DD]/50">{EDUCATION.period}</span>
            </div>
            <p className="mt-1 text-[#FFF7DD]/70">{EDUCATION.degree}</p>
            <p className="mt-2 text-base text-[#FFF7DD]/70">{EDUCATION.detail}</p>
          </div>
        </Row>

        {/* Skills */}
        <Row heading="Technical skills">
          <ul className="space-y-3">
            {SKILLS.map((s) => (
              <li key={s.label} className="grid grid-cols-1 gap-1 sm:grid-cols-[7rem_1fr] sm:gap-4">
                <span className="text-sm uppercase tracking-wider text-[#FFF7DD]/50">{s.label}</span>
                <span>{s.items}</span>
              </li>
            ))}
          </ul>
        </Row>

        {/* CTA */}
        <div className="mt-4 flex flex-wrap items-center gap-3 border-t border-dashed border-white/20 pt-10">
          <a
            href={`mailto:${EMAIL}`}
            className="rounded-lg bg-[#FFF7DD] px-5 py-3 text-sm font-bold uppercase tracking-wider text-[#0E100F] transition-colors hover:bg-white"
          >
            Get in touch
          </a>
          <Link
            to="/projects"
            className="rounded-lg border border-dashed border-white/25 px-5 py-3 text-sm font-bold uppercase tracking-wider text-[#FFF7DD]/80 transition-colors hover:border-[#FFF7DD]/60 hover:text-[#FFF7DD]"
          >
            See the work
          </Link>
        </div>
      </main>
    </div>
  );
}

function Row({ heading, children }: { heading: string; children: React.ReactNode }) {
  return (
    <section className="grid grid-cols-1 gap-4 border-t border-dashed border-white/20 py-10 md:py-12 lg:grid-cols-[1fr_2fr] lg:gap-16">
      <h2 className="text-2xl font-semibold md:text-3xl" style={{ fontFamily: '"Mori", sans-serif' }}>
        {heading}
      </h2>
      <div className="space-y-4 text-lg leading-relaxed text-[#FFF7DD]/70">{children}</div>
    </section>
  );
}
