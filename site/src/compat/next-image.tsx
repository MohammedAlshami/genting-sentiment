/**
 * Compatibility: next/image -> plain img for Vite
 */
import type { ReactNode } from "react";

type ImageProps = {
  src: string | { src: string; height?: number; width?: number };
  alt: string;
  width?: number;
  height?: number;
  fill?: boolean;
  sizes?: string;
  priority?: boolean;
  loading?: "lazy" | "eager";
  className?: string;
  style?: React.CSSProperties;
  children?: ReactNode;
};

export default function Image({
  src,
  alt,
  width,
  height,
  fill,
  className,
  style = {},
  ...rest
}: ImageProps) {
  const resolvedSrc = typeof src === "object" && src && "src" in src ? src.src : String(src);
  if (fill) {
    return (
      <img
        src={resolvedSrc}
        alt={alt}
        className={className}
        style={{ objectFit: "cover", width: "100%", height: "100%", ...style }}
        {...rest}
      />
    );
  }
  return (
    <img
      src={resolvedSrc}
      alt={alt}
      width={width}
      height={height}
      className={className}
      style={style}
      {...rest}
    />
  );
}
