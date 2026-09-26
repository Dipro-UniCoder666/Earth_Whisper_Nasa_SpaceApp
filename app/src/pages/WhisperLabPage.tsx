import { useEffect, useMemo, useRef, useState } from 'react'
import { BookOpen, Camera, Check, CloudRain, Database, Eye, GitCompareArrows, Grip, Layers3, MapPin, Mountain, Radar, Satellite, Sparkles, Waves, X } from 'lucide-react'
import { getSandhyaCandidate, getSandhyaCandidates } from '@/features/candidates/services/candidateService'
import type { CandidateDetail } from '@/features/candidates/types'
import { MONDA_INVESTIGATION, SANDHYA_INVESTIGATION } from '@/features/investigation/data/investigationSite'

type CaseId = 'sandhya' | 'monda'
type ScanState = 'idle' | 'scanning' | 'processing' | 'scanned'
interface LabCase { id: CaseId; name: string; place: string; coords: string; kind: 'river' | 'mountain'; sources: string[]; radar: { change: string; before: string; after: string; unit: string; detail: string }; compare: { value: string; detail: string }; context: { value: string; detail: string }; finding: string; limitation: string; science: string[] }

const WHISPER_LAB_LEARN_MORE = [
  ['What did Nebula help us do?', 'Nebula guided us through the game: aim the satellite, receive a signal, compare views, and collect clues.'],
  ['What is a satellite?', 'A satellite is a machine that travels around Earth. It can carry sensors that observe land, water, and ice from above.'],
  ['What is radar?', 'Radar sends and receives energy to learn about a surface. It can work even when clouds make a picture hard to see.'],
  ['What did the satellite signal show?', 'The verified radar evidence showed a measurable change in this investigated area. It showed where to look more closely.'],
  ['Why did we compare two views?', 'A single view is only one moment. Comparing earlier and later observations helps scientists notice what changed.'],
  ['Why did we collect rain or terrain clues?', 'Extra clues give helpful context. Rain can affect a river area, while terrain helps explain a mountain area.'],
  ['Why was the image clue unclear?', 'Some observations are not clear enough to answer every question. Saying “unclear” is more honest than guessing.'],
  ['Did the game recalculate raw satellite data?', 'No. Earth Whisper loaded verified, prepared observations. The game explains how scientists organize evidence; it does not pretend to recalculate it live.'],
  ['Does a radar change tell us the cause?', 'No. It tells us that something changed. Scientists need more observations and careful study to learn why.'],
  ['What did we learn as Earth detectives?', 'We learned to observe, compare, check context, and be honest about limits. Good science asks questions before making a claim.'],
] as const

const MONDA: LabCase = {
  id: 'monda', name: MONDA_INVESTIGATION.shortName, place: 'Uttarakhand, India', coords: MONDA_INVESTIGATION.coordLabel, kind: 'mountain', sources: ['NISAR', 'NASADEM'],
  radar: { change: MONDA_INVESTIGATION.nisar.meanChange.toFixed(4), before: MONDA_INVESTIGATION.nisar.beforeCoherence.toFixed(4), after: MONDA_INVESTIGATION.nisar.afterCoherence.toFixed(4), unit: 'coherence', detail: MONDA_INVESTIGATION.nisar.observationSummary },
  compare: { value: 'Different', detail: 'Radar noticed a change.' }, context: { value: `${MONDA_INVESTIGATION.terrain.elevationMeters.toLocaleString()} m`, detail: `High mountain terrain. Slope ${MONDA_INVESTIGATION.terrain.localSlopeDegrees.toFixed(1)} degrees.` }, finding: 'Something changed here.', limitation: 'We need more evidence to know why.',
  science: [`NISAR GUNW coherence: ${MONDA_INVESTIGATION.nisar.beforeCoherence.toFixed(4)} before, ${MONDA_INVESTIGATION.nisar.afterCoherence.toFixed(4)} after.`, `${MONDA_INVESTIGATION.nisar.validPixels.toLocaleString()} valid pixels were used in the regional comparison.`, `NASADEM terrain: ${MONDA_INVESTIGATION.terrain.elevationMeters.toLocaleString()} m elevation, ${MONDA_INVESTIGATION.terrain.localSlopeDegrees.toFixed(1)} degree slope.`],
}

