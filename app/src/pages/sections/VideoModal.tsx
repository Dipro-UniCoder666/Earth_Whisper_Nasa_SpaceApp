import { useEffect, useCallback, useRef, useState } from 'react'

interface VideoModalProps {
  isOpen: boolean
  onClose: () => void
}

function distToEdge(rect: DOMRect, cx: number, cy: number): number {
  const dx = Math.max(rect.left - cx, 0, cx - rect.right)
  const dy = Math.max(rect.top  - cy, 0, cy - rect.bottom)
  return Math.sqrt(dx * dx + dy * dy)
}

// ─────────────────────────────────────────────────────────────────────────────
// Inner video component — rendered ONLY when modal is open.
// Because it mounts fresh each open, useEffect here always fires after the
// <video> element is in the DOM, so videoRef.current is never null.
// ─────────────────────────────────────────────────────────────────────────────
function VideoPlayer() {
  const videoRef = useRef<HTMLVideoElement>(null)

  // Autoplay immediately after mount
  useEffect(() => {
    const vid = videoRef.current
    if (!vid) return
    vid.muted       = true   // must be muted for autoplay to work in all browsers
    vid.currentTime = 0
    vid.play().catch(() => {
      // Silently ignore — video is muted so autoplay policy won't block it
    })
    // On unmount (modal close) → pause + reset
    return () => {
      vid.pause()
      vid.currentTime = 0
    }
  }, [])

  return (
    <video
      ref={videoRef}
      autoPlay
      muted
      loop
      controls
      playsInline
      style={{
        width: '100%',
        height: '100%',
        display: 'block',
        objectFit: 'contain',
      }}
    >
      <source src="/images/Video.mp4" type="video/mp4" />
    </video>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Modal shell — handles backdrop, glow, zoom, ESC, scroll-lock
// ─────────────────────────────────────────────────────────────────────────────
export function VideoModal({ isOpen, onClose }: VideoModalProps) {
  const wrapperRef = useRef<HTMLDivElement>(null)
  const [zoomed, setZoomed]   = useState(false)

  const handleEsc = useCallback(
    (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() },
    [onClose],
  )

  // Proximity zoom on the modal container
  useEffect(() => {
    if (!isOpen) return
    const onMove = (e: MouseEvent) => {
      if (!wrapperRef.current) return
      const rect = wrapperRef.current.getBoundingClientRect()
      setZoomed(distToEdge(rect, e.clientX, e.clientY) <= 3)
    }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [isOpen])

  // ESC key + scroll lock
  useEffect(() => {
    if (!isOpen) return
    document.addEventListener('keydown', handleEsc)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = ''
    }
  }, [isOpen, handleEsc])

  if (!isOpen) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Investigation video"
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        backgroundColor: 'rgba(4, 9, 18, 0.88)',
        backdropFilter: 'blur(10px)',
        animation: 'ew-modal-in 0.28s ease both',
      }}
    >
      <style>{`
        @keyframes ew-modal-in {
          from { opacity: 0; }
          to   { opacity: 1; }
        }
        @keyframes ew-modal-scale-in {
          from { opacity: 0; transform: scale(0.93); }
          to   { opacity: 1; transform: scale(1); }
        }
        @keyframes ew-modal-glow {
          0%, 100% {
            box-shadow:
              0 0 0   4px rgba(24,183,201,0.22),
              0 0 32px 12px rgba(24,183,201,0.20),
              0 0 70px 24px rgba(24,183,201,0.10),
              0 32px 80px rgba(0,0,0,0.7);
          }
          50% {
            box-shadow:
              0 0 0   4px rgba(24,183,201,0.45),
              0 0 48px 18px rgba(24,183,201,0.35),
              0 0 100px 36px rgba(24,183,201,0.18),
              0 32px 80px rgba(0,0,0,0.7);
          }
        }
        .ew-modal-wrapper {
          animation: ew-modal-scale-in 0.32s ease both, ew-modal-glow 3s ease-in-out 0.35s infinite;
          transition: transform 0.2s cubic-bezier(0.34,1.56,0.64,1);
        }
        .ew-modal-wrapper.zoomed {
          transform: scale(1.022) !important;
        }
      `}</style>

      {/* OUTER: glow + zoom — no overflow:hidden so box-shadow is visible */}
      <div
        ref={wrapperRef}
        onClick={e => e.stopPropagation()}
        className={`ew-modal-wrapper${zoomed ? ' zoomed' : ''}`}
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: '960px',
          aspectRatio: '16/9',
          borderRadius: '16px',
          border: '1px solid rgba(24,183,201,0.32)',
          background: '#000',
        }}
      >
        {/* INNER: clips video to rounded corners */}
        <div style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '16px',
          overflow: 'hidden',
          background: '#000',
        }}>
          {/* VideoPlayer mounts here — its own useEffect fires after DOM is ready */}
          <VideoPlayer />
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          aria-label="Close video"
          style={{
            position: 'absolute',
            top: '14px',
            right: '14px',
            zIndex: 10,
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            border: '1px solid rgba(255,255,255,0.2)',
            background: 'rgba(6,13,26,0.8)',
            color: '#fff',
            fontSize: '1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            backdropFilter: 'blur(8px)',
            transition: 'background 0.15s, border-color 0.15s',
          }}
        >
          ✕
        </button>
      </div>
    </div>
  )
}
