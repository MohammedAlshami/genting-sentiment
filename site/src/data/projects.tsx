import {
  BookOpen,
  Calculator,
  FileSearch,
  Files,
  Glasses,
  GraduationCap,
  Layers,
  Mail,
  Mic,
  Newspaper,
  ShoppingBag,
  Smartphone,
  Users,
  Wrench,
  Map,
  Presentation,
  Bot,
  FileText,
  MessageCircle,
  type LucideIcon,
} from 'lucide-react';

export type ProjectSection = {
  heading: string;
  body?: string;
  points?: string[];
};

export type Tech = { name: string; logo: string };

export type ArchLayer = { label: string; detail: string };

export type BuildStep = { title: string; body: string };

export type Screenshot = { src: string; caption: string };

export type Stat = { value: string; label: string };

export type Feature = { icon: string; title: string; body: string };

export type Snippet = { label: string; code: string };

export type UseCase = { title: string; body: string };

export type Faq = { q: string; a: string };

export type Flow = { image?: string; steps: { title: string; body: string }[] };

export type Project = {
  id: string;
  title: string;
  category: string;
  date?: string;
  url?: { label: string; href: string };
  repo?: { label: string; href: string };
  icon: LucideIcon;
  summary: string;
  tags: string[];
  screenshots: Screenshot[];
  sections: ProjectSection[];
  architecture: { summary: string; layers: ArchLayer[] };
  stack: Tech[];
  /** At-a-glance figures shown as a strip under the hero. */
  stats?: Stat[];
  /** Capability cards ("What it does"). */
  features?: Feature[];
  /** Optional lead-in paragraph above the code samples. */
  snippetIntro?: string;
  /** Tabbed code samples (cURL / Python / JavaScript / MCP config). */
  snippets?: Snippet[];
  /** Decorative illustration shown beside the architecture section. */
  diagram?: string;
  /** End-to-end request flow ("Under the hood"). */
  flow?: Flow;
  /** Real-world use cases. */
  useCases?: UseCase[];
  /** Frequently asked questions. */
  faq?: Faq[];
  build?: BuildStep[];
  learned?: string;
};

const T = (name: string, logo: string): Tech => ({ name, logo });

const shots = (id: string, kind: 'screenshot', captions: [string, string]): Screenshot[] =>
  captions.map((caption, i) => ({ src: `/projects/${id}/${kind}-${i + 1}.jpg`, caption }));

