import { useNavigate } from 'react-router-dom'
import { WhisperNav } from '@/components/navigation/WhisperNav'
import { ROUTES } from '@/lib/constants'
import { EarthSignalSection } from '@/pages/sections/EarthSignalSection'
import { SignalToStorySection } from '@/pages/sections/SignalToStorySection'
import { TeamSection } from '@/pages/sections/TeamSection'
import { Footer } from '@/pages/sections/Footer'

export function LandingPage() {
  const navigate = useNavigate()

  return (
    <>
    <div className="ew-hero-root" style={{ position: 'relative', width: '100%', height: '100vh', overflow: 'hidden', margin: 0, padding: 0 }}>

      {/* ── Hero SVG — full viewport, unchanged ───────────────── */}
      <picture style={{ display: 'contents' }}>
        {/* Portrait hero artwork on phones; the landscape artwork everywhere else */}
        <source media="(max-width: 767px)" srcSet="/images/Hero_Mobile.svg" />
        <img
          src="/images/Hero.svg"
          alt="Earth Whisper hero"
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition: 'center',
            display: 'block',
          }}
          aria-hidden="true"
        />
      </picture>

      {/* ── Star field — behind everything, z-index 1 ─────────── */}
      <svg
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          zIndex: 1,
          pointerEvents: 'none',
        }}
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          {/* 16 animation phases — varied speeds 1.2s–4.8s, stronger opacity swings */}
          <style>{`
            @keyframes ew-t1  { 0%,100%{opacity:0.90} 50%{opacity:0.15} }
            @keyframes ew-t2  { 0%,100%{opacity:0.70} 50%{opacity:0.10} }
            @keyframes ew-t3  { 0%,100%{opacity:1.00} 50%{opacity:0.25} }
            @keyframes ew-t4  { 0%,100%{opacity:0.55} 50%{opacity:0.08} }
            @keyframes ew-t5  { 0%,100%{opacity:0.80} 50%{opacity:0.20} }
            @keyframes ew-t6  { 0%,100%{opacity:0.65} 50%{opacity:0.12} }
            @keyframes ew-t7  { 0%,100%{opacity:0.45} 50%{opacity:0.05} }
            @keyframes ew-t8  { 0%,100%{opacity:0.95} 50%{opacity:0.30} }
            @keyframes ew-t9  { 0%,100%{opacity:0.60} 50%{opacity:0.10} }
            @keyframes ew-t10 { 0%,100%{opacity:0.75} 50%{opacity:0.18} }
            @keyframes ew-t11 { 0%,100%{opacity:0.85} 50%{opacity:0.22} }
            @keyframes ew-t12 { 0%,100%{opacity:0.50} 50%{opacity:0.07} }
            @keyframes ew-t13 { 0%,100%{opacity:1.00} 50%{opacity:0.35} }
            @keyframes ew-t14 { 0%,100%{opacity:0.72} 50%{opacity:0.14} }
            @keyframes ew-t15 { 0%,100%{opacity:0.88} 50%{opacity:0.28} }
            @keyframes ew-t16 { 0%,100%{opacity:0.40} 50%{opacity:0.06} }

            .ew-s1  { animation: ew-t1  1.4s ease-in-out infinite; }
            .ew-s2  { animation: ew-t2  2.1s ease-in-out infinite; }
            .ew-s3  { animation: ew-t3  1.7s ease-in-out infinite; }
            .ew-s4  { animation: ew-t4  3.2s ease-in-out infinite; }
            .ew-s5  { animation: ew-t5  1.9s ease-in-out infinite; }
            .ew-s6  { animation: ew-t6  2.6s ease-in-out infinite; }
            .ew-s7  { animation: ew-t7  3.8s ease-in-out infinite; }
            .ew-s8  { animation: ew-t8  1.5s ease-in-out infinite; }
            .ew-s9  { animation: ew-t9  4.1s ease-in-out infinite; }
            .ew-s10 { animation: ew-t10 2.3s ease-in-out infinite; }
            .ew-s11 { animation: ew-t11 1.8s ease-in-out infinite; }
            .ew-s12 { animation: ew-t12 3.5s ease-in-out infinite; }
            .ew-s13 { animation: ew-t13 1.3s ease-in-out infinite; }
            .ew-s14 { animation: ew-t14 2.8s ease-in-out infinite; }
            .ew-s15 { animation: ew-t15 1.6s ease-in-out infinite; }
            .ew-s16 { animation: ew-t16 4.6s ease-in-out infinite; }
          `}</style>

          {/*
            Star mask — stars only appear in blank dark space.
            Excluded zones (Hero.svg coords scaled to 1440×900 viewBox):
              • Earth globe disc:  centre ≈ (720, 415), radius ≈ 360
              • Title text block:  x=[163,1290], y=[278,490]
              • Subtitle text:     x=[530,910],  y=[455,515]
              • Icons + badges:    x=[440,1000],  y=[575,670]
            We build the clip as: full canvas MINUS those shapes.
            SVG clipPath only supports additive shapes, so we use
            an evenodd <mask> instead: white everywhere, black on
            excluded zones → multiply mask onto stars.
          */}
          <mask id="ew-star-mask">
            {/* White = show stars */}
            <rect x="0" y="0" width="1440" height="900" fill="white"/>
            {/* Black = hide stars — Earth globe (very large, covers most of visible frame) */}
            <circle cx="580" cy="480" r="700" fill="black"/>
            {/* Black out left strip — start at y=280 so the top-left space zone stays open */}
            <rect x="0" y="280" width="260" height="620" fill="black"/>
            {/* Black out bottom-left quadrant */}
            <rect x="0" y="550" width="900" height="350" fill="black"/>
            {/* Black = hide stars — title text area — extended to cover full WHISPER */}
            <rect x="0" y="268" width="1440" height="240" fill="black"/>
            {/* Black = hide stars — subtitle text */}
            <rect x="440" y="440" width="560" height="80" fill="black"/>
            {/* Black = hide stars — icons + badges row */}
            <rect x="400" y="555" width="640" height="120" fill="black"/>
            {/* Re-open top-left corner beside + below navbar: x=0–220, y=0–270 stays WHITE (stars visible) */}
            {/* Re-open top-right corner: x=1200–1440, y=0–270 stays WHITE (already unmasked by globe circle) */}
          </mask>
        </defs>

        {/* ── Stars TOP-RIGHT corner above/beside navbar (x=900–1430, y=8–118) — outside mask ── */}
        <circle className="ew-s3"  cx="962"  cy="22"  r="1.8" fill="#ddeeff"/>
        <circle className="ew-s8"  cx="1048" cy="14"  r="1.2" fill="#f0f6ff"/>
        <circle className="ew-s13" cx="1134" cy="38"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s1"  cx="1198" cy="18"  r="1.0" fill="#f8fbff"/>
        <circle className="ew-s11" cx="1278" cy="44"  r="1.5" fill="#e8f0ff"/>
        <circle className="ew-s5"  cx="928"  cy="68"  r="1.2" fill="#f0f6ff"/>
        <circle className="ew-s15" cx="1072" cy="82"  r="1.6" fill="#e8f0ff"/>
        <circle className="ew-s3"  cx="1162" cy="62"  r="1.0" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="1338" cy="28"  r="1.8" fill="#ddeeff"/>
        <circle className="ew-s13" cx="1414" cy="52"  r="1.2" fill="#f0f6ff"/>
        <circle className="ew-s1"  cx="1244" cy="96"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s11" cx="1382" cy="108" r="1.6" fill="#e8f0ff"/>
        <circle className="ew-s5"  cx="1098" cy="48"  r="0.9" fill="#f8fbff"/>
        <circle className="ew-s15" cx="1308" cy="74"  r="1.0" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="1432" cy="88"  r="1.3" fill="#f0f6ff"/>

        {/* ── Stars LEFT OF NAVBAR — outside mask, always visible ── */}
        <circle className="ew-s3"  cx="18"  cy="58"  r="2.2" fill="#ddeeff"/>
        <circle className="ew-s13" cx="82"  cy="88"  r="0.6" fill="#fff"/>
        <circle className="ew-s8"  cx="44"  cy="102" r="1.6" fill="#e8f0ff"/>
        <circle className="ew-s1"  cx="128" cy="74"  r="0.5" fill="#fff"/>
        <circle className="ew-s11" cx="162" cy="112" r="1.1" fill="#f0f6ff"/>
        <circle className="ew-s5"  cx="26"  cy="138" r="0.7" fill="#f8fbff"/>
        <circle className="ew-s15" cx="96"  cy="128" r="1.8" fill="#ddeeff"/>
        <circle className="ew-s3"  cx="148" cy="154" r="0.5" fill="#fff"/>
        <circle className="ew-s8"  cx="58"  cy="168" r="0.9" fill="#f8fbff"/>
        <circle className="ew-s13" cx="188" cy="92"  r="0.6" fill="#fff"/>
        <circle className="ew-s1"  cx="114" cy="184" r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s11" cx="36"  cy="198" r="0.5" fill="#fff"/>
        <circle className="ew-s5"  cx="172" cy="178" r="0.8" fill="#f8fbff"/>
        <circle className="ew-s15" cx="68"  cy="212" r="2.0" fill="#ddeeff"/>
        <circle className="ew-s3"  cx="142" cy="208" r="0.5" fill="#fff"/>
        <circle className="ew-s8"  cx="198" cy="224" r="1.2" fill="#f0f6ff"/>

        {/* ── Stars RIGHT SIDE dark space (x=1100–1430, y=380–820) — outside mask ── */}
        <circle className="ew-s8"  cx="1312" cy="412" r="0.5" fill="#fff"/>
        <circle className="ew-s11" cx="1388" cy="436" r="1.8" fill="#ddeeff"/>
        <circle className="ew-s5"  cx="1156" cy="496" r="0.5" fill="#fff"/>
        <circle className="ew-s15" cx="1316" cy="506" r="1.1" fill="#f0f6ff"/>
        <circle className="ew-s3"  cx="1428" cy="504" r="0.6" fill="#fff"/>
        <circle className="ew-s8"  cx="1224" cy="528" r="1.6" fill="#e8f0ff"/>
        <circle className="ew-s13" cx="1108" cy="544" r="0.5" fill="#fff"/>
        <circle className="ew-s1"  cx="1362" cy="538" r="0.9" fill="#f8fbff"/>
        <circle className="ew-s11" cx="1142" cy="582" r="2.2" fill="#ddeeff"/>
        <circle className="ew-s5"  cx="1276" cy="568" r="0.5" fill="#fff"/>
        <circle className="ew-s15" cx="1408" cy="594" r="1.3" fill="#f0f6ff"/>
        <circle className="ew-s3"  cx="1198" cy="618" r="0.6" fill="#fff"/>
        <circle className="ew-s8"  cx="1332" cy="608" r="1.0" fill="#f8fbff"/>
        <circle className="ew-s13" cx="1124" cy="642" r="0.5" fill="#fff"/>
        <circle className="ew-s1"  cx="1264" cy="654" r="1.7" fill="#e8f0ff"/>
        <circle className="ew-s11" cx="1396" cy="638" r="0.6" fill="#fff"/>
        <circle className="ew-s5"  cx="1168" cy="688" r="0.5" fill="#fff"/>
        <circle className="ew-s15" cx="1314" cy="674" r="1.2" fill="#f0f6ff"/>
        <circle className="ew-s3"  cx="1432" cy="702" r="0.7" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="1212" cy="718" r="2.0" fill="#ddeeff"/>
        <circle className="ew-s13" cx="1348" cy="728" r="0.5" fill="#fff"/>
        <circle className="ew-s1"  cx="1114" cy="754" r="0.8" fill="#f8fbff"/>
        <circle className="ew-s11" cx="1378" cy="764" r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s5"  cx="1248" cy="782" r="0.5" fill="#fff"/>
        <circle className="ew-s15" cx="1422" cy="798" r="0.9" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="1136" cy="812" r="1.6" fill="#e8f0ff"/>

        {/* ── All other stars (masked to avoid Earth/text) ── */}
        <g mask="url(#ew-star-mask)">

        {/* ── Extra stars: top-left below navbar (x=0–220, y=90–268) ── */}
        <circle className="ew-s3"  cx="28"  cy="98"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s8"  cx="72"  cy="142" r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="14"  cy="178" r="1.1" fill="#f0f6ff"/>
        <circle className="ew-s11" cx="108" cy="112" r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="154" cy="196" r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s13" cx="38"  cy="231" r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="88"  cy="258" r="1.1" fill="#f0f6ff"/>
        <circle className="ew-s2"  cx="178" cy="224" r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="124" cy="248" r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s6"  cx="58"  cy="174" r="0.5" fill="#fff"/>
        <circle className="ew-s10" cx="196" cy="138" r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="142" cy="162" r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="22"  cy="214" r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="168" cy="254" r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="18"   cy="12"   r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="55"   cy="43"   r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="93"   cy="8"    r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="131"  cy="61"   r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="168"  cy="27"   r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="206"  cy="74"   r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="244"  cy="19"   r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="282"  cy="56"   r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="319"  cy="32"   r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="357"  cy="81"   r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="395"  cy="14"   r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="433"  cy="68"   r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="470"  cy="38"   r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="508"  cy="87"   r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="546"  cy="22"   r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="584"  cy="59"   r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="621"  cy="5"    r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="659"  cy="48"   r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="697"  cy="83"   r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="735"  cy="16"   r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="772"  cy="70"   r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="810"  cy="31"   r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="848"  cy="77"   r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="886"  cy="10"   r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="923"  cy="54"   r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="961"  cy="89"   r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="999"  cy="25"   r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1037" cy="63"   r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1074" cy="41"   r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1112" cy="86"   r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1150" cy="17"   r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1188" cy="52"   r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1225" cy="79"   r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1263" cy="33"   r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1301" cy="67"   r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1339" cy="7"    r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1376" cy="44"   r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1414" cy="82"   r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="36"   cy="128"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="74"   cy="163"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="111"  cy="107"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="149"  cy="149"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="187"  cy="116"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="225"  cy="178"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="262"  cy="134"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="300"  cy="169"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="338"  cy="112"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="376"  cy="155"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="413"  cy="141"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="451"  cy="188"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="489"  cy="122"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="527"  cy="173"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="564"  cy="103"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="602"  cy="159"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="640"  cy="185"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="678"  cy="118"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="715"  cy="144"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="753"  cy="191"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="791"  cy="126"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="829"  cy="162"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="866"  cy="138"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="904"  cy="177"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="942"  cy="110"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="980"  cy="153"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1017" cy="183"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1055" cy="121"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1093" cy="166"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1131" cy="108"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1168" cy="147"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1206" cy="189"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1244" cy="114"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1282" cy="157"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1319" cy="132"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1357" cy="175"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1395" cy="119"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1433" cy="161"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="23"   cy="228"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="61"   cy="271"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="99"   cy="207"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="136"  cy="254"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="174"  cy="239"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="212"  cy="283"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="250"  cy="218"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="287"  cy="261"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="325"  cy="244"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="363"  cy="289"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="401"  cy="222"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="438"  cy="267"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="476"  cy="212"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="514"  cy="278"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="552"  cy="233"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="589"  cy="258"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="627"  cy="295"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="665"  cy="217"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="703"  cy="264"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="740"  cy="249"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="778"  cy="286"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="816"  cy="228"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="854"  cy="271"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="891"  cy="208"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="929"  cy="253"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="967"  cy="239"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1005" cy="282"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1042" cy="214"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1080" cy="269"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1118" cy="234"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1156" cy="275"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1193" cy="221"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1231" cy="258"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1269" cy="292"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1307" cy="243"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1344" cy="211"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1382" cy="267"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1420" cy="237"  r="0.5" fill="#fff"/>
        {/* rows 300-500 */}
        <circle className="ew-s16" cx="47"   cy="318"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="85"   cy="361"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="123"  cy="307"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="160"  cy="349"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="198"  cy="388"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="236"  cy="323"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="274"  cy="375"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="311"  cy="341"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="349"  cy="398"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="387"  cy="314"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="425"  cy="357"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="462"  cy="382"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="500"  cy="328"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="538"  cy="369"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="576"  cy="311"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="613"  cy="354"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="651"  cy="391"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="689"  cy="336"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="727"  cy="363"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="764"  cy="395"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="802"  cy="322"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="840"  cy="377"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="878"  cy="348"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="915"  cy="393"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="953"  cy="317"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="991"  cy="362"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1029" cy="338"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1066" cy="385"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1255" cy="368"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1293" cy="345"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1331" cy="392"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1368" cy="326"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1406" cy="371"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="29"   cy="428"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="67"   cy="471"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="104"  cy="414"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="142"  cy="457"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="180"  cy="493"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="218"  cy="432"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="255"  cy="474"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="293"  cy="448"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="331"  cy="488"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="369"  cy="421"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="406"  cy="466"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="444"  cy="444"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="482"  cy="491"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="520"  cy="418"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="557"  cy="461"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="595"  cy="437"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="633"  cy="483"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="671"  cy="428"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="708"  cy="469"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="746"  cy="453"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="784"  cy="497"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="822"  cy="416"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="859"  cy="463"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="897"  cy="441"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="935"  cy="486"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="973"  cy="429"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1010" cy="472"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1048" cy="456"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1086" cy="493"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1124" cy="424"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1161" cy="467"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1199" cy="445"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1237" cy="489"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1275" cy="431"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1312" cy="476"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1350" cy="452"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1388" cy="495"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1426" cy="427"  r="0.5" fill="#fff"/>
        {/* rows 500-900 */}
        <circle className="ew-s16" cx="51"   cy="528"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="89"   cy="571"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="126"  cy="514"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="164"  cy="558"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="202"  cy="543"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="240"  cy="586"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="277"  cy="521"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="315"  cy="564"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="353"  cy="537"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="391"  cy="578"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="428"  cy="516"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="466"  cy="553"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="504"  cy="592"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="542"  cy="528"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="579"  cy="567"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="617"  cy="542"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="655"  cy="583"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="693"  cy="519"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="730"  cy="561"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="768"  cy="548"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="806"  cy="589"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="844"  cy="524"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="881"  cy="572"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="919"  cy="536"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="957"  cy="579"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="995"  cy="513"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1032" cy="557"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1070" cy="541"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1108" cy="584"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1146" cy="527"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1183" cy="568"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1221" cy="553"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1259" cy="592"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1297" cy="519"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1334" cy="562"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1372" cy="538"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1410" cy="577"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="33"   cy="628"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="71"   cy="671"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="108"  cy="614"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="146"  cy="657"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="184"  cy="643"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="222"  cy="686"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="259"  cy="621"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="297"  cy="664"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="335"  cy="637"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="373"  cy="678"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="410"  cy="616"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="448"  cy="659"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="486"  cy="693"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="524"  cy="628"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="561"  cy="671"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="599"  cy="645"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="637"  cy="688"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="675"  cy="623"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="712"  cy="666"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="750"  cy="652"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="788"  cy="695"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="826"  cy="619"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="863"  cy="662"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="901"  cy="638"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="939"  cy="679"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="977"  cy="627"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1014" cy="673"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1052" cy="648"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1090" cy="691"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1128" cy="632"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1165" cy="675"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1203" cy="641"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1241" cy="684"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1279" cy="618"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1316" cy="661"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1354" cy="656"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1392" cy="693"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1430" cy="624"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="57"   cy="728"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="94"   cy="771"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="132"  cy="714"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="170"  cy="757"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="208"  cy="743"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="245"  cy="786"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="283"  cy="721"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="321"  cy="764"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="359"  cy="737"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="396"  cy="778"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="434"  cy="716"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="472"  cy="753"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="510"  cy="792"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="547"  cy="728"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="585"  cy="767"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="623"  cy="742"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="661"  cy="783"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="698"  cy="719"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="736"  cy="761"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="774"  cy="748"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="812"  cy="789"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="849"  cy="724"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="887"  cy="772"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="925"  cy="736"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="963"  cy="779"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1000" cy="713"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1038" cy="757"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1076" cy="741"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1114" cy="784"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1151" cy="727"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1189" cy="768"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1227" cy="753"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1265" cy="792"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1302" cy="719"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1340" cy="762"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1378" cy="738"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1416" cy="779"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="39"   cy="828"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="77"   cy="871"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="114"  cy="814"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="152"  cy="857"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="190"  cy="843"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="228"  cy="886"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="265"  cy="821"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="303"  cy="864"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="341"  cy="837"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="379"  cy="878"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="416"  cy="816"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="454"  cy="859"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="492"  cy="893"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="530"  cy="828"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="567"  cy="871"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="605"  cy="845"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="643"  cy="888"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="681"  cy="823"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="718"  cy="866"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="756"  cy="852"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="794"  cy="895"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="832"  cy="819"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="869"  cy="862"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="907"  cy="838"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="945"  cy="879"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="983"  cy="827"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1020" cy="873"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1058" cy="848"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1096" cy="891"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1134" cy="832"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1171" cy="875"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1209" cy="841"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1247" cy="884"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1285" cy="818"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1322" cy="861"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1360" cy="856"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1398" cy="893"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1436" cy="824"  r="0.5" fill="#fff"/>

        {/* ── Medium stars r=0.85 — frequent visible twinklers ── */}
        <circle className="ew-s1"  cx="42"   cy="38"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="118"  cy="72"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="195"  cy="21"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="268"  cy="88"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="341"  cy="14"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="423"  cy="55"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="502"  cy="91"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s6"  cx="577"  cy="33"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s10" cx="649"  cy="67"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s13" cx="724"  cy="18"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="801"  cy="79"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="876"  cy="42"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="953"  cy="8"    r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="1031" cy="61"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="1108" cy="29"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="1184" cy="84"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="1259" cy="47"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s6"  cx="1338" cy="19"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s10" cx="1401" cy="73"   r="0.85" fill="#f8fbff"/>
        <circle className="ew-s13" cx="75"   cy="152"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="229"  cy="138"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="385"  cy="171"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="538"  cy="149"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="692"  cy="124"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="847"  cy="157"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="1001" cy="133"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="1156" cy="162"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s6"  cx="1311" cy="143"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s10" cx="31"   cy="258"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s13" cx="186"  cy="237"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="341"  cy="278"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="496"  cy="249"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="651"  cy="267"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="805"  cy="248"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="960"  cy="281"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="1115" cy="260"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="1270" cy="238"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s6"  cx="1425" cy="271"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="58"   cy="368"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="213"  cy="347"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="368"  cy="382"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="523"  cy="359"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="678"  cy="377"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="833"  cy="348"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="988"  cy="361"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s6"  cx="1143" cy="384"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s10" cx="1298" cy="352"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s13" cx="24"   cy="468"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="179"  cy="447"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="334"  cy="478"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="489"  cy="456"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="644"  cy="487"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="799"  cy="448"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="954"  cy="471"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="1109" cy="459"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s6"  cx="1264" cy="482"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s10" cx="1419" cy="467"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s13" cx="67"   cy="558"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="222"  cy="547"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="377"  cy="578"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="532"  cy="556"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="687"  cy="567"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="842"  cy="548"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="997"  cy="579"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="1152" cy="550"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s6"  cx="1307" cy="568"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s10" cx="44"   cy="648"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s13" cx="199"  cy="667"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="354"  cy="648"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="509"  cy="676"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="664"  cy="657"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="819"  cy="688"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="974"  cy="659"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="1129" cy="670"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="1284" cy="648"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s6"  cx="1439" cy="679"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s10" cx="83"   cy="758"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s13" cx="238"  cy="777"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="393"  cy="748"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="548"  cy="786"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="703"  cy="757"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="858"  cy="778"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="1013" cy="749"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="1168" cy="770"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="1323" cy="758"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s6"  cx="29"   cy="858"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s10" cx="184"  cy="877"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s13" cx="339"  cy="858"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s1"  cx="494"  cy="872"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s5"  cx="649"  cy="853"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s2"  cx="804"  cy="884"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s8"  cx="959"  cy="865"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s11" cx="1114" cy="876"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s3"  cx="1269" cy="844"  r="0.85" fill="#f8fbff"/>
        <circle className="ew-s15" cx="1424" cy="875"  r="0.85" fill="#f8fbff"/>

        {/* ── Larger bright stars r=1.4 — sparse, vivid twinkle ── */}
        <circle className="ew-s13" cx="88"   cy="53"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s8"  cx="319"  cy="74"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s3"  cx="597"  cy="29"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s15" cx="832"  cy="61"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s1"  cx="1104" cy="48"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s5"  cx="1387" cy="84"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s11" cx="214"  cy="183"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s13" cx="461"  cy="156"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s8"  cx="789"  cy="201"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s3"  cx="1052" cy="172"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s15" cx="1321" cy="198"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s1"  cx="138"  cy="331"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s5"  cx="347"  cy="297"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s11" cx="597"  cy="321"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s13" cx="918"  cy="288"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s8"  cx="1163" cy="334"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s3"  cx="1387" cy="301"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s15" cx="183"  cy="452"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s1"  cx="523"  cy="443"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s5"  cx="978"  cy="469"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s11" cx="1272" cy="427"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s13" cx="61"   cy="571"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s8"  cx="412"  cy="614"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s3"  cx="847"  cy="578"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s15" cx="1198" cy="607"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s1"  cx="288"  cy="723"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s5"  cx="721"  cy="761"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s11" cx="1089" cy="718"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s13" cx="1401" cy="749"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s8"  cx="172"  cy="832"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s3"  cx="634"  cy="867"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s15" cx="1048" cy="841"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s1"  cx="1355" cy="873"  r="1.4" fill="#e8f0ff"/>

        {/* ── Giant prominent stars r=2.0 — very few, obvious ── */}
        <circle className="ew-s3"  cx="447"  cy="51"   r="2.0" fill="#ddeeff"/>
        <circle className="ew-s13" cx="1197" cy="31"   r="2.0" fill="#ddeeff"/>
        <circle className="ew-s8"  cx="762"  cy="182"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s1"  cx="112"  cy="271"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s15" cx="1388" cy="234"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s5"  cx="597"  cy="391"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s11" cx="183"  cy="512"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s13" cx="978"  cy="449"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s3"  cx="1302" cy="531"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s8"  cx="447"  cy="671"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s1"  cx="1231" cy="668"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s15" cx="88"   cy="798"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s5"  cx="762"  cy="812"  r="2.0" fill="#ddeeff"/>
        <circle className="ew-s11" cx="1355" cy="823"  r="2.0" fill="#ddeeff"/>
        </g>{/* end ew-star-mask group */}
      </svg>

      {/* ── Atmospheric rim glow + strong sunlight flare — z-index 2 ── */}
      <svg
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          zIndex: 2,
          pointerEvents: 'none',
        }}
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          {/* Wide atmospheric scatter — blue-white halo over lit hemisphere */}
          <radialGradient id="ew-atm-scatter" cx="56%" cy="30%" r="42%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#c8dcf4" stopOpacity="0.22"/>
            <stop offset="35%"  stopColor="#8ab4e0" stopOpacity="0.12"/>
            <stop offset="100%" stopColor="#0a1a2e"  stopOpacity="0"/>
          </radialGradient>

          {/* Tighter rim highlight */}
          <radialGradient id="ew-rim-light" cx="56%" cy="28%" r="30%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#ffffff"  stopOpacity="0.28"/>
            <stop offset="30%"  stopColor="#ddeeff"  stopOpacity="0.14"/>
            <stop offset="100%" stopColor="#0a1f38"  stopOpacity="0"/>
          </radialGradient>

          {/* Primary sunlight flare — warm-white from upper-left, pulled back so navbar stays readable */}
          <radialGradient id="ew-sun-flare" cx="22%" cy="5%" r="52%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#fffcf0"  stopOpacity="0.38"/>
            <stop offset="12%"  stopColor="#fff4d0"  stopOpacity="0.24"/>
            <stop offset="28%"  stopColor="#fde8a0"  stopOpacity="0.13"/>
            <stop offset="50%"  stopColor="#c8d8f0"  stopOpacity="0.05"/>
            <stop offset="100%" stopColor="#04090f"  stopOpacity="0"/>
          </radialGradient>

          {/* Secondary diffuse glow further into frame */}
          <radialGradient id="ew-sun-halo" cx="30%" cy="18%" r="45%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#fff0c0"  stopOpacity="0.10"/>
            <stop offset="40%"  stopColor="#d0e4f8"  stopOpacity="0.04"/>
            <stop offset="100%" stopColor="#04090f"  stopOpacity="0"/>
          </radialGradient>

          {/* Cool dark-side scatter */}
          <radialGradient id="ew-dark-scatter" cx="75%" cy="68%" r="28%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#1a3a6a"  stopOpacity="0.10"/>
            <stop offset="100%" stopColor="#04090f"  stopOpacity="0"/>
          </radialGradient>
        </defs>

        {/* Layer 1 — wide atmospheric scatter */}
        <rect x="0" y="0" width="1440" height="900" fill="url(#ew-atm-scatter)"/>
        {/* Layer 2 — tighter rim highlight */}
        <rect x="0" y="0" width="1440" height="900" fill="url(#ew-rim-light)"/>
        {/* Layer 3 — strong sunlight source flare */}
        <rect x="0" y="0" width="1440" height="900" fill="url(#ew-sun-flare)"/>
        {/* Layer 4 — diffuse secondary sun halo */}
        <rect x="0" y="0" width="1440" height="900" fill="url(#ew-sun-halo)"/>
        {/* Layer 5 — cool dark-side scatter */}
        <rect x="0" y="0" width="1440" height="900" fill="url(#ew-dark-scatter)"/>
      </svg>

      {/* ── Satellite image — top-right, below navbar ── */}
      <div
        style={{
          position: 'absolute',
          top: '104px',
          right: '52px',
          zIndex: 10,
          pointerEvents: 'none',
          animation: 'ew-satellite-float 8s ease-in-out infinite',
        }}
        aria-hidden="true"
      >
        <style>{`
          @keyframes ew-satellite-float {
            0%   { transform: translate(0px, 0px) rotate(0deg); }
            25%  { transform: translate(6px, -8px) rotate(1.2deg); }
            50%  { transform: translate(12px, -4px) rotate(0deg); }
            75%  { transform: translate(6px, 4px) rotate(-1.2deg); }
            100% { transform: translate(0px, 0px) rotate(0deg); }
          }
        `}</style>
        <img
          src="/images/sattelite.png"
          alt=""
          style={{
            width: '220px',
            height: 'auto',
            opacity: 0.88,
            display: 'block',
            filter: 'drop-shadow(0 0 16px rgba(0,0,0,0.35)) drop-shadow(0 0 6px rgba(0,0,0,0.45))',
          }}
        />
      </div>

      <WhisperNav variant="overlay" />
      {/* ── Compact white pill CTA — below feature items ── */}
      <div
        style={{
          position: 'absolute',
          bottom: 'calc(10% - 50px)',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 20,
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <button
          type="button"
          onClick={() => navigate(ROUTES.investigate)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#ffffff',
            color: '#0B2A4A',
            border: 'none',
            borderRadius: '999px',
            padding: '7px 18px',
            fontSize: '0.875rem',
            fontWeight: 600,
            boxShadow: '0 2px 12px rgba(0,0,0,0.22)',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            letterSpacing: '-0.01em',
          }}
        >
          Begin the Investigation ⮞
        </button>
      </div>

    </div>

      <div className="ew-landing-sections">
        <EarthSignalSection />
        <SignalToStorySection />
        <TeamSection />
        <Footer />
      </div>
    </>
  )
}




