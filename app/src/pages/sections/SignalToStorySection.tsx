import { useEffect, useRef, useState } from 'react'

// ─────────────────────────────────────────────────────────────────────────────
// INTERSECTION HOOK
// ─────────────────────────────────────────────────────────────────────────────
function useInView(threshold = 0.25) {
  const ref = useRef<HTMLElement>(null)
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { setInView(true); obs.disconnect() } },
      { threshold },
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [threshold])
  return { ref, inView }
}

// ─────────────────────────────────────────────────────────────────────────────
// BLOCK VISUALS
// ─────────────────────────────────────────────────────────────────────────────

function DetectVisual({ active }: { active: boolean }) {
  return (
    <svg viewBox="0 0 120 100" width="120" height="100" aria-hidden="true">
      <defs>
        <style>{`
          @keyframes sts-ring { 0%{opacity:0.7;r:8} 100%{opacity:0;r:26} }
          @keyframes sts-grid { 0%,100%{opacity:0.07} 50%{opacity:0.14} }
        `}</style>
      </defs>
      {[20,40,60,80,100].map(x => (
        <line key={`v${x}`} x1={x} y1={0} x2={x} y2={100} stroke="rgba(24,183,201,0.1)" strokeWidth="0.5"
          style={{ animation: 'sts-grid 3s ease-in-out infinite' }} />
      ))}
      {[20,40,60,80].map(y => (
        <line key={`h${y}`} x1={0} y1={y} x2={120} y2={y} stroke="rgba(24,183,201,0.1)" strokeWidth="0.5"
          style={{ animation: 'sts-grid 3s ease-in-out infinite' }} />
      ))}
      <rect x="14" y="22" width="28" height="16" rx="2" fill="rgba(24,183,201,0.08)" stroke="rgba(24,183,201,0.15)" strokeWidth="0.5"/>
      <rect x="52" y="30" width="32" height="20" rx="2" fill="rgba(24,183,201,0.06)" stroke="rgba(24,183,201,0.1)" strokeWidth="0.5"/>
      <rect x="28" y="54" width="24" height="18" rx="2" fill="rgba(24,183,201,0.06)" stroke="rgba(24,183,201,0.1)" strokeWidth="0.5"/>
      <rect x="68" y="52" width="30" height="22" rx="3"
        fill={active ? 'rgba(24,183,201,0.18)' : 'rgba(24,183,201,0.04)'}
        stroke={active ? 'rgba(24,183,201,0.7)' : 'rgba(24,183,201,0.15)'}
        strokeWidth="1"
        style={{ transition: 'fill 0.6s ease, stroke 0.6s ease' }}
      />
      {active && [0, 0.5, 1.0].map(d => (
        <circle key={d} cx="83" cy="63" r="8" fill="none" stroke="rgba(24,183,201,0.5)" strokeWidth="0.8"
          style={{ animation: `sts-ring 2s ease-out ${d}s infinite` }} />
      ))}
      <circle cx="83" cy="63" r="3" fill={active ? '#18B7C9' : 'rgba(24,183,201,0.2)'}
        style={{ transition: 'fill 0.4s ease', filter: active ? 'drop-shadow(0 0 4px #18B7C9)' : 'none' }} />
      <text x="6" y="10" fontSize="5.5" fill="rgba(24,183,201,0.4)" letterSpacing="0.8" fontFamily="monospace">NISAR · SAR</text>
      {active && <text x="60" y="86" fontSize="5" fill="rgba(24,183,201,0.55)" letterSpacing="0.5" fontFamily="monospace">ΔCOHERENCE</text>}
    </svg>
  )
}

