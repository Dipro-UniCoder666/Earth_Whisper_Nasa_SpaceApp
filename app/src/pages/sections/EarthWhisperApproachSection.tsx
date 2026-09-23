import { useEffect, useRef, useState } from 'react'

// ─────────────────────────────────────────────────────────────────────────────
// DATA
// ─────────────────────────────────────────────────────────────────────────────

const CHALLENGE_POINTS = [
  {
    num: '01',
    label: 'SUBTLE SIGNALS',
    body: 'Important surface changes can begin as patterns too small or complex to interpret visually.',
  },
  {
    num: '02',
    label: 'MULTIPLE POSSIBILITIES',
    body: 'The same observed change can have different possible explanations.',
  },
  {
    num: '03',
    label: 'DISCONNECTED EVIDENCE',
    body: 'Radar, terrain, rainfall, land cover and other observations often need to be examined together.',
  },
] as const

const PIPELINE_STAGES = [
  {
    num: '01',
    label: 'OBSERVE',
    body: 'NISAR radar observations reveal surface change.',
    accent: '#18B7C9',
  },
  {
    num: '02',
    label: 'COMPARE',
    body: 'Temporal observations isolate where the signal changed.',
    accent: '#4FAF83',
  },
  {
    num: '03',
    label: 'COLLECT EVIDENCE',
    body: 'Terrain, rainfall, land cover and other independent clues provide context.',
    accent: '#7EB8E8',
  },
  {
    num: '04',
    label: 'INVESTIGATE',
    body: 'Evidence is compared against multiple possible explanations.',
    accent: '#18B7C9',
  },
] as const

const EVIDENCE_LAYERS = [
  { id: 'nisar',    label: 'NISAR',             sublabel: 'Radar Change',           body: 'Detect surface change across time.', accent: '#18B7C9' },
  { id: 'terrain',  label: 'TERRAIN',            sublabel: 'Elevation & Slope',      body: 'Understand the physical landscape.', accent: '#4FAF83' },
  { id: 'rainfall', label: 'RAINFALL',           sublabel: 'Precipitation Context',  body: 'Examine recent environmental conditions.', accent: '#7EB8E8' },
  { id: 'cover',    label: 'LAND COVER',         sublabel: 'Surface Context',        body: 'Understand what occupies the changed area.', accent: '#A8D5A2' },
  { id: 'optical',  label: 'OPTICAL / ENV',      sublabel: 'Visual Context',         body: 'Add complementary Earth-observation evidence when available.', accent: '#6BA3C8' },
] as const

// ─────────────────────────────────────────────────────────────────────────────
// INTERSECTION HOOK
// ─────────────────────────────────────────────────────────────────────────────

function useInView(threshold = 0.18) {
  const ref = useRef<HTMLDivElement>(null)
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setInView(true); obs.disconnect() } },
      { threshold },
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [threshold])
  return { ref, inView }
}

// ─────────────────────────────────────────────────────────────────────────────
// SUB-COMPONENTS
// ─────────────────────────────────────────────────────────────────────────────

/** Thin horizontal divider with optional cyan glow */
function Divider({ glow = false }: { glow?: boolean }) {
  return (
    <div style={{
      width: '100%',
      height: '1px',
      background: glow
        ? 'linear-gradient(90deg, transparent 0%, rgba(24,183,201,0.22) 40%, rgba(24,183,201,0.22) 60%, transparent 100%)'
        : 'rgba(255,255,255,0.06)',
      margin: '72px 0',
    }} aria-hidden="true" />
  )
}

