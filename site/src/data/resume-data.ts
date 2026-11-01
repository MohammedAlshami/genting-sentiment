/**
 * Single source of truth for the résumé. Used by the website page (routes/resume.tsx)
 * and the downloadable PDF (components/resume/ResumePdf.tsx).
 */

export const NAME = 'Mohammed Al-shami';
export const TITLE = 'AI Engineer — Agentic Workflows & Orchestration';
export const LOCATION = 'Malaysia';
export const EMAIL = 'mshami2021@gmail.com';
export const PORTFOLIO = 'portfolio.mshami2021.workers.dev';
export const PORTFOLIO_URL = 'https://portfolio.mshami2021.workers.dev';

export const PROFILE =
  'AI engineer with nearly three years of experience building LLM agents that do real work in production. At IJO-BS, an academic journal, I built Imper, the platform the review team uses every day, where agents find references for a paper, check that each one is real and relevant, and fact-check claims against their sources. I focus on what makes agents dependable: clear limits on what they can do, runs that recover after a crash, and measuring where the time and cost go.';

export type Job = { role: string; org: string; meta: string; period: string; points: string[] };

export const EXPERIENCE: Job[] = [
  {
    role: 'AI Engineer',
    org: 'IJO-BS, International Journal of Business and Society',
    meta: 'Full-time, remote · Malaysia',
    period: '01/2024 — Present',
    points: [
      'Built Imper (imper.app), the journal’s internal tool for reviewing papers, used daily by the whole review team. Teams of LLM agents, orchestrated with LangGraph, find references for a paper, check each one, and fact-check claims against the cited sources.',
      'Wrote the checks that keep fake or unreachable citations out. Every candidate is looked up in Crossref, DOAJ, Semantic Scholar and Unpaywall, then an LLM judge reads it against the paper’s topic. Anything that fails is dropped and replaced.',
      'Made runs predictable. Agents follow a fixed plan with a step limit and a tool budget instead of deciding for themselves when to stop, and progress is saved to MongoDB so a crashed run picks up where it left off. This came from debugging runs that reported “completed” while silently losing most of their results.',
      'Cut run time by measuring it. Gathering 150 references now takes about 5 minutes, where the first version took about an hour for 200. Most of the gain came from fewer agent steps and turning off model reasoning for simple scoring (about 18s down to 1.3s per batch). The last large run collected 463 candidates and kept 150, with no duplicates.',
      'Also maintain the journal’s website: submissions, peer review, issues and article search (Flask, MongoDB), with automatic DOI registration through Crossref.',
    ],
  },
  {
    role: 'Software Engineer',
    org: 'Arabic Arena',
    meta: 'Part-time, remote · Indonesia',
    period: '06/2024 — Present',
    points: [
      'Maintain the platform behind an online Arabic school: a bilingual (EN/AR) Next.js site, admin dashboard and learning platform.',
      'Added AI assistance for content and student support, plus Terraform infrastructure and Playwright end-to-end tests.',
    ],
  },
  {
    role: 'Software Engineering Intern',
    org: 'Aonic (formerly Poladrone)',
    meta: 'Selangor, Malaysia',
    period: '07/2023 — 10/2023',
    points: [
      'Built a UAV performance analysis system that detected defects and generated datasets for an AI path-navigation system.',
      'Cut project creation from two days to minutes by automating the workflow across the GIS and software teams.',
    ],
  },
];

export type ResumeProject = {
  title: string;
  tag: string;
  /** Project page id on this site, when it is public there. */
  siteId?: string;
  /** Source repository, shown as a link. */
  repo?: { label: string; href: string };
  points: string[];
};