function InvestigateVisual({ active }: { active: boolean }) {
  const icons = [
    { label: 'TERRAIN',    y: 16, delay: '0s',   color: '#4FAF83', path: 'M6 22 L12 8 L18 22 Z' },
    { label: 'RAINFALL',   y: 44, delay: '0.2s', color: '#7EB8E8', path: 'M12 8 Q14 12 12 16 Q10 12 12 8 M9 14 L7 20 M15 14 L17 20' },
    { label: 'LAND COVER', y: 72, delay: '0.4s', color: '#A8D5A2', path: 'M4 18 Q12 8 20 18 Q12 14 4 18 Z' },
  ]
  return (
    <svg viewBox="0 0 120 100" width="120" height="100" aria-hidden="true">
      <circle cx="60" cy="50" r="18" fill="rgba(24,183,201,0.05)"
        stroke={active ? 'rgba(24,183,201,0.25)' : 'rgba(24,183,201,0.08)'}
        strokeWidth="0.8" strokeDasharray="3 3"
        style={{ transition: 'stroke 0.6s ease' }}
      />
      <circle cx="60" cy="50" r="3" fill={active ? '#18B7C9' : 'rgba(24,183,201,0.2)'}
        style={{ transition: 'fill 0.4s ease', filter: active ? 'drop-shadow(0 0 4px #18B7C9)' : 'none' }}
      />
      {icons.map(({ label, y, delay, color, path }) => (
        <g key={label} style={{ opacity: active ? 1 : 0, transition: `opacity 0.5s ease ${delay}` }}>
          <line x1="60" y1="50" x2="26" y2={y + 8} stroke={`${color}44`} strokeWidth="0.6" strokeDasharray="2 2"/>
          <rect x="4" y={y - 2} width="42" height="20" rx="3" fill={`${color}0d`} stroke={`${color}33`} strokeWidth="0.6"/>
          <g transform={`translate(7, ${y + 1})`}>
            <path d={path} stroke={color} strokeWidth="1.2" fill="none" strokeLinecap="round"/>
          </g>
          <text x="22" y={y + 12} fontSize="5.5" fill={color} opacity="0.75" letterSpacing="0.5" fontFamily="monospace">{label}</text>
        </g>
      ))}
      <rect x="94" y="30" width="22" height="40" rx="3"
        fill="rgba(79,175,131,0.06)" stroke="rgba(79,175,131,0.2)" strokeWidth="0.6"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease 0.6s' }}
      />
      <text x="97" y="52" fontSize="4.5" fill="rgba(79,175,131,0.6)" letterSpacing="0.3" fontFamily="monospace"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease 0.7s' }}>CLUES</text>
      <text x="97" y="60" fontSize="4.5" fill="rgba(79,175,131,0.6)" letterSpacing="0.3" fontFamily="monospace"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease 0.7s' }}>ADDED</text>
    </svg>
  )
}

