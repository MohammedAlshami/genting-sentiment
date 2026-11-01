import type { ReactNode } from 'react';

type Props = { className?: string };

/** Notion "Freebie" line illustrations, tinted cream for the dark theme. */
const ILLUSTRATIONS: Record<string, string> = {
  'imper-enterprise': '/illustrations/imper-enterprise.svg',
  paper: '/illustrations/paper.svg',
  openabstracts: '/illustrations/openabstracts.svg',
  cashirk: '/illustrations/cashirk.svg',
  'mail-platform': '/illustrations/mail-platform.svg',
  'feasibility-study': '/illustrations/feasibility-study.svg',
  'news-platform': '/illustrations/news-platform.svg',
  'arabic-arena': '/illustrations/arabic-arena.svg',
  'ijo-bs': '/illustrations/ijo-bs.svg',
  'workshop-management': '/illustrations/workshop-management.svg',
  'waffa-app': '/illustrations/waffa-app.svg',
  'gold-queen': '/illustrations/gold-queen.svg',
  crm: '/illustrations/crm.svg',
  hololens: '/illustrations/hololens.svg',
};

export const PROJECT_ILLUSTRATION: Record<string, (p: Props) => ReactNode> = Object.fromEntries(
  Object.entries(ILLUSTRATIONS).map(([id, src]) => [
    id,
    ({ className }: Props) => <img src={src} alt="" className={className} draggable={false} />,
  ]),
) as Record<string, (p: Props) => ReactNode>;
