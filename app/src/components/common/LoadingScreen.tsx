export function LoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg)]" role="status" aria-live="polite">
      <div className="flex flex-col items-center gap-4">
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none" aria-hidden="true">
          <circle cx="28" cy="28" r="24" stroke="var(--color-sky)" strokeWidth="3" />
          <path
            d="M28 4a24 24 0 0 1 24 24"
            stroke="var(--color-primary)"
            strokeWidth="3"
            strokeLinecap="round"
            className="ew-orbit-slow"
            style={{ animationDuration: '1.4s' }}
          />
        </svg>
        <span className="text-sm text-[var(--color-muted)]">Loading Earth Whisper…</span>
      </div>
    </div>
  )
}
