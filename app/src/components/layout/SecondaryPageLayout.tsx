import type { ReactNode } from 'react'
import { SkipLink } from '@/components/common/SkipLink'
import { WhisperNav } from '@/components/navigation/WhisperNav'
import { Footer } from '@/pages/sections/Footer'
import { HeroAtmosphere } from '@/components/layout/HeroAtmosphere'

interface SecondaryPageLayoutProps {
  children: ReactNode
}

/**
 * Shared layout for every non-landing page.
 *
 * Structure:
 *   - Other_Page.svg covers the full viewport as a fixed atmospheric background
 *   - A subtle dark overlay keeps text readable without killing the image
 *   - WhisperNav in overlay variant — visually identical to the landing page navbar
 *   - Scrollable content sits above both layers
 *   - Landing Footer at the bottom
 */
export function SecondaryPageLayout({ children }: SecondaryPageLayoutProps) {
  return (
    <div
      data-theme="dark"
      style={{
        position: 'relative',
        minHeight: '100vh',
        color: '#e6eef8',
        isolation: 'isolate',
      }}
    >
      {/* ── Full-viewport Other_Page background — fixed so it never scrolls ── */}
      <div
        aria-hidden="true"
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 0,
          backgroundImage: 'url(/images/Other_Page.svg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center top',
          backgroundRepeat: 'no-repeat',
        }}
      />

      {/* ── Subtle dark overlay — preserves image atmosphere, ensures readability ── */}
      <div
        aria-hidden="true"
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 1,
          background: 'linear-gradient(180deg, rgba(4,9,18,0.52) 0%, rgba(4,9,18,0.42) 40%, rgba(4,9,18,0.58) 100%)',
        }}
      />

      {/* ── Skip link ── */}
      {/* Keep the shared hero atmosphere inside the top hero band so it does
          not continue behind the page footer or lower content. */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: '0 0 auto',
          height: '900px',
          overflow: 'hidden',
          pointerEvents: 'none',
          zIndex: 2,
        }}
      >
        <HeroAtmosphere />
      </div>

      <SkipLink />

      {/* ── Navbar — overlay variant, floats over background exactly like landing page ── */}
      <div style={{ position: 'relative', zIndex: 40 }}>
        <WhisperNav variant="overlay" />
      </div>

      {/* ── Page content — padded top to clear the overlay navbar ── */}
      <main
        id="main-content"
        tabIndex={-1}
        style={{
          position: 'relative',
          zIndex: 10,
          paddingTop: '110px', /* clears the absolute-positioned navbar */
          minHeight: 'calc(100vh - 110px)',
        }}
      >
        {children}
      </main>

      {/* ── Footer ── */}
      <div style={{ position: 'relative', zIndex: 10 }}>
        <Footer />
      </div>
    </div>
  )
}
