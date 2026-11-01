'use client';

import React from 'react';
import { Download, Loader2 } from 'lucide-react';

/**
 * Generates the Harvard-style résumé with @react-pdf/renderer in the browser and
 * downloads it. The PDF library and document are dynamically imported so they stay
 * out of the server bundle. Falls back to the print dialog if generation fails.
 */
export default function DownloadPdfButton() {
  const [busy, setBusy] = React.useState(false);

  const onClick = async () => {
    setBusy(true);
    try {
      const [{ pdf }, { ResumePdf }] = await Promise.all([
        import('@react-pdf/renderer'),
        import('./ResumePdf'),
      ]);
      const blob = await pdf(<ResumePdf />).toBlob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Mohammed-Al-shami-Resume.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF generation failed, falling back to print', err);
      window.print();
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      className="inline-flex items-center gap-2 rounded-lg bg-[#FFF7DD] px-4 py-2.5 text-sm font-bold uppercase tracking-wider text-[#0E100F] transition-colors hover:bg-white disabled:opacity-70 print:hidden"
    >
      {busy ? <Loader2 className="size-4 animate-spin" /> : <Download className="size-4" />}
      {busy ? 'Preparing…' : 'Download PDF'}
    </button>
  );
}