function formatValue(value: number | null | undefined, digits = 2) { return value === null || value === undefined || Number.isNaN(value) ? 'Not available' : value.toFixed(digits) }

function buildSandhya(candidate: CandidateDetail | null): LabCase {
  const rainfall = candidate?.environmental.gunw_023_rainfall_14day_mm
  const radarChange = candidate?.nisar_change ?? -0.3040
  return {
    id: 'sandhya', name: SANDHYA_INVESTIGATION.shortName, place: SANDHYA_INVESTIGATION.subtitle, coords: SANDHYA_INVESTIGATION.coordLabel, kind: 'river', sources: ['NISAR', 'Sentinel-1', 'GPM IMERG'],
    radar: { change: radarChange.toFixed(4), before: 'Pair A', after: 'Pair B', unit: 'radar change', detail: candidate?.observations.observation_summary ?? 'Verified radar evidence is ready.' },
    compare: { value: candidate?.s1_median_db == null ? 'Seen' : `${candidate.s1_median_db.toFixed(2)} dB`, detail: 'Another radar saw this area.' }, context: { value: rainfall == null ? 'Context' : `${rainfall.toFixed(1)} mm`, detail: 'Rain is another clue.' }, finding: 'Something changed here.', limitation: 'We need more evidence to know why.',
    science: [`NISAR change: ${formatValue(candidate?.nisar_change, 4)}; signal band: ${candidate?.nisar_signal_band ?? 'Not available'}.`, `Sentinel-1 median: ${formatValue(candidate?.s1_median_db, 2)} dB; cross-radar status: ${candidate?.cross_radar_status ?? 'Not available'}.`, `Optical status: ${candidate?.optical_status ?? 'Not tested'}; rainfall: ${candidate?.rainfall_context_status ?? 'Context available'}.`],
  }
}

