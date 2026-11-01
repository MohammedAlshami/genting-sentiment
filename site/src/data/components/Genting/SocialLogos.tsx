const SOCIALS = [
  { name: 'Reddit', src: '/logos/social/reddit.svg' },
  { name: 'YouTube', src: '/logos/social/youtube.svg' },
  { name: 'TikTok', src: '/logos/social/tiktok.svg' },
  { name: 'Telegram', src: '/logos/social/telegram.svg' },
  { name: 'Facebook', src: '/logos/social/facebook.svg' },
  { name: 'Instagram', src: '/logos/social/instagram.svg' },
  { name: 'X', src: '/logos/social/x.svg' },
];

export function SocialLogos({
  className = '',
  showNames = false,
}: {
  className?: string;
  showNames?: boolean;
}) {
  return (
    <div className={`flex flex-wrap items-center gap-4 ${className}`}>
      {SOCIALS.map((social) => (
        <span
          key={social.name}
          className="inline-flex items-center gap-2 opacity-55 transition-opacity hover:opacity-100"
          title={social.name}
        >
          <img
            src={social.src}
            alt={social.name}
            className="h-4 w-4 object-contain"
          />
          {showNames && (
            <span className="font-mono text-[8px] uppercase tracking-[0.14em] text-[#0E100F]/50">
              {social.name}
            </span>
          )}
        </span>
      ))}
      <span
        className="inline-flex items-center gap-2 opacity-55 transition-opacity hover:opacity-100"
        title="LinkedIn"
      >
        <svg
          viewBox="0 0 24 24"
          className="h-4 w-4 fill-[#0E100F]"
          aria-label="LinkedIn"
        >
          <path d="M4.98 3.5C4.98 4.88 3.87 6 2.5 6S0 4.88 0 3.5 1.11 1 2.5 1s2.48 1.12 2.48 2.5zM.22 8h4.56v14H.22zM8.34 8h4.37v1.9h.06c.61-1.16 2.1-2.38 4.32-2.38 4.62 0 5.47 3.04 5.47 7v8.48h-4.56v-7.52c0-1.8-.03-4.11-2.5-4.11-2.5 0-2.88 1.95-2.88 3.97v7.66H8.34z" />
        </svg>
        {showNames && (
          <span className="font-mono text-[8px] uppercase tracking-[0.14em] text-[#0E100F]/50">
            LinkedIn
          </span>
        )}
      </span>
    </div>
  );
}
