import { useState } from 'react'

// ── Team data ─────────────────────────────────────────────────────────────────
const TEAM = [
  {
    name: 'Shakil Ahmed',
    role: 'QA Lead & Data Coordinator',
    image: '/images/Shakil_Ahmed_Data_Analysis.jpeg',
    featured: false,
    imageScale: '145%',
    imageTranslate: '-20px, -4px',
    gmail: null,
    whatsapp: null,
  },
  {
    name: 'Dipro Das',
    role: 'Project Architect & Full-Stack Developer',
    image: '/images/Team-Leader_Dipro_Das_Full_stack_developed.jpeg',
    featured: true,
    imageScale: '100%',
    imageTranslate: '0px, 0px',
    gmail: 'mailto:rajdiprodas666666@gmail.com',
    whatsapp: 'https://wa.me/8801322643456',
  },
  {
    name: 'Jerin Tasnim',
    role: 'Media & Communications Lead',
    image: '/images/Jerin_Tasnim_Story.jpeg',
    featured: false,
    imageScale: '170%',
    imageTranslate: '-32px, -14px',
    gmail: null,
    whatsapp: null,
  },
  {
    name: 'Devjyoti Dey Mugdho',
    role: 'Earth Science & Geospatial Research Contributor',
    // Placeholder portrait - the real photo will be added later.
    image: '/images/team_placeholder.svg',
    featured: false,
    imageScale: '100%',
    imageTranslate: '0px, 0px',
    gmail: null,
    whatsapp: null,
  },
] as const

// ── Gmail SVG icon ────────────────────────────────────────────────────────────
function GmailIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="2" y="4" width="20" height="16" rx="2" fill="none" stroke="rgba(24,183,201,0.75)" strokeWidth="1.2"/>
      <path d="M2 6l10 7 10-7" stroke="rgba(24,183,201,0.90)" strokeWidth="1.2" fill="none" strokeLinecap="round"/>
    </svg>
  )
}

// ── WhatsApp SVG icon ─────────────────────────────────────────────────────────
function WhatsAppIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="10" fill="none" stroke="rgba(24,183,201,0.75)" strokeWidth="1.2"/>
      <path
        d="M16.7 14.9c-.3-.1-1.7-.8-1.9-.9-.3-.1-.5-.1-.7.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-.3-.2-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.6-2.1-.2-.3 0-.5.1-.6.2-.2.3-.3.5-.5.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5-.1-.2-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4C7 8.1 6.4 8.9 6.4 10.4c0 1.5 1.1 2.9 1.2 3.1.1.2 2.1 3.2 5.1 4.4.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.7-.7 2-1.4.3-.7.3-1.2.2-1.3-.1-.1-.3-.2-.6-.3z"
        fill="rgba(24,183,201,0.90)"
      />
    </svg>
  )
}

// ── Contact icon button ───────────────────────────────────────────────────────
function ContactIcon({
  href,
  label,
  children,
}: {
  href: string | null
  label: string
  children: React.ReactNode
}) {
  const [over, setOver] = useState(false)

  const props: React.HTMLAttributes<HTMLElement> & { href?: string; target?: string; rel?: string } = {
    onMouseEnter: () => setOver(true),
    onMouseLeave: () => setOver(false),
    'aria-label': label,
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '32px',
      height: '32px',
      borderRadius: '50%',
      border: `1px solid rgba(24,183,201,${over ? '0.65' : '0.35'})`,
      background: over ? 'rgba(24,183,201,0.16)' : 'rgba(24,183,201,0.07)',
      cursor: href ? 'pointer' : 'default',
      transition: 'border-color 0.2s ease, background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease',
      transform: over ? 'scale(1.14)' : 'scale(1)',
      boxShadow: over ? '0 0 10px rgba(24,183,201,0.30)' : '0 0 6px rgba(24,183,201,0.10)',
      opacity: 1,
      textDecoration: 'none',
      flexShrink: 0,
    },
  }

  if (href) {
    props.href = href
    props.target = '_blank'
    props.rel = 'noopener noreferrer'
  }

  return href
    ? <a {...props}>{children}</a>
    : <span {...props}>{children}</span>
}