/** Small uppercase eyebrow label */
function Eyebrow({ children, accent = '#18B7C9' }: { children: string; accent?: string }) {
  return (
    <p style={{
      fontSize: '0.68rem',
      fontWeight: 700,
      letterSpacing: '0.24em',
      textTransform: 'uppercase',
      color: accent,
      opacity: 0.82,
      margin: '0 0 18px 0',
    }}>
      {children}
    </p>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// PART 1 — THE CHALLENGE
// ─────────────────────────────────────────────────────────────────────────────

function ChallengeBlock() {
  const { ref, inView } = useInView(0.15)
  return (
    <div ref={ref}>
      <Eyebrow>The Challenge</Eyebrow>

      <h3 style={{
        fontSize: 'clamp(1.6rem, 3.2vw, 2.4rem)',
        fontWeight: 700,
        color: '#f0f6ff',
        lineHeight: 1.15,
        margin: '0 0 20px 0',
        letterSpacing: '-0.02em',
        maxWidth: '640px',
      }}>
        Earth's biggest changes don't always announce themselves.
      </h3>

      <p style={{
        fontSize: '0.92rem',
        color: 'rgba(160,195,230,0.7)',
        lineHeight: 1.75,
        maxWidth: '580px',
        margin: '0 0 56px 0',
      }}>
        Radar can reveal that a landscape has changed, but a single observation rarely
        explains why. The challenge is turning a detected change into a scientifically
        grounded investigation.
      </p>

      {/* Three challenge points */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1px',
        border: '1px solid rgba(255,255,255,0.07)',
        borderRadius: '12px',
        overflow: 'hidden',
      }}>
        {CHALLENGE_POINTS.map((pt, i) => (
          <div
            key={pt.num}
            style={{
              padding: '32px 28px',
              background: 'rgba(255,255,255,0.024)',
              borderRight: i < CHALLENGE_POINTS.length - 1 ? '1px solid rgba(255,255,255,0.06)' : 'none',
              opacity: inView ? 1 : 0,
              transform: inView ? 'translateY(0)' : 'translateY(20px)',
              transition: `opacity 0.6s ease ${0.1 + i * 0.15}s, transform 0.6s ease ${0.1 + i * 0.15}s`,
            }}
          >
            <span style={{
              display: 'block',
              fontSize: '0.6rem',
              fontWeight: 700,
              letterSpacing: '0.2em',
              color: 'rgba(100,155,210,0.5)',
              marginBottom: '14px',
            }}>{pt.num}</span>
            <span style={{
              display: 'block',
              fontSize: '0.72rem',
              fontWeight: 700,
              letterSpacing: '0.16em',
              color: '#7EB8E8',
              marginBottom: '10px',
              textTransform: 'uppercase',
            }}>{pt.label}</span>
            <p style={{
              fontSize: '0.85rem',
              color: 'rgba(140,180,220,0.65)',
              lineHeight: 1.65,
              margin: 0,
            }}>{pt.body}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// PART 2 — INVESTIGATION PIPELINE
// ─────────────────────────────────────────────────────────────────────────────

function PipelineBlock() {
  const { ref, inView } = useInView(0.2)

  return (
    <div ref={ref}>
      <Eyebrow>The Earth Whisper Approach</Eyebrow>

      <h3 style={{
        fontSize: 'clamp(1.6rem, 3.2vw, 2.4rem)',
        fontWeight: 700,
        color: '#f0f6ff',
        lineHeight: 1.15,
        margin: '0 0 16px 0',
        letterSpacing: '-0.02em',
      }}>
        Don't just detect the change.{' '}
        <span style={{ color: '#18B7C9', textShadow: '0 0 30px rgba(24,183,201,0.3)' }}>
          Investigate it.
        </span>
      </h3>

      <p style={{
        fontSize: '0.92rem',
        color: 'rgba(160,195,230,0.65)',
        lineHeight: 1.75,
        maxWidth: '560px',
        margin: '0 0 56px 0',
      }}>
        Earth Whisper turns satellite observations into an evidence-based investigation —
        keeping the measured signal separate from the interpretation.
      </p>

      {/* Pipeline row */}
      <div style={{
        position: 'relative',
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '0',
      }}>

        {/* Animated connecting line */}
        <div style={{
          position: 'absolute',
          top: '28px',
          left: '12.5%',
          right: '12.5%',
          height: '1px',
          background: 'rgba(24,183,201,0.15)',
          zIndex: 0,
        }} aria-hidden="true">
          <div style={{
            height: '100%',
            background: 'linear-gradient(90deg, #18B7C9, #4FAF83, #7EB8E8, #18B7C9)',
            transformOrigin: 'left center',
            transform: inView ? 'scaleX(1)' : 'scaleX(0)',
            transition: 'transform 1.2s cubic-bezier(0.4,0,0.2,1) 0.3s',
            opacity: 0.55,
          }} />
        </div>

        {PIPELINE_STAGES.map((stage, i) => (
          <div
            key={stage.num}
            style={{
              position: 'relative',
              zIndex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              padding: '0 16px',
              opacity: inView ? 1 : 0,
              transform: inView ? 'translateY(0)' : 'translateY(16px)',
              transition: `opacity 0.55s ease ${0.3 + i * 0.18}s, transform 0.55s ease ${0.3 + i * 0.18}s`,
            }}
          >
            {/* Dot on the line */}
            <div style={{
              width: '14px',
              height: '14px',
              borderRadius: '50%',
              background: stage.accent,
              boxShadow: `0 0 14px ${stage.accent}99`,
              border: `2px solid rgba(255,255,255,0.12)`,
              marginBottom: '20px',
              flexShrink: 0,
            }} />

            <span style={{
              fontSize: '0.58rem',
              fontWeight: 700,
              letterSpacing: '0.18em',
              color: 'rgba(100,155,210,0.45)',
              marginBottom: '8px',
            }}>{stage.num}</span>

            <span style={{
              fontSize: '0.7rem',
              fontWeight: 700,
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              color: stage.accent,
              marginBottom: '10px',
            }}>{stage.label}</span>

            <p style={{
              fontSize: '0.78rem',
              color: 'rgba(140,175,210,0.6)',
              lineHeight: 1.6,
              margin: 0,
              maxWidth: '160px',
            }}>{stage.body}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// PART 3 — EVIDENCE LAYERS
// ─────────────────────────────────────────────────────────────────────────────

function EvidenceBlock() {
  const { ref, inView } = useInView(0.15)

  return (
    <div ref={ref}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <Eyebrow>Evidence Layers</Eyebrow>
        <h3 style={{
          fontSize: 'clamp(1.4rem, 2.8vw, 2rem)',
          fontWeight: 700,
          color: '#f0f6ff',
          letterSpacing: '-0.01em',
          margin: '0 0 10px 0',
          textTransform: 'uppercase',
        }}>
          One Signal.{' '}
          <span style={{ color: '#18B7C9' }}>Multiple Clues.</span>
        </h3>
        <p style={{
          fontSize: '0.88rem',
          color: 'rgba(140,175,210,0.55)',
          margin: 0,
        }}>
          No single layer tells the whole story.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
        gap: '12px',
      }}>
        {EVIDENCE_LAYERS.map((layer, i) => (
          <div
            key={layer.id}
            style={{
              padding: '24px 20px',
              borderRadius: '10px',
              border: `1px solid ${layer.accent}22`,
              background: `linear-gradient(135deg, ${layer.accent}0a 0%, rgba(6,14,26,0.6) 100%)`,
              opacity: inView ? 1 : 0,
              transform: inView ? 'translateY(0)' : 'translateY(18px)',
              transition: `opacity 0.55s ease ${0.1 + i * 0.12}s, transform 0.55s ease ${0.1 + i * 0.12}s`,
            }}
          >
            {/* Accent bar */}
            <div style={{
              width: '24px',
              height: '2px',
              background: layer.accent,
              borderRadius: '2px',
              marginBottom: '14px',
              boxShadow: `0 0 8px ${layer.accent}66`,
            }} />

            <span style={{
              display: 'block',
              fontSize: '0.65rem',
              fontWeight: 700,
              letterSpacing: '0.18em',
              color: layer.accent,
              marginBottom: '4px',
              textTransform: 'uppercase',
            }}>{layer.label}</span>

            <span style={{
              display: 'block',
              fontSize: '0.72rem',
              color: 'rgba(180,210,240,0.55)',
              marginBottom: '10px',
            }}>{layer.sublabel}</span>

            <p style={{
              fontSize: '0.78rem',
              color: 'rgba(130,165,200,0.55)',
              lineHeight: 1.6,
              margin: 0,
            }}>{layer.body}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// PART 4 — EARTH EVENT FINGERPRINT
// ─────────────────────────────────────────────────────────────────────────────

function FingerprintBlock() {
  const { ref, inView } = useInView(0.18)

  const checkRow = (label: string, delay: string) => (
    <div
      key={label}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '7px 0',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        opacity: inView ? 1 : 0,
        transition: `opacity 0.5s ease ${delay}`,
      }}
    >
      <span style={{ fontSize: '0.72rem', color: 'rgba(160,195,230,0.6)', letterSpacing: '0.08em' }}>
        {label}
      </span>
      <span style={{
        fontSize: '0.65rem',
        color: '#4FAF83',
        letterSpacing: '0.12em',
        fontWeight: 600,
      }}>✓</span>
    </div>
  )

  return (
    <div ref={ref} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <h3 style={{
          fontSize: 'clamp(1.3rem, 2.4vw, 1.8rem)',
          fontWeight: 700,
          color: '#f0f6ff',
          letterSpacing: '0.04em',
          textTransform: 'uppercase',
          margin: '0 0 10px 0',
          opacity: inView ? 1 : 0,
          transform: inView ? 'translateY(0)' : 'translateY(14px)',
          transition: 'opacity 0.6s ease 0.1s, transform 0.6s ease 0.1s',
        }}>
          Earth Event{' '}
          <span style={{ color: '#18B7C9', textShadow: '0 0 24px rgba(24,183,201,0.4)' }}>
            Fingerprint
          </span>
        </h3>
        <p style={{
          fontSize: '0.82rem',
          color: 'rgba(130,165,200,0.5)',
          margin: 0,
          opacity: inView ? 1 : 0,
          transition: 'opacity 0.6s ease 0.2s',
        }}>
          Earth Whisper separates observation from interpretation.
        </p>
      </div>

      {/* Fingerprint card */}
      <div style={{
        width: '100%',
        maxWidth: '520px',
        borderRadius: '14px',
        border: '1px solid rgba(24,183,201,0.18)',
        background: 'linear-gradient(160deg, rgba(10,28,52,0.9) 0%, rgba(6,14,26,0.95) 100%)',
        boxShadow: '0 0 60px rgba(24,183,201,0.07), 0 24px 64px rgba(0,0,0,0.5)',
        overflow: 'hidden',
        opacity: inView ? 1 : 0,
        transform: inView ? 'translateY(0)' : 'translateY(24px)',
        transition: 'opacity 0.7s ease 0.25s, transform 0.7s ease 0.25s',
      }}>

        {/* Header bar */}
        <div style={{
          padding: '14px 24px',
          borderBottom: '1px solid rgba(24,183,201,0.14)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(24,183,201,0.05)',
        }}>
          <span style={{
            fontSize: '0.62rem',
            fontWeight: 700,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: '#18B7C9',
          }}>
            Earth Event Fingerprint
          </span>
          <span style={{
            fontSize: '0.58rem',
            color: 'rgba(24,183,201,0.45)',
            letterSpacing: '0.1em',
            fontFamily: 'monospace',
          }}>
            EWF-001
          </span>
        </div>

        <div style={{ padding: '24px' }}>
          {/* Two-column data grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '20px',
            marginBottom: '24px',
          }}>
            {/* Location */}
            <div style={{
              opacity: inView ? 1 : 0,
              transition: 'opacity 0.5s ease 0.4s',
            }}>
              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.18em', color: 'rgba(100,155,210,0.45)', textTransform: 'uppercase', marginBottom: '6px' }}>
                Location
              </span>
              <span style={{ display: 'block', fontSize: '0.82rem', color: '#e0eeff', fontFamily: 'monospace', lineHeight: 1.5 }}>
                31.1105° N
              </span>
              <span style={{ display: 'block', fontSize: '0.82rem', color: '#e0eeff', fontFamily: 'monospace' }}>
                77.9373° E
              </span>
            </div>

            {/* NISAR change */}
            <div style={{
              opacity: inView ? 1 : 0,
              transition: 'opacity 0.5s ease 0.5s',
            }}>
              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.18em', color: 'rgba(100,155,210,0.45)', textTransform: 'uppercase', marginBottom: '6px' }}>
                NISAR Change
              </span>
              <span style={{ display: 'block', fontSize: '0.82rem', color: '#e0eeff', fontFamily: 'monospace', lineHeight: 1.5 }}>
                0.665 → 0.219
              </span>
              <span style={{ display: 'block', fontSize: '0.68rem', color: 'rgba(24,183,201,0.5)', fontFamily: 'monospace' }}>
                Δ −0.446
              </span>
            </div>

            {/* Terrain */}
            <div style={{
              opacity: inView ? 1 : 0,
              transition: 'opacity 0.5s ease 0.58s',
            }}>
              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.18em', color: 'rgba(100,155,210,0.45)', textTransform: 'uppercase', marginBottom: '6px' }}>
                Terrain
              </span>
              <span style={{ display: 'block', fontSize: '0.82rem', color: '#e0eeff', fontFamily: 'monospace', lineHeight: 1.5 }}>
                2,794 m elev.
              </span>
              <span style={{ display: 'block', fontSize: '0.68rem', color: 'rgba(79,175,131,0.55)', fontFamily: 'monospace' }}>
                40.8° slope
              </span>
            </div>

            {/* Evidence collected */}
            <div style={{
              opacity: inView ? 1 : 0,
              transition: 'opacity 0.5s ease 0.65s',
            }}>
              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.18em', color: 'rgba(100,155,210,0.45)', textTransform: 'uppercase', marginBottom: '6px' }}>
                Evidence
              </span>
              <div>
                {['NISAR', 'TERRAIN', 'RAINFALL', 'LAND COVER'].map((l, i) =>
                  checkRow(l, `${0.7 + i * 0.08}s`),
                )}
              </div>
            </div>
          </div>

          {/* Status bar — last to appear */}
          <div style={{
            borderTop: '1px solid rgba(255,255,255,0.07)',
            paddingTop: '18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '8px',
            opacity: inView ? 1 : 0,
            transition: 'opacity 0.6s ease 1.0s',
          }}>
            <div>
              <span style={{ display: 'block', fontSize: '0.58rem', letterSpacing: '0.16em', color: 'rgba(100,155,210,0.4)', textTransform: 'uppercase', marginBottom: '4px' }}>
                Status
              </span>
              <span style={{ fontSize: '0.78rem', color: '#c8dff4', fontWeight: 500 }}>
                Evidence collected
              </span>
            </div>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '7px',
              padding: '6px 14px',
              borderRadius: '999px',
              border: '1px solid rgba(24,183,201,0.25)',
              background: 'rgba(24,183,201,0.06)',
            }}>
              {/* Pulsing dot */}
              <span style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: '#18B7C9',
                display: 'inline-block',
                boxShadow: '0 0 8px #18B7C9',
                animation: 'ew-fp-pulse 2s ease-in-out infinite',
              }} />
              <style>{`@keyframes ew-fp-pulse{0%,100%{opacity:1}50%{opacity:0.35}}`}</style>
              <span style={{
                fontSize: '0.65rem',
                letterSpacing: '0.12em',
                color: '#18B7C9',
                fontWeight: 600,
                textTransform: 'uppercase',
              }}>
                Cause under investigation
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// BACKGROUND
// ─────────────────────────────────────────────────────────────────────────────

function Background() {
  return (
    <svg
      aria-hidden="true"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 0, pointerEvents: 'none' }}
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <radialGradient id="ewa-bg1" cx="15%" cy="20%" r="40%" gradientUnits="objectBoundingBox">
          <stop offset="0%"  stopColor="#0a2040" stopOpacity="0.5"/>
          <stop offset="100%" stopColor="#04090f" stopOpacity="0"/>
        </radialGradient>
        <radialGradient id="ewa-bg2" cx="85%" cy="75%" r="38%" gradientUnits="objectBoundingBox">
          <stop offset="0%"  stopColor="#061828" stopOpacity="0.45"/>
          <stop offset="100%" stopColor="#04090f" stopOpacity="0"/>
        </radialGradient>
        <style>{`
          @keyframes ewa-arc { 0%,100%{opacity:0.06} 50%{opacity:0.14} }
          @keyframes ewa-star { 0%,100%{opacity:0.55} 50%{opacity:0.08} }
        `}</style>
      </defs>

      <rect x="0" y="0" width="100%" height="100%" fill="url(#ewa-bg1)"/>
      <rect x="0" y="0" width="100%" height="100%" fill="url(#ewa-bg2)"/>

      {/* Subtle orbital arcs */}
      <path d="M -100 600 Q 400 200 1000 400" fill="none" stroke="rgba(24,183,201,0.07)" strokeWidth="1"
        style={{ animation: 'ewa-arc 7s ease-in-out infinite' }}/>
      <path d="M 500 1200 Q 900 700 1500 500" fill="none" stroke="rgba(79,175,131,0.05)" strokeWidth="1"
        style={{ animation: 'ewa-arc 9s ease-in-out 2s infinite' }}/>

      {/* Sparse stars */}
      {[
        [60,80,0.5],[180,40,0.4],[340,120,0.6],[520,60,0.5],[700,90,0.4],
        [880,50,0.5],[1060,80,0.4],[1240,40,0.6],[1400,70,0.5],[1440,200,0.4],
        [100,300,0.4],[420,260,0.5],[760,280,0.4],[1100,300,0.5],[1380,260,0.4],
      ].map(([cx, cy, r], i) => (
        <circle key={i} cx={cx} cy={cy} r={r} fill="#e0eeff"
          style={{ animation: `ewa-star ${2.5 + (i % 4) * 0.8}s ease-in-out ${(i % 3) * 0.6}s infinite` }}/>
      ))}
    </svg>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN EXPORT
// ─────────────────────────────────────────────────────────────────────────────

export function EarthWhisperApproachSection() {
  const { ref: titleRef, inView: titleInView } = useInView(0.2)

  return (
    <section
      style={{
        position: 'relative',
        width: '100%',
        background: 'linear-gradient(180deg, #07111f 0%, #050d1a 50%, #04090f 100%)',
        overflow: 'hidden',
        paddingTop: '96px',
        paddingBottom: '112px',
      }}
      aria-labelledby="ewa-main-heading"
    >
      <Background />

      <div style={{
        position: 'relative',
        zIndex: 2,
        maxWidth: '1080px',
        margin: '0 auto',
        padding: '0 32px',
      }}>

        {/* ── Section title ── */}
        <div
          ref={titleRef}
          style={{
            textAlign: 'center',
            marginBottom: '80px',
            opacity: titleInView ? 1 : 0,
            transform: titleInView ? 'translateY(0)' : 'translateY(24px)',
            transition: 'opacity 0.7s ease, transform 0.7s ease',
          }}
        >
          <h2
            id="ewa-main-heading"
            style={{
              fontSize: 'clamp(2rem, 4.5vw, 3.4rem)',
              fontWeight: 800,
              color: '#f0f6ff',
              letterSpacing: '-0.02em',
              textTransform: 'uppercase',
              lineHeight: 1.0,
              margin: '0 0 18px 0',
            }}
          >
            From Signal to{' '}
            <span style={{ color: '#18B7C9', textShadow: '0 0 40px rgba(24,183,201,0.4)' }}>
              Understanding
            </span>
          </h2>
          <p style={{
            fontSize: 'clamp(0.9rem, 1.5vw, 1.05rem)',
            color: 'rgba(180,210,240,0.65)',
            maxWidth: '600px',
            margin: '0 auto 14px',
            lineHeight: 1.6,
            fontStyle: 'italic',
          }}>
            Earth changes are easy to see after the event. Earth Whisper investigates
            the signals before the story is obvious.
          </p>
          <p style={{
            fontSize: '0.85rem',
            color: 'rgba(130,165,200,0.5)',
            maxWidth: '540px',
            margin: '0 auto',
            lineHeight: 1.75,
          }}>
            Surface changes can appear as subtle patterns in satellite observations.
            Earth Whisper brings those observations together with independent environmental
            evidence to investigate what changed, where it changed, and which explanations
            are consistent with the evidence.
          </p>
        </div>

        {/* ── Part 1: Challenge ── */}
        <ChallengeBlock />

        <Divider glow />

        {/* ── Part 2: Pipeline ── */}
        <PipelineBlock />

        <Divider />

        {/* ── Part 3: Evidence layers ── */}
        <EvidenceBlock />

        <Divider glow />

        {/* ── Part 4: Fingerprint ── */}
        <FingerprintBlock />

      </div>
    </section>
  )
}