/** Supporting builds: the flagship agentic platform lives under Experience (IJO-BS / Imper). */
export const PROJECTS: ResumeProject[] = [
  {
    title: 'OpenAbstracts',
    tag: 'Citation search for AI assistants (MCP server and API)',
    siteId: 'openabstracts',
    repo: { label: 'github.com/MohammedAlshami/openabstracts', href: 'https://github.com/MohammedAlshami/openabstracts' },
    points: [
      'A remote MCP server and Claude Skill that lets an AI assistant look up and check real citations across more than 10 million papers from 100,000+ journals, searching titles, abstracts and full PDF text (OpenSearch).',
      'Built the pipeline that collects journals, extracts PDF text and indexes it, plus API keys, usage tracking and pay-per-search billing.',
    ],
  },
  {
    title: 'Agentic News',
    tag: 'Automated Arabic newsroom',
    siteId: 'news-platform',
    repo: { label: 'github.com/MohammedAlshami/news-app', href: 'https://github.com/MohammedAlshami/news-app' },
    points: [
      'Collects articles from Arabic news outlets every hour, groups the ones about the same event, and writes a sourced Arabic article for each every 10 minutes.',
      'Grouping was the hard part. I labelled 162 articles by hand and tested 11 methods. The one I shipped (LLM-extracted signatures, blocking, then an LLM judge) scored F1 0.90, against 0.53 for the original logic.',
      'Guards against bad output: stale or duplicate stories are skipped before any model call, a claim step stops two writers taking the same story, and every article links its sources.',
    ],
  },
  {
    title: 'Cashirk',
    tag: 'Voice agent in the browser',
    siteId: 'cashirk',
    points: ['Create an agent on the ElevenLabs Agents platform and talk to it in the browser, with live WebRTC audio, a running transcript and a 3D visual.'],
  },
  {
    title: 'Workshop',
    tag: 'Multi-tenant POS and workshop management',
    siteId: 'workshop-management',
    points: [
      'Job cards with QC checks and customer approval, quotations, invoices, stock and purchase orders, staff reports and five user roles (TanStack Start, PostgreSQL, Socket.IO).',
    ],
  },
  {
    title: 'Waffa',
    tag: 'Arabic e-commerce marketplace app',
    siteId: 'waffa-app',
    points: [
      'React Native (Expo) marketplace with orders, buyer-seller chat and seller stores, plus a right-to-left Arabic UI over a Flask API and MongoDB.',
    ],
  },
];

export const EDUCATION = {
  school: 'Universiti Tenaga Nasional',
  degree: 'Bachelor of Computer Science (Software Engineering) (Hons.)',
  period: '09/2021 — 09/2024',
  detail: 'CGPA 3.79 / 4.00 · Head of Program Management, Programming Club (2022–23) · Directed HACK@10, a national-level hackathon',
};

export const RESEARCH = {
  authors: 'Solemon, B., Ahmed, A. M. Z., & Zarime, N. A. (2025).',
  title: 'A comparative analysis of web-based tools for landslide mapping and visualization.',
  venue: 'Smart Construction and Sustainable Cities.',
  doi: 'doi.org/10.1007/s44268-025-00054-w',
  href: 'https://doi.org/10.1007/s44268-025-00054-w',
};

export const ACHIEVEMENTS = [
  'Champion — Agrinxt (national)',
  'Champion — UMHackathon (national)',
  'Champion — SafetyHack (national)',
  '1st Runner-up — TCS Sustainathon (national)',
  'Top 7 — Hilti IT Competition (international)',
  'Top 15 — PolyHack Hong Kong (international)',
];

export const SKILLS: { label: string; items: string }[] = [
  { label: 'Agents & orchestration', items: 'LangGraph, LangChain, OpenAI Agents SDK, MCP, tool calling, multi-agent workflows, RAG, ElevenLabs Agents' },
  { label: 'Reliability & evaluation', items: 'LLM judges, benchmarking, resumable and durable runs, step limits, cost and latency tuning, LLM APIs' },
  { label: 'Languages', items: 'TypeScript / JavaScript, Python, SQL · Arabic (native), English (fluent)' },
  { label: 'Web', items: 'React, Next.js, Node.js, TanStack Start, Flask, Tailwind CSS, React Native (Expo)' },
  { label: 'Data & infra', items: 'PostgreSQL, MongoDB, OpenSearch, Redis, Docker, Amazon S3, Cloudflare Workers / D1 / R2, Terraform, Drizzle' },
];