// ── Single card ───────────────────────────────────────────────────────────────
function TeamCard({
  name,
  role,
  image,
  featured,
  imageScale,
  imageTranslate,
  gmail,
  whatsapp,
}: {
  name: string
  role: string
  image: string
  featured: boolean
  imageScale: string
  imageTranslate: string
  gmail: string | null
  whatsapp: string | null
}) {
  const [hovered, setHovered] = useState(false)

  // Same glow intensity for all cards
  const glowBase = '0 0 0 1.5px rgba(24,183,201,0.28), 0 0 24px 6px rgba(24,183,201,0.14), 0 0 56px 16px rgba(24,183,201,0.07)'
  const glowHover = '0 0 0 2px rgba(24,183,201,0.55), 0 0 36px 12px rgba(24,183,201,0.30), 0 0 80px 24px rgba(24,183,201,0.15)'

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="ew-team-card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '36px 28px 28px',
        borderRadius: '18px',
        border: hovered
          ? '1px solid rgba(24,183,201,0.55)'
          : `1px solid rgba(24,183,201,${featured ? '0.30' : '0.22'})`,
        background: hovered
          ? 'rgba(24,183,201,0.06)'
          : 'rgba(24,183,201,0.025)',
        boxShadow: hovered ? glowHover : glowBase,
        transform: hovered ? 'translateY(-6px) scale(1.03)' : 'translateY(0) scale(1)',
        transition: 'transform 0.26s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.26s ease, border-color 0.26s ease, background 0.26s ease',
        cursor: 'default',
        width: '100%',
        maxWidth: '280px',
        boxSizing: 'border-box',
      }}
    >
      {/* ── Circular profile image ── */}
      <div
        className="ew-team-photo"
        style={{
          width: '110px',
          height: '110px',
          borderRadius: '50%',
          overflow: 'hidden',
          border: hovered
            ? '2px solid rgba(24,183,201,0.60)'
            : '2px solid rgba(24,183,201,0.35)',
          boxShadow: hovered
            ? '0 0 0 4px rgba(24,183,201,0.14), 0 0 18px rgba(24,183,201,0.20)'
            : '0 0 0 3px rgba(24,183,201,0.08)',
          transform: hovered ? 'scale(1.06)' : 'scale(1)',
          transition: 'transform 0.26s cubic-bezier(0.34,1.56,0.64,1), border-color 0.26s ease, box-shadow 0.26s ease',
          flexShrink: 0,
          marginBottom: '22px',
        }}
      >
        <img
          src={image}
          alt={name}
          style={{
            width: imageScale,
            height: imageScale,
            objectFit: 'cover',
            display: 'block',
            maxWidth: 'none',
            transform: `translate(${imageTranslate})`,
            transformOrigin: 'center center',
          }}
        />
      </div>

      {/* ── Name ── */}
      <p className="ew-team-name" style={{
        margin: '0 0 8px 0',
        fontSize: '1.05rem',
        fontWeight: 700,
        color: '#f0f6ff',
        letterSpacing: '0.02em',
        textAlign: 'center',
        lineHeight: 1.2,
      }}>
        {name}
      </p>

      {/* ── Role ── */}
      <p className="ew-team-role" style={{
        margin: '0 0 20px 0',
        fontSize: '0.75rem',
        fontWeight: 500,
        color: 'rgba(24,183,201,0.85)',
        letterSpacing: '0.06em',
        textAlign: 'center',
        lineHeight: 1.5,
      }}>
        {role}
      </p>

      {/* ── Contact icons ── */}
      <div className="ew-team-icons" style={{ display: 'flex', gap: '10px', alignItems: 'center', justifyContent: 'center' }}>
        <ContactIcon href={gmail} label={gmail ? `Email ${name}` : `Email ${name} (coming soon)`}>
          <GmailIcon size={16} />
        </ContactIcon>
        <ContactIcon href={whatsapp} label={whatsapp ? `WhatsApp ${name}` : `WhatsApp ${name} (coming soon)`}>
          <WhatsAppIcon size={16} />
        </ContactIcon>
      </div>
    </div>
  )
}

// ── Main export ───────────────────────────────────────────────────────────────
export function TeamSection() {
  return (
    <section
      className="ew-team-section"
      style={{
        position: 'relative',
        width: '100%',
        background: 'linear-gradient(180deg, #07111f 0%, #060e1c 50%, #04090f 100%)',
        overflow: 'hidden',
        padding: '80px 32px 90px',
        boxSizing: 'border-box',
        isolation: 'isolate',
      }}
      aria-labelledby="team-heading"
    >
      <style>{`
        @keyframes team-bg-pulse { 0%,100%{opacity:0.5} 50%{opacity:0.8} }
        @media (max-width: 768px) {
          .team-cards-row { flex-direction: column !important; align-items: center !important; }
        }
      `}</style>

      {/* Soft radial background glow */}
      <div style={{ position:'absolute', inset:0, background:'radial-gradient(ellipse at 50% 60%, rgba(10,28,52,0.6) 0%, transparent 70%)', pointerEvents:'none', animation:'team-bg-pulse 6s ease-in-out infinite' }} aria-hidden="true" />


      <div style={{ position:'relative', zIndex:2, maxWidth:'960px', margin:'0 auto', display:'flex', flexDirection:'column', alignItems:'center' }}>

        <h2 id="team-heading" style={{ fontSize:'clamp(1.8rem, 4vw, 2.8rem)', fontWeight:800, color:'#f0f6ff', letterSpacing:'-0.01em', textTransform:'uppercase', textAlign:'center', margin:'0 0 56px 0', lineHeight:1.0 }}>
          Meet the{' '}
          <span style={{ color:'#18B7C9', textShadow:'0 0 32px rgba(24,183,201,0.40)' }}>AquaByte Team</span>
        </h2>

        <div className="team-cards-row" style={{ display:'flex', flexDirection:'row', alignItems:'stretch', justifyContent:'center', gap:'24px', width:'100%' }}>
          {TEAM.map((member) => (
            <TeamCard key={member.name} {...member} />
          ))}
        </div>

      </div>
    </section>
  )
}
