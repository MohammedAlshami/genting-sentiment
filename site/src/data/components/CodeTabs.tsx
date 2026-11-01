'use client';

import React from 'react';
import { Check, Copy } from 'lucide-react';
import type { Snippet } from '@/data/projects';

/** Tabbed code samples (cURL / Python / JavaScript / MCP config) with a copy button. */
export default function CodeTabs({ snippets }: { snippets: Snippet[] }) {
  const [active, setActive] = React.useState(0);
  const [copied, setCopied] = React.useState(false);

  const current = snippets[active] ?? snippets[0];

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(current.code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div className="overflow-hidden rounded-xl border border-white/15 bg-black/30">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 px-2 py-2">
        <div className="flex flex-wrap gap-1">
          {snippets.map((snippet, i) => (
            <button
              key={snippet.label}
              type="button"
              onClick={() => setActive(i)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium uppercase tracking-wider transition ${
                i === active
                  ? 'bg-white/10 text-[#FFF7DD]'
                  : 'text-[#FFF7DD]/55 hover:text-[#FFF7DD]'
              }`}
            >
              {snippet.label}
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={copy}
          className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs uppercase tracking-wider text-[#FFF7DD]/60 transition hover:text-[#FFF7DD]"
        >
          {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <pre className="overflow-x-auto p-4 text-[13px] leading-relaxed">
        <code className="font-mono text-[#FFF7DD]/90">{current.code}</code>
      </pre>
    </div>
  );
}
