import { useState } from 'react'
import { Search, MapPin, Loader2, AlertCircle } from 'lucide-react'
import { useLocationSearch } from '@/features/investigation/hooks/useLocationSearch'
import type { LocationSearchResult } from '@/features/investigation/types'
import { cn } from '@/lib/utils'

interface LocationSearchBoxProps {
  onSelect: (result: LocationSearchResult) => void
  placeholder?: string
}

export function LocationSearchBox({ onSelect, placeholder = 'Search a place, region, or coordinates…' }: LocationSearchBoxProps) {
  const { query, setQuery, state, reset } = useLocationSearch()
  const [focused, setFocused] = useState(false)

  const showPanel = focused && query.trim().length >= 2

  function handleSelect(result: LocationSearchResult) {
    onSelect(result)
    reset()
    setFocused(false)
  }

  return (
    <div className="relative">
      <div className="relative">
        <Search
          size={18}
          className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-muted)]"
          aria-hidden="true"
        />
        <input
          type="text"
          role="combobox"
          aria-expanded={showPanel}
          aria-controls="location-search-results"
          aria-autocomplete="list"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setTimeout(() => setFocused(false), 150)}
          placeholder={placeholder}
          className="w-full rounded-xl border border-[var(--color-sky)] bg-[var(--color-bg)] py-3.5 pl-11 pr-4 text-[var(--color-text)] placeholder:text-[var(--color-muted)] transition-colors focus:border-[var(--color-primary)] focus:bg-white focus:outline-none"
        />
        {state.status === 'loading' && (
          <Loader2
            size={16}
            className="absolute right-4 top-1/2 -translate-y-1/2 animate-spin text-[var(--color-primary)]"
            aria-hidden="true"
          />
        )}
      </div>

      {showPanel && (
        <div
          id="location-search-results"
          role="listbox"
          className="absolute left-0 right-0 top-full z-20 mt-2 overflow-hidden rounded-xl border border-[var(--color-sky)] bg-white shadow-[0_20px_50px_-24px_rgba(7,59,102,0.45)]"
        >
          {state.status === 'loading' && (
            <div className="flex items-center gap-2 px-4 py-3.5 text-sm text-[var(--color-muted)]">
              <Loader2 size={14} className="animate-spin" aria-hidden="true" />
              Searching…
            </div>
          )}

          {state.status === 'success' &&
            state.results.map((result) => (
              <button
                key={result.id}
                type="button"
                role="option"
                aria-selected={false}
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => handleSelect(result)}
                className={cn(
                  'flex w-full items-start gap-3 border-b border-[var(--color-sky)] px-4 py-3 text-left last:border-b-0',
                  'transition-colors hover:bg-[var(--color-sky)]',
                )}
              >
                <MapPin size={16} className="mt-0.5 shrink-0 text-[var(--color-primary)]" aria-hidden="true" />
                <span className="min-w-0">
                  <span className="block truncate text-sm font-medium text-[var(--color-navy)]">{result.label}</span>
                  {result.context && (
                    <span className="block truncate text-xs text-[var(--color-muted)]">{result.context}</span>
                  )}
                </span>
              </button>
            ))}

          {state.status === 'no-results' && (
            <div className="px-4 py-3.5 text-sm text-[var(--color-muted)]">
              No places found for &ldquo;{query}&rdquo;. Try a different search, or enter coordinates directly.
            </div>
          )}

          {state.status === 'error' && (
            <div className="flex items-start gap-2 px-4 py-3.5 text-sm text-[#B3432B]">
              <AlertCircle size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
              <span>{state.message}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
