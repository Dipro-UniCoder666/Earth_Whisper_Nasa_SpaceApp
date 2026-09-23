/**
 * A distinctive, stylized Earth-observation visual for the hero section.
 *
 * Concept: a calm, semi-realistic globe with a soft atmospheric glow,
 * two slow-rotating orbit arcs representing satellite passes, a single
 * radar sweep, a small highlighted anomaly with a pulsing ring, and two
 * restrained scientific annotations. Everything here is custom SVG —
 * no stock photography, no HUD clutter.
 */
export function HeroEarth() {
  return (
    <div className="relative mx-auto aspect-square w-full max-w-[560px] select-none" aria-hidden="true">
      <svg viewBox="0 0 560 560" width="100%" height="100%" fill="none">
        <defs>
          <radialGradient id="ew-atmosphere" cx="50%" cy="42%" r="60%">
            <stop offset="0%" stopColor="#DDF7FA" stopOpacity="0.9" />
            <stop offset="60%" stopColor="#9FD8EE" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#9FD8EE" stopOpacity="0" />
          </radialGradient>

          <radialGradient id="ew-globe" cx="38%" cy="34%" r="70%">
            <stop offset="0%" stopColor="#1E8FC4" />
            <stop offset="45%" stopColor="#0B5EA8" />
            <stop offset="100%" stopColor="#073B66" />
          </radialGradient>

          <linearGradient id="ew-sweep" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#18B7C9" stopOpacity="0" />
            <stop offset="100%" stopColor="#18B7C9" stopOpacity="0.55" />
          </linearGradient>

          <clipPath id="ew-globe-clip">
            <circle cx="280" cy="280" r="168" />
          </clipPath>
        </defs>

        {/* Atmospheric glow */}
        <circle cx="280" cy="280" r="260" fill="url(#ew-atmosphere)" />

        {/* Faint orbit rings */}
        <ellipse
          cx="280"
          cy="280"
          rx="238"
          ry="238"
          stroke="#0B5EA8"
          strokeOpacity="0.14"
          strokeWidth="1"
        />
        <ellipse
          cx="280"
          cy="280"
          rx="205"
          ry="205"
          stroke="#0B5EA8"
          strokeOpacity="0.1"
          strokeWidth="1"
        />

        {/* Rotating satellite-pass arcs */}
        <g className="ew-orbit-slow">
          <path
            d="M 90 280 A 190 190 0 0 1 470 280"
            stroke="#18B7C9"
            strokeOpacity="0.55"
            strokeWidth="1.4"
            strokeDasharray="2 10"
            strokeLinecap="round"
          />
        </g>
        <g className="ew-orbit-slow-reverse">
          <path
            d="M 130 150 A 210 210 0 0 1 430 410"
            stroke="#4FAF83"
            strokeOpacity="0.4"
            strokeWidth="1.2"
            strokeDasharray="1 9"
            strokeLinecap="round"
          />
        </g>

        {/* The globe */}
        <circle cx="280" cy="280" r="168" fill="url(#ew-globe)" />

        {/* Simplified landmass forms, softly stylized, clipped to globe */}
        <g clipPath="url(#ew-globe-clip)" opacity="0.5">
          <path
            d="M150 210c20-18 55-24 78-10 14 8 12 24 32 26 24 2 40-16 62-8 16 6 18 24 10 36-14 20-46 14-64 28-16 12-14 34-34 40-22 6-40-14-58-8-16 6-20 26-38 22-14-4-16-22-8-36 10-18 4-38 20-52z"
            fill="#0A4E88"
          />
          <path
            d="M300 340c18-10 42-6 54 8 10 12 2 28-12 34-16 6-32-4-46 2-12 6-10 20-24 22-12 2-20-10-16-22 6-16 26-32 44-44z"
            fill="#0A4E88"
          />
          <circle cx="230" cy="260" r="3.5" fill="#DDF7FA" opacity="0.6" />
          <circle cx="310" cy="230" r="2.5" fill="#DDF7FA" opacity="0.5" />
        </g>

        {/* Terminator shading for depth */}
        <circle cx="280" cy="280" r="168" fill="url(#ew-atmosphere)" opacity="0.12" />

        {/* Radar sweep across the globe */}
        <g clipPath="url(#ew-globe-clip)">
          <g className="ew-orbit-slow" style={{ transformOrigin: '280px 280px' }}>
            <rect x="280" y="112" width="168" height="168" fill="url(#ew-sweep)" opacity="0.5" />
          </g>
        </g>

        {/* Globe rim highlight */}
        <circle cx="280" cy="280" r="168" stroke="#EAF6FF" strokeOpacity="0.35" strokeWidth="1.5" />

        {/* Anomaly marker */}
        <g transform="translate(336, 232)">
          <circle r="18" fill="#18B7C9" opacity="0.18" className="ew-pulse-ring" />
          <circle r="18" fill="#18B7C9" opacity="0.18" className="ew-pulse-ring" style={{ animationDelay: '1.1s' }} />
          <circle r="5" fill="#18B7C9" />
          <circle r="5" stroke="#FFFFFF" strokeWidth="1.5" fillOpacity="0" />
        </g>

        {/* Annotation: NISAR OBSERVATION */}
        <g className="ew-drift" transform="translate(336, 232)">
          <line x1="0" y1="0" x2="46" y2="-38" stroke="#073B66" strokeOpacity="0.3" strokeWidth="1" />
          <text x="52" y="-34" fontSize="11" fontFamily="Inter, sans-serif" fontWeight="600" fill="#073B66" letterSpacing="0.02em">
            NISAR OBSERVATION
          </text>
        </g>

        {/* Annotation: CHANGE DETECTED */}
        <g className="ew-drift" style={{ animationDelay: '2.4s' }} transform="translate(336, 232)">
          <line x1="0" y1="0" x2="-38" y2="52" stroke="#073B66" strokeOpacity="0.3" strokeWidth="1" />
          <text
            x="-40"
            y="66"
            textAnchor="end"
            fontSize="11"
            fontFamily="Inter, sans-serif"
            fontWeight="600"
            fill="#0B5EA8"
            letterSpacing="0.02em"
          >
            CHANGE DETECTED
          </text>
        </g>

        {/* Small satellite observation points */}
        <circle cx="130" cy="150" r="3" fill="#4FAF83" opacity="0.7" />
        <circle cx="430" cy="410" r="3" fill="#4FAF83" opacity="0.5" />
        <circle cx="90" cy="280" r="2.5" fill="#18B7C9" opacity="0.6" />
        <circle cx="470" cy="280" r="2.5" fill="#18B7C9" opacity="0.6" />
      </svg>
    </div>
  )
}