function UnderstandVisual({ active }: { active: boolean }) {
  const rows = ['NISAR', 'TERRAIN', 'RAINFALL', 'LAND COVER']
  return (
    <svg viewBox="0 0 120 100" width="120" height="100" aria-hidden="true">
      <defs>
        <style>{`@keyframes sts-glow { 0%,100%{opacity:0.6} 50%{opacity:1} }`}</style>
      </defs>
      <rect x="8" y="4" width="104" height="92" rx="6"
        fill="rgba(10,28,52,0.6)" stroke="rgba(24,183,201,0.25)" strokeWidth="0.8"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease' }}
      />
      <rect x="8" y="4" width="104" height="14" rx="6" fill="rgba(24,183,201,0.08)"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease 0.1s' }}
      />
      <text x="14" y="13" fontSize="5" fill="#18B7C9" letterSpacing="0.6" fontFamily="monospace"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease 0.15s' }}>EARTH EVENT FINGERPRINT</text>
      <text x="14" y="30" fontSize="4.8" fill="rgba(100,155,210,0.4)" letterSpacing="0.5" fontFamily="monospace"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease 0.2s' }}>LOCATION</text>
      <text x="14" y="38" fontSize="5.5" fill="#e0eeff" letterSpacing="0.3" fontFamily="monospace"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease 0.25s' }}>31.1105°N 77.9373°E</text>
      <text x="14" y="50" fontSize="4.5" fill="rgba(100,155,210,0.4)" letterSpacing="0.5" fontFamily="monospace"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease 0.3s' }}>EVIDENCE</text>
      {rows.map((r, i) => (
        <g key={r} style={{ opacity: active ? 1 : 0, transition: `opacity 0.4s ease ${0.38 + i * 0.1}s` }}>
          <text x="14" y={60 + i * 8} fontSize="5" fill="rgba(160,195,230,0.65)" letterSpacing="0.3" fontFamily="monospace">{r}</text>
          <circle cx="100" cy={56.5 + i * 8} r="2.5" fill="#4FAF83" style={{ filter: 'drop-shadow(0 0 3px #4FAF83)' }}/>
        </g>
      ))}
      <rect x="10" y="90" width="100" height="0.6" fill="rgba(255,255,255,0.06)"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.4s ease 0.8s' }}
      />
      <circle cx="18" cy="97" r="2" fill="#18B7C9"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.4s ease 0.9s', animation: active ? 'sts-glow 2s ease-in-out infinite' : 'none', filter: 'drop-shadow(0 0 4px #18B7C9)' }}
      />
      <text x="24" y="99" fontSize="4.8" fill="#18B7C9" letterSpacing="0.4" fontFamily="monospace"
        style={{ opacity: active ? 1 : 0, transition: 'opacity 0.4s ease 0.95s' }}>CAUSE UNDER INVESTIGATION</text>
    </svg>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// ANIMATED CONNECTOR
// ─────────────────────────────────────────────────────────────────────────────
function Connector({ active, delay }: { active: boolean; delay: string }) {
  return (
    <div style={{ display:'flex', alignItems:'center', flexShrink:0, gap:'0', width:'80px' }} aria-hidden="true">
      <div style={{ flex:1, height:'1px', background:'linear-gradient(90deg, rgba(24,183,201,0.15), rgba(24,183,201,0.5))', transformOrigin:'left center', transform: active ? 'scaleX(1)' : 'scaleX(0)', transition: `transform 0.8s cubic-bezier(0.4,0,0.2,1) ${delay}` }}/>
      <div style={{ width:0, height:0, borderTop:'4px solid transparent', borderBottom:'4px solid transparent', borderLeft:`6px solid ${active ? 'rgba(24,183,201,0.55)' : 'transparent'}`, flexShrink:0, transition: `border-left-color 0.3s ease ${delay}` }}/>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// GLOWING CARD — hover zooms toward viewer (scale 1.03), glow intensifies
// ─────────────────────────────────────────────────────────────────────────────
interface CardProps {
  children: React.ReactNode
  glowColor: string   // e.g. '24,183,201'
  inView: boolean
  fadeDelay: string
  style?: React.CSSProperties
}

function GlowCard({ children, glowColor, inView, fadeDelay, style }: CardProps) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      className="ew-signal-story-card"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: '260px',
        borderRadius: '14px',
        border: `1px solid rgba(${glowColor},${hovered ? '0.45' : '0.22'})`,
        background: hovered ? `rgba(${glowColor},0.04)` : 'rgba(255,255,255,0.022)',
        cursor: 'default',
        // all transitions unified — transform handles both entrance slide and hover zoom
        transition: `
          opacity 0.55s ease ${fadeDelay},
          transform 0.28s cubic-bezier(0.34,1.56,0.64,1),
          box-shadow 0.28s ease,
          border-color 0.28s ease,
          background 0.28s ease
        `,
        opacity: inView ? 1 : 0,
        // entrance slides up; once in view, hover zooms toward front
        transform: inView
          ? hovered ? 'translateY(0) scale(1.03)' : 'translateY(0) scale(1)'
          : 'translateY(22px) scale(1)',
        // glow brightens on hover
        boxShadow: inView
          ? hovered
            ? [
                `0 0 0 3px rgba(${glowColor},0.35)`,
                `0 0 32px 10px rgba(${glowColor},0.30)`,
                `0 0 72px 22px rgba(${glowColor},0.16)`,
              ].join(', ')
            : [
                `0 0 0 2px rgba(${glowColor},0.10)`,
                `0 0 20px 6px rgba(${glowColor},0.14)`,
                `0 0 48px 14px rgba(${glowColor},0.07)`,
              ].join(', ')
          : 'none',
        animation: inView ? `sts-card-glow-${glowColor.replace(/,/g,'_')} 3s ease-in-out infinite` : 'none',
        ...style,
      }}
    >
      <div className="ew-signal-story-card-content" style={{ padding: '28px 24px', display:'flex', flexDirection:'column', alignItems:'center', textAlign:'center' }}>
        {children}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN EXPORT
// ─────────────────────────────────────────────────────────────────────────────
export function SignalToStorySection() {
  const { ref, inView } = useInView(0.25)

  return (
    <section
      ref={ref as React.RefObject<HTMLElement>}
      className="ew-signal-story-section"
      style={{
        position: 'relative',
        width: '100%',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(180deg, #04090f 0%, #060e1c 50%, #07111f 100%)',
        overflow: 'hidden',
        padding: '48px 32px',
        boxSizing: 'border-box',
      }}
      aria-labelledby="sts-heading"
    >
      <style>{`
        @keyframes sts-card-glow-24_183_201 {
          0%, 100% {
            box-shadow:
              0 0 0 2px rgba(24,183,201,0.10),
              0 0 20px 6px rgba(24,183,201,0.14),
              0 0 48px 14px rgba(24,183,201,0.07);
          }
          50% {
            box-shadow:
              0 0 0 2px rgba(24,183,201,0.28),
              0 0 32px 12px rgba(24,183,201,0.26),
              0 0 72px 22px rgba(24,183,201,0.13);
          }
        }
        @keyframes sts-card-glow-79_175_131 {
          0%, 100% {
            box-shadow:
              0 0 0 2px rgba(79,175,131,0.10),
              0 0 20px 6px rgba(79,175,131,0.14),
              0 0 48px 14px rgba(79,175,131,0.07);
          }
          50% {
            box-shadow:
              0 0 0 2px rgba(79,175,131,0.28),
              0 0 32px 12px rgba(79,175,131,0.26),
              0 0 72px 22px rgba(79,175,131,0.13);
          }
        }
        @keyframes sts-pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
      `}</style>

      {/* Atmospheric background */}
      <div style={{ position:'absolute', inset:0, background:'radial-gradient(ellipse at 50% 40%, rgba(10,28,52,0.55) 0%, transparent 65%)', pointerEvents:'none' }} aria-hidden="true"/>


      <div className="ew-signal-story-inner" style={{ position:'relative', zIndex:2, width:'100%', maxWidth:'1040px', display:'flex', flexDirection:'column', alignItems:'center', gap:'0' }}>

        {/* ── Header ── */}
        <div className="ew-signal-story-header" style={{
          textAlign:'center',
          marginBottom:'52px',
          opacity: inView ? 1 : 0,
          transform: inView ? 'translateY(0)' : 'translateY(20px)',
          transition: 'opacity 0.6s ease, transform 0.6s ease',
        }}>
          <p style={{ fontSize:'0.65rem', fontWeight:700, letterSpacing:'0.26em', textTransform:'uppercase', color:'#18B7C9', opacity:0.75, margin:'0 0 14px 0' }}>
            How Earth Whisper Works
          </p>
          <h2 id="sts-heading" style={{ fontSize:'clamp(2rem, 4.5vw, 3.2rem)', fontWeight:800, color:'#f0f6ff', letterSpacing:'-0.02em', textTransform:'uppercase', lineHeight:1.0, margin:'0 0 14px 0' }}>
            From Signal{' '}
            <span style={{ color:'#18B7C9', textShadow:'0 0 36px rgba(24,183,201,0.38)' }}>to Story</span>
          </h2>
          <p style={{ fontSize:'0.9rem', color:'rgba(170,205,235,0.62)', margin:0, letterSpacing:'0.01em', fontStyle:'italic' }}>
            Detect the change. Follow the clues. Understand the event.
          </p>
        </div>

        {/* ── Three cards + connectors ── */}
        <div className="ew-signal-story-cards" style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:'0', width:'100%', flexWrap:'wrap', rowGap:'32px' }}>

          {/* CARD 01 — DETECT */}
          <GlowCard glowColor="24,183,201" inView={inView} fadeDelay="0.1s">
            <span style={{ fontSize:'0.58rem', fontWeight:700, letterSpacing:'0.2em', color:'rgba(100,155,210,0.4)', marginBottom:'14px', display:'block' }}>01</span>
            <DetectVisual active={inView} />
            <h3 style={{ fontSize:'0.72rem', fontWeight:700, letterSpacing:'0.2em', color:'#18B7C9', textTransform:'uppercase', margin:'16px 0 8px 0' }}>Detect</h3>
            <p style={{ fontSize:'0.8rem', color:'rgba(150,185,220,0.62)', lineHeight:1.6, margin:0 }}>NISAR reveals a surface change.</p>
          </GlowCard>

          <Connector active={inView} delay="0.55s" />

          {/* CARD 02 — INVESTIGATE */}
          <GlowCard glowColor="79,175,131" inView={inView} fadeDelay="0.45s">
            <span style={{ fontSize:'0.58rem', fontWeight:700, letterSpacing:'0.2em', color:'rgba(100,155,210,0.4)', marginBottom:'14px', display:'block' }}>02</span>
            <InvestigateVisual active={inView} />
            <h3 style={{ fontSize:'0.72rem', fontWeight:700, letterSpacing:'0.2em', color:'#4FAF83', textTransform:'uppercase', margin:'16px 0 8px 0' }}>Investigate</h3>
            <p style={{ fontSize:'0.8rem', color:'rgba(150,185,220,0.62)', lineHeight:1.6, margin:0 }}>Independent clues add context.</p>
          </GlowCard>

          <Connector active={inView} delay="1.1s" />

          {/* CARD 03 — UNDERSTAND */}
          <GlowCard glowColor="24,183,201" inView={inView} fadeDelay="0.8s">
            <span style={{ fontSize:'0.58rem', fontWeight:700, letterSpacing:'0.2em', color:'rgba(100,155,210,0.4)', marginBottom:'14px', display:'block' }}>03</span>
            <UnderstandVisual active={inView} />
            <h3 style={{ fontSize:'0.72rem', fontWeight:700, letterSpacing:'0.2em', color:'#18B7C9', textTransform:'uppercase', margin:'16px 0 8px 0' }}>Understand</h3>
            <p style={{ fontSize:'0.8rem', color:'rgba(150,185,220,0.62)', lineHeight:1.6, margin:0 }}>Evidence becomes an Earth Event Fingerprint.</p>
          </GlowCard>

        </div>

        {/* ── Status line ── */}
        <div style={{ marginTop:'44px', display:'inline-flex', alignItems:'center', gap:'12px', padding:'10px 22px', borderRadius:'999px', border:'1px solid rgba(24,183,201,0.2)', background:'rgba(24,183,201,0.04)', opacity: inView ? 1 : 0, transition:'opacity 0.6s ease 1.4s' }}>
          <span style={{ width:'7px', height:'7px', borderRadius:'50%', background:'#18B7C9', flexShrink:0, boxShadow:'0 0 8px #18B7C9', animation: inView ? 'sts-pulse 2.2s ease-in-out infinite' : 'none' }} aria-hidden="true"/>
          <span style={{ fontSize:'0.65rem', fontWeight:700, letterSpacing:'0.18em', textTransform:'uppercase', color:'#18B7C9' }}>Earth Event Fingerprint</span>
          <span style={{ width:'1px', height:'12px', background:'rgba(24,183,201,0.25)', flexShrink:0 }} aria-hidden="true"/>
          <span style={{ fontSize:'0.7rem', color:'rgba(160,200,235,0.55)', letterSpacing:'0.06em' }}>Evidence collected · Cause under investigation</span>
        </div>

      </div>
    </section>
  )
}
