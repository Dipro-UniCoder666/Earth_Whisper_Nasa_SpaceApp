/**
 * HeroAtmosphere
 *
 * Extracts the exact visual layers from the LandingPage hero:
 *   1. Twinkling star field (full SVG with mask + all circles)
 *   2. Atmospheric rim glow + sunlight flare overlays
 *   3. Floating satellite (top-right, same position/animation)
 *
 * Used by SecondaryPageLayout so every non-landing page shares
 * the identical space atmosphere without duplicating code.
 * The landing page continues rendering these inline — unchanged.
 */
export function HeroAtmosphere() {
  return (
    <>
      {/* ── 1. Star field — z-index 1 ─────────────────────── */}
      <svg
        aria-hidden="true"
        style={{
          position: 'fixed',
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
          {/* No content-exclusion mask needed on secondary pages — stars fill freely */}
        </defs>

        {/* TOP-RIGHT corner stars */}
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
        {/* LEFT side stars */}
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
        {/* RIGHT SIDE dark space */}
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
        {/* Full-field scattered stars — no mask needed on secondary pages */}
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
        <circle className="ew-s4"  cx="47"   cy="318"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="123"  cy="307"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="160"  cy="349"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="236"  cy="323"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="311"  cy="341"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="387"  cy="314"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="462"  cy="382"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="538"  cy="369"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="613"  cy="354"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="689"  cy="336"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="764"  cy="395"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="840"  cy="377"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="915"  cy="393"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="991"  cy="362"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1066" cy="385"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1142" cy="348"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1218" cy="371"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1293" cy="345"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1368" cy="326"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1406" cy="371"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="51"   cy="528"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="126"  cy="514"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="202"  cy="543"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="277"  cy="521"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="353"  cy="537"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="428"  cy="516"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="504"  cy="592"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="579"  cy="567"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="655"  cy="583"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="730"  cy="561"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="806"  cy="589"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="881"  cy="572"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="957"  cy="579"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1032" cy="557"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1108" cy="527"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1183" cy="568"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1259" cy="592"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1334" cy="562"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1410" cy="577"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="33"   cy="628"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="108"  cy="614"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="184"  cy="643"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="259"  cy="621"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="335"  cy="637"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="410"  cy="616"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="486"  cy="628"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="562"  cy="643"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="638"  cy="659"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="713"  cy="671"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="789"  cy="628"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="864"  cy="663"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="940"  cy="686"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1015" cy="672"  r="0.5" fill="#fff"/>
        <circle className="ew-s7"  cx="1091" cy="648"  r="0.5" fill="#fff"/>
        <circle className="ew-s16" cx="1166" cy="657"  r="0.5" fill="#fff"/>
        <circle className="ew-s4"  cx="1242" cy="684"  r="0.5" fill="#fff"/>
        <circle className="ew-s9"  cx="1317" cy="662"  r="0.5" fill="#fff"/>
        <circle className="ew-s12" cx="1393" cy="675"  r="0.5" fill="#fff"/>
        {/* Medium bright stars */}
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
        {/* Large bright stars r=1.4 */}
        <circle className="ew-s13" cx="88"   cy="53"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s8"  cx="319"  cy="74"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s3"  cx="597"  cy="29"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s15" cx="832"  cy="61"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s1"  cx="1104" cy="48"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s5"  cx="1387" cy="84"   r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s11" cx="214"  cy="183"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s13" cx="461"  cy="156"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s8"  cx="708"  cy="178"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s3"  cx="955"  cy="148"  r="1.4" fill="#e8f0ff"/>
        <circle className="ew-s15" cx="1202" cy="181"  r="1.4" fill="#e8f0ff"/>
      </svg>

      {/* ── 2. Atmospheric rim glow + sunlight flare — z-index 3 ── */}
      <svg
        aria-hidden="true"
        style={{
          position: 'fixed',
          inset: 0,
          width: '100%',
          height: '100%',
          zIndex: 3,
          pointerEvents: 'none',
        }}
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <radialGradient id="sp-atm-scatter" cx="56%" cy="30%" r="42%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#c8dcf4" stopOpacity="0.22"/>
            <stop offset="35%"  stopColor="#8ab4e0" stopOpacity="0.12"/>
            <stop offset="100%" stopColor="#0a1a2e"  stopOpacity="0"/>
          </radialGradient>
          <radialGradient id="sp-rim-light" cx="56%" cy="28%" r="30%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#ffffff"  stopOpacity="0.28"/>
            <stop offset="30%"  stopColor="#ddeeff"  stopOpacity="0.14"/>
            <stop offset="100%" stopColor="#0a1f38"  stopOpacity="0"/>
          </radialGradient>
          <radialGradient id="sp-sun-flare" cx="22%" cy="5%" r="52%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#fffcf0"  stopOpacity="0.38"/>
            <stop offset="12%"  stopColor="#fff4d0"  stopOpacity="0.24"/>
            <stop offset="28%"  stopColor="#fde8a0"  stopOpacity="0.13"/>
            <stop offset="50%"  stopColor="#c8d8f0"  stopOpacity="0.05"/>
            <stop offset="100%" stopColor="#04090f"  stopOpacity="0"/>
          </radialGradient>
          <radialGradient id="sp-sun-halo" cx="30%" cy="18%" r="45%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#fff0c0"  stopOpacity="0.10"/>
            <stop offset="40%"  stopColor="#d0e4f8"  stopOpacity="0.04"/>
            <stop offset="100%" stopColor="#04090f"  stopOpacity="0"/>
          </radialGradient>
          <radialGradient id="sp-dark-scatter" cx="75%" cy="68%" r="28%" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stopColor="#1a3a6a"  stopOpacity="0.10"/>
            <stop offset="100%" stopColor="#04090f"  stopOpacity="0"/>
          </radialGradient>
        </defs>
        <rect x="0" y="0" width="1440" height="900" fill="url(#sp-atm-scatter)"/>
        <rect x="0" y="0" width="1440" height="900" fill="url(#sp-rim-light)"/>
        <rect x="0" y="0" width="1440" height="900" fill="url(#sp-sun-flare)"/>
        <rect x="0" y="0" width="1440" height="900" fill="url(#sp-sun-halo)"/>
        <rect x="0" y="0" width="1440" height="900" fill="url(#sp-dark-scatter)"/>
      </svg>

      {/* ── 3. Floating satellite — top-right, same as landing page ── */}
      <div
        aria-hidden="true"
        style={{
          position: 'fixed',
          top: '104px',
          right: '52px',
          zIndex: 4,
          pointerEvents: 'none',
          animation: 'ew-satellite-float 8s ease-in-out infinite',
        }}
      >
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
    </>
  )
}
