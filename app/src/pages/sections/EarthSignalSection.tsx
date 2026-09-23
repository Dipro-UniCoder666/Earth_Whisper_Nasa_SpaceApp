import { useRef, useState } from 'react'
import { VideoMapOverlay } from '@/pages/sections/VideoMapOverlay'

// ── Four-stage scientific process ─────────────────────────────────────────────
const STAGES = [
  { num: '01', label: 'OBSERVE',      accent: '#18B7C9', body: 'NISAR sees the signal.' },
  { num: '02', label: 'CHANGE',       accent: '#4FAF83', body: 'We isolate what changed.' },
  { num: '03', label: 'INVESTIGATE',  accent: '#7EB8E8', body: 'Independent evidence adds context.' },
  { num: '04', label: 'UNDERSTAND',   accent: '#18B7C9', body: 'An Earth Event Fingerprint brings the clues together.' },
] as const

// ── Inline styles ─────────────────────────────────────────────────────────────
const S = {
  section: {
    position: 'relative' as const,
    width: '100%',
    background: 'linear-gradient(180deg, #04090f 0%, #060e1c 40%, #07111f 100%)',
    overflow: 'hidden',
    paddingTop: '100px',
    paddingBottom: '100px',
  },
  inner: {
    position: 'relative' as const,
    zIndex: 2,
    maxWidth: '1100px',
    margin: '0 auto',
    padding: '0 32px',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
  },
  eyebrow: {
    fontSize: '0.72rem',
    fontWeight: 600,
    letterSpacing: '0.22em',
    textTransform: 'uppercase' as const,
    color: '#18B7C9',
    marginBottom: '22px',
    opacity: 0.85,
  },
  headingWrap: {
    textAlign: 'center' as const,
    marginBottom: '20px',
  },
  heading: {
    fontSize: 'clamp(2.2rem, 5vw, 3.8rem)',
    fontWeight: 800,
    letterSpacing: '-0.02em',
    lineHeight: 1.0,
    color: '#f0f6ff',
    margin: 0,
    textTransform: 'uppercase' as const,
  },
  headingAccent: {
    color: '#18B7C9',
    textShadow: '0 0 40px rgba(24,183,201,0.45)',
  },
  subtitle: {
    fontSize: 'clamp(0.95rem, 1.6vw, 1.15rem)',
    color: 'rgba(180,210,240,0.78)',
    textAlign: 'center' as const,
    maxWidth: '620px',
    lineHeight: 1.55,
    margin: '0 0 18px 0',
    fontStyle: 'italic',
  },
  body: {
    fontSize: '0.9rem',
    color: 'rgba(140,175,210,0.65)',
    textAlign: 'center' as const,
    maxWidth: '560px',
    lineHeight: 1.75,
    margin: '0 0 64px 0',
  },
  // Outer wrapper: carries glow + zoom. No overflow:hidden so box-shadow is visible.
  videoGlowWrap: {
    width: '100%',
    maxWidth: '1000px',
    position: 'relative' as const,
    borderRadius: '18px',
    border: '1px solid rgba(24,183,201,0.28)',
    aspectRatio: '16/9' as const,
    background: '#060d1a',
    cursor: 'pointer',
    marginBottom: '64px',
  },
  // Inner wrapper: clips content only
  videoInner: {
    position: 'absolute' as const,
    inset: 0,
    borderRadius: '18px',
    overflow: 'hidden' as const,
  },
  stagesRow: {
    width: '100%',
    maxWidth: '1000px',
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '0',
    position: 'relative' as const,
  },
  stageItem: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    textAlign: 'center' as const,
    padding: '0 20px',
    position: 'relative' as const,
  },
  stageNum: {
    fontSize: '0.65rem',
    fontWeight: 700,
    letterSpacing: '0.16em',
    color: 'rgba(100,160,220,0.45)',
    marginBottom: '10px',
  },
  stageDot: (accent: string) => ({
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: accent,
    boxShadow: `0 0 10px ${accent}88`,
    marginBottom: '14px',
    flexShrink: 0,
  }),
  stageLabel: (accent: string) => ({
    fontSize: '0.72rem',
    fontWeight: 700,
    letterSpacing: '0.18em',
    textTransform: 'uppercase' as const,
    color: accent,
    marginBottom: '8px',
  }),
  stageBody: {
    fontSize: '0.8rem',
    color: 'rgba(140,175,210,0.6)',
    lineHeight: 1.6,
    maxWidth: '160px',
  },
  connector: {
    position: 'absolute' as const,
    top: '42px',
    left: '50%',
    right: '-50%',
    height: '1px',
    background: 'linear-gradient(90deg, rgba(24,183,201,0.25) 0%, rgba(24,183,201,0.05) 100%)',
    pointerEvents: 'none' as const,
  },
} as const

