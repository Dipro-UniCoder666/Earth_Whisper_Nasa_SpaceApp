import { useState } from 'react'
import { Link } from 'react-router-dom'

// ── Config — contact details never rendered as visible text ───────────────────
const CONTACT = {
  gmail:    'mailto:rajdiprodas666666@gmail.com',
  whatsapp: 'https://wa.me/8801322643456',
  github:   null as string | null,
  linkedin: null as string | null,
}

const NAV_LINKS = [
  { label: 'Home',        to: '/' },
  { label: 'Investigate', to: '/investigate' },
  { label: 'Whisper Lab', to: '/science' },
  { label: 'About',       to: '/about' },
]

const DATA_SOURCES = [
  { name: 'NISAR',            credit: 'NASA / JPL' },
  { name: 'NASADEM',          credit: 'NASA' },
  { name: 'GPM IMERG',        credit: 'NASA / GPM' },
  { name: 'MODIS Land Cover', credit: 'NASA / LP DAAC' },
]

// ── Helpers ───────────────────────────────────────────────────────────────────
function ColHead({ children }: { children: React.ReactNode }) {
  return (
    <p style={{
      fontSize: '0.60rem',
      fontWeight: 700,
      letterSpacing: '0.26em',
      textTransform: 'uppercase',
      color: '#18B7C9',
      margin: '0 0 22px 0',
      opacity: 0.90,
    }}>{children}</p>
  )
}

function NavLink({ label, to }: { label: string; to: string }) {
  const [over, setOver] = useState(false)
  return (
    <Link to={to}
      onMouseEnter={() => setOver(true)}
      onMouseLeave={() => setOver(false)}
      style={{
        fontSize: '0.84rem',
        color: over ? '#c8e8f4' : 'rgba(160,200,230,0.58)',
        textDecoration: 'none',
        letterSpacing: '0.04em',
        transition: 'color 0.18s ease',
        display: 'block',
        lineHeight: 1,
      }}
    >{label}</Link>
  )
}

// ── Social icon button — icon only, no visible text ───────────────────────────
function SocialBtn({
  href, label, children,
}: { href: string | null; label: string; children: React.ReactNode }) {
  const [over, setOver] = useState(false)
  const sharedStyle: React.CSSProperties = {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    border: `1px solid rgba(24,183,201,${over ? '0.55' : '0.20'})`,
    background: over ? 'rgba(24,183,201,0.10)' : 'rgba(24,183,201,0.04)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: href ? 'pointer' : 'default',
    transition: 'border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease',
    boxShadow: over ? '0 0 14px 4px rgba(24,183,201,0.18)' : 'none',
    transform: over ? 'scale(1.10)' : 'scale(1)',
    opacity: href ? 1 : 0.38,
    textDecoration: 'none',
    flexShrink: 0,
  }
  if (href) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" aria-label={label}
        onMouseEnter={() => setOver(true)} onMouseLeave={() => setOver(false)}
        style={sharedStyle}
      >{children}</a>
    )
  }
  return (
    <span aria-label={label} title={label}
      onMouseEnter={() => setOver(true)} onMouseLeave={() => setOver(false)}
      style={sharedStyle}
    >{children}</span>
  )
}

// ── SVG Icons ─────────────────────────────────────────────────────────────────
function IconGmail() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="2" y="4" width="20" height="16" rx="2" stroke="rgba(200,230,244,0.80)" strokeWidth="1.4" fill="none"/>
      <path d="M2 7l10 7 10-7" stroke="rgba(200,230,244,0.90)" strokeWidth="1.4" fill="none" strokeLinecap="round"/>
    </svg>
  )
}
function IconWhatsApp() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="10" stroke="rgba(200,230,244,0.80)" strokeWidth="1.4"/>
      <path d="M16.7 14.9c-.3-.1-1.7-.8-1.9-.9-.3-.1-.5-.1-.7.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-.3-.2-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.6-2.1-.2-.3 0-.5.1-.6.2-.2.3-.3.5-.5.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5-.1-.2-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4C7 8.1 6.4 8.9 6.4 10.4c0 1.5 1.1 2.9 1.2 3.1.1.2 2.1 3.2 5.1 4.4.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.7-.7 2-1.4.3-.7.3-1.2.2-1.3-.1-.1-.3-.2-.6-.3z" fill="rgba(200,230,244,0.85)"/>
    </svg>
  )
}
function IconGitHub() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.49.5.09.68-.22.68-.48v-1.71c-2.78.6-3.37-1.34-3.37-1.34-.45-1.15-1.11-1.46-1.11-1.46-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.89 1.52 2.34 1.08 2.91.83.09-.65.35-1.08.63-1.33-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.02A9.56 9.56 0 0112 6.8c.85.004 1.71.11 2.51.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.37.2 2.39.1 2.64.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.85v2.74c0 .27.18.58.69.48A10.01 10.01 0 0022 12c0-5.52-4.48-10-10-10z" fill="rgba(200,230,244,0.80)"/>
    </svg>
  )
}
function IconLinkedIn() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="2" y="2" width="20" height="20" rx="4" stroke="rgba(200,230,244,0.80)" strokeWidth="1.4" fill="none"/>
      <path d="M7 10v7M7 7v.5" stroke="rgba(200,230,244,0.85)" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M11 17v-3.5c0-1.38 1.12-2.5 2.5-2.5S16 12.12 16 13.5V17" stroke="rgba(200,230,244,0.85)" strokeWidth="1.4" strokeLinecap="round"/>
      <path d="M11 10v7" stroke="rgba(200,230,244,0.85)" strokeWidth="1.4" strokeLinecap="round"/>
    </svg>
  )
}