export function WhisperLabPage() {
  const [selectedCase, setSelectedCase] = useState<CaseId>('sandhya')
  const [candidate, setCandidate] = useState<CandidateDetail | null>(null)
  const [scanState, setScanState] = useState<ScanState>('idle')
  const [focused, setFocused] = useState(false)
  const [targetFound, setTargetFound] = useState(false)
  const [matched, setMatched] = useState(false)
  const [compareSlots, setCompareSlots] = useState(0)
  const [receiverReady, setReceiverReady] = useState(false)
  const [dataProcessed, setDataProcessed] = useState(false)
  const [crossRadar, setCrossRadar] = useState(false)
  const [contextFound, setContextFound] = useState(false)
  const [opticalViewed, setOpticalViewed] = useState(false)
  const [assembled, setAssembled] = useState<string[]>([])
  const [investigated, setInvestigated] = useState(false)
  const [message, setMessage] = useState('')
  const [companionSpeech, setCompanionSpeech] = useState('Something changed here.')
  const [scienceDetail, setScienceDetail] = useState(false)
  const [learnMoreOpen, setLearnMoreOpen] = useState(false)
  const [learnQuestion, setLearnQuestion] = useState<number | null>(null)
  const [learnAnswerLoading, setLearnAnswerLoading] = useState(false)
  const scanTimer = useRef<number | null>(null)
  const processingTimer = useRef<number | null>(null)
  const hintTimer = useRef<number | null>(null)
  const learnAnswerTimer = useRef<number | null>(null)

  useEffect(() => { let cancelled = false; async function loadSandhya() { try { const list = await getSandhyaCandidates(true); const first = list.candidates[0]; if (!first) throw new Error('No verified Sandhya candidate'); const detail = await getSandhyaCandidate(first.candidate_key); if (!cancelled) setCandidate(detail) } catch { /* The prepared game values remain usable while evidence loads. */ } } void loadSandhya(); return () => { cancelled = true } }, [])
  useEffect(() => { if (scanTimer.current !== null) window.clearTimeout(scanTimer.current); if (processingTimer.current !== null) window.clearTimeout(processingTimer.current); if (learnAnswerTimer.current !== null) window.clearTimeout(learnAnswerTimer.current); setScanState('idle'); setFocused(false); setTargetFound(false); setMatched(false); setCompareSlots(0); setReceiverReady(false); setDataProcessed(false); setCrossRadar(false); setContextFound(false); setOpticalViewed(false); setAssembled([]); setInvestigated(false); setLearnMoreOpen(false); setLearnQuestion(null); setLearnAnswerLoading(false); setMessage(''); setCompanionSpeech('Something changed here.'); return () => { if (scanTimer.current !== null) window.clearTimeout(scanTimer.current); if (processingTimer.current !== null) window.clearTimeout(processingTimer.current); if (learnAnswerTimer.current !== null) window.clearTimeout(learnAnswerTimer.current) } }, [selectedCase])

  useEffect(() => {
    if (hintTimer.current !== null) window.clearTimeout(hintTimer.current)
    hintTimer.current = window.setTimeout(() => {
      if (scanState === 'idle' && !focused) setCompanionSpeech('Try the satellite.')
      else if (scanState === 'scanned' && !receiverReady) setCompanionSpeech('Catch the returning signal.')
      else if (receiverReady && !dataProcessed) setCompanionSpeech('Feed it into the data machine.')
      else if (dataProcessed && !matched) setCompanionSpeech('Put the signal patterns together.')
    }, 8000)
    return () => { if (hintTimer.current !== null) window.clearTimeout(hintTimer.current) }
  }, [dataProcessed, focused, matched, receiverReady, scanState])

  useEffect(() => {
    if (assembled.length === 4 && investigated) {
      setCompanionSpeech('We found a real Earth clue!')
      setMessage('You used satellite data to investigate it.')
    }
  }, [assembled.length, investigated])

  const activeCase = useMemo(() => selectedCase === 'monda' ? MONDA : buildSandhya(candidate), [candidate, selectedCase])
  const complete = investigated && assembled.length === 4
  // The shared game can start from prepared case context while Sandhya details load in the background.
  const canPlay = true
  function speak(text: string, short = text) { setMessage(short); setCompanionSpeech(text) }
  function activateSatellite() { if (!canPlay || scanState !== 'idle') return; setScanState('scanning'); setMessage(''); setCompanionSpeech('Signal down!'); scanTimer.current = window.setTimeout(() => { setScanState('processing'); setCompanionSpeech('Signal back!'); setMessage('Return signal received'); processingTimer.current = window.setTimeout(() => { setScanState('scanned'); speak('We turn the signal into data. Now we can compare.', 'Data ready') }, 1100) }, 4000) }
  function captureReceiver() { if (scanState !== 'scanned' || receiverReady) return; setReceiverReady(true); speak('That returning signal carries information.', 'Signal received!') }
  function processData() { if (!receiverReady || dataProcessed) return; setDataProcessed(true); speak('We turn the signal into useful data.', 'Data ready') }
  function placeCompareData() { if (!dataProcessed || matched) return; setCompareSlots((value) => { const next = Math.min(2, value + 1); if (next === 2) { setMatched(true); speak('More alike means a stronger match.', 'The observations changed.') } else { speak('Add the second radar view.', 'One view placed') } return next }) }
  function matchSignals() { placeCompareData() }
  function alignRadars() { if (!matched || crossRadar) return; setCrossRadar(true); speak('Another radar saw this area.', 'Another view!') }
  function revealContext() { if (!crossRadar || contextFound) return; setContextFound(true); speak(activeCase.kind === 'river' ? 'Rain is another clue.' : 'High mountain terrain.', activeCase.kind === 'river' ? 'Rain!' : 'High terrain!') }
  function inspectOptical() { if (!contextFound || opticalViewed) return; setOpticalViewed(true); speak('Too hazy to tell. We need more clues.', 'Too hazy.') }
  function collectToken(token: string) { if (!assembled.includes(token)) setAssembled((current) => [...current, token]) }
  function investigateNow() { if (assembled.length !== 4 || investigated) return; setInvestigated(true); speak('We compared the evidence. That is our Earth clue.', 'Radar change found!') }
  function askLearnQuestion(index: number) { if (learnAnswerTimer.current !== null) window.clearTimeout(learnAnswerTimer.current); setLearnQuestion(index); setLearnAnswerLoading(true); learnAnswerTimer.current = window.setTimeout(() => setLearnAnswerLoading(false), 2000) }
  function resetGame() { if (scanTimer.current !== null) window.clearTimeout(scanTimer.current); if (processingTimer.current !== null) window.clearTimeout(processingTimer.current); setScanState('idle'); setFocused(false); setTargetFound(false); setMatched(false); setCompareSlots(0); setReceiverReady(false); setDataProcessed(false); setCrossRadar(false); setContextFound(false); setOpticalViewed(false); setAssembled([]); setInvestigated(false); setMessage(''); setCompanionSpeech('Something changed here.') }
  function dragStart(event: React.DragEvent<HTMLElement>, action: string) { event.dataTransfer.setData('whisper-action', action) }
  function dropAction(event: React.DragEvent<HTMLDivElement>) { event.preventDefault(); const action = event.dataTransfer.getData('whisper-action'); if (action === 'satellite') activateSatellite(); if (action === 'receiver') captureReceiver(); if (action === 'processor') processData(); if (action === 'signal') placeCompareData(); if (action === 'radar') alignRadars(); if (action === 'context') revealContext() }

  return <div className="whisper-lab-page">
    <header className="whisper-lab-header"><div><p className="whisper-lab-eyebrow"><Sparkles size={14} aria-hidden="true" /> Whisper Lab</p><h1>Find the Earth clue.</h1></div><button type="button" className="whisper-lab-detail-toggle" onClick={() => setScienceDetail(true)}><BookOpen size={16} aria-hidden="true" /> Science Detail</button></header>
    <main className="whisper-lab-shell">
      <div className={`whisper-lab-world is-${scanState}${focused ? ' is-focused' : ''}${matched ? ' is-matched' : ''}${contextFound ? ' is-context-found' : ''}`} onDragOver={(event) => event.preventDefault()} onDrop={dropAction}>
        <div className="whisper-lab-stars" aria-hidden="true" /><div className="whisper-lab-orbit orbit-one" aria-hidden="true" /><div className="whisper-lab-orbit orbit-two" aria-hidden="true" /><div className="whisper-lab-clouds" aria-hidden="true"><span /><span /><span /></div>
        <div className="whisper-lab-location-picker" aria-label="Choose location"><button type="button" className={selectedCase === 'sandhya' ? 'is-selected' : ''} onClick={() => setSelectedCase('sandhya')} title="Sandhya River"><Waves size={17} /><span>Sandhya</span></button><button type="button" className={selectedCase === 'monda' ? 'is-selected' : ''} onClick={() => setSelectedCase('monda')} title="Monda, Uttarakhand"><Mountain size={17} /><span>Monda</span></button></div>
        <button type="button" className="whisper-lab-satellite" draggable onDragStart={(event) => dragStart(event, 'satellite')} onClick={activateSatellite} disabled={!canPlay || scanState !== 'idle'} aria-label="Activate satellite" title={canPlay ? 'Tap or drag satellite to the glowing place' : 'Loading verified evidence'}><Satellite size={32} strokeWidth={1.5} /><span className="whisper-lab-signal-ring" />{scanState === 'idle' && <small>{canPlay ? 'Tap' : 'Loading'}</small>}</button>
        <div className="whisper-lab-beam" aria-hidden="true" /><div className="whisper-lab-return-signal" aria-hidden="true"><i /><i /><i /></div>{(scanState === 'processing' || (scanState === 'scanned' && !complete)) && <div className="whisper-lab-data-capsule" aria-label="Returned signal transformed into processed data"><span className="whisper-lab-raw-signal">RAW SIGNAL</span><b>DATA</b><i /><i /><i /></div>}
        <div className="whisper-lab-earth"><div className="whisper-lab-land land-one" /><div className="whisper-lab-land land-two" /><div className="whisper-lab-river" />{!targetFound && !investigated && <button type="button" className="whisper-lab-target" onClick={() => { setTargetFound(true); setFocused(true) }} aria-label="Look at the glowing investigation area" title="Look here"><MapPin size={25} fill="currentColor" /><small>Look</small></button>}{matched && investigated && <div className="whisper-lab-radar-layer" aria-label={`Radar change ${activeCase.radar.change}`}><div className="whisper-lab-signal-trace"><i /><i /><i /><i /><i /><i /></div><div className="whisper-lab-measurement"><small>{activeCase.kind === 'mountain' ? 'COHERENCE CHANGE' : 'RADAR CHANGE'}</small><b>{activeCase.radar.change}</b><span>{activeCase.kind === 'mountain' ? 'mean change' : 'processed observation'}</span></div><strong className="whisper-lab-discovery-tag">RADAR CHANGE FOUND</strong></div>}</div>
        <div className="whisper-lab-scene-copy"><span className="whisper-lab-live"><span /> Earth scene</span><strong>{activeCase.name}</strong><span>{activeCase.place}</span></div><div className="whisper-lab-source-row" aria-label="Evidence sources">{activeCase.sources.map((source) => <span key={source}>{source}</span>)}</div>
        <div className="whisper-lab-companion" aria-live="polite"><div className="whisper-lab-companion-body"><i /><i /><b /><span /></div><div className="whisper-lab-speech"><strong>{companionSpeech}</strong></div></div>
        {scanState === 'scanned' && !receiverReady && <button type="button" className="whisper-lab-equipment receiver-machine" draggable aria-label="Catch the returning radar signal" onDragStart={(event) => dragStart(event, 'receiver')} onClick={captureReceiver} title="Catch the returning signal"><Radar size={34} /><b>Signal Receiver</b><small>Radar return</small><span className="machine-light" /></button>}
        {receiverReady && !dataProcessed && <button type="button" className="whisper-lab-equipment processor-machine" draggable aria-label="Feed the signal into the data processor" onDragStart={(event) => dragStart(event, 'processor')} onClick={processData} title="Feed signal into processor"><span className="processor-screen"><i /><i /><i /><i /></span><b>Data Processor</b><small>Radar data</small><span className="machine-light" /></button>}
        {dataProcessed && !matched && <button type="button" className="whisper-lab-object signal-object" draggable aria-label="Match the radar signal" onDragStart={(event) => dragStart(event, 'signal')} onClick={matchSignals} title="Drag signal to the comparison machine"><Radar size={22} /><b>{activeCase.radar.before}</b><small>Compare</small><Grip size={14} /></button>}
        {matched && !crossRadar && <button type="button" className="whisper-lab-object radar-object" draggable aria-label={`Bring ${activeCase.kind === 'river' ? 'Sentinel-1' : 'the second NISAR view'} near the radar signal`} onDragStart={(event) => dragStart(event, 'radar')} onClick={alignRadars} title="Drag near the first signal"><Radar size={21} /><b>{activeCase.kind === 'river' ? 'Sentinel-1' : 'NISAR pair'}</b><small>Near it</small><Grip size={14} /></button>}
        {crossRadar && !contextFound && <button type="button" className="whisper-lab-object context-object" draggable aria-label={activeCase.kind === 'river' ? 'Bring rain to the river' : 'Inspect the mountain terrain'} onDragStart={(event) => dragStart(event, 'context')} onClick={revealContext} title={activeCase.kind === 'river' ? 'Drag rain to the river' : 'Look at the mountain'}>{activeCase.kind === 'river' ? <CloudRain size={25} /> : <Mountain size={25} />}<b>{activeCase.kind === 'river' ? 'Rain?' : 'Look closer'}</b><Grip size={14} /></button>}
        {contextFound && !opticalViewed && <button type="button" className="whisper-lab-object camera-object" aria-label="Inspect the unclear optical view" onClick={inspectOptical} title="Inspect the view"><Camera size={25} /><b>Look</b><small>Too hazy?</small></button>}
        {opticalViewed && !complete && <div className="whisper-lab-evidence-core"><span className="whisper-lab-board-title">Earth Clue Core</span><div className="whisper-lab-core-orb"><Sparkles size={19} /></div><div className="whisper-lab-evidence-tokens"><button type="button" className={assembled.includes('radar') ? 'is-collected' : ''} onClick={() => collectToken('radar')}><Radar size={17} /><small>Radar</small></button><button type="button" className={assembled.includes('another') ? 'is-collected' : ''} onClick={() => collectToken('another')}><Eye size={17} /><small>Another view</small></button><button type="button" className={assembled.includes('context') ? 'is-collected' : ''} onClick={() => collectToken('context')}>{activeCase.kind === 'river' ? <CloudRain size={17} /> : <Mountain size={17} />}<small>{activeCase.kind === 'river' ? 'Rain' : 'Terrain'}</small></button><button type="button" className={assembled.includes('image') ? 'is-collected' : ''} onClick={() => collectToken('image')}><Camera size={17} /><small>Image</small></button></div></div>}
        {message && <div className="whisper-lab-discovery" aria-live="polite"><Sparkles size={15} /> <span>{message}</span></div>}{scanState === 'idle' && !focused && canPlay && <span className="whisper-lab-hint">Look here</span>}{scanState === 'scanning' && <span className="whisper-lab-hint is-scanning">Listening...</span>}
      </div>
      <section className="whisper-lab-game-sections" aria-label="Investigation workstations">
        <article className={`whisper-lab-game-section process-section${dataProcessed ? ' is-complete' : ''}`} onDragOver={(event) => event.preventDefault()} onDrop={dropAction}>
          <header><span className="section-orb">01</span><div><h2>Process data</h2><small>Radar data</small></div></header>
          <div className={`section-processor-machine${dataProcessed ? ' is-ready' : receiverReady ? ' is-active' : ''}`}><div className="processor-chamber"><Database size={23} /><span className="processor-wave"><i /><i /><i /><i /><i /></span></div><div className="processor-flow"><span>signal</span><i /><span>data</span></div></div>
          {receiverReady && !dataProcessed && <button type="button" className="section-drop-object is-signal" draggable onDragStart={(event) => dragStart(event, 'processor')} onClick={processData}><Radar size={17} /><span>RADAR SIGNAL</span><Grip size={12} /></button>}
          {dataProcessed && <button type="button" className="section-drop-object is-data" draggable onDragStart={(event) => dragStart(event, 'signal')} onClick={placeCompareData}><Database size={17} /><span>RADAR DATA</span><Grip size={12} /></button>}
          <p className="section-status">{dataProcessed ? 'Ready for comparison' : receiverReady ? 'Drop signal into processor' : 'Waiting for radar signal'}</p>
        </article>
        <article className={`whisper-lab-game-section compare-section${matched ? ' is-complete' : ''}`} onDragOver={(event) => event.preventDefault()} onDrop={dropAction}>
          <header><span className="section-orb blue">02</span><div><h2>Compare</h2><small>Radar observations</small></div></header>
          <div className="section-compare-machine"><div className={`compare-slot earlier${compareSlots > 0 ? ' is-filled' : ''}`}><span>Earlier</span><i /><i /><i /></div><span className="section-scanner"><GitCompareArrows size={22} /></span><div className={`compare-slot later${compareSlots > 1 ? ' is-filled' : ''}`}><span>Later</span><i /><i /><i /></div></div>
          {dataProcessed && !matched && <button type="button" className="section-drop-object is-data compare-data-object" draggable onDragStart={(event) => dragStart(event, 'signal')} onClick={placeCompareData}><Database size={16} /><span>{compareSlots === 0 ? 'RADAR DATA A' : 'RADAR DATA B'}</span><Grip size={12} /></button>}
          <button type="button" className="section-machine-action" disabled={compareSlots < 2 || matched} onClick={matchSignals}>{matched ? 'Compared' : compareSlots < 2 ? `${compareSlots}/2 views` : 'Compare signals'}</button>
          <p className="section-status">{matched ? 'Change clue produced' : 'Place two observations'}</p>
        </article>
        <article className={`whisper-lab-game-section clues-section${crossRadar && contextFound && opticalViewed ? ' is-complete' : ''}`}>
          <header><span className="section-orb purple">03</span><div><h2>Check clues</h2><small>Earth context</small></div></header>
          <div className="section-clue-equipment"><button type="button" className={crossRadar ? 'is-filled' : ''} disabled={!matched || crossRadar} onClick={alignRadars}><Radar size={24} /><small>{activeCase.kind === 'river' ? 'Sentinel-1' : 'Second radar'}</small></button><button type="button" className={contextFound ? 'is-filled' : ''} disabled={!crossRadar || contextFound} onClick={revealContext}>{activeCase.kind === 'river' ? <CloudRain size={24} /> : <Mountain size={24} />}<small>{activeCase.kind === 'river' ? 'Rain' : 'Terrain'}</small></button><button type="button" className={opticalViewed ? 'is-filled' : ''} disabled={!contextFound || opticalViewed} onClick={inspectOptical}><Camera size={24} /><small>Optical view</small></button></div>
          <p className="section-status">{opticalViewed ? 'Context checked' : matched ? 'Add the available clues' : 'Waiting for change clue'}</p>
        </article>
        <article className={`whisper-lab-game-section core-section${complete ? ' is-complete' : ''}`}>
          <header><span className="section-orb amber">04</span><div><h2>Build evidence</h2><small>Earth clue core</small></div></header>
          <div className="section-core-machine"><div className="section-core-glow"><Layers3 size={24} /></div><div className="section-core-slots"><span className={assembled.includes('radar') ? 'is-filled' : ''}>Radar</span><span className={assembled.includes('another') ? 'is-filled' : ''}>View</span><span className={assembled.includes('context') ? 'is-filled' : ''}>{activeCase.kind === 'river' ? 'Rain' : 'Terrain'}</span><span className={assembled.includes('image') ? 'is-filled' : ''}>Image</span></div></div>
          {opticalViewed && !complete && <div className="section-core-actions"><button type="button" onClick={() => collectToken('radar')}>Radar</button><button type="button" onClick={() => collectToken('another')}>View</button><button type="button" onClick={() => collectToken('context')}>{activeCase.kind === 'river' ? 'Rain' : 'Terrain'}</button><button type="button" onClick={() => collectToken('image')}>Image</button></div>}
          {!complete && <button type="button" className="investigate-now-button" disabled={assembled.length !== 4} onClick={investigateNow}>{investigated ? 'Investigated' : 'Investigate now'}</button>}
          <p className="section-status">{complete ? 'Investigation complete' : `${assembled.length}/4 evidence placed`}</p>
        </article>
      </section>
      <div className={`whisper-lab-pipeline is-${scanState}${focused ? ' has-focus' : ''}`} aria-label="How the observation becomes a finding"><span className="is-done"><Satellite size={19} /><b>Satellite</b></span><i>signal</i><span className={scanState !== 'idle' ? 'is-done' : ''}><Radar size={19} /><b>Earth</b></span><i>return</i><span className={scanState === 'processing' || scanState === 'scanned' ? 'is-done' : ''}><span className="whisper-lab-data-glyph" /><b>Data</b></span><i>compare</i><span className={matched ? 'is-done' : ''}><Eye size={19} /><b>Compare</b></span><i>clue</i><span className={complete ? 'is-done' : ''}><Sparkles size={19} /><b>Change</b></span></div>
      <div className="whisper-lab-play-strip" aria-live="polite"><span className="whisper-lab-play-copy">{complete ? 'Clues collected' : matched ? 'Bring the next clue near the place' : scanState === 'scanned' ? 'Match the signals' : focused ? 'Wake the satellite' : 'Touch the glowing place'}</span><div className="whisper-lab-mini-sources">{scanState === 'scanned' && <span><Radar size={14} /> NISAR</span>}{crossRadar && <span><Eye size={14} /> {activeCase.kind === 'river' ? 'Sentinel-1' : 'Second view'}</span>}{contextFound && <span>{activeCase.kind === 'river' ? <CloudRain size={14} /> : <Mountain size={14} />} {activeCase.kind === 'river' ? 'GPM IMERG' : 'NASADEM'}</span>}</div></div>
        {complete && <section className="whisper-lab-final" aria-live="polite"><div className="whisper-lab-complete-badge"><Sparkles size={15} /> INVESTIGATION COMPLETE <Sparkles size={15} /></div><div className="whisper-lab-final-visual"><div className="whisper-lab-mini-earth"><MapPin size={22} /></div><div className="whisper-lab-final-lines"><span /><span /><span /></div><Satellite size={28} /></div><p className="whisper-lab-eyebrow">Earth whispered a clue</p><h2>{activeCase.kind === 'river' ? 'RIVER RADAR SIGNAL DISCOVERED' : 'MOUNTAIN RADAR SIGNAL DISCOVERED'}</h2><div className="whisper-lab-final-measurement"><small>{activeCase.kind === 'mountain' ? 'COHERENCE CHANGE' : 'RADAR CHANGE'}</small><strong>{activeCase.radar.change}</strong><span>verified processed observation</span></div><p>{activeCase.kind === 'river' ? 'A measurable radar change was detected in the investigated area.' : 'A measurable radar change was detected across the investigated mountain area.'}</p><p className="whisper-lab-limitation">Scientists use additional observations to investigate what may have caused a change.</p><div className="whisper-lab-final-sources"><span>NISAR</span>{activeCase.kind === 'river' && <span>Sentinel-1</span>}{activeCase.kind === 'river' && <span>GPM IMERG</span>}{activeCase.kind === 'mountain' && <span>NASADEM</span>}</div><div className="whisper-lab-final-actions"><button type="button" onClick={resetGame}>Play again</button><button type="button" onClick={() => setSelectedCase(activeCase.kind === 'river' ? 'monda' : 'sandhya')}>Explore {activeCase.kind === 'river' ? 'Monda' : 'Sandhya'}</button><button type="button" onClick={() => setLearnMoreOpen(true)}>Learn more</button></div><div className="whisper-lab-final-nebula"><div className="whisper-lab-companion-body" aria-hidden="true"><i /><i /><b /><span /></div><p><strong>Nebula says:</strong> Ask me about the science!</p></div></section>}
        {learnMoreOpen && <div className="whisper-lab-learning-backdrop" role="presentation" onClick={() => setLearnMoreOpen(false)}><aside className="whisper-lab-learning-panel" role="dialog" aria-modal="true" aria-labelledby="whisper-lab-learning-title" onClick={(event) => event.stopPropagation()}><button type="button" className="whisper-lab-learning-close" aria-label="Close Learn more" title="Close Learn more" onClick={() => setLearnMoreOpen(false)}><X size={17} /></button><div className="whisper-lab-learning-heading"><div className="whisper-lab-companion-body" aria-hidden="true"><i /><i /><b /><span /></div><div><p className="whisper-lab-eyebrow">Nebula's field notes</p><h2 id="whisper-lab-learning-title">Learn more</h2><p>Choose a question and Nebula will answer.</p></div></div><div className="whisper-lab-learning-list">{WHISPER_LAB_LEARN_MORE.map(([question], index) => <button type="button" className={`whisper-lab-learning-question${learnQuestion === index ? ' is-selected' : ''}`} key={question} onClick={() => askLearnQuestion(index)}><span>{String(index + 1).padStart(2, '0')}</span><strong>{question}</strong></button>)}</div>{learnQuestion !== null && <div className="whisper-lab-learning-reply" aria-live="polite">{learnAnswerLoading ? <><span className="whisper-lab-learning-thinking">Nebula is thinking<span>.</span><span>.</span><span>.</span></span></> : <><small>Nebula replies</small><p>{WHISPER_LAB_LEARN_MORE[learnQuestion][1]}</p></>}</div>}</aside></div>}
    </main>
    <p className="whisper-lab-data-note">Verified Earth observation evidence</p>
    {scienceDetail && <div className="whisper-lab-drawer-backdrop" role="presentation" onClick={() => setScienceDetail(false)}><aside className="whisper-lab-drawer" role="dialog" aria-modal="true" aria-labelledby="whisper-lab-detail-title" onClick={(event) => event.stopPropagation()}><button type="button" className="whisper-lab-close" aria-label="Close science detail" title="Close science detail" onClick={() => setScienceDetail(false)}><X size={19} /></button><p className="whisper-lab-eyebrow"><BookOpen size={14} /> Science Detail</p><h2 id="whisper-lab-detail-title">{activeCase.name}</h2><p className="whisper-lab-drawer-coords"><MapPin size={15} /> {activeCase.coords}</p><div className="whisper-lab-detail-list">{activeCase.science.map((line) => <p key={line}><Check size={15} /> {line}</p>)}</div><p className="whisper-lab-detail-honesty">These are verified observations prepared by Earth Whisper. The lab does not recalculate raw satellite data in your browser.</p></aside></div>}
  </div>
}