// ── Distance helper ───────────────────────────────────────────────────────────
function distToEdge(rect: DOMRect, cx: number, cy: number): number {
  const dx = Math.max(rect.left - cx, 0, cx - rect.right)
  const dy = Math.max(rect.top  - cy, 0, cy - rect.bottom)
  return Math.sqrt(dx * dx + dy * dy)
}

// ── Atmospheric SVG background ────────────────────────────────────────────────
function SectionBackground() {
  return (
    <svg
      aria-hidden="true"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 0, pointerEvents: 'none', overflow: 'hidden' }}
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <style>{`
          @keyframes ew-sig-pulse  { 0%,100%{opacity:0.18} 50%{opacity:0.38} }
          @keyframes ew-sig-pulse2 { 0%,100%{opacity:0.08} 50%{opacity:0.20} }
          @keyframes ew-sig-twinkle  { 0%,100%{opacity:0.6} 50%{opacity:0.1} }
          @keyframes ew-sig-twinkle2 { 0%,100%{opacity:0.4} 50%{opacity:0.05} }
        `}</style>
        <radialGradient id="ew-sig-top-glow" cx="50%" cy="0%" r="55%" gradientUnits="objectBoundingBox">
          <stop offset="0%"  stopColor="#0b2a4a" stopOpacity="0.9"/>
          <stop offset="100%" stopColor="#04090f" stopOpacity="0"/>
        </radialGradient>
        <radialGradient id="ew-sig-radar-glow" cx="50%" cy="42%" r="35%" gradientUnits="objectBoundingBox">
          <stop offset="0%"  stopColor="#0a2040" stopOpacity="0.55"/>
          <stop offset="100%" stopColor="#04090f" stopOpacity="0"/>
        </radialGradient>
      </defs>
      <rect x="0" y="0" width="100%" height="220" fill="url(#ew-sig-top-glow)"/>
      <rect x="0" y="0" width="100%" height="100%" fill="url(#ew-sig-radar-glow)"/>
      {[180, 260, 340, 420].map((r, i) => (
        <ellipse key={r} cx="50%" cy="38%" rx={r} ry={r * 0.28} fill="none" stroke="rgba(24,183,201,0.07)" strokeWidth="1"
          style={{ animation: `ew-sig-pulse ${3.5 + i * 0.6}s ease-in-out infinite` }} />
      ))}
      <path d="M -80 420 Q 280 80 720 200" fill="none" stroke="rgba(24,183,201,0.06)" strokeWidth="1.5"
        style={{ animation: 'ew-sig-pulse2 6s ease-in-out infinite' }} />
      <path d="M 760 820 Q 1100 500 1500 380" fill="none" stroke="rgba(79,175,131,0.05)" strokeWidth="1"
        style={{ animation: 'ew-sig-pulse2 8s ease-in-out 1s infinite' }} />
      {[
        [82,48,.5],[218,24,.4],[364,72,.6],[512,18,.4],[688,56,.5],[854,32,.4],
        [1022,64,.6],[1188,28,.5],[1342,48,.4],[1428,82,.5],[140,140,.4],[420,124,.5],
        [740,108,.4],[1060,132,.5],[1280,116,.4],[48,680,.4],[196,720,.5],[380,760,.4],
        [1180,740,.5],[1360,700,.4],[1440,640,.5],
      ].map(([cx, cy, r], i) => (
        <circle key={i} cx={cx} cy={cy} r={r} fill="#e8f4ff"
          style={{ animation: `${i%2===0?'ew-sig-twinkle':'ew-sig-twinkle2'} ${2.4+(i%5)*0.7}s ease-in-out ${(i%4)*0.5}s infinite` }} />
      ))}
    </svg>
  )
}


