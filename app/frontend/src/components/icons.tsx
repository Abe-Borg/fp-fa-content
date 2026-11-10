/** The app's small pictures, drawn as SVG in the current colour. The star is the app mark. */

export function Star({ size = 20, className = "star" }: { size?: number; className?: string }) {
  return (
    <svg className={className} width={size} height={size} viewBox="-50 -50 100 100" aria-hidden="true">
      <path d="M0-48 9.6-9.6 48 0 9.6 9.6 0 48-9.6 9.6-48 0-9.6-9.6Z" fill="currentColor" />
    </svg>
  );
}

export function More() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
      <circle cx="3.5" cy="9" r="1.6" fill="currentColor" />
      <circle cx="9" cy="9" r="1.6" fill="currentColor" />
      <circle cx="14.5" cy="9" r="1.6" fill="currentColor" />
    </svg>
  );
}

export function Panel() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
      <rect x="1.5" y="2.5" width="13" height="11" rx="2.2" fill="none" stroke="currentColor" strokeWidth="1.4" />
      <path d="M10 2.8v10.4" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}

export function Close() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
      <path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

export function Chevron() {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true">
      <path d="M2 3.5l3 3 3-3" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Check() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
      <path d="M2.5 6.2l2.4 2.4 4.6-5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function ArrowDown() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
      <path d="M6 2v8M2.5 6.5 6 10l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
