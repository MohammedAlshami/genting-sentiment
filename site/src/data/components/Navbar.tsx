'use client';

import Link from '@/compat/next-link';

const NAV = [
  { href: '/projects', label: 'Projects', icon: '/icons/kanban.svg' },
  { href: '/resume', label: 'Résumé', icon: '/icons/resume.svg' },
];

/** Site-wide top bar, fixed over the page. Used by the root layout on every route. */
export default function Navbar() {
  return (
    <header className="fixed left-0 right-0 top-0 z-50 w-full px-4 pt-2 font-sf-pro-display sm:px-6">
      <div className="flex w-full text-[#FFF7DD]">
        <nav className="font-sf-pro-display h-14 w-full overflow-hidden rounded-2xl border-0 py-2">
          <div className="flex w-full items-center justify-between px-4 text-[#FFF7DD] sm:px-5">
            <Link href="/" className="block">
              <h2
                className="flex text-xl font-bold tracking-tight transition-opacity hover:opacity-90"
                style={{ fontFamily: '"Mori", sans-serif' }}
              >
                SHAMI
              </h2>
            </Link>
            <div className="flex items-center gap-5 sm:gap-7">
              {NAV.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="group inline-flex items-center gap-2 text-base font-bold uppercase tracking-wider transition-opacity hover:opacity-80"
                >
                  <img
                    src={item.icon}
                    alt=""
                    aria-hidden
                    draggable={false}
                    className="h-[18px] w-[18px] object-contain opacity-70 transition-opacity group-hover:opacity-100"
                  />
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </nav>
      </div>
    </header>
  );
}
