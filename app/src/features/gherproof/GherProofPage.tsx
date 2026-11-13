import { useCallback, useEffect, useRef, useState } from 'react'
import { AlertTriangle, ArrowLeft, ArrowRight, Check, LoaderCircle, MapPinned, Satellite, ShieldAlert, Waves } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import { GherProofWorkspace } from './GherProofWorkspace'
import { loadGherProofData } from './services/gherproofApi'
import type { GherProofData } from './services/gherproofApi'
import './gherproof.css'

export function GherProofPage(){
 const [params,setParams]=useSearchParams()
 const stage=params.get('stage')==='select'||params.get('stage')==='results'?params.get('stage'):'intro'
 const [selected,setSelected]=useState(false)
 const [loading,setLoading]=useState(false)
 const [error,setError]=useState<string|null>(null)
 const [data,setData]=useState<GherProofData|null>(null)
 const [failureList,setFailureList]=useState<string[]>([])
 const attempted=useRef(false)

 useEffect(()=>{document.title='Earth Whisper - DHARA'},[])
 const moveTo=useCallback((next:'intro'|'select'|'results',replace=false)=>setParams(next==='intro'?{}:{stage:next},{replace}),[setParams])

 const loadAnalysis=useCallback(async()=>{
  setLoading(true);setError(null);setFailureList([])
  try{
   const loaded=await loadGherProofData()
   setData(loaded.data);setFailureList(loaded.failures);attempted.current=true;setLoading(false);moveTo('results');return true
  }catch(reason){setError(reason instanceof Error?reason.message:'The DHARA evidence service could not be reached.');setLoading(false);return false}
 },[moveTo])

 useEffect(()=>{if(stage==='results'&&!data&&!loading&&!attempted.current)void loadAnalysis()},[stage,data,loading,loadAnalysis])

 async function analyze(){if(!selected)return;await loadAnalysis()}

 return <div className="gp-page page-container">
  {stage!=='results'&&<div className="gp-crumb"><span>EARTH WHISPER</span><i>/</i><strong>DHARA</strong></div>}
  {stage==='intro'&&<IntroScreen onStart={()=>moveTo('select')}/>}
  {stage==='select'&&<SelectionScreen selected={selected} onSelect={()=>setSelected(true)} loading={loading} error={error} onBack={()=>moveTo('intro')} onAnalyze={()=>void analyze()} onRetry={()=>void analyze()}/>}
  {stage==='results'&&<>
   {loading&&!data&&<div className="gp-results-loading"><LoaderCircle className="gp-spin" size={25}/><strong>Loading prepared satellite evidence…</strong><span>Connecting to registered observations, maps and comparison products.</span></div>}
   {!loading&&data&&<GherProofWorkspace data={data} failures={failureList} onRetry={()=>void loadAnalysis()} onBack={()=>moveTo('select')}/>}
   {error&&!data&&<div className="gp-load-error"><AlertTriangle size={18}/><p>{error}</p><button onClick={()=>void loadAnalysis()}>Retry evidence loading</button><button className="gp-text-button" onClick={()=>moveTo('select')}>Back to investigation</button></div>}
  </>}
 </div>
}

function IntroScreen({onStart}:{onStart:()=>void}){
 return <section className="gp-intro" aria-labelledby="gp-title">
  <div className="gp-intro-copy"><div className="gp-eyebrow"><span className="gp-eyebrow-mark"><Waves size={14}/></span> EARTH WHISPER · WATER MONITORING</div><h1 id="gp-title">DHARA</h1><h2>Seeing Water Changes. Supporting Better Decisions.</h2><p>Satellite-powered environmental monitoring and decision support.</p><p>Review reported fisheries and aquaculture incidents, compare satellite evidence, and identify locations that may benefit from field inspection.</p><div className="gp-intro-actions"><button className="gp-primary" onClick={onStart}>Open investigation <ArrowRight size={17}/></button><span><ShieldAlert size={14}/> Exploratory evidence · field verification pending</span></div></div>
  <div className="gp-intro-visual"><img src="/api/gherproof/context/sentinel2" alt="Sentinel-2 regional context image captured before the reported event"/><span className="gp-image-credit">SENTINEL-2 CONTEXT · 13 JAN 2026</span></div>
 </section>
}

function SelectionScreen({selected,onSelect,loading,error,onBack,onAnalyze,onRetry}:{selected:boolean;onSelect:()=>void;loading:boolean;error:string|null;onBack:()=>void;onAnalyze:()=>void;onRetry:()=>void}){
 return <section className="gp-select-screen" aria-labelledby="gp-select-title"><div className="gp-back-line"><button className="gp-back-button" onClick={onBack}><ArrowLeft size={15}/> Back</button><span>STEP 1 OF 2 · CHOOSE AN INVESTIGATION</span></div><div className="gp-select-heading"><div><div className="gp-eyebrow">AVAILABLE REGIONAL EVIDENCE</div><h1 id="gp-select-title">Select an investigation area</h1><p>Only scenarios with prepared satellite evidence are listed.</p></div></div>
  <button type="button" className={`gp-scenario-card ${selected?'is-selected':''}`} aria-pressed={selected} onClick={onSelect}><div className="gp-card-image"><img src="/api/gherproof/context/sentinel2" alt="Sentinel-2 regional context image captured January 13, before the reported incident"/><span className="gp-status-pill">REPORTED INVESTIGATION</span><span className="gp-card-check">{selected&&<Check size={15}/>}</span></div><div className="gp-scenario-content"><div><span className="gp-eyebrow">JANUARY 2026</span><h2>Pallimangal Fisheries Enclosure Incident</h2><p className="gp-scenario-place"><MapPinned size={14}/> Sujatpur · Manirampur, Jashore, Bangladesh</p><p className="gp-scenario-description">Reported date: January 14, 2026. Regional evidence is available; the exact enclosure boundary has not been established.</p></div><div className="gp-scenario-data"><span><Satellite size={14}/> Sentinel-1 &amp; Sentinel-2</span><span><Waves size={14}/> Two exploratory AI models</span><span className="gp-small-caution"><ShieldAlert size={14}/> Boundary not delineated</span></div></div></button>
  {error&&<div className="gp-load-error gp-load-error-compact"><AlertTriangle size={17}/><span>{error}</span><button onClick={onRetry}>Retry</button></div>}
  <div className="gp-analyze-row"><span>{selected?'Investigation selected':'Select the regional scenario to continue'}</span><button className="gp-primary" disabled={!selected||loading} onClick={onAnalyze}>{loading?<><LoaderCircle className="gp-spin" size={16}/> Loading…</>:<>Analyze Now <ArrowRight size={17}/></>}</button></div>
 </section>
}
