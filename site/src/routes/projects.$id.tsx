import type React from 'react';
import { createFileRoute, Link, notFound } from '@tanstack/react-router';
import { ArrowLeft, ArrowRight, ArrowUpRight, Github } from 'lucide-react';
import { NotFound } from '@/data/components/NotFound';
import ProjectGallery from '@/data/components/ProjectGallery';
import CodeTabs from '@/data/components/CodeTabs';
import { PROJECT_ILLUSTRATION } from '@/data/components/project-illustrations';
import { PROJECTS, getProject } from '@/data/projects';

export const Route = createFileRoute('/projects/$id')({
  loader: ({ params }) => {
    const project = getProject(params.id);
    if (!project) throw notFound();
    return project.id;
  },
  head: ({ params }) => {
    const project = getProject(params.id);
    return {
      meta: [
        { title: `${project?.title ?? 'Project'} · Shami` },
        { name: 'description', content: project?.summary ?? '' },
      ],
    };
  },
  notFoundComponent: () => <NotFound />,
  component: ProjectPage,
});

/** Section illustrations from the Notion freebie pack (cream line art). */
const SECTION_ART: Record<string, string> = {
  overview: '/illustrations/sections/overview.svg',
  'the problem': '/illustrations/sections/problem.svg',
  highlights: '/illustrations/sections/highlights.svg',
  'what it does': '/illustrations/sections/features.svg',
  architecture: '/illustrations/sections/architecture.svg',
  'under the hood': '/illustrations/sections/process.svg',
  usage: '/illustrations/sections/usage.svg',
  'use cases': '/illustrations/sections/usecases.svg',
  'tech stack': '/illustrations/sections/stack.svg',
  'how it was built': '/illustrations/sections/build.svg',
  'key takeaways': '/illustrations/sections/takeaways.svg',
  faq: '/illustrations/sections/faq.svg',
};

const art = (heading: string) => SECTION_ART[heading.trim().toLowerCase()];

function Art({ src, className = 'h-40 w-40 object-contain' }: { src?: string; className?: string }) {
  if (!src) return null;
  return <img src={src} alt="" className={className} draggable={false} />;
}

