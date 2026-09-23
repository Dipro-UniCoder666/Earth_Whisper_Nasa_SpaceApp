export function SciencePage() {
  return (
    <div style={{ padding: '80px 32px 120px', maxWidth: '800px', margin: '0 auto' }}>
      <p style={{
        fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.22em',
        textTransform: 'uppercase', color: '#18B7C9', marginBottom: '16px', opacity: 0.85,
      }}>
        Science
      </p>
      <h1 style={{
        fontSize: 'clamp(2rem, 4vw, 3rem)', fontWeight: 800, color: '#f0f6ff',
        letterSpacing: '-0.02em', lineHeight: 1.1, margin: '0 0 24px 0',
        textTransform: 'uppercase',
      }}>
        The Science Behind <span style={{ color: '#18B7C9', textShadow: '0 0 32px rgba(24,183,201,0.40)' }}>Earth Whisper</span>
      </h1>
      <p style={{
        fontSize: '1.05rem', color: 'rgba(160,200,230,0.75)', lineHeight: 1.7,
        maxWidth: '600px', marginBottom: '48px',
      }}>
        This section will explain the NISAR coherence methodology, evidence engine, and
        investigation workflow. Coming in a future update.
      </p>

      {/* Placeholder cards */}
      {[
        { title: 'NISAR Coherence Methodology', body: 'How the radar signal changes between acquisitions reveal surface displacement, vegetation shifts, and structural deformation.' },
        { title: 'Evidence Engine', body: 'Six independent data layers — elevation, rainfall, seismicity, land cover, geology and InSAR — are cross-referenced to produce a ranked evidence board.' },
        { title: 'Investigation Workflow', body: 'From raw GUNW products to an Earth Event Fingerprint: the complete processing pipeline from signal to story.' },
      ].map((card) => (
        <div key={card.title} style={{
          marginBottom: '20px', padding: '28px 32px',
          borderRadius: '14px',
          border: '1px solid rgba(24,183,201,0.18)',
          background: 'rgba(24,183,201,0.04)',
        }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#f0f6ff', margin: '0 0 10px 0', letterSpacing: '0.01em' }}>
            {card.title}
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'rgba(160,200,230,0.68)', lineHeight: 1.65, margin: 0 }}>
            {card.body}
          </p>
        </div>
      ))}
    </div>
  )
}
