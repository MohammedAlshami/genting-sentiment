import { createFileRoute } from '@tanstack/react-router';
import ProjectGrid from '@/data/components/ProjectGrid';
import { PROJECTS } from '@/data/projects';

export const Route = createFileRoute('/projects/')({
  head: () => ({
    meta: [
      { title: 'Projects · Shami' },
      {
        name: 'description',
        content:
          'AI, automation and full-stack projects by Shami — agentic platforms, APIs and search, mobile and business software.',
      },
    ],
  }),
  component: ProjectsPage,
});

function ProjectsPage() {
  return (
    <div className="text-[#FFF7DD]">
      <main className="mx-auto max-w-7xl px-4 pb-24 pt-16 sm:px-6 md:pt-24 lg:px-8">
        <header className="max-w-4xl">
          <p className="text-xs uppercase tracking-[0.2em] text-[#FFF7DD]/50">
            Selected work · {PROJECTS.length} projects
          </p>
          <h1
            className="mt-5 text-5xl font-extrabold leading-[0.95] tracking-tight sm:text-7xl lg:text-8xl"
            style={{ fontFamily: '"Mori", sans-serif' }}
          >
            Projects
          </h1>
          <p className="mt-7 max-w-2xl text-lg leading-relaxed text-[#FFF7DD]/60">
            Things I have built and researched — agentic AI platforms, APIs and search, mobile and business
            software. Each one has a page that breaks down the problem, the approach and the key takeaways.
          </p>
        </header>

        <div className="mt-14 md:mt-20">
          <ProjectGrid projects={PROJECTS} />
        </div>
      </main>
    </div>
  );
}