function ProjectPage() {
  const { id } = Route.useParams();
  const project = getProject(id)!;
  const index = PROJECTS.findIndex((p) => p.id === id);
  const next = PROJECTS[(index + 1) % PROJECTS.length];
  const Icon = project.icon;
  const Illustration = PROJECT_ILLUSTRATION[project.id];

  return (
    <div className="text-[#FFF7DD]">
      <main className="container mx-auto px-4 pt-12 pb-24 sm:px-6 md:pt-20 lg:px-8">
        <Link
          to="/projects"
          className="inline-flex items-center gap-2 text-sm uppercase tracking-wider text-[#FFF7DD]/60 transition-colors hover:text-[#FFF7DD]"
        >
          <ArrowLeft className="size-4" /> All projects
        </Link>

        {/* Hero */}
        <header className="mt-10 mb-12 md:mb-16">
          <div className="grid grid-cols-1 items-center gap-10 lg:grid-cols-[1.5fr_1fr] lg:gap-16">
            <div className="max-w-3xl">
              <div className="flex items-center gap-2 text-sm uppercase tracking-wider text-[#FFF7DD]/60">
                <Icon className="size-4" />
                {project.category}
                {project.date ? ` · ${project.date}` : ''}
              </div>
              <h1
                className="mt-6 text-4xl font-extrabold uppercase leading-[0.95] tracking-tighter sm:text-6xl lg:text-7xl"
                style={{ fontFamily: '"Mori", sans-serif' }}
              >
                {project.title}
              </h1>
              <p className="mt-8 max-w-2xl text-xl leading-relaxed text-[#FFF7DD]/80">
                {project.summary}
              </p>
              <div className="mt-8 flex flex-wrap items-center gap-3">
                {project.url && (
                  <a
                    href={project.url.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 rounded-lg bg-[#FFF7DD] px-5 py-3 text-sm font-bold uppercase tracking-wider text-[#0E100F] transition-colors hover:bg-white"
                  >
                    Visit {project.url.label} <ArrowUpRight className="size-4" />
                  </a>
                )}
                {project.repo && (
                  <a
                    href={project.repo.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 rounded-lg border border-dashed border-white/30 px-5 py-3 text-sm font-bold uppercase tracking-wider text-[#FFF7DD]/85 transition-colors hover:border-white/70 hover:text-[#FFF7DD]"
                  >
                    <Github className="size-4" /> {project.repo.label}
                  </a>
                )}
              </div>
              <ul className="mt-8 flex flex-wrap gap-2">
                {project.tags.map((tag) => (
                  <li
                    key={tag}
                    className="rounded-full border border-dashed border-white/25 px-3 py-1 text-xs uppercase tracking-wider text-[#FFF7DD]/70"
                  >
                    {tag}
                  </li>
                ))}
              </ul>
            </div>

            {Illustration && (
              <div className="hidden justify-center lg:flex" aria-hidden>
                <Illustration className="h-64 w-64 object-contain xl:h-72 xl:w-72" />
              </div>
            )}
          </div>
        </header>

        {/* At a glance */}
        {project.stats && project.stats.length > 0 && (
          <dl className="mb-12 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/10 md:mb-16 md:grid-cols-4">
            {project.stats.map((stat) => (
              <div key={stat.label} className="bg-[#0E100F] px-5 py-6 md:px-6 md:py-7">
                <dd
                  className="text-3xl font-bold tracking-tight md:text-4xl"
                  style={{ fontFamily: '"Mori", sans-serif' }}
                >
                  {stat.value}
                </dd>
                <dt className="mt-1.5 text-xs uppercase tracking-wider text-[#FFF7DD]/50">
                  {stat.label}
                </dt>
              </div>
            ))}
          </dl>
        )}

        {/* Gallery */}
        {project.screenshots.length > 0 && (
          <div className="mb-12 md:mb-20">
            <ProjectGallery key={project.id} shots={project.screenshots} />
          </div>
        )}

        <div>
          {project.sections.map((section) => (
            <Row key={section.heading} heading={section.heading} media={<Art src={art(section.heading)} />}>
              {section.body && <p>{section.body}</p>}
              {section.points && (
                <ul className="space-y-3">
                  {section.points.map((point) => (
                    <li key={point} className="flex gap-3">
                      <span className="mt-3 h-px w-4 shrink-0 bg-[#FFF7DD]/50" aria-hidden />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Row>
          ))}

          {project.features && project.features.length > 0 && (
            <Row heading="What it does" media={<Art src={art('what it does')} />}>
              <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {project.features.map((feature) => (
                  <li
                    key={feature.title}
                    className="rounded-xl border border-dashed border-white/25 p-5 transition-colors hover:border-white/50 hover:bg-white/[0.03]"
                  >
                    <img src={feature.icon} alt="" className="size-7" draggable={false} />
                    <h3 className="mt-4 text-lg font-semibold text-[#FFF7DD]">{feature.title}</h3>
                    <p className="mt-1.5 text-base leading-relaxed text-[#FFF7DD]/65">{feature.body}</p>
                  </li>
                ))}
              </ul>
            </Row>
          )}

          <Row heading="Architecture" media={<Art src={project.diagram ?? art('architecture')} />}>
            <p>{project.architecture.summary}</p>
            <ol className="mt-6 rounded-xl border border-dashed border-white/25">
              {project.architecture.layers.map((layer, i) => (
                <li
                  key={layer.label}
                  className="flex gap-4 border-dashed border-white/25 p-4 md:p-5 [&:not(:last-child)]:border-b"
                >
                  <span className="w-6 shrink-0 font-mono text-sm text-[#FFF7DD]/40">
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <div>
                    <p className="font-semibold text-[#FFF7DD]">{layer.label}</p>
                    <p className="mt-1 text-base text-[#FFF7DD]/65">{layer.detail}</p>
                  </div>
                </li>
              ))}
            </ol>
          </Row>

          {project.flow && (
            <Row
              heading="Under the hood"
              media={<Art src={art('under the hood')} />}
            >
              <ol className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                {project.flow.steps.map((step, i) => (
                  <li key={step.title} className="rounded-xl border border-dashed border-white/25 p-5">
                    <span className="font-mono text-xs text-[#FFF7DD]/40">
                      {String(i + 1).padStart(2, '0')}
                    </span>
                    <p className="mt-2 text-lg font-semibold text-[#FFF7DD]">{step.title}</p>
                    <p className="mt-1.5 text-base leading-relaxed text-[#FFF7DD]/65">{step.body}</p>
                  </li>
                ))}
              </ol>
              {project.flow.image && (
                <figure className="mt-6 overflow-hidden rounded-xl border border-dashed border-white/20 bg-white/[0.02] p-6">
                  <img
                    src={project.flow.image}
                    alt=""
                    className="mx-auto h-auto w-full max-w-md object-contain"
                    draggable={false}
                  />
                </figure>
              )}
            </Row>
          )}

          {project.snippets && project.snippets.length > 0 && (
            <Row heading="Usage" media={<Art src={art('usage')} />}>
              {project.snippetIntro && <p>{project.snippetIntro}</p>}
              <CodeTabs snippets={project.snippets} />
            </Row>
          )}

          {project.useCases && project.useCases.length > 0 && (
            <Row heading="Use cases" media={<Art src={art('use cases')} />}>
              <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {project.useCases.map((useCase) => (
                  <li key={useCase.title} className="rounded-xl border border-dashed border-white/25 p-5">
                    <p className="text-lg font-semibold text-[#FFF7DD]">{useCase.title}</p>
                    <p className="mt-1.5 text-base leading-relaxed text-[#FFF7DD]/65">{useCase.body}</p>
                  </li>
                ))}
              </ul>
            </Row>
          )}

          <Row heading="Tech stack" media={<Art src={art('tech stack')} />}>
            <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {project.stack.map((tech) => (
                <li
                  key={tech.name}
                  className="flex items-center gap-3 rounded-xl border border-dashed border-white/25 px-4 py-3 text-base text-[#FFF7DD] transition-all duration-200 hover:-translate-y-0.5 hover:border-[#FFF7DD]/70 hover:bg-white/[0.06]"
                >
                  <span
                    role="img"
                    aria-label={`${tech.name} logo`}
                    className="size-6 shrink-0 bg-[#FFF7DD]"
                    style={{
                      maskImage: `url(/logos/${tech.logo}.svg)`,
                      WebkitMaskImage: `url(/logos/${tech.logo}.svg)`,
                      maskRepeat: 'no-repeat',
                      WebkitMaskRepeat: 'no-repeat',
                      maskSize: 'contain',
                      WebkitMaskSize: 'contain',
                      maskPosition: 'center',
                      WebkitMaskPosition: 'center',
                    }}
                  />
                  {tech.name}
                </li>
              ))}
            </ul>
          </Row>

          {project.build && project.build.length > 0 && (
            <Row heading="How it was built" media={<Art src={art('how it was built')} />}>
              <ol className="space-y-6">
                {project.build!.map((step, i) => (
                  <li key={step.title} className="flex gap-4">
                    <span className="w-6 shrink-0 pt-1 font-mono text-sm text-[#FFF7DD]/40">
                      {String(i + 1).padStart(2, '0')}
                    </span>
                    <div>
                      <p className="text-xl font-semibold text-[#FFF7DD]">{step.title}</p>
                      <p className="mt-1">{step.body}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </Row>
          )}

          {project.faq && project.faq.length > 0 && (
            <Row heading="FAQ" media={<Art src={art('faq')} />}>
              <dl className="space-y-6">
                {project.faq.map((item) => (
                  <div key={item.q}>
                    <dt className="text-lg font-semibold text-[#FFF7DD]">{item.q}</dt>
                    <dd className="mt-1.5 text-base leading-relaxed text-[#FFF7DD]/65">{item.a}</dd>
                  </div>
                ))}
              </dl>
            </Row>
          )}

          {project.learned && (
            <Row heading="Key takeaways" media={<Art src={art('key takeaways')} />}>
              <p>{project.learned}</p>
            </Row>
          )}
        </div>

        <Link
          to="/projects/$id"
          params={{ id: next.id }}
          className="group mt-8 flex items-center justify-between gap-6 border-t border-dashed border-white/25 pt-10"
        >
          <div>
            <p className="text-sm uppercase tracking-wider text-[#FFF7DD]/50">Next project</p>
            <p
              className="mt-2 text-2xl font-bold tracking-tight md:text-4xl"
              style={{ fontFamily: '"Mori", sans-serif' }}
            >
              {next.title}
            </p>
          </div>
          <ArrowRight className="size-8 shrink-0 transition-transform group-hover:translate-x-1" />
        </Link>
      </main>
    </div>
  );
}

function Row({
  heading,
  media,
  children,
}: {
  heading: string;
  media?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="grid grid-cols-1 gap-4 border-t border-dashed border-white/25 py-10 lg:grid-cols-[1fr_2fr] lg:gap-20 md:py-14">
      <div>
        <h2 className="text-2xl font-semibold md:text-3xl" style={{ fontFamily: '"Mori", sans-serif' }}>
          {heading}
        </h2>
        {media && <div className="mt-6 hidden lg:block">{media}</div>}
      </div>
      <div className="space-y-4 text-lg leading-relaxed text-[#FFF7DD]/70">{children}</div>
    </section>
  );
}