// ── Main Footer ───────────────────────────────────────────────────────────────
export function Footer() {
  return (
    <footer
      style={{
        position: 'relative',
        width: '100%',
        background: 'linear-gradient(180deg, #040a12 0%, #030810 60%, #020609 100%)',
        overflow: 'hidden',
        boxSizing: 'border-box',
      }}
      aria-label="Site footer"
    >
      <style>{`
        @keyframes fw-orb   { 0%,100%{opacity:0.22} 50%{opacity:0.38} }
        @keyframes fw-orb2  { 0%,100%{opacity:0.12} 50%{opacity:0.22} }
        @keyframes fw-star  { 0%,100%{opacity:0.55} 50%{opacity:0.06} }
        @keyframes fw-arc   { 0%,100%{opacity:0.05} 50%{opacity:0.10} }

        @media (max-width: 900px) {
          .fw-grid  { flex-wrap: wrap !important; gap: 44px 48px !important; }
          .fw-identity { min-width: 100% !important; }
        }
        @media (max-width: 560px) {
          .fw-grid  { flex-direction: column !important; gap: 36px !important; }
          .fw-bottom-bar { flex-direction: column !important; gap: 8px !important; text-align: center !important; }
          .fw-identity { min-width: unset !important; }
        }
      `}</style>

      {/* ── Atmospheric layer ── */}
      <div style={{ position:'absolute', inset:0, pointerEvents:'none', zIndex:0 }} aria-hidden="true">
        {/* Large soft orb — bottom left */}
        <div style={{
          position:'absolute', bottom:'-100px', left:'-120px',
          width:'500px', height:'500px', borderRadius:'50%',
          background:'radial-gradient(circle, rgba(8,24,56,0.60) 0%, transparent 70%)',
          animation:'fw-orb 9s ease-in-out infinite',
        }}/>
        {/* Smaller orb — top right */}
        <div style={{
          position:'absolute', top:'-60px', right:'-80px',
          width:'340px', height:'340px', borderRadius:'50%',
          background:'radial-gradient(circle, rgba(6,18,44,0.45) 0%, transparent 70%)',
          animation:'fw-orb2 11s ease-in-out 2s infinite',
        }}/>
        {/* Faint orbital arcs */}
        <svg style={{ position:'absolute', inset:0, width:'100%', height:'100%' }}>
          <path d="M -80 300 Q 380 80 840 220 Q 1180 330 1600 140"
            fill="none" stroke="rgba(24,183,201,0.055)" strokeWidth="1"
            style={{ animation:'fw-arc 7s ease-in-out infinite' }}/>
          <path d="M 0 380 Q 420 160 900 280 Q 1240 380 1600 220"
            fill="none" stroke="rgba(24,183,201,0.035)" strokeWidth="0.8"
            style={{ animation:'fw-arc 10s ease-in-out 1.5s infinite' }}/>
          {/* Subtle radar rings behind identity */}
          <ellipse cx="160" cy="50%" rx="180" ry="60" fill="none" stroke="rgba(24,183,201,0.03)" strokeWidth="0.8"/>
          <ellipse cx="160" cy="50%" rx="280" ry="100" fill="none" stroke="rgba(24,183,201,0.02)" strokeWidth="0.6"/>
        </svg>
        {/* Stars */}
        <svg style={{ position:'absolute', inset:0, width:'100%', height:'100%' }}>
          {[
            [55,28],[185,14],[390,50],[620,12],[840,42],[1060,18],[1280,46],[1460,64],
            [120,130],[460,108],[780,138],[1040,114],[1300,132],[260,220],[700,200],[1180,228],
            [80,310],[430,290],[820,320],[1120,298],[1400,316],[200,400],[600,380],[1000,408],
          ].map(([cx,cy],i) => (
            <circle key={i} cx={cx} cy={cy} r={i%4===0?0.9:i%3===0?0.7:0.5} fill="#c0d8f0"
              style={{ animation:`fw-star ${2.0+(i%6)*0.55}s ease-in-out ${(i%5)*0.38}s infinite` }}/>
          ))}
        </svg>
      </div>

      {/* ── Top edge line ── */}
      <div style={{
        width:'100%', height:'1px',
        background:'linear-gradient(90deg, transparent 0%, rgba(24,183,201,0.22) 25%, rgba(24,183,201,0.22) 75%, transparent 100%)',
        position:'relative', zIndex:1,
      }}/>

      {/* ── Main content grid ── */}
      <div
        className="fw-grid"
        style={{
          position:'relative', zIndex:2,
          maxWidth:'1200px', margin:'0 auto',
          padding:'72px 48px 60px',
          display:'flex', flexDirection:'row',
          justifyContent:'space-between', alignItems:'flex-start',
          gap:'48px',
          boxSizing:'border-box',
        }}
      >

        {/* ── IDENTITY ── */}
        <div className="fw-identity" style={{ minWidth:'240px', maxWidth:'280px', flexShrink:0 }}>
          {/* Logo + name */}
          <div style={{ display:'flex', alignItems:'center', gap:'12px', marginBottom:'16px' }}>
            <img
              src="/images/LOGO_EW.svg"
              alt="Earth Whisper"
              style={{ width:'38px', height:'38px', objectFit:'contain', flexShrink:0 }}
            />
            <span style={{
              fontSize:'0.95rem', fontWeight:800, color:'#f0f6ff',
              letterSpacing:'0.10em', textTransform:'uppercase',
            }}>Earth Whisper</span>
          </div>
          {/* Tagline */}
          <p style={{
            fontSize:'0.82rem', color:'rgba(155,195,225,0.60)',
            lineHeight:1.7, margin:'0 0 14px 0', letterSpacing:'0.02em',
          }}>
            Turning Earth observations into<br/>understandable evidence.
          </p>
          {/* By AquaByte */}
          <p style={{
            fontSize:'0.65rem', fontWeight:700,
            color:'rgba(24,183,201,0.60)',
            letterSpacing:'0.18em', textTransform:'uppercase',
            margin:0,
          }}>by AquaByte</p>
        </div>

        {/* ── EXPLORE ── */}
        <div style={{ flexShrink:0 }}>
          <ColHead>Explore</ColHead>
          <div style={{ display:'flex', flexDirection:'column', gap:'14px' }}>
            {NAV_LINKS.map(n => <NavLink key={n.label} label={n.label} to={n.to} />)}
          </div>
        </div>

        {/* ── DATA SOURCES ── */}
        <div style={{ flexShrink:0 }}>
          <ColHead>Data Sources</ColHead>
          <div style={{ display:'flex', flexDirection:'column', gap:'14px' }}>
            {DATA_SOURCES.map(ds => (
              <div key={ds.name}>
                <p style={{ fontSize:'0.82rem', color:'rgba(200,225,245,0.75)', letterSpacing:'0.04em', margin:'0 0 2px 0', fontWeight:500 }}>
                  {ds.name}
                </p>
                <p style={{ fontSize:'0.68rem', color:'rgba(24,183,201,0.50)', letterSpacing:'0.06em', margin:0 }}>
                  {ds.credit}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* ── CONNECT — icons only, no visible contact text ── */}
        <div style={{ flexShrink:0 }}>
          <ColHead>Connect</ColHead>
          {/* Row 1 */}
          <div style={{ display:'flex', gap:'12px', marginBottom:'12px' }}>
            <SocialBtn href={CONTACT.gmail} label="Send an email">
              <IconGmail />
            </SocialBtn>
            <SocialBtn href={CONTACT.whatsapp} label="Chat on WhatsApp">
              <IconWhatsApp />
            </SocialBtn>
          </div>
          {/* Row 2 */}
          <div style={{ display:'flex', gap:'12px' }}>
            <SocialBtn href={CONTACT.github} label="GitHub (coming soon)">
              <IconGitHub />
            </SocialBtn>
            <SocialBtn href={CONTACT.linkedin} label="LinkedIn (coming soon)">
              <IconLinkedIn />
            </SocialBtn>
          </div>
        </div>

      </div>

      {/* ── Bottom bar ── */}
      <div style={{ position:'relative', zIndex:2, width:'100%' }}>
        {/* Divider */}
        <div style={{
          height:'1px',
          background:'linear-gradient(90deg, transparent 0%, rgba(24,183,201,0.10) 20%, rgba(24,183,201,0.10) 80%, transparent 100%)',
          margin:'0 48px',
        }}/>
        <div
          className="fw-bottom-bar"
          style={{
            maxWidth:'1200px', margin:'0 auto',
            padding:'20px 48px',
            display:'flex', flexDirection:'row',
            alignItems:'center', justifyContent:'space-between',
            boxSizing:'border-box',
          }}
        >
          <span style={{ fontSize:'0.70rem', color:'rgba(120,160,200,0.40)', letterSpacing:'0.06em' }}>
            © 2026 AquaByte — Earth Whisper
          </span>
          <span style={{ fontSize:'0.66rem', fontWeight:600, color:'rgba(24,183,201,0.32)', letterSpacing:'0.14em', textTransform:'uppercase' }}>
            NASA Space Apps Challenge 2026
          </span>
        </div>
      </div>

    </footer>
  )
}
