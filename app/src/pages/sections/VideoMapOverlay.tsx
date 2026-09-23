import { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, Marker, Circle, ZoomControl } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const LAT = 31.1105
const LNG = 77.9373
const POSITION: [number, number] = [LAT, LNG]

const investigationIcon = L.divIcon({
  className: 'ew-overlay-marker',
  html: `
    <svg width="14" height="14" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="15" cy="15" r="9" fill="#18B7C9" stroke="#FFFFFF" stroke-width="2.5"/>
      <circle cx="15" cy="15" r="13" fill="#18B7C9" fill-opacity="0.18"/>
    </svg>
  `,
  iconSize: [14, 14],
  iconAnchor: [7, 7],
})

export function VideoMapOverlay() {
  const containerRef = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)
  const [settled, setSettled] = useState(false)

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); obs.disconnect() } },
      { threshold: 0.15 },
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  useEffect(() => {
    if (!visible) return
    const t = setTimeout(() => setSettled(true), 900)
    return () => clearTimeout(t)
  }, [visible])

  return (
    <>
      <style>{`
        @keyframes ew-map-rise {
          from { opacity: 0; transform: perspective(600px) rotateX(4deg) rotateY(-2deg) translateY(8px); }
          to   { opacity: 1; transform: perspective(600px) rotateX(4deg) rotateY(-2deg) translateY(0px); }
        }
        .ew-map-overlay-settled {
          transform: perspective(600px) rotateX(4deg) rotateY(-2deg) !important;
          opacity: 1 !important;
        }
        .ew-map-overlay .leaflet-tile {
          filter: brightness(0.60) saturate(0.65) hue-rotate(180deg) invert(1)
                  hue-rotate(180deg) saturate(0.55) brightness(0.55);
        }
        .ew-map-overlay .leaflet-control-attribution { display: none; }

        /* Zoom control — top-left, tiny */
        .ew-map-overlay .leaflet-top.leaflet-left {
          top: 3px !important;
          left: 3px !important;
        }
        .ew-map-overlay .leaflet-control-zoom {
          border: none !important;
          margin: 0 !important;
        }
        .ew-map-overlay .leaflet-control-zoom a {
          width: 12px !important;
          height: 12px !important;
          line-height: 11px !important;
          font-size: 10px !important;
          background: rgba(4,9,20,0.85) !important;
          color: #18B7C9 !important;
          border: 1px solid rgba(24,183,201,0.35) !important;
          border-radius: 2px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          text-decoration: none !important;
        }
        .ew-map-overlay .leaflet-control-zoom a:hover {
          background: rgba(24,183,201,0.20) !important;
        }
        .ew-map-overlay .leaflet-control-zoom-in {
          margin-bottom: 1px !important;
        }
        .ew-overlay-marker { background: none !important; border: none !important; }
      `}</style>

      <div
        ref={containerRef}
        title="© OpenStreetMap contributors"
        style={{
          width: 'clamp(72px, 8%, 92px)',
          aspectRatio: '4/3',

          position: 'absolute',
          right: '5%',
          bottom: '10%',
          zIndex: 10,

          borderRadius: '5px',
          border: '1px solid rgba(24,183,201,0.55)',
          overflow: 'hidden',
          background: '#060e1c',

          boxShadow: `
            0 0 0 1px rgba(24,183,201,0.08),
            0 3px 10px rgba(0,0,0,0.65),
            0 0 14px 2px rgba(24,183,201,0.10),
            0 0 30px 5px rgba(24,183,201,0.05)
          `,

          animation: visible && !settled ? 'ew-map-rise 0.72s cubic-bezier(0.22,1,0.36,1) both' : undefined,
          opacity: visible ? 1 : 0,
          transition: !visible ? 'opacity 0.1s' : undefined,

          transformOrigin: 'bottom right',
          transformStyle: 'preserve-3d',
          touchAction: 'none',
        }}
        className={`ew-map-overlay${settled ? ' ew-map-overlay-settled' : ''}`}
        onClick={e => e.stopPropagation()}
        onPointerDown={e => e.stopPropagation()}
      >
        <MapContainer
          center={POSITION}
          zoom={11}
          scrollWheelZoom={false}
          zoomControl={false}
          dragging
          style={{ width: '100%', height: '100%' }}
          aria-label="Investigation location — 31.1105°N 77.9373°E"
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <Circle
            center={POSITION}
            radius={3000}
            pathOptions={{
              color: '#18B7C9',
              weight: 1,
              fillColor: '#18B7C9',
              fillOpacity: 0.10,
              dashArray: '3 3',
            }}
          />
          <Marker position={POSITION} icon={investigationIcon} />
          {/* Explicit ZoomControl pinned to top-left */}
          <ZoomControl position="topleft" />
        </MapContainer>

        {/* Coordinates — bottom-right, very small */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            bottom: '2px',
            right: '2px',
            zIndex: 500,
            pointerEvents: 'none',
            lineHeight: 1,
          }}
        >
          <span style={{
            fontSize: '0.34rem',
            fontWeight: 500,
            letterSpacing: '0.04em',
            color: 'rgba(140,210,230,0.65)',
            fontVariantNumeric: 'tabular-nums',
            textShadow: '0 0 4px rgba(0,0,0,1)',
            whiteSpace: 'nowrap',
          }}>
            {LAT.toFixed(4)}°N {LNG.toFixed(4)}°E
          </span>
        </div>
      </div>
    </>
  )
}



