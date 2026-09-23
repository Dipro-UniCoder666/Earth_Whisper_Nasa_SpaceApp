export function AboutPage() {
  const S = {
    eyebrow: {
      fontSize: '0.72rem', fontWeight: 700 as const, letterSpacing: '0.22em',
      textTransform: 'uppercase' as const, color: '#18B7C9', marginBottom: '16px', opacity: 0.85,
    },
    h1: {
      fontSize: 'clamp(2rem, 4vw, 3rem)', fontWeight: 800 as const, color: '#f0f6ff',
      letterSpacing: '-0.02em', lineHeight: 1.1, margin: '0 0 16px 0', textTransform: 'uppercase' as const,
    },
    lead: {
      fontSize: '1.05rem', color: 'rgba(160,200,230,0.75)', lineHeight: 1.7,
      maxWidth: '600px', marginBottom: '60px',
    },
    h2: {
      fontSize: '1rem', fontWeight: 700 as const, color: '#f0f6ff',
      margin: '0 0 12px 0', letterSpacing: '0.04em', textTransform: 'uppercase' as const,
    },
    body: { fontSize: '0.9rem', color: 'rgba(160,200,230,0.72)', lineHeight: 1.7, margin: '0 0 10px 0' },
    divider: { border: 'none', borderTop: '1px solid rgba(24,183,201,0.10)', margin: '40px 0' },
    section: {
      padding: '28px 32px', borderRadius: '14px',
      border: '1px solid rgba(24,183,201,0.15)',
      background: 'rgba(24,183,201,0.03)',
      marginBottom: '20px',
    },
    disclaimer: {
      padding: '16px 20px', borderRadius: '10px',
      border: '1px dashed rgba(24,183,201,0.22)',
      background: 'rgba(24,183,201,0.04)',
      fontSize: '0.78rem', color: 'rgba(140,190,220,0.55)', lineHeight: 1.6,
    },
    link: { color: '#18B7C9', textDecoration: 'none', fontWeight: 600 as const },
  }

  return (
    <div style={{ padding: '80px 32px 120px', maxWidth: '800px', margin: '0 auto' }}>
      <p style={S.eyebrow}>About</p>
      <h1 style={S.h1}>
        Earth{' '}
        <span style={{ color: '#18B7C9', textShadow: '0 0 32px rgba(24,183,201,0.40)' }}>Whisper</span>
      </h1>
      <p style={S.lead}>
        A scientific investigation platform built around NASA-ISRO NISAR surface-change observations.
      </p>

      <div style={S.section}>
        <h2 style={S.h2}>Purpose</h2>
        <p style={S.body}>
          Earth Whisper transforms NISAR radar observations of Earth&rsquo;s changing surface into
          understandable scientific investigations. It does not simply label events. Instead it asks:
          What changed? What evidence do we have? What could explain it? What are we still uncertain about?
        </p>
        <p style={{ ...S.body, marginBottom: 0 }}>
          The experience is designed to feel like a scientific investigation — presenting observations,
          collecting independent clues, and weighing competing hypotheses with honest uncertainty.
        </p>
      </div>

      <div style={S.section}>
        <h2 style={S.h2}>AquaByte</h2>
        <p style={{ ...S.body, marginBottom: 0 }}>
          Earth Whisper was created by AquaByte for the NASA Space Apps Challenge 2026. The team built
          the scientific processing pipeline, evidence engine, and investigation interface around real
          NISAR prototype data.
        </p>
      </div>

      <div style={S.section}>
        <h2 style={S.h2}>NASA-ISRO NISAR Mission</h2>
        <p style={S.body}>
          NISAR (NASA-ISRO Synthetic Aperture Radar) is a joint Earth-observation satellite mission
          operated by NASA and the Indian Space Research Organisation. It provides high-resolution
          radar measurements of Earth&rsquo;s surface, enabling detection of subtle changes in terrain,
          vegetation, ice, and more — even through clouds and at night.
        </p>
        <p style={{ ...S.body, marginBottom: 0 }}>
          Earth Whisper uses NISAR GUNW coherence products to identify regions where the radar
          signal has changed significantly between acquisitions.
        </p>
      </div>

      <div style={S.section}>
        <h2 style={S.h2}>NASA Space Apps Challenge 2026</h2>
        <p style={S.body}>
          Earth Whisper was built for the{' '}
          <strong style={{ color: '#f0f6ff' }}>&ldquo;Dancing with the SARs&rdquo;</strong>{' '}
          challenge at NASA Space Apps 2026, which asks teams to use NISAR radar observations
          to track and visualise changes on Earth&rsquo;s surface.
        </p>
        <a
          href="https://www.spaceappschallenge.org/"
          target="_blank"
          rel="noreferrer"
          style={S.link}
        >
          Visit NASA Space Apps Challenge ↗
        </a>
      </div>

      <div style={S.disclaimer}>
        Earth Whisper is a submission for the NASA Space Apps Challenge and is not an official NASA product.
        All NISAR data shown is demonstration data from the AquaByte QGIS prototype workspace.
      </div>
    </div>
  )
}
