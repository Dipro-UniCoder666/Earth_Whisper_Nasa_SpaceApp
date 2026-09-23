import { Link } from 'react-router-dom'
import { ROUTES } from '@/lib/constants'

export function Footer() {
  return (
    <footer className="border-t border-[var(--color-border)] bg-white">
      <div className="page-container py-10">
        <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
          {/* Brand */}
          <div>
            <p className="text-sm font-semibold text-[var(--color-navy)]">Earth Whisper</p>
            <p className="mt-1 text-xs text-[var(--color-text-muted)]">
              Where Earth&rsquo;s Changes Tell Their Story
            </p>
            <p className="mt-3 text-xs text-[var(--color-text-muted)]">
              AquaByte · NASA Space Apps Challenge 2026
            </p>
          </div>

          {/* Links */}
          <div className="flex flex-wrap gap-x-8 gap-y-2">
            <Link
              to={ROUTES.investigate}
              className="text-sm text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-navy)]"
            >
              Investigate
            </Link>
            <Link
              to={ROUTES.about}
              className="text-sm text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-navy)]"
            >
              About
            </Link>
            <a
              href="https://www.spaceappschallenge.org/"
              target="_blank"
              rel="noreferrer"
              className="text-sm text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-navy)]"
            >
              NASA Space Apps ↗
            </a>
          </div>

          {/* Data source */}
          <div className="text-xs text-[var(--color-text-muted)]">
            <p className="font-medium uppercase tracking-wide text-[var(--color-text-muted)]">Data</p>
            <p className="mt-1">NASA-ISRO NISAR</p>
          </div>
        </div>

        <div className="mt-8 border-t border-[var(--color-border-subtle)] pt-6 text-xs text-[var(--color-text-muted)]">
          Earth Whisper is a submission for the NASA Space Apps Challenge and is not an official NASA product.
        </div>
      </div>
    </footer>
  )
}