// ── Main export ───────────────────────────────────────────────────────────────
export function EarthSignalSection() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [muted, setMuted] = useState(true)

  const toggleMute = () => {
    const vid = videoRef.current
    if (!vid) return
    vid.muted = !vid.muted
    setMuted(vid.muted)
  }

  return (
    <>
      <section style={S.section} aria-labelledby="ew-signal-heading">
        <style>{`
          @keyframes ew-signal-glow {
            0%, 100% {
              box-shadow:
                0 0 0   4px rgba(24,183,201,0.22),
                0 0 32px 12px rgba(24,183,201,0.20),
                0 0 70px 24px rgba(24,183,201,0.10);
            }
            50% {
              box-shadow:
                0 0 0   4px rgba(24,183,201,0.48),
                0 0 48px 18px rgba(24,183,201,0.36),
                0 0 100px 36px rgba(24,183,201,0.18);
            }
          }
          .ew-video-glow {
            animation: ew-signal-glow 3s ease-in-out infinite;
          }
          .ew-mute-btn:hover {
            background: rgba(24,183,201,0.20) !important;
            border-color: rgba(24,183,201,0.70) !important;
          }
        `}</style>
        <SectionBackground />

        <div style={S.inner}>

          <p style={S.eyebrow} aria-hidden="true">Earth Observation · NISAR · Radar Analysis</p>

          <div style={S.headingWrap}>
            <h2 id="ew-signal-heading" style={S.heading}>
              THE EARTH LEFT A{' '}
              <span style={S.headingAccent}>SIGNAL</span>
            </h2>
          </div>

          <p style={S.subtitle}>
            From an invisible radar change to evidence you can investigate.
          </p>

          {/* Outer glow wrapper — position:relative so button anchors to it */}
          <div className="ew-video-glow" style={S.videoGlowWrap}>

            {/* Inner div clips the video */}
            <div style={S.videoInner}>
              <video
                ref={videoRef}
                autoPlay
                muted
                loop
                playsInline
                style={{ width: '100%', height: '100%', display: 'block', objectFit: 'cover' }}
              >
                <source src="/images/Video.mp4" type="video/mp4" />
              </video>
            </div>

            {/* Mute / Unmute button — outside inner clip, always visible */}
            <button
              className="ew-mute-btn"
              onClick={toggleMute}
              aria-label={muted ? 'Unmute video' : 'Mute video'}
              title={muted ? 'Unmute' : 'Mute'}
              style={{
                position: 'absolute',
                top: '14px',
                left: '14px',
                zIndex: 20,
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                border: '1.5px solid rgba(255,255,255,0.35)',
                background: 'rgba(4,9,18,0.80)',
                backdropFilter: 'blur(10px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                transition: 'background 0.2s, border-color 0.2s',
                padding: 0,
              }}
            >
              {muted ? (
                /* Speaker with X = muted */
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path d="M11 5L6 9H2v6h4l5 4V5z" fill="white"/>
                  <line x1="22" y1="9" x2="16" y2="15" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                  <line x1="16" y1="9" x2="22" y2="15" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              ) : (
                /* Speaker with waves = unmuted */
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path d="M11 5L6 9H2v6h4l5 4V5z" fill="white"/>
                  <path d="M15.54 8.46a5 5 0 0 1 0 7.07" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}
            </button>

          
            {/* ── Live Leaflet map overlay — covers Gemini sparkle area ── */}
            <VideoMapOverlay />

          </div>

          {/* ── Four-stage process ── */}
          <div style={S.stagesRow}>
            {STAGES.map((stage, i) => (
              <div key={stage.num} style={S.stageItem}>
                {i < STAGES.length - 1 && <div style={S.connector} aria-hidden="true" />}
                <span style={S.stageNum}>{stage.num}</span>
                <div style={S.stageDot(stage.accent)} aria-hidden="true" />
                <span style={S.stageLabel(stage.accent)}>{stage.label}</span>
                <p style={S.stageBody}>{stage.body}</p>
              </div>
            ))}
          </div>

        </div>
      </section>
    </>
  )
}

