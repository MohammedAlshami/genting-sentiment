/**
 * Compatibility: next/link -> TanStack Router Link
 */
import { Link as TanStackLink } from "@tanstack/react-router";
import type { ReactNode } from "react";

interface NextLinkProps {
  href: string;
  children: ReactNode;
  className?: string;
  replace?: boolean;
  scroll?: boolean;
  prefetch?: boolean;
}

export default function Link({ href, children, className, replace }: NextLinkProps) {
  return (
    <TanStackLink to={href} className={className} replace={replace}>
      {children}
    </TanStackLink>
  );
}