const rawProjects: Project[] = [
  {
    id: 'imper-enterprise',
    title: 'Imper Enterprise',
    category: 'Agentic review platform',
    icon: Files,
    summary:
      'The internal agentic platform behind a journal review desk: agents gather candidate references, vet each one, check claims against the sources and prepare a verified package for an editor. LangGraph workflows, checkpointed runs, cost and latency tuning.',
    tags: ['Agents', 'LangGraph', 'Verification', 'Citations'],
    screenshots: shots('imper-enterprise', 'screenshot', ['Reference bank with title, abstract and full-text search', 'A staged review pipeline: gather, score, screen and verify']),
    sections: [
      {
        heading: 'Overview',
        body: 'Imper Enterprise is the internal tool a journal review desk runs on. A staged pipeline turns a paper title and description into a vetted reference bank: one pass gathers candidates across a local journal index, Crossref, DOAJ, Semantic Scholar and Unpaywall, a scoring pass ranks them, and a screening pass decides which ones actually fit. Claims are then checked back against the source before anything reaches an editor.',
      },
      {
        heading: 'Highlights',
        points: [
          'LangGraph workflows where agents plan, call tools and pass results from one stage to the next.',
          'Reference gathering that fills an exact quota from a title and description, with per-theme shares and year windows.',
          'Reference vetting: every candidate is scored, screened and kept only when its source PDF can actually be fetched.',
          'Claim checking against the source, matching quotes to the cited paper and page and correcting or dropping mismatches.',
          'Checkpointed runs that resume from the last completed stage instead of repeating the expensive search.',
          'Cost and latency tuning: mechanical steps skip the model, scoring batches run in parallel, and every step records its model, tokens, cost and duration.',
        ],
      },
    ],
    architecture: {
      summary: 'A Next.js front end over a LangGraph workflow engine, an OpenCode agent runtime and a Python tool layer.',
      layers: [
        { label: 'Web app', detail: 'Chat, reference bank, journal search and workflow runs.' },
        { label: 'Workflow engine', detail: 'LangGraph graphs that order the stages and checkpoint each one in the database.' },
        { label: 'Agent runtime', detail: 'Agents and subagents that plan, search and call tools through an OpenCode server.' },
        { label: 'Tool layer', detail: 'Academic search, reference collect, bank search and document tools.' },
        { label: 'Reference index', detail: 'Journals and papers harvested and searchable by title, abstract and full text.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('React', 'react'), T('Tailwind CSS', 'tailwindcss'), T('Python', 'python'), T('LangChain', 'langchain'), T('Neon', 'neon')],
  },
  {
    id: 'paper',
    title: 'Paper',
    category: 'React UI library · MCP',
    date: '2026',
    url: { label: 'paper.mshami2021.workers.dev', href: 'https://paper.mshami2021.workers.dev' },
    repo: { label: 'GitHub', href: 'https://github.com/MohammedAlshami/paper' },
    icon: Layers,
    summary:
      'Copy-paste React components for maps, fleets and app screens: 30 map components, 30 for running and maintaining a fleet, 49 app building blocks and four full templates. Built on shadcn/ui and MapLibre, with a public MCP server so AI agents can search the components, read their source and plan a copy.',
    tags: ['React', 'TypeScript', 'shadcn/ui', 'Maps', 'Logistics', 'MCP'],
    screenshots: [
      { src: '/projects/paper/screenshot-1.jpg', caption: 'Landing page hero' },
      { src: '/projects/paper/screenshot-2.jpg', caption: '/components gallery: 109 components in three filterable families' },
      { src: '/projects/paper/screenshot-3.jpg', caption: 'DeliveryTrackerCard component page: the live MapLibre demo, cart/driver state row and the start of the full so' },
      { src: '/projects/paper/screenshot-4.jpg', caption: 'Courier template running live at /t/courier: dispatcher console with today\'s jobs, drivers and the fleet on on' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'Paper is a component library for logistics and operations software, shipped as files you copy into your own app. Tracking a delivery, locating a store, dispatching a driver, scheduling maintenance, reading a fleet on a map: each screen is a component with its full source in the docs, not a dependency to keep in sync. The whole library is also served to agents, so an assistant can find the component, read it and plan the same copy a developer would.',
      },
      {
        heading: 'The problem',
        body: 'Most map libraries stop at drawing a map, so every team rebuilds the product screens on top of it: the delivery tracker, the dispatch board, the work-order board. Paper ships those finished, product-facing screens instead, and proves them by building whole templates from nothing else. Because the check script fails the build when a template reaches outside the library, the templates act as an end-to-end test that keeps the components honest.',
      },
      {
        heading: 'Highlights',
        points: [
          'Three families: 30 components where a map is the visual, 30 for running and maintaining a fleet, and 49 app building blocks (shell, auth, data table, billing, marketing, lists and forms).',
          'Four full templates built only from those components: Courier (last-mile delivery), Garage (fleet maintenance), Ledger (SaaS starter) and Harbor (a 29-page retail back-office).',
          'Built on shadcn/ui and MapLibre GL with OpenFreeMap tiles, so the maps are open source and need no API key.',
          'A public, stateless MCP server at /mcp lets Claude, Cursor and other agents search the components, read their source and plan a copy.',
          'A check script fails the build if a template imports anything but library components or uses a raw button, input or table, so the four templates act as an end-to-end test of the library.',
        ],
      },
    ],
    stats: [
      { value: '109', label: 'Components' },
      { value: '3', label: 'Families' },
      { value: '4', label: 'Templates' },
      { value: 'MCP', label: 'Server built in' },
    ],
    features: [
      {
        icon: '/icons/diagram.svg',
        title: 'Track a delivery',
        body: 'DeliveryTrackerCard, OrderRouteMini, DriverArrivingSheet, ShipmentJourney and ProofOfDelivery show where an order is, who has it and when it arrives.',
      },
      {
        icon: '/icons/reference.svg',
        title: 'Find and pick places',
        body: 'StoreLocator, AddressPicker, ServiceAreaChecker and PickupPointSelector keep a map and a list in agreement while a customer chooses where to collect or deliver.',
      },
      {
        icon: '/icons/gauge.svg',
        title: 'Run the fleet',
        body: 'FleetOverview, VehicleDetailPanel, DispatchBoard, RouteOptimizerResult and GeofenceAlertFeed turn vehicles on a map into decisions a dispatcher can make.',
      },
      {
        icon: '/icons/check.svg',
        title: 'Maintain vehicles',
        body: 'VehicleHealthCard, WorkOrderBoard, MaintenanceCalendar, PartsInventoryTable and ServiceDueList cover health, scheduling, repairs, parts and cost.',
      },
      {
        icon: '/icons/medal.svg',
        title: 'Read data on a map',
        body: 'RegionChoropleth, OriginDestinationFlow, HeatmapCard, CoverageMap and TripReplay show where activity is dense and how far a network reaches.',
      },
      {
        icon: '/icons/clock.svg',
        title: 'Start from a whole screen',
        body: 'Courier, Garage, Ledger and Harbor are full sub-projects, each running live and built only from the library.',
      },
    ],
    snippetIntro:
      'No package to install. Add the map engine, copy the shared map kit and the component you need, and pass it your data. Positions are [longitude, latitude], as in GeoJSON. An agent does the same job over MCP: it searches the components, reads a file and returns the install plan.',
    snippets: [
      {
        label: 'Install',
        code: `# the map engine and helpers\npnpm add maplibre-gl lucide-react clsx tailwind-merge\n\n# the shadcn/ui primitives a component uses\npnpm dlx shadcn@latest add card button badge input`,
      },
      {
        label: 'Copy',
        code: `# one shared map kit, then the component you need\ncp src/components/maps/map-kit.tsx ./src/components/maps/\ncp src/components/maps/store-locator.tsx ./src/components/maps/`,
      },
      {
        label: 'Use',
        code: `import { DeliveryTrackerCard } from '@/components/maps/delivery-tracker-card';\n\n<DeliveryTrackerCard\n  orderId="#48213"\n  origin={{ label: 'Bi-Rite Market', position: [-122.4241, 37.7615] }}\n  destination={{ label: '412 Hayes St', position: [-122.434, 37.7758] }}\n  route={route}\n  etaMinutes={6}\n/>`,
      },
      {
        label: 'MCP',
        code: `# remote MCP server: stateless, read-only, no keys\nhttps://paper.mshami2021.workers.dev/mcp\n\n# tools: get_guidelines, list_components, search_components,\n# get_component, get_install_plan, list_templates, get_template, get_source`,
      },
    ],
    diagram: '/illustrations/sections/architecture.svg',
    architecture: {
      summary:
        'A docs site and MCP server on Cloudflare, over three component families that share small kit files and compose shadcn/ui primitives, with MapLibre as the map engine.',
      layers: [
        { label: 'Templates', detail: 'Courier, Garage, Ledger and Harbor: whole sub-projects built only from library components.' },
        { label: 'Components', detail: '30 map, 30 fleet and 49 app components, each a single file with usage, examples and an API reference.' },
        { label: 'Shared kits', detail: 'map-kit for the MapLibre hook, canvas and markers; fleet-kit for formatting; app-kit for the app blocks.' },
        { label: 'Primitives', detail: 'shadcn/ui and MapLibre GL with OpenFreeMap tiles, so everything follows the host theme and needs no map key.' },
        { label: 'Docs and MCP', detail: 'A page per component, deployed as a Cloudflare Worker that also serves a read-only MCP server at /mcp.' },
      ],
    },
    build: [
      { title: 'Pivot to logistics', body: 'The first version was a set of components for AI workflow runs. A new direction replaced all thirty with map and logistics components.' },
      { title: 'Build the map layer', body: 'Thirty components where a map is the visual, on one shared map kit over MapLibre GL.' },
      { title: 'Add the fleet family', body: 'Thirty more for vehicle health, maintenance scheduling, work orders, parts, tyres, fuel and fleet costs.' },
      { title: 'Prove it with templates', body: 'Courier, Garage and Ledger, then Harbor, a 29-page retail back-office, each built from library components only and checked by a script.' },
      { title: 'Open it to assistants', body: 'A public MCP server and an llms.txt file so Claude, Cursor and other agents can find a component, read its source and plan the copy.' },
    ],
    learned:
      'A template is the best test of a component library, and the check script turns that into a build-time eval: when a template reaches for anything outside the library, the build fails, so every missing piece (filters, date pickers, kanban boards, file upload) had to become a proper component first.',
    flow: {
      image: '/illustrations/paper-flow.svg',
      steps: [
        { title: 'Pick', body: 'Choose the screen you need, a delivery tracker, a dispatch board or a whole template, from the docs or by asking an agent through MCP.' },
        { title: 'Copy', body: 'Add the shadcn primitives it uses, copy the file and the shared kit, and own it from then on.' },
        { title: 'Wire your data', body: 'Pass it your orders, vehicles and routes. Routes come from your own routing API; the components draw them and never fetch them.' },
        { title: 'Theme', body: 'Everything runs on standard shadcn/ui tokens, so it inherits the theme you already have.' },
      ],
    },
    useCases: [
      { title: 'Last-mile delivery', body: 'Public order tracking and checkout, plus a dispatcher console with routes and analytics.' },
      { title: 'Fleet maintenance', body: 'A dashboard, vehicle records, a work-order board, scheduling, inventory and reports.' },
      { title: 'Retail back-office', body: 'Orders, pick and pack, delivery dispatch, stock, purchasing, stores and customers on one shared data set.' },
      { title: 'SaaS starter', body: 'Landing page, auth flow, dashboard, customers, billing, team and settings.' },
    ],
    faq: [
      { q: 'Is it a package?', a: 'No. It is copy-paste, the shadcn model: there is no version to chase. You copy the file and own it.' },
      { q: 'Why MapLibre?', a: 'It is open source, and with OpenFreeMap tiles the maps need no API key.' },
      { q: 'Where do routes come from?', a: 'From your own routing API (OSRM, Mapbox, Google). The components draw routes and never fetch them.' },
      { q: 'Can AI assistants use it?', a: 'Yes. The site is a public, read-only MCP server at /mcp, so Claude, Cursor and other agents can search components, read source and plan an install.' },
    ],
    stack: [
      T('React', 'react'),
      T('TypeScript', 'typescript'),
      T('Tailwind CSS', 'tailwindcss'),
      T('shadcn/ui', 'shadcnui'),
      T('Radix UI', 'radixui'),
      T('Vite', 'vite'),
      T('MCP', 'modelcontextprotocol'),
      T('Cloudflare', 'cloudflare'),
    ],
  },
  {
    id: 'openabstracts',
    title: 'OpenAbstracts',
    category: 'API & MCP server',
    icon: FileSearch,
    url: { label: 'openabstracts.com', href: 'https://openabstracts.com' },
    summary:
      'A paper search API and MCP server for academic literature, built as a retrieval tool for AI agents. Keyword and full-text search across journals, with a Claude Skill that verifies a citation against the real paper before an agent uses it.',
    tags: ['API', 'MCP', 'Search', 'Claude Skill'],
    screenshots: [
      { src: '/projects/openabstracts/live-1.jpg', caption: 'Landing page — one search API over 10M+ papers' },
      { src: '/projects/openabstracts/live-3.jpg', caption: 'Capabilities — keyword, full-text, metadata and sources' },
      { src: '/projects/openabstracts/live-5.jpg', caption: 'Remote MCP server — connect Claude or Cursor in one click' },
      { src: '/projects/openabstracts/live-4.jpg', caption: 'Indexed sources across 100,000+ journals' },
      { src: '/projects/openabstracts/live-6.jpg', caption: 'Free tier and usage-based pricing' },
      { src: '/projects/openabstracts/screenshot-2.jpg', caption: 'API documentation — quickstart and authentication' },
      { src: '/projects/openabstracts/live-2.jpg', caption: 'Built on a real index — 10M+ papers, two search modes' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'OpenAbstracts gives developers and AI agents one endpoint for finding academic papers. Each result includes title, authors, year, journal, DOI, abstract, journal quartile and links to the PDF and publisher page, so an agent can quote a real paper instead of inventing one.',
      },
      {
        heading: 'The problem',
        body: 'Academic search is split across thousands of publisher sites, and language models tend to invent references that look real. OpenAbstracts puts one index and one endpoint in front of the literature, so a citation can be checked instead of guessed, and the companion Claude Skill can verify it against the real paper before it is used.',
      },
    ],
    stats: [
      { value: '10M+', label: 'Indexed papers' },
      { value: '100,000+', label: 'Journals' },
      { value: '2', label: 'Search modes' },
      { value: '$0.0015', label: 'Per search' },
    ],
    features: [
      { icon: '/icons/reference.svg', title: 'Fast keyword search', body: 'Fuzzy matching across titles, abstracts, keywords and authors, with filters for category, year range and journal quartile.' },
      { icon: '/icons/file-text.svg', title: 'Full-text PDF search', body: 'Search inside the paper itself, not just the metadata, with highlighted matches showing exactly where a term appears.' },
      { icon: '/icons/metadata.svg', title: 'Abstracts & metadata', body: 'Authors, year, journal, quartile and abstract come back with every result — everything you need without a second request.' },
      { icon: '/icons/link.svg', title: 'Original PDFs & sources', body: 'Each result links to the original PDF and publisher page when available, so your app shows the real source, not a snippet.' },
      { icon: '/icons/api.svg', title: 'Simple REST API', body: 'One GET endpoint, an API key in a header and JSON back. No SDK required, works from any language.' },
      { icon: '/icons/connect.svg', title: 'Works inside Claude & Cursor', body: 'Connect the remote MCP server in one click and let an assistant search and cite real papers directly in the conversation.' },
    ],
    snippetIntro:
      'Search from any language with an API key, or connect the MCP server and let an agent call the same search as a tool. The MCP config below is what an assistant needs to start grounding its citations.',
    snippets: [
      {
        label: 'cURL',
        code: `curl "https://openabstracts.com/api/references-search?q=marketing&mode=papers&limit=5" \\\n  -H "x-api-key: isk_live_YOUR_KEY"`,
      },
      {
        label: 'Python',
        code: `import requests\n\nres = requests.get(\n    "https://openabstracts.com/api/references-search",\n    params={"q": "marketing", "mode": "papers", "limit": 5},\n    headers={"x-api-key": "isk_live_YOUR_KEY"},\n)\nprint(res.json())`,
      },
      {
        label: 'JavaScript',
        code: `const res = await fetch(\n  "https://openabstracts.com/api/references-search?q=marketing&mode=papers&limit=5",\n  { headers: { "x-api-key": "isk_live_YOUR_KEY" } },\n);\nconsole.log(await res.json());`,
      },
      {
        label: 'MCP',
        code: `{\n  "mcpServers": {\n    "openabstracts": {\n      "url": "https://openabstracts.com/mcp",\n      "headers": { "x-api-key": "isk_live_YOUR_KEY" }\n    }\n  }\n}`,
      },
    ],
    diagram: '/illustrations/sections/architecture.svg',
    architecture: {
      summary: 'A harvesting and indexing pipeline feeds a search service that is exposed as both an API and an MCP server.',
      layers: [
        { label: 'Harvesting', detail: 'Scrapers collect journal metadata and PDF links across 100,000+ journals.' },
        { label: 'Extraction', detail: 'PDF text is extracted and language-checked before indexing.' },
        { label: 'Index', detail: 'OpenSearch holds titles, abstracts and full text for fast search at scale.' },
        { label: 'API', detail: 'A key-authenticated REST endpoint with metering, a free allowance and usage billing.' },
        { label: 'MCP server', detail: 'The same search exposed to Claude, Cursor and other assistants as a tool.' },
      ],
    },
    build: [
      { title: 'Harvest', body: 'Scrapers collect journal metadata and PDF links across 100,000+ journals and keep the index fresh.' },
      { title: 'Extract', body: 'PDFs are downloaded, text is extracted and language-checked before anything is indexed.' },
      { title: 'Index', body: 'Titles, abstracts and full text go into OpenSearch so both metadata and content can be searched at scale.' },
      { title: 'Meter', body: 'Every request is authenticated with a key, counted against a free monthly allowance and billed per search above it.' },
      { title: 'Expose', body: 'The same search is served as a REST endpoint, a remote MCP server and a Claude Skill that verifies citations.' },
    ],
    learned:
      'Making a dataset searchable is the easy part. Keeping 10M+ records fresh across thousands of publishers, and designing an API an LLM agent can call correctly — not just a developer — were the real problems.',
    flow: {
      image: '/illustrations/openabstracts-flow.svg',
      steps: [
        { title: 'Ask', body: 'A query arrives from your app over REST, or from an assistant through the MCP server.' },
        { title: 'Search', body: 'OpenSearch matches titles, abstracts and full PDF text, then ranks the results.' },
        { title: 'Answer', body: 'Results come back with metadata, DOI, quartile and links — everything needed to cite.' },
      ],
    },
    useCases: [
      { title: 'Literature reviews', body: 'Pull a reading list for a topic, then follow each result straight to its PDF and publisher page.' },
      { title: 'Systematic reviews', body: 'Filter by category, year and journal quartile to build a reproducible, citable search set.' },
      { title: 'Grounding AI assistants', body: 'Give an assistant a citation tool so it quotes real papers instead of inventing references.' },
      { title: 'Journal & author discovery', body: 'Browse 100,000+ journals to find where a field publishes and who is working in it.' },
    ],
    faq: [
      { q: 'Do I need an SDK?', a: 'No. One GET endpoint, an API key in a header and JSON back — it works from any language.' },
      { q: 'What does it cost?', a: 'There is a free monthly allowance, then usage-based billing at $0.0015 per search.' },
      { q: 'How does the MCP server work?', a: 'Add the remote MCP server URL to Claude or Cursor and the assistant calls the same search as a tool.' },
      { q: 'Where do the papers come from?', a: 'Metadata and PDFs are harvested across 100,000+ journals and indexed in OpenSearch.' },
    ],
    repo: { label: 'GitHub', href: 'https://github.com/MohammedAlshami/openabstracts' },
    stack: [T('Node.js', 'nodedotjs'), T('MongoDB', 'mongodb'), T('OpenSearch', 'opensearch'), T('MCP', 'modelcontextprotocol'), T('Anthropic', 'anthropic')],
  },
  {
    id: 'ermap',
    title: 'ERMAP: Agentic Map Assistant',
    category: 'Agentic workflows',
    repo: { label: 'GitHub', href: 'https://github.com/MohammedAlshami/ermap' },
    icon: Map,
    summary:
      'An interactive Mapbox app with an AI agent that can search places, restyle the map, find and plot raster data, manage slides and run detection inside an area you draw.',
    tags: ['Agents', 'LangGraph', 'Maps', 'Computer vision'],
    screenshots: [],
    sections: [
      {
        heading: 'Overview',
        body: 'ERMAP is a map-based web app for building spatial presentations. Instead of clicking through menus, you can ask the assistant to do it: it chooses from a set of typed map tools, runs them and streams its answer back while the map updates.',
      },
      {
        heading: 'Highlights',
        points: [
          'A LangGraph ReAct agent with about a dozen typed tools (place search, map style, zoom, dataset search, raster plotting, layer and slide control, detection in a drawn area) and streaming chat.',
          'Building and tree detection from ONNX/YOLO masks, converted into GeoJSON polygons on the map.',
          'Dataset search with one-click raster plotting.',
          'Slide-based map presentations with editable descriptions.',
        ],
      },
    ],
    architecture: {
      summary: 'A React map front end over a NestJS API that hosts a tool-calling agent.',
      layers: [
        { label: 'Map app', detail: 'A Vite and React front end on Mapbox GL with slides and a chat panel.' },
        { label: 'API', detail: 'A NestJS backend that runs the agent and streams its responses.' },
        { label: 'Agent', detail: 'LangChain and LangGraph with OpenAI, calling typed map tools.' },
        { label: 'Detection', detail: 'ONNX/YOLO models whose masks become GeoJSON polygons.' },
      ],
    },
    stack: [T('NestJS', 'nestjs'), T('TypeScript', 'typescript'), T('LangChain', 'langchain'), T('OpenAI', 'openai'), T('React', 'react'), T('Mapbox', 'mapbox'), T('Supabase', 'supabase')],
  },
  {
    id: 'slidesmaker',
    title: 'Presly: AI Presentation Generator',
    category: 'Agentic workflows',
    repo: { label: 'GitHub', href: 'https://github.com/MohammedAlshami/SlidesMaker' },
    icon: Presentation,
    summary:
      'A multi-agent app where a chat leads into parallel research, slide planning and generation of Reveal.js and PowerPoint decks that can be shared by link.',
    tags: ['Agents', 'LangChain', 'Presentations', 'Full-stack'],
    screenshots: [],
    sections: [
      {
        heading: 'Overview',
        body: 'Presly turns a conversation into a finished deck. A chatbot agent understands the request, a research agent gathers material with parallel queries, a structure agent plans the slides around a template, and a generator produces the presentation as Reveal.js HTML and a PPTX download.',
      },
      {
        heading: 'Highlights',
        points: [
          'Four agents with clear jobs: chatbot, research, structure and generation.',
          'Research runs several queries in parallel before planning begins.',
          'Decks are produced as Reveal.js HTML and as PPTX files.',
          'Presentations are saved and shared by URL, with accounts and conversation memory.',
        ],
      },
    ],
    architecture: {
      summary: 'A Next.js app that passes a request through four cooperating agents.',
      layers: [
        { label: 'Web app', detail: 'A Next.js interface with chat, preview and sharing.' },
        { label: 'Agents', detail: 'LangChain agents with OpenAI for research, planning and generation.' },
        { label: 'Export', detail: 'Reveal.js HTML and PPTX files built with PptxGenJS.' },
        { label: 'Storage', detail: 'MongoDB for presentations and Supabase for sign-in.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('LangChain', 'langchain'), T('OpenAI', 'openai'), T('MongoDB', 'mongodb'), T('Supabase', 'supabase'), T('Flask', 'flask')],
  },
  {
    id: 'academic-agents',
    title: 'Academic Writing Agents',
    category: 'Agentic workflows',
    repo: { label: 'GitHub', href: 'https://github.com/MohammedAlshami/Agents' },
    icon: Bot,
    summary:
      'A set of separate agent services for academic documents: humanizing text, paraphrasing with references, extracting references from Word files and generating documents.',
    tags: ['Agents', 'LangChain', 'Python', 'Documents'],
    screenshots: [],
    sections: [
      {
        heading: 'Overview',
        body: 'A collection of standalone Python services, each one an LLM agent for a single job in academic writing. Every agent exposes its own HTTP routes, so they can be combined into larger workflows.',
      },
      {
        heading: 'Highlights',
        points: [
          'Separate agents for conversation, document generation, DOCX processing, humanizing, paraphrasing with references, reference extraction and writing help.',
          'Reference lookups through OpenAlex and Perplexity.',
          'One route per agent, so services can be composed.',
          'Docker packaging for deployment.',
        ],
      },
    ],
    architecture: {
      summary: 'Independent agent services behind HTTP routes that can be chained together.',
      layers: [
        { label: 'Agents', detail: 'One service per task, built with LangChain and OpenAI.' },
        { label: 'References', detail: 'OpenAlex and Perplexity searches for sources.' },
        { label: 'Documents', detail: 'Word and PDF parsing with python-docx and PyMuPDF.' },
        { label: 'API', detail: 'Flask routes that expose each agent.' },
      ],
    },
    stack: [T('Python', 'python'), T('Flask', 'flask'), T('LangChain', 'langchain'), T('OpenAI', 'openai'), T('MongoDB', 'mongodb'), T('Docker', 'docker')],
  },
  {
    id: 'feasibility-study',
    title: 'Feasibility Study Builder',
    category: 'Business planning',
    icon: Calculator,
    url: { label: 'Live demo', href: 'https://feasibility-study.mshami2021.workers.dev' },
    summary:
      'A guided tool that turns a set of project inputs into a full feasibility study: market, technical, legal and financial sections with a formatted report.',
    tags: ['Full-stack', 'Reports', 'Finance'],
    screenshots: shots('feasibility-study', 'screenshot', ['Generated executive summary', 'The four study sections']),
    sections: [
      {
        heading: 'Overview',
        body: 'Users enter the basics of a business idea once. The figures are computed from those inputs rather than generated by a model: break-even, revenues, costs and cash flows come out of a deterministic calculation, the written sections are assembled around them, and every version is kept so a plan can be revised without starting again.',
      },
      {
        heading: 'Highlights',
        points: [
          'Four study sections: market, technical, legal and administrative, and financial.',
          'A report view with executive summary, revenues and costs, break-even, cash flows and charts.',
          'Versioned studies with export to a formatted document.',
          'Multi-language support.',
        ],
      },
    ],
    architecture: {
      summary: 'A Next.js app on Cloudflare with a small relational database for studies and versions.',
      layers: [
        { label: 'Inputs', detail: 'Guided forms for the project’s products, people, systems and sales.' },
        { label: 'Calculation', detail: 'Financial figures such as break-even and cash flow computed from the inputs.' },
        { label: 'Storage', detail: 'Studies and versions saved in a database through Drizzle.' },
        { label: 'Report', detail: 'Written sections and charts assembled into one report.' },
        { label: 'Export', detail: 'Download as a formatted document.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('Tailwind CSS', 'tailwindcss'), T('Drizzle', 'drizzle'), T('SQLite', 'sqlite'), T('Cloudflare', 'cloudflare')],
  },
  {
    id: 'news-platform',
    title: 'Agentic News',
    category: 'Agentic pipeline',
    icon: Newspaper,
    url: { label: 'Live site', href: 'https://news-site.mshami2021.workers.dev/' },
    repo: { label: 'GitHub', href: 'https://github.com/MohammedAlshami/news-app' },
    summary:
      'An Arabic news site that runs itself: it collects articles from outlets every hour, groups them into events, and writes a sourced Arabic article for each one every 10 minutes.',
    tags: ['Agents', 'LLM clustering', 'Arabic', 'Cloudflare'],
    screenshots: [
      { src: '/projects/news-platform/screenshot-1.jpg', caption: 'Public home page (Arabic, right-to-left): hero lead stories plus the per-category carousels.' },
      { src: '/projects/news-platform/screenshot-2.jpg', caption: 'Article page for one pipeline-written story: the «أبرز النقاط» key-points panel and the Arabic body the writer' },
      { src: '/projects/news-platform/screenshot-3.jpg', caption: 'Admin dashboard' },
      { src: '/projects/news-platform/screenshot-4.jpg', caption: 'Admin «المواضيع»' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'A scheduled worker drives the whole pipeline every 10 minutes: scrape the outlets, group articles about the same event, then write one article per event. Readers get a right-to-left, server-rendered news site, and an admin panel controls categories, daily quotas and sources.',
      },
      {
        heading: 'Highlights',
        points: [
          'Grouping articles into events was the hard part. I labelled 162 articles by hand and tested 11 methods. The one I shipped (LLM-extracted signatures, blocking, then an LLM judge) scored F1 0.90, against 0.53 for the original logic.',
          'The writer only uses facts from the sources, attributes each outlet and links them at the end of the article.',
          'Guards against bad output: stories older than 48 hours are never published, near-duplicates are skipped before any model call, and a claim step stops two writers taking the same story.',
          'A health check raises an alert when the pipeline stalls, and a failed story goes back in the queue instead of getting stuck.',
          'Right-to-left layout and Arabic typography throughout.',
        ],
      },
    ],
    architecture: {
      summary: 'A Next.js app on Cloudflare, with a scheduler worker that runs the pipeline against the same database.',
      layers: [
        { label: 'Public site', detail: 'Server-rendered pages for the home page, categories and articles.' },
        { label: 'Scheduler', detail: 'A Cloudflare worker that runs scrape, cluster, write and health check every 10 minutes.' },
        { label: 'Clustering', detail: 'LLM signatures, blocking and an LLM judge turn raw articles into events.' },
        { label: 'Writer', detail: 'An LLM writes a sourced Arabic article per event, with quota, freshness and duplicate checks.' },
        { label: 'Database', detail: 'Articles, topics and sources stored in D1 with Drizzle; images in R2.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('Drizzle', 'drizzle'), T('Cloudflare', 'cloudflare'), T('Tailwind CSS', 'tailwindcss')],
  },
  {
    id: 'arabic-arena',
    title: 'Arabic Arena',
    category: 'Learning platform',
    icon: GraduationCap,
    url: { label: 'arabicarena.com', href: 'https://www.arabicarena.com/en' },
    summary:
      'A learning management system for teaching Arabic online: courses, a blog, a placement test, and an admin dashboard for running the school.',
    tags: ['LMS', 'Full-stack', 'Education'],
    screenshots: [
      { src: '/projects/arabic-arena/screenshot-1.jpg', caption: 'Arabic' },
      { src: '/projects/arabic-arena/screenshot-2.jpg', caption: 'Course catalogue: the three tracks, Children\'s, Adult and Special' },
      { src: '/projects/arabic-arena/screenshot-3.jpg', caption: 'Placement test: the public "Placement Test Registration" form' },
      { src: '/projects/arabic-arena/screenshot-4.jpg', caption: 'Listening exercises: Quran verses split into tappable words with meanings and audio ("Play Entire Verse").' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'Arabic Arena is an online Arabic school I work on part-time as a software engineer. It covers both sides of the school: the public site where learners find courses, and the admin app where staff manage students, content and payments.',
      },
      {
        heading: 'Highlights',
        points: [
          'Public marketing site in English and Arabic with an SEO-focused blog.',
          'A placement test to route learners to the right level.',
          'An admin dashboard with a calendar, student records, transactions and a rich-text content editor.',
          'Agent-based helpers for content and student support inside the admin tools.',
        ],
      },
    ],
    architecture: {
      summary: 'Two Next.js apps, a marketing site and an admin app, sharing one database.',
      layers: [
        { label: 'Marketing site', detail: 'Localised pages, blog and placement test.' },
        { label: 'Admin app', detail: 'Students, calendar, transactions and content management.' },
        { label: 'Database', detail: 'MongoDB for users, courses and records.' },
        { label: 'Storage', detail: 'Object storage for media and documents.' },
        { label: 'AI', detail: 'Agent-based helpers inside the admin tools.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('MongoDB', 'mongodb'), T('OpenAI', 'openai'), T('Amazon S3', 'amazons3'), T('Tailwind CSS', 'tailwindcss')],
  },
  {
    id: 'ijo-bs',
    title: 'IJO-BS Journal',
    category: 'AI engineering · Publishing',
    icon: BookOpen,
    url: { label: 'ijo-bs.com', href: 'https://ijo-bs.com' },
    summary:
      'The International Journal of Business and Society platform, and Imper, the internal agentic pipeline I build there: agents gather references, vet each one, check claims against the sources and prepare a verified package for editors.',
    tags: ['Agents', 'LangGraph', 'Verification', 'Publishing'],
    screenshots: [
      { src: '/projects/ijo-bs/screenshot-1.jpg', caption: 'Home page: hero ("Uniting Research for Global Impact") with the site-wide article/author/keyword search box.' },
      { src: '/projects/ijo-bs/screenshot-2.jpg', caption: 'Archive page' },
      { src: '/projects/ijo-bs/screenshot-3.jpg', caption: 'Article page' },
      { src: '/projects/ijo-bs/screenshot-4.jpg', caption: 'Search results page' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'IJO-BS publishes the International Journal of Business and Society. I work on it full-time as an AI engineer, building Imper, the internal agentic platform the journal uses to review submissions: a staged pipeline that turns a paper title and description into a vetted reference bank, checks that every claim has a source that can be opened, and leaves the editorial decision with a person. The public journal platform sits alongside it, carrying a paper from submission to a published, citable article.',
      },
      {
        heading: 'Highlights',
        points: [
          'Reference gathering: agents plan search angles, query a local index of harvested journals plus Crossref, DOAJ, Semantic Scholar and Unpaywall, and fill an exact reference count.',
          'Reference vetting: candidates are scored, screened by an agent and kept only when their source PDF can actually be fetched.',
          'Claim checking: quotes are matched to the cited paper and page, and mismatches are corrected or dropped before an editor sees them.',
          'LangGraph workflows with checkpointed stages, so an interrupted run resumes instead of repeating the expensive search.',
          'Every step records its model, tokens, cost and duration, which is what the cost and latency tuning runs on.',
          'The journal platform itself: author submission, peer review screens, issues and archive with search, and automated DOI registration with Crossref.',
        ],
      },
    ],
    architecture: {
      summary: 'A public Next.js front end talking to a Python API, with the internal Imper agentic platform running as a separate LangGraph service alongside it.',
      layers: [
        { label: 'Public site', detail: 'Home, issues, article pages and search.' },
        { label: 'Author area', detail: 'Submission and review screens.' },
        { label: 'API', detail: 'A Flask backend for papers, users and status changes.' },
        { label: 'Agentic review platform', detail: 'Imper: LangGraph workflows that gather, vet and verify references for editorial review.' },
        { label: 'DOI service', detail: 'Scripts that deposit metadata to Crossref.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('Python', 'python'), T('Flask', 'flask'), T('MongoDB', 'mongodb')],
  },
  {
    id: 'workshop-management',
    title: 'Workshop Management System',
    category: 'Operations',
    icon: Wrench,
    url: { label: 'pos.imper.app', href: 'https://pos.imper.app/' },
    summary:
      'Software for running a repair workshop: jobs, quotations, suppliers, customer tracking and support tickets.',
    tags: ['Full-stack', 'POS', 'Operations'],
    screenshots: [
      { src: '/projects/workshop-management/screenshot-1.jpg', caption: 'Super-admin dashboard: 204 users, 69 workshops, 4 tickets, 7 active sessions, users-by-role breakdown' },
      { src: '/projects/workshop-management/screenshot-2.jpg', caption: 'Job cards board with real jobs: status filter tabs' },
      { src: '/projects/workshop-management/screenshot-3.jpg', caption: 'Job card JOB-599594, Quotation tab: APPROVED quotation with bill-to, job details, line items' },
      { src: '/projects/workshop-management/screenshot-4.jpg', caption: 'Public job tracker at /job-status?vehicleNumber=ERT445' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'A multi-business system where each workshop or store manages its own jobs, and a super-admin looks after the platform. Every job runs as a tracked workflow: a status change is stored, pushed to a live view and reflected on the customer’s tracking page, so the state of a repair is never guesswork.',
      },
      {
        heading: 'Highlights',
        points: [
          'Job status tracking and a public tracking page for customers.',
          'Quotations and PDF documents.',
          'Supplier management.',
          'QR codes for jobs and assets.',
          'A built-in support ticketing system with roles and internal notes.',
        ],
      },
    ],
    architecture: {
      summary: 'A TanStack Start app with a relational database and live updates.',
      layers: [
        { label: 'Web app', detail: 'Job status, quotations, suppliers and tracking.' },
        { label: 'API', detail: 'Role-based routes for staff, clients and super-admins.' },
        { label: 'Database', detail: 'PostgreSQL storing jobs, customers and tickets.' },
        { label: 'Realtime', detail: 'Socket connections for live status changes.' },
        { label: 'Notifications', detail: 'Email updates to customers.' },
      ],
    },
    stack: [T('TanStack', 'tanstack'), T('React', 'react'), T('TypeScript', 'typescript'), T('PostgreSQL', 'postgresql'), T('Socket.IO', 'socketdotio'), T('Cloudflare', 'cloudflare')],
  },
  {
    id: 'waffa-app',
    title: 'Waffa Marketplace App',
    category: 'Mobile app',
    icon: Smartphone,
    summary:
      'An Android marketplace app with an Arabic, right-to-left interface where shoppers browse products and message sellers.',
    tags: ['Mobile', 'E-commerce', 'RTL'],
    screenshots: [
      { src: '/projects/waffa-app/screenshot-1.jpg', caption: 'Home page with banner and category browsing (Arabic, right to left)' },
      { src: '/projects/waffa-app/screenshot-2.jpg', caption: 'Shop with filters and product listings' },
      { src: '/projects/waffa-app/screenshot-3.jpg', caption: 'Product page with price, quantity and seller' },
      { src: '/projects/waffa-app/screenshot-4.jpg', caption: 'Mobile layout with bottom navigation' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'A React Native app for buying and selling. Shoppers collect items in a saved list and contact the seller directly, and sellers get their own store.',
      },
      {
        heading: 'Highlights',
        points: [
          'Categories, search, wishlists and a full order flow.',
          'Buyer-to-seller chat with product cards.',
          'Seller stores with product management.',
          'Arabic fonts and a right-to-left layout.',
        ],
      },
    ],
    architecture: {
      summary: 'One Expo client, one API and object storage for images.',
      layers: [
        { label: 'Mobile app', detail: 'Expo Router app, shipped on Android with a web target.' },
        { label: 'API', detail: 'A Flask service handling orders, chat and accounts.' },
        { label: 'Database', detail: 'MongoDB for products, users and orders.' },
        { label: 'Image storage', detail: 'Cloudflare R2, accessed only from the server.' },
      ],
    },
    stack: [T('Expo', 'expo'), T('React', 'react'), T('TypeScript', 'typescript'), T('Flask', 'flask'), T('MongoDB', 'mongodb'), T('Cloudflare', 'cloudflare')],
  },
  {
    id: 'gold-queen',
    title: 'Gold Queen Store',
    category: 'E-commerce',
    icon: ShoppingBag,
    url: { label: 'goldqueen.store', href: 'https://goldqueen.store/' },
    summary:
      'An Arabic e-commerce store for a personal-care brand, with a storefront, product pages, a blog and an admin area.',
    tags: ['E-commerce', 'RTL', 'Full-stack'],
    screenshots: [
      { src: '/projects/gold-queen/screenshot-1.jpg', caption: 'Storefront home: the Arabic right-to-left header, category menu and hero banner, with the floating WhatsApp bu' },
      { src: '/projects/gold-queen/screenshot-2.jpg', caption: 'Shop page (المتجر): the products banner, category cards and the first row of product cards with prices.' },
      { src: '/projects/gold-queen/screenshot-3.jpg', caption: 'Product detail page' },
      { src: '/projects/gold-queen/screenshot-4.jpg', caption: 'Blog (المدونة): the article list with a published post, its tags and the category navigation.' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'A fast, right-to-left storefront that lets the owner manage products and orders without a developer.',
      },
      {
        heading: 'Highlights',
        points: [
          'Product catalogue with collections and search.',
          'Customer accounts and a WhatsApp contact button.',
          'Blog for content marketing.',
          'Admin panel for products and orders.',
        ],
      },
    ],
    architecture: {
      summary: 'A Next.js store deployed to Cloudflare with an edge database.',
      layers: [
        { label: 'Storefront', detail: 'Server-rendered pages for home, shop, products and blog.' },
        { label: 'Admin', detail: 'Protected screens for products and orders.' },
        { label: 'Database', detail: 'Cloudflare D1 with SQL migrations.' },
        { label: 'Media', detail: 'Product images served from object storage.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('Tailwind CSS', 'tailwindcss'), T('Cloudflare', 'cloudflare')],
  },
  {
    id: 'crm',
    title: 'Events CRM',
    category: 'Business software',
    icon: Users,
    summary:
      'A CRM for an events business: clients, events, speakers, sponsors and files, with reports and scheduled syncing.',
    tags: ['Full-stack', 'CRM', 'Reports'],
    screenshots: [
      { src: '/projects/crm/screenshot-1.jpg', caption: 'Clients module: the client table with company, event, contact details and owner, plus the module navigation' },
      { src: '/projects/crm/screenshot-2.jpg', caption: 'Events list: status tabs, and per event the client/sponsor counts, confirmation counts, dates and venue.' },
      { src: '/projects/crm/screenshot-3.jpg', caption: 'Event record' },
      { src: '/projects/crm/screenshot-4.jpg', caption: 'Tasks board: task cards with status, priority, category, assignee and due date across events.' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'The CRM keeps everything about an event in one place, from the clients attending to the speakers and sponsors involved. Reports and data syncing run as scheduled jobs on a cron, so a status update is produced rather than assembled by hand.',
      },
      {
        heading: 'Highlights',
        points: [
          'Clients linked to events, speakers and sponsors.',
          'File management with permissions by file type.',
          'Daily and weekly reports generated automatically.',
          'Scheduled jobs and backups.',
        ],
      },
    ],
    architecture: {
      summary: 'A Next.js front end on Cloudflare, with Python workers and a D1 database.',
      layers: [
        { label: 'CRM app', detail: 'Events, clients, speakers, sponsors and files.' },
        { label: 'Workers', detail: 'Python API routes that read and write the database.' },
        { label: 'Database', detail: 'Cloudflare D1 with a defined schema per entity.' },
        { label: 'Schedules', detail: 'Cron jobs for nightly reports and syncing.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('Python', 'python'), T('Cloudflare', 'cloudflare')],
  },
  {
    id: 'mail-platform',
    title: 'Intelli Mail Platform',
    category: 'AI email',
    icon: Mail,
    summary:
      'An email platform where language-model agents draft inbox replies and campaigns for a person to review before anything is sent.',
    tags: ['Agents', 'Email', 'Campaigns'],
    screenshots: [
      { src: '/projects/mail-platform/screenshot-1.jpg', caption: 'Dashboard showing 3 scanned websites, 3 leads extracted, and a websites-by-category chart.' },
      { src: '/projects/mail-platform/screenshot-2.jpg', caption: 'Mail inbox with a selected thread, its message body, and a Reply action.' },
      { src: '/projects/mail-platform/screenshot-3.jpg', caption: 'Campaigns list with Q1 Newsletter and Product Launch plus sent/recipient/bounce counts.' },
      { src: '/projects/mail-platform/screenshot-4.jpg', caption: 'Campaign detail for Q1 Newsletter: sent/recipient/bounced totals, response rate, and recipients.' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'A mail client and campaign tool built around agents. It receives and sends real email, stores the conversation, and lets an agent draft a reply or a campaign, with a person approving anything that goes out.',
      },
      {
        heading: 'Highlights',
        points: [
          'Multiple mailboxes with inbound and outbound tracking.',
          'Templates and signatures.',
          'Bounce and auto-reply detection.',
          'Agent-written replies and campaign drafts.',
        ],
      },
    ],
    architecture: {
      summary: 'Mail flows through an email engine, which notifies the app by webhook.',
      layers: [
        { label: 'Email engine', detail: 'Connects mailboxes and sends and receives messages.' },
        { label: 'Webhooks', detail: 'New, sent and bounced messages are pushed to the app.' },
        { label: 'App', detail: 'A Next.js interface for inboxes, templates and campaigns.' },
        { label: 'Agents', detail: 'Language-model agents that draft replies and campaigns for human review.' },
        { label: 'Database', detail: 'Messages and attachments stored for search.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('Docker', 'docker'), T('Redis', 'redis'), T('OpenAI', 'openai'), T('LangChain', 'langchain'), T('Drizzle', 'drizzle')],
  },
  {
    id: 'cashirk',
    title: 'Cashirk Voice Agent',
    category: 'Voice AI',
    icon: Mic,
    summary:
      'A real-time voice agent you create and talk to in the browser: the server provisions an ElevenLabs agent from a name and prompt, issues a short-lived token, and the browser streams the live conversation over WebRTC with a transcript and speaking state.',
    tags: ['Voice AI', 'Real-time', 'WebRTC'],
    screenshots: [
      { src: '/projects/cashirk/screenshot-1.jpg', caption: 'Arabic landing hero for Cashirk, the drive-thru voice ordering product.' },
      { src: '/projects/cashirk/screenshot-2.jpg', caption: '/demo voice screen at idle (6-digit gate cleared), showing the 3D orb ready to start a conversation.' },
      { src: '/projects/cashirk/screenshot-3.jpg', caption: '/menu catalogue of the 40-item demo coffee shop menu.' },
      { src: '/projects/cashirk/screenshot-4.jpg', caption: 'the same idle voice screen on a mobile viewport.' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'Give the app a name and a system prompt and the server provisions a voice agent on the ElevenLabs Agents platform, issues a short-lived token and opens a live session. Press start and talk to it in the browser, with a running transcript and on-screen speaking state.',
      },
      {
        heading: 'Highlights',
        points: [
          'Agents provisioned from the browser with a name and a custom prompt.',
          'Short-lived tokens per conversation, with live audio streamed over WebRTC.',
          'On-screen state showing when the agent is listening or speaking, plus a running transcript.',
          'A live 3D visual for the agent.',
        ],
      },
    ],
    architecture: {
      summary: 'The server creates the agent and issues tokens; the browser talks to it directly.',
      layers: [
        { label: 'Setup', detail: 'The server creates the agent from a name and prompt.' },
        { label: 'Token', detail: 'A short-lived token is issued for each conversation.' },
        { label: 'Session', detail: 'The browser streams audio over WebRTC.' },
        { label: 'Interface', detail: 'Live transcript and speaking state with a 3D visual.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('TypeScript', 'typescript'), T('ElevenLabs', 'elevenlabs'), T('Three.js', 'threedotjs'), T('Cloudflare', 'cloudflare')],
  },
  {
    id: 'arabic-editor',
    title: 'Arabic Document Writer',
    category: 'Writing tools',
    repo: { label: 'GitHub', href: 'https://github.com/MohammedAlshami/arabic_document_writter' },
    icon: FileText,
    summary:
      'An Arabic document editor with AI actions that expand, summarise, rewrite and autocomplete the text you select, streamed straight into the page.',
    tags: ['LLM', 'Arabic', 'Editor', 'Full-stack'],
    screenshots: [],
    sections: [
      {
        heading: 'Overview',
        body: 'A Tiptap-based editor for writing in Arabic, with a document list and saved documents. Select some text and the AI can expand it, summarise it, rewrite it or continue it, with the answer streaming into the editor in Arabic.',
      },
      {
        heading: 'Highlights',
        points: [
          'Four contextual AI actions: expand, summarise, rewrite and autocomplete.',
          'Responses stream into the editor as they are written.',
          'Prompts keep the output in Arabic HTML so the formatting survives.',
          'Documents are saved in PostgreSQL.',
        ],
      },
    ],
    architecture: {
      summary: 'A Next.js editor that streams model output back into the document.',
      layers: [
        { label: 'Editor', detail: 'A Tiptap editor in a Next.js App Router app.' },
        { label: 'AI actions', detail: 'Streaming calls to an OpenAI-compatible model through OpenRouter.' },
        { label: 'Database', detail: 'Prisma over PostgreSQL for documents.' },
      ],
    },
    stack: [T('Next.js', 'nextdotjs'), T('React', 'react'), T('TypeScript', 'typescript'), T('Tailwind CSS', 'tailwindcss'), T('OpenAI', 'openai'), T('Prisma', 'prisma'), T('PostgreSQL', 'postgresql')],
  },
  {
    id: 'duri',
    title: 'Duri: Companion Chatbot',
    category: 'Conversational AI',
    repo: { label: 'GitHub', href: 'https://github.com/MohammedAlshami/Duri' },
    icon: MessageCircle,
    summary:
      'A Django chatbot where a cartoon character replies in structured JSON that changes its face and background, with multilingual chat and voice input.',
    tags: ['LLM', 'Django', 'Voice', 'Structured output'],
    screenshots: [],
    sections: [
      {
        heading: 'Overview',
        body: 'Duri is a playful companion bot. Every reply from the model is structured JSON that includes the text, an emotion and a background scene, so the interface can change the character’s face and setting to match what it says.',
      },
      {
        heading: 'Highlights',
        points: [
          'Structured OpenAI replies drive the character’s emotion and scene.',
          'Small talk in Russian, German, Arabic and Japanese.',
          'Voice capture in the browser.',
          'Optional Firebase storage for chat history.',
        ],
      },
    ],
    architecture: {
      summary: 'A Django app whose model replies in JSON that the interface turns into animation.',
      layers: [
        { label: 'Web app', detail: 'A Django app with the chat interface and character art.' },
        { label: 'Model', detail: 'OpenAI chat completions returning a fixed JSON shape.' },
        { label: 'Storage', detail: 'Optional Firebase chat history per user.' },
      ],
    },
    stack: [T('Python', 'python'), T('Django', 'django'), T('OpenAI', 'openai'), T('Firebase', 'firebase')],
  },
  {
    id: 'hololens',
    title: 'HoloLens 2 and Arduino',
    category: 'Mixed reality',
    icon: Glasses,
    summary:
      'A mixed-reality project that reads live data from an Arduino on a HoloLens 2, using networked Unity apps to relay it.',
    tags: ['Mixed reality', 'Hardware', 'Unity'],
    screenshots: [
      { src: '/projects/hololens/screenshot-1.jpg', caption: 'Unity server project: SampleScene with the Server and Cube objects, and the Photon PUN server settings' },
      { src: '/projects/hololens/screenshot-2.jpg', caption: 'Photon network protocol set to WebSocket (client and server have to match).' },
      { src: '/projects/hololens/screenshot-3.jpg', caption: 'Visual Studio deploying the Universal Windows server app to the HoloLens 2 over "Remote Machine" (ARM64).' },
    ],
    sections: [
      {
        heading: 'Overview',
        body: 'A working example of connecting hardware to a headset. An Arduino sends sensor data over serial, and a HoloLens 2 shows it in the user’s view.',
      },
      {
        heading: 'Highlights',
        points: [
          'A client app that reads the Arduino over serial.',
          'A HoloLens 2 app that receives and displays the data.',
          'Networking through Photon Unity Networking.',
          'A written guide covering setup, emulator testing and device testing.',
        ],
      },
    ],
    architecture: {
      summary: 'Data flows from the sensor, through a Unity client, to the headset.',
      layers: [
        { label: 'Arduino', detail: 'Reads the sensor and writes to serial.' },
        { label: 'Client', detail: 'A Unity app that reads the serial port.' },
        { label: 'Network', detail: 'Photon relays the values between devices.' },
        { label: 'HoloLens 2', detail: 'A Unity app that shows the live data in mixed reality.' },
      ],
    },
    stack: [T('Unity', 'unity'), T('C#', 'csharp'), T('Arduino', 'arduino'), T('C++', 'cplusplus')],
  },
];

/** Live-site screenshots captured from the deployed apps — appended to each gallery. */
const LIVE_SHOT: Record<string, string> = {
  'feasibility-study': '/projects/feasibility-study/live-1.jpg',
  'news-platform': '/projects/news-platform/live-1.jpg',
  'arabic-arena': '/projects/arabic-arena/live-1.jpg',
  'ijo-bs': '/projects/ijo-bs/live-1.jpg',
  'gold-queen': '/projects/gold-queen/live-1.jpg',
};

/** Projects whose scrolled second capture differs from the first. */
const SECOND_LIVE_SHOT = new Set([
  'feasibility-study',
  'news-platform',
  'arabic-arena',
  'ijo-bs',
  'gold-queen',
]);

/**
 * Extra, data-driven content per project page — capability cards ("What it does"),
 * process flow ("Under the hood"), real-world use cases and an FAQ.
 * Kept separate from the core records so pages stay easy to extend.
 */
const ENRICH: Record<string, Partial<Project>> = {
  'imper-enterprise': {
    features: [
      { icon: '/icons/checklist.svg', title: 'Staged gathering', body: 'An agent plans the search angles, a researcher fan-out queries every source, and the shortlist is checkpointed stage by stage.' },
      { icon: '/icons/reference.svg', title: 'Reference vetting', body: 'Every candidate is scored and screened, then kept only when its source PDF can actually be fetched.' },
      { icon: '/icons/check.svg', title: 'Claim checking', body: 'Quotes are matched against the cited paper and page; wording and pages are corrected and unknown sources are dropped.' },
      { icon: '/icons/gauge.svg', title: 'Observability and resume', body: 'Each step records its model, tokens, cost and duration, and a failed run continues from its last checkpoint.' },
    ],
    flow: {
      steps: [
        { title: 'Brief', body: 'A paper title and description set the task, along with the study context and how many references it needs.' },
        { title: 'Gather and vet', body: 'Agents search the journal index and open sources in parallel, score every candidate and keep the ones whose PDF can be fetched.' },
        { title: 'Verify', body: 'Quotes and claims are checked against the cited paper and page, and the vetted list is saved for an editor to review.' },
      ],
    },
    useCases: [
      { title: 'Reference gathering', body: 'Fill an exact reference count for a paper from a title and description.' },
      { title: 'Reference vetting', body: 'Score and screen candidates so only sources that fit the argument, and can be opened, stay in the list.' },
      { title: 'Claim checking', body: 'Match every quote back to the paper and page it came from before an editor reads it.' },
      { title: 'Review pipelines', body: 'A checkpointed workflow a review desk can inspect, resume and cost out run by run.' },
    ],
    faq: [
      { q: 'What does the platform do?', a: 'It gathers, vets and verifies the references behind a paper, then hands a checked list to an editor.' },
      { q: 'Where do the references come from?', a: 'A local index of harvested journals, plus Crossref, DOAJ, Semantic Scholar and Unpaywall.' },
      { q: 'Can a failed run be resumed?', a: 'Yes. Each stage checkpoints its result, so a run continues from the last completed stage.' },
      { q: 'How is cost kept down?', a: 'Mechanical steps skip the model, scoring batches run in parallel, and each step records its model, tokens, cost and duration.' },
    ],
  },

  'feasibility-study': {
    features: [
      { icon: '/icons/checklist.svg', title: 'Guided inputs', body: 'Products, people, systems and sales are entered once as simple guided forms.' },
      { icon: '/icons/chart.svg', title: 'Financial model', body: 'Break-even, revenues and costs, cash flows and charts are computed from those inputs.' },
      { icon: '/icons/pencil.svg', title: 'Report builder', body: 'Written sections and charts assemble into one formatted report.' },
      { icon: '/icons/folder.svg', title: 'Versioned studies', body: 'Every revision is kept, so a plan can be revisited without starting again.' },
    ],
    flow: {
      steps: [
        { title: 'Describe', body: 'The idea is captured once: product, people, systems and expected sales.' },
        { title: 'Calculate', body: 'The model turns those inputs into break-even, cash flows and charts.' },
        { title: 'Report', body: 'Sections and figures are assembled into a formatted document you can export.' },
      ],
    },
    useCases: [
      { title: 'Validating a business idea', body: 'Put numbers behind an idea before spending money on it.' },
      { title: 'Client studies for consultants', body: 'A consistent structure for feasibility work, produced far faster.' },
      { title: 'Funding applications', body: 'A formatted pack to hand to a bank, lender or investor.' },
      { title: 'Teaching & coursework', body: 'A worked example of market, technical, legal and financial analysis.' },
    ],
    faq: [
      { q: 'What does a study cover?', a: 'Four sections — market, technical, legal & administrative, and financial.' },
      { q: 'Can I export the report?', a: 'Yes. The report view exports to a formatted document with the executive summary and charts.' },
      { q: 'Does it support other languages?', a: 'Yes — the app is multi-language.' },
      { q: 'Can I revise a study later?', a: 'Yes. Versions are kept, so you can update inputs and regenerate without losing the original.' },
    ],
  },

  'news-platform': {
    features: [
      { icon: '/icons/quotes.svg', title: 'Arabic-first typography', body: 'A right-to-left layout and Arabic type treatment built for comfortable reading.' },
      { icon: '/icons/users.svg', title: 'Collaborative editing', body: 'Rich text with tables, images and maths, shared between writers and editors.' },
      { icon: '/icons/pencil.svg', title: 'Editorial workflow', body: 'Writers draft and editors review in the same editor before anything is published.' },
      { icon: '/icons/clock.svg', title: 'Background workers', body: 'Scheduled jobs gather and prepare content so the newsroom starts from a draft.' },
    ],
    flow: {
      steps: [
        { title: 'Write', body: 'A writer drafts in the collaborative editor, with tables, images and maths.' },
        { title: 'Edit', body: 'Editors review and adjust in the same shared editor.' },
        { title: 'Publish', body: 'The piece is filed under its categories and served as a fast, right-to-left page.' },
      ],
    },
    useCases: [
      { title: 'Newsrooms', body: 'A public site and an editorial back office in one system.' },
      { title: 'Content marketing teams', body: 'Multiple writers producing articles under one editorial standard.' },
      { title: 'Arabic publishers', body: 'A reading experience designed for right-to-left from the start.' },
      { title: 'Community & association sites', body: 'Publish updates and long-form content without a custom build.' },
    ],
    faq: [
      { q: 'Is it Arabic-first?', a: 'Yes — right-to-left layout and Arabic typography throughout, with an editor view behind it.' },
      { q: 'Can several editors work at once?', a: 'Yes. The editor is collaborative and supports rich text, tables, images and maths.' },
      { q: 'Who decides what gets published?', a: 'People. Writers draft and editors review in the shared editor before anything is published.' },
      { q: 'How does content get in?', a: 'Background workers on a schedule gather and prepare content for review.' },
    ],
  },

  'arabic-arena': {
    features: [
      { icon: '/icons/globe.svg', title: 'Bilingual public site', body: 'Marketing pages in English and Arabic, with an SEO-focused blog.' },
      { icon: '/icons/checklist.svg', title: 'Placement test', body: 'A short test routes each learner to the level that fits them.' },
      { icon: '/icons/calendar.svg', title: 'Admin dashboard', body: 'A calendar, student records, transactions and a content editor in one place.' },
      { icon: '/icons/users.svg', title: 'AI helpers', body: 'Agent-based assistance for content and student support inside the admin tools.' },
    ],
    flow: {
      steps: [
        { title: 'Apply', body: 'A learner finds a course on the public site and signs up.' },
        { title: 'Assess', body: 'The placement test decides the right starting level.' },
        { title: 'Manage', body: 'Staff run scheduling, records and payments from the admin app.' },
      ],
    },
    useCases: [
      { title: 'Language schools', body: 'Courses, learners and staff in one place instead of spreadsheets.' },
      { title: 'Tutoring businesses', body: 'Scheduling, records and payments without a custom build.' },
      { title: 'Training academies', body: 'A catalogue, a placement step and an admin back office.' },
      { title: 'Corporate language programmes', body: 'Manage cohorts and track progress for staff learning a language.' },
    ],
    faq: [
      { q: 'Is the site bilingual?', a: 'Yes — English and Arabic marketing pages, plus a blog built for search.' },
      { q: 'How do learners start at the right level?', a: 'A placement test assigns them a level before enrolment.' },
      { q: 'Where are payments handled?', a: 'In the admin app, alongside student records and a calendar.' },
      { q: 'What do the AI features do?', a: 'They help staff with content and student support inside the admin tools.' },
    ],
  },

  'ijo-bs': {
    features: [
      { icon: '/icons/search.svg', title: 'Reference gathering', body: 'Agents plan search angles and fill an exact reference count from a local journal index, Crossref, DOAJ, Semantic Scholar and Unpaywall.' },
      { icon: '/icons/fingerprint.svg', title: 'Reference vetting', body: 'Every candidate is scored and screened, and kept only when its source PDF can actually be fetched.' },
      { icon: '/icons/check.svg', title: 'Claim checking', body: 'Quotes are matched against the cited paper and page; mismatches are corrected or dropped before review.' },
      { icon: '/icons/users.svg', title: 'Human in the loop', body: 'The pipeline prepares a verified package for editors, and the editorial decision stays with a person.' },
    ],
    flow: {
      steps: [
        { title: 'Submit', body: 'A paper arrives on the journal platform with a title and a description, and an editorial review run starts.' },
        { title: 'Gather and vet', body: 'Agents search, score and screen the candidates, keeping only references whose source PDF can be fetched.' },
        { title: 'Verify and hand over', body: 'Quotes are checked against the cited paper and page, and the vetted package goes to an editor.' },
      ],
    },
    useCases: [
      { title: 'Reference gathering', body: 'Fill an exact reference count for a submission from its title and description.' },
      { title: 'Reference vetting', body: 'Score and screen candidates so only sources that fit the paper, and can be opened, reach review.' },
      { title: 'Claim checking', body: 'Match quotes back to the paper and page they came from before publication.' },
      { title: 'Journal workflows', body: 'A checkpointed agentic pipeline that runs alongside the journal site, from submission to a citable DOI.' },
    ],
    faq: [
      { q: 'What is Imper?', a: 'The internal agentic platform behind the journal: reference gathering, vetting and claim checking for submissions.' },
      { q: 'Do articles get a DOI?', a: 'Yes — metadata is deposited to Crossref automatically.' },
      { q: 'How does review work?', a: 'Authors submit and track status; editors and reviewers use dedicated screens, with a vetted reference package prepared by the pipeline.' },
      { q: 'What is the stack?', a: 'A Next.js front end over a Python (Flask) API with MongoDB; the internal Imper platform runs LangGraph workflows on an agent runtime.' },
    ],
  },

  'workshop-management': {
    features: [
      { icon: '/icons/clock.svg', title: 'Job status tracking', body: 'Every job moves through clear stages, with a public page customers can follow.' },
      { icon: '/icons/file-text.svg', title: 'Quotations & documents', body: 'Quotations and job documents are generated as PDFs.' },
      { icon: '/icons/truck.svg', title: 'Supplier management', body: 'Parts and suppliers are tracked alongside the jobs that need them.' },
      { icon: '/icons/fingerprint.svg', title: 'QR codes & support', body: 'QR codes identify jobs and assets, and a ticketing system handles support.' },
    ],
    flow: {
      steps: [
        { title: 'Intake', body: 'A job is logged, tagged with a QR code and quoted.' },
        { title: 'Repair', body: 'Status updates flow to a public tracking page the customer can check.' },
        { title: 'Collect', body: 'Payment and hand-over close the job, with documents on file.' },
      ],
    },
    useCases: [
      { title: 'Repair workshops', body: 'Jobs, quotations, suppliers and customers in one system.' },
      { title: 'Service centres', body: 'Multi-branch operations with per-business data and a super-admin.' },
      { title: 'Multi-branch stores', body: 'Each branch manages its own jobs while head office sees the whole picture.' },
      { title: 'Field service teams', body: 'Track jobs and assets with QR codes and live status.' },
    ],
    faq: [
      { q: 'Can customers track their job?', a: 'Yes — each job has a public tracking page, updated as the status changes.' },
      { q: 'Does it support several businesses?', a: 'Yes. Each workshop or store has its own data, with a super-admin across the platform.' },
      { q: 'How are quotations handled?', a: 'Quotations and job documents are produced as PDFs.' },
      { q: 'Are updates live?', a: 'Status changes are pushed over socket connections, and customers also get email updates.' },
    ],
  },

  'waffa-app': {
    features: [
      { icon: '/icons/mic.svg', title: 'Buyer-to-seller chat', body: 'Shoppers message sellers directly, with product cards inside the conversation.' },
      { icon: '/icons/cart.svg', title: 'Orders & wishlists', body: 'Categories, search, saved items and a full order flow.' },
      { icon: '/icons/briefcase.svg', title: 'Seller stores', body: 'Sellers run their own storefront and manage products.' },
      { icon: '/icons/globe.svg', title: 'Arabic, right-to-left UI', body: 'Arabic fonts and a right-to-left layout designed for the region.' },
    ],
    flow: {
      steps: [
        { title: 'Browse', body: 'A shopper searches categories and collects items in a saved list.' },
        { title: 'Chat', body: 'The buyer messages the seller directly, product cards in the chat.' },
        { title: 'Order', body: 'The order is placed through the app and managed by the seller.' },
      ],
    },
    useCases: [
      { title: 'Local marketplaces', body: 'Connect nearby buyers and sellers with a mobile-first app.' },
      { title: 'Classifieds', body: 'Listings with direct chat instead of phone numbers in a feed.' },
      { title: 'Social commerce', body: 'Give an Instagram-style seller a real storefront and order flow.' },
      { title: 'Niche B2C apps', body: 'A branded app for a category or community that shops locally.' },
    ],
    faq: [
      { q: 'Which platforms does it run on?', a: 'Android, built with Expo Router — with a web target as well.' },
      { q: 'Where are product photos stored?', a: 'In object storage (Cloudflare R2), accessed only from the server.' },
      { q: 'Who manages products?', a: 'Each seller manages their own store from inside the app.' },
      { q: 'Is it Arabic?', a: 'Yes — the interface is Arabic-first with a right-to-left layout.' },
    ],
  },

  'gold-queen': {
    features: [
      { icon: '/icons/cart.svg', title: 'Catalogue & collections', body: 'Products organised into collections, with search for the whole store.' },
      { icon: '/icons/share.svg', title: 'WhatsApp contact', body: 'A direct WhatsApp button turns browsing into a conversation.' },
      { icon: '/icons/pencil.svg', title: 'Blog & content', body: 'A blog for content marketing, tied to the same storefront.' },
      { icon: '/icons/gauge.svg', title: 'Admin panel', body: 'The owner manages products and orders without a developer.' },
    ],
    flow: {
      steps: [
        { title: 'Browse', body: 'A customer lands on a fast, right-to-left storefront.' },
        { title: 'Contact', body: 'They start a WhatsApp conversation or place the order directly.' },
        { title: 'Fulfil', body: 'The owner manages the order and catalogue from the admin panel.' },
      ],
    },
    useCases: [
      { title: 'Personal-care brands', body: 'A storefront that matches the packaging and the audience.' },
      { title: 'Local retail', body: 'Sell online without leaving WhatsApp for the conversation.' },
      { title: 'Instagram-first shops', body: 'Give a social audience a real store with search and collections.' },
      { title: 'Regional direct-to-consumer', body: 'A fast, Arabic, mobile-friendly shop for regional customers.' },
    ],
    faq: [
      { q: 'Where is the store hosted?', a: 'On Cloudflare with an edge database (D1) — pages are server-rendered and fast.' },
      { q: 'Can the owner manage it alone?', a: 'Yes — products and orders are handled from the built-in admin panel.' },
      { q: 'Is there marketing content?', a: 'A blog is built in, so content marketing lives with the shop.' },
      { q: 'How do customers ask questions?', a: 'Through a WhatsApp contact button on the storefront.' },
    ],
  },

  crm: {
    features: [
      { icon: '/icons/calendar.svg', title: 'Clients, events, speakers', body: 'Every part of an event is linked: clients, speakers, sponsors and the event itself.' },
      { icon: '/icons/folder.svg', title: 'File management', body: 'Files are stored with permissions by file type.' },
      { icon: '/icons/chart.svg', title: 'Automatic reports', body: 'Daily and weekly reports are generated without anyone asking.' },
      { icon: '/icons/share.svg', title: 'Scheduled sync & backups', body: 'Cron jobs keep data in sync and take backups on a schedule.' },
    ],
    flow: {
      steps: [
        { title: 'Capture', body: 'Clients, speakers and sponsors are recorded against an event.' },
        { title: 'Organise', body: 'Files, notes and responsibilities are attached to the right record.' },
        { title: 'Report', body: 'Daily and weekly reports summarise where each event stands.' },
      ],
    },
    useCases: [
      { title: 'Event agencies', body: 'Keep every event, client and partner in one place.' },
      { title: 'Conference organisers', body: 'Track speakers, sponsors and files across a programme.' },
      { title: 'Sponsorship teams', body: 'Follow sponsor relationships and deliverables per event.' },
      { title: 'Membership bodies', body: 'A structured record of members, events and communication.' },
    ],
    faq: [
      { q: 'Does it produce reports?', a: 'Yes — daily and weekly reports are generated automatically.' },
      { q: 'How is file access controlled?', a: 'Files carry permissions by file type.' },
      { q: 'What keeps it safe?', a: 'Scheduled jobs and backups run on a cron, with read/write routes behind roles.' },
      { q: 'What does it link together?', a: 'Clients, events, speakers, sponsors and files — all related to each other.' },
    ],
  },

  'mail-platform': {
    features: [
      { icon: '/icons/inbox.svg', title: 'Multiple mailboxes', body: 'Several mailboxes with inbound and outbound tracking per conversation.' },
      { icon: '/icons/pencil.svg', title: 'Templates & signatures', body: 'Reusable templates and signatures keep replies consistent.' },
      { icon: '/icons/bell.svg', title: 'Bounce & auto-reply detection', body: 'Bounced messages and automatic replies are detected and filed.' },
      { icon: '/icons/connect.svg', title: 'Agent-drafted replies', body: 'Agents draft replies and campaigns for a human to review and send.' },
    ],
    flow: {
      steps: [
        { title: 'Connect', body: 'Mailboxes are connected through an email engine.' },
        { title: 'Sync', body: 'New, sent and bounced messages are pushed to the app by webhook.' },
        { title: 'Reply', body: 'An agent drafts the reply or campaign; a person approves it.' },
      ],
    },
    useCases: [
      { title: 'Sales outreach', body: 'Campaigns with templates and tracking, drafted by an agent.' },
      { title: 'Support inboxes', body: 'Several mailboxes handled with consistent, templated replies.' },
      { title: 'Founder-led sales', body: 'One person handling a lot of mail with assistance.' },
      { title: 'Agency campaigns', body: 'Run and track campaigns for multiple clients from one place.' },
    ],
    faq: [
      { q: 'Does it send real email?', a: 'Yes — the platform receives and sends real email through an email engine.' },
      { q: 'How does the app know what happened?', a: 'Webhooks push new, sent and bounced messages to the app.' },
      { q: 'Can the agent send replies by itself?', a: 'It drafts replies and campaigns; a person reviews and approves them.' },
      { q: 'Where is mail stored?', a: 'Messages and attachments are stored in the database so they stay searchable.' },
    ],
  },

  cashirk: {
    features: [
      { icon: '/icons/mic.svg', title: 'An agent from a prompt', body: 'Give it a name and a system prompt and a voice agent is created for you.' },
      { icon: '/icons/users.svg', title: 'Live conversation', body: 'Press start and talk to it over WebRTC, straight from the browser.' },
      { icon: '/icons/gauge.svg', title: 'Listening & speaking state', body: 'The screen shows when the agent is listening, thinking or speaking.' },
      { icon: '/icons/devices.svg', title: 'A 3D agent', body: 'A live 3D visual gives the voice something to look at.' },
    ],
    flow: {
      steps: [
        { title: 'Configure', body: 'A name and a system prompt are sent to the server to create the agent.' },
        { title: 'Talk', body: 'The browser gets a short-lived token and streams audio over WebRTC.' },
        { title: 'Review', body: 'The live transcript and speaking state show exactly what was said.' },
      ],
    },
    useCases: [
      { title: 'Voice demos', body: 'Show a speaking agent without writing any telephony code.' },
      { title: 'Support experiments', body: 'Prototype an inbound voice assistant before committing to a platform.' },
      { title: 'Language practice', body: 'Talk to an agent that holds a conversation and shows the transcript.' },
      { title: 'Voice UX prototyping', body: 'Test prompts and flows in the browser in minutes.' },
    ],
    faq: [
      { q: 'Which platform does it use?', a: 'The ElevenLabs Agents platform, with tokens issued by the server.' },
      { q: 'Is the audio streamed live?', a: 'Yes — the conversation runs over WebRTC in the browser.' },
      { q: 'Can I see what was said?', a: 'Yes, there is a live transcript and an on-screen speaking state.' },
      { q: 'Do I need a phone number?', a: 'No — it runs entirely in the browser.' },
    ],
  },

  hololens: {
    features: [
      { icon: '/icons/cells.svg', title: 'Arduino over serial', body: 'Sensor values are read from an Arduino over the serial port.' },
      { icon: '/icons/server.svg', title: 'Unity client relay', body: 'A Unity client receives the values and passes them on.' },
      { icon: '/icons/share.svg', title: 'Photon networking', body: 'Photon Unity Networking carries the data between devices.' },
      { icon: '/icons/file-text.svg', title: 'Written setup guide', body: 'A guide covers setup, emulator testing and device testing.' },
    ],
    flow: {
      steps: [
        { title: 'Read', body: 'The Arduino reads its sensor and writes values to the serial port.' },
        { title: 'Relay', body: 'A Unity client reads the port and publishes the values over Photon.' },
        { title: 'Display', body: 'The HoloLens 2 app shows the live data in mixed reality.' },
      ],
    },
    useCases: [
      { title: 'Mixed-reality demos', body: 'Show live hardware data floating in a headset.' },
      { title: 'Hardware integration teaching', body: 'A worked example of connecting a device to a headset.' },
      { title: 'Lab instrument overlays', body: 'Surface sensor readings where the work actually happens.' },
      { title: 'Industrial training', body: 'Walk through equipment with live readings in view.' },
    ],
    faq: [
      { q: 'What hardware does it use?', a: 'An Arduino for the sensor and a HoloLens 2 for the display.' },
      { q: 'How does the data get to the headset?', a: 'Serial to a Unity client, then relayed with Photon Unity Networking.' },
      { q: 'Can I test without a headset?', a: 'Yes — the guide covers emulator testing as well as device testing.' },
      { q: 'Is there documentation?', a: 'Yes, a written guide to setup and testing.' },
    ],
  },
};

/** Long-form overview copy per project — replaces the short one-liner on each page. */
const OVERVIEW: Record<string, string> = {
  'imper-enterprise':
    'Imper Enterprise is the internal platform a journal review desk runs on. Give it a paper title and a description and a staged pipeline goes to work: an agent plans the search angles, a fan-out of researchers queries a local index of harvested journals alongside Crossref, DOAJ, Semantic Scholar and Unpaywall, and candidates are scored and screened until the requested number of references is filled. From there the work is verification. Scoring batches rank every candidate, the PDF gate keeps only references whose source file can actually be fetched, and quotes are checked against the cited paper and page so a claim cannot drift away from its source. The workflows are LangGraph graphs, and each stage is checkpointed, so a failed or interrupted run resumes where it stopped instead of repeating the expensive search. Every step records its model, tokens, cost and duration, which is what makes the cost and latency tuning possible.',
  openabstracts:
    'OpenAbstracts is one endpoint for finding academic papers, built for developers and AI agents alike. A single REST call searches a real index of literature (titles, abstracts and the full text inside PDFs), and every result returns the metadata a citation needs: authors, year, journal, DOI, quartile, abstract and links to the PDF and publisher page. The same search is exposed as a remote MCP server, so Claude, Cursor or any other agent can look a paper up as a tool instead of guessing at a reference. A companion Claude Skill verifies a citation against the real paper before it is used, which is the difference between an agent that sounds convincing and one that is actually correct.',
  'feasibility-study':
    'Feasibility Study Builder takes a business idea and turns it into the document an investor, lender or manager actually asks for. Inputs are collected once through guided forms (products, people, systems and expected sales) and a deterministic pipeline does the rest: market, technical, legal and administrative, and financial sections, with break-even, revenues and costs, cash flows and charts computed from the figures rather than generated by a model. The result is a formatted report with an executive summary you can export, and because every version is kept, a plan can be revised and regenerated without starting over. It runs on Cloudflare with a small relational database and supports multiple languages.',
  'news-platform':
    'An Arabic news platform with a full editorial back office behind it. Readers get a fast, right-to-left front end with a home page, categories and article pages, while writers and editors work in a collaborative editor that handles rich text, tables, images and maths. Scheduled workers run in the background gathering and preparing content, so the newsroom starts from a draft instead of a blank page. Everything is server-rendered on Cloudflare, with articles, categories and users held in a shared database.',
  'arabic-arena':
    'Arabic Arena is an online Arabic school I work on part-time as a software engineer, covering both sides of the school. On one side is the public site: bilingual English and Arabic marketing pages, a course catalogue, a blog written for search, and a placement test that routes each learner to the level that actually fits them. On the other is the admin app where staff run the school (a calendar, student records, transactions and a rich-text content editor), with small assistants built into those admin tools for content and student support. Two Next.js applications share one MongoDB database and object storage for media, so the public site and the back office never drift apart.',
  'ijo-bs':
    'IJO-BS is the International Journal of Business and Society, and my full-time work there is building Imper, the internal agentic platform that reviews its submissions. A run starts from a paper title and description: agents plan the search angles, fan out across a local index of harvested journals and open sources, then score and screen candidates until the requested reference count is filled. Verification is the point of the pipeline. The PDF gate keeps only sources that can actually be opened, quotes are matched back to the cited paper and page, and anything that cannot be tied to a real source is corrected or dropped. The workflows are LangGraph graphs with checkpointed stages, so an interrupted run resumes instead of repeating the search, and each step records its model, tokens, cost and duration. The public journal platform carries a paper the rest of the way: submission, peer review, issues and archive, and an automatic Crossref deposit so a published article gets a real DOI.',
  'workshop-management':
    'A system for running a repair workshop end to end: jobs, quotations, suppliers, customers and support. Each job moves through clear stages, and every one gets a QR code so staff can pull it up instantly, plus a public tracking page so the customer can check progress without calling. Quotations and job documents are generated as PDFs, and a built-in ticketing system handles support with roles and internal notes. It is multi-tenant: each workshop or store manages its own data while a super-admin oversees the platform. Status changes flow over socket connections, with email updates for customers.',
  'waffa-app':
    'A mobile marketplace built for buying and selling locally, with an Arabic, right-to-left interface. Shoppers browse categories, search, save items to a wishlist and collect them in a cart, then message the seller directly — with product cards inside the conversation, so the listing stays in view while they talk. Sellers get their own store and manage products without leaving the app. It is a single Expo client talking to a Flask API over MongoDB, with product images in object storage that is only ever accessed from the server.',
  'gold-queen':
    'An Arabic e-commerce storefront for a personal-care brand, built so the owner can run it without a developer. Customers get a fast, right-to-left shop: a catalogue organised into collections, product pages, search and a blog used for content marketing. A WhatsApp button turns browsing into a conversation, which is how a lot of regional commerce actually happens. Behind it an admin panel handles products and orders, media is served from object storage, and the store runs on Cloudflare with an edge database and server-rendered pages.',
  crm:
    'A CRM for an events business, built around the way events actually relate to everything else. Clients, events, speakers and sponsors are linked to one another rather than kept in separate lists, and files are stored with permissions by file type. Daily and weekly reports are generated automatically, so nobody has to assemble a status update by hand. Scheduled jobs keep data in sync and take backups on a cron. It runs as a Next.js front end on Cloudflare over a D1 database, with Python workers behind the routes.',
  'mail-platform':
    'An email platform where agents do the drafting. It connects real mailboxes, sends and receives actual mail through an email engine, and keeps every conversation searchable — with multiple inboxes, templates and signatures. Webhooks push new, sent and bounced messages into the app, and bounce and auto-reply detection keeps the noise out of the way. On top of that, language-model agents draft replies and campaigns for a person to review before anything is sent. The stack is a Next.js interface with Docker, Redis, LangChain, OpenAI and Drizzle underneath.',
  cashirk:
    'A real-time voice agent you create and talk to in the browser. Give it a name and a system prompt, and the server provisions the agent on the ElevenLabs Agents platform and issues a short-lived token for the conversation; from there the browser streams audio directly over WebRTC and the conversation happens live. The screen shows whether the agent is listening or speaking, keeps a running transcript, and gives the voice a live 3D visual so there is something to look at while you talk. The ElevenLabs Agents platform handles the hard parts of speech — turn-taking, latency, audio — while this app owns provisioning, session tokens and the browser experience.',
  hololens:
    'A mixed-reality project that connects hardware to a headset. An Arduino reads its sensor and writes values to the serial port; a Unity client on a PC reads that stream and relays it over Photon Unity Networking; and a HoloLens 2 app displays the live values in the user’s view. It is a small system, but it is a working example of the whole chain — sensor to client to headset — and it is documented: a written guide covers setup, emulator testing and testing on the device, so someone else can reproduce it end to end.',
};

/** Swap in the long overview, replacing the short section or prepending a new one. */
function withOverview(p: Project): Project {
  const text = OVERVIEW[p.id];
  if (!text) return p;
  const hasOverview = p.sections.some((s) => s.heading === 'Overview');
  return {
    ...p,
    sections: hasOverview
      ? p.sections.map((s) => (s.heading === 'Overview' ? { ...s, body: text } : s))
      : [{ heading: 'Overview', body: text }, ...p.sections],
  };
}

/**
 * Projects kept in the codebase but hidden from the site for now.
 * Remove an id from this set to bring the project back everywhere.
 */
const HIDDEN_PROJECT_IDS = new Set(['imper-enterprise', 'news-platform']);

export const PROJECTS: Project[] = rawProjects
  .filter((p) => !HIDDEN_PROJECT_IDS.has(p.id))
  .map((p) => {
    const base = withOverview(ENRICH[p.id] ? { ...p, ...ENRICH[p.id] } : p);
    const primary = LIVE_SHOT[base.id];
    if (!primary || base.screenshots.length >= 3) return base;
    const host = base.url ? base.url.href.replace(/^https?:\/\//, '').replace(/\/$/, '') : base.title;
    const extra = [{ src: primary, caption: `Live site — ${host}` }];
    if (SECOND_LIVE_SHOT.has(base.id)) {
      extra.push({ src: primary.replace('live-1.jpg', 'live-2.jpg'), caption: `Live site — ${host} (scrolled)` });
    }
    return { ...base, screenshots: [...base.screenshots, ...extra] };
  });

export const getProject = (id: string) => PROJECTS.find((p) => p.id === id);
