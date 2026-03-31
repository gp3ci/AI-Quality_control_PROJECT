import React, { useState, useEffect } from 'react';
import { Upload, Play, Settings2, FileImage, X, AlertTriangle, CheckCircle2, ChevronRight, Loader2, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '../ui/Card';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

// ── Simulated flagged tiles from backend ──────────────────────────────────────
const MOCK_TILES = [
  { id: 1, label: 'Tile #A-04', location: 'Row 2 · Col 4', flag: 'Ambiguous symbol detected near node junction' },
  { id: 2, label: 'Tile #B-11', location: 'Row 5 · Col 11', flag: 'Low confidence detection on line extender' },
  { id: 3, label: 'Tile #C-07', location: 'Row 3 · Col 7', flag: 'Overlapping symbols, manual review required' },
];

// ── Analysis Progress Stage Modal ─────────────────────────────────────────────
const STAGES = [
  { id: 'init',    label: 'Initialising Engine',    detail: 'Loading model weights and configurations…' },
  { id: 'detect',  label: 'Detecting Symbols',      detail: 'Running AI inference on map tiles…' },
  { id: 'compare', label: 'Comparing Before/After', detail: 'Diffing node topologies between layers…' },
  { id: 'flag',    label: 'Flagging Anomalies',     detail: 'Surfacing tiles that need human review…' },
];

const AnalysisModal = ({ onDone }) => {
  const [stage, setStage] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => {
      if (stage < STAGES.length - 1) setStage(s => s + 1);
      else setDone(true);
    }, 1300);
    return () => clearTimeout(t);
  }, [stage]);

  const progress = done ? 100 : Math.round((stage / STAGES.length) * 100);

  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000 }}
    >
      <motion.div
        initial={{ scale: 0.9, y: 24, opacity: 0 }} animate={{ scale: 1, y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 28 }}
        style={{ width: '100%', maxWidth: '500px', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-lg)', boxShadow: '0 32px 64px -16px rgba(0,0,0,0.5)', overflow: 'hidden' }}
      >
        {/* Header */}
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)' }}>
          <h3 style={{ margin: 0, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
            {done ? '⚙️ Analysis Complete' : '⚙️ Processing Coax Analysis'}
          </h3>
          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {done ? `${MOCK_TILES.length} tiles flagged for human review.` : 'Please wait while maps are being analysed…'}
          </p>
        </div>

        {/* Body */}
        <div style={{ padding: '2rem' }}>
          {/* Progress bar */}
          <div style={{ height: '6px', backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--radius-pill)', overflow: 'hidden', marginBottom: '1.75rem' }}>
            <motion.div
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              style={{ height: '100%', borderRadius: 'var(--radius-pill)', background: done ? 'linear-gradient(90deg,#10b981,#34d399)' : 'linear-gradient(90deg,var(--accent-primary),var(--accent-hover))', boxShadow: done ? '0 0 10px rgba(16,185,129,0.4)' : '0 0 10px rgba(79,70,229,0.4)' }}
            />
          </div>

          {/* Stage list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {STAGES.map((s, i) => {
              const completed = done || i < stage;
              const active = !done && i === stage;
              return (
                <motion.div
                  key={s.id}
                  initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.07 }}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.875rem', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', backgroundColor: active ? 'var(--accent-light)' : 'transparent', border: `1px solid ${active ? 'var(--border-focus)' : 'var(--border-color)'}`, opacity: (!done && i > stage) ? 0.35 : 1, transition: 'all 0.3s ease' }}
                >
                  <div style={{ flexShrink: 0 }}>
                    {completed ? <CheckCircle2 size={18} color="var(--success)" /> :
                     active    ? <Loader2 size={18} color="var(--accent-primary)" style={{ animation: 'spin 1s linear infinite' }} /> :
                     <div style={{ width: 18, height: 18, borderRadius: '50%', border: '2px solid var(--border-color)' }} />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.875rem', color: active ? 'var(--accent-primary)' : completed ? 'var(--text-primary)' : 'var(--text-muted)' }}>{s.label}</div>
                    {active && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>{s.detail}</div>}
                  </div>
                  {active && <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--accent-primary)', backgroundColor: 'var(--bg-secondary)', padding: '0.15rem 0.55rem', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border-focus)' }}>{progress}%</div>}
                </motion.div>
              );
            })}
          </div>

          {/* Done CTA */}
          <AnimatePresence>
            {done && (
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} style={{ marginTop: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '1rem', backgroundColor: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.35)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
                  <AlertTriangle size={18} color="#f59e0b" />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#b45309' }}>{MOCK_TILES.length} tile{MOCK_TILES.length > 1 ? 's' : ''} require human verification before download.</span>
                </div>
                <button
                  onClick={onDone}
                  style={{ width: '100%', padding: '0.9rem', background: 'linear-gradient(135deg,var(--accent-primary),var(--accent-hover))', color: '#fff', border: 'none', borderRadius: 'var(--radius-md)', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', boxShadow: '0 4px 16px rgba(79,70,229,0.35)' }}
                >
                  Review Flagged Tiles <ChevronRight size={18} />
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
};

// ── Multi-Tile Verification Modal ─────────────────────────────────────────────
const TileVerificationModal = ({ tiles, onAllDone }) => {
  const [current, setCurrent] = useState(0);
  const [decisions, setDecisions] = useState({});
  const [direction, setDirection] = useState(1);

  const tile = tiles[current];
  const isLast = current === tiles.length - 1;

  const decide = (hasIssue) => {
    const updated = { ...decisions, [tile.id]: hasIssue };
    setDecisions(updated);
    if (isLast) {
      onAllDone(updated);
    } else {
      setDirection(1);
      setCurrent(c => c + 1);
    }
  };

  // Checkerboard pattern colours by tile index (simulate different tiles)
  const tileColors = ['#c7d2fe', '#fde68a', '#bbf7d0'];
  const tileBgColor = tileColors[current % tileColors.length];

  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000 }}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 28 }}
        style={{ width: '100%', maxWidth: '580px', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-lg)', boxShadow: '0 32px 64px -16px rgba(0,0,0,0.5)', overflow: 'hidden' }}
      >
        {/* Header */}
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <AlertTriangle size={20} color="#f59e0b" />
            <div>
              <h3 style={{ margin: 0, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>Human Verification Required</h3>
              <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-muted)' }}>Review each flagged tile and confirm whether an issue exists.</p>
            </div>
          </div>
          {/* Progress pills */}
          <div style={{ display: 'flex', gap: '0.35rem' }}>
            {tiles.map((_, i) => (
              <div key={i} style={{ width: 28, height: 6, borderRadius: 'var(--radius-pill)', backgroundColor: i < current ? 'var(--success)' : i === current ? 'var(--accent-primary)' : 'var(--border-color)', transition: 'all 0.3s ease' }} />
            ))}
          </div>
        </div>

        {/* Body */}
        <div style={{ padding: '2rem' }}>
          {/* Tile counter */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Tile {current + 1} of {tiles.length}
            </span>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', backgroundColor: 'var(--bg-secondary)', padding: '0.2rem 0.75rem', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border-color)' }}>
              {tile.location}
            </span>
          </div>

          {/* Animated tile image */}
          <AnimatePresence mode="wait">
            <motion.div
              key={tile.id}
              initial={{ opacity: 0, x: direction * 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -direction * 40 }}
              transition={{ duration: 0.25 }}
            >
              {/* Mock tile visual */}
              <div style={{ width: '100%', height: '260px', borderRadius: 'var(--radius-md)', backgroundColor: tileBgColor, border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '1.25rem', position: 'relative', overflow: 'hidden' }}>
                {/* Grid lines to simulate a map tile */}
                <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(var(--border-color) 1px,transparent 1px),linear-gradient(90deg,var(--border-color) 1px,transparent 1px)', backgroundSize: '32px 32px', opacity: 0.4 }} />
                <div style={{ position: 'relative', backgroundColor: 'rgba(0,0,0,0.55)', color: 'white', padding: '0.5rem 1.25rem', borderRadius: 'var(--radius-pill)', fontSize: '1rem', fontWeight: 700, letterSpacing: '0.5px' }}>
                  {tile.label}
                </div>
                <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.4)', padding: '0.4rem 1rem', borderRadius: 'var(--radius-md)', fontSize: '0.78rem', fontWeight: 600, color: '#92400e' }}>
                  <AlertTriangle size={13} color="#f59e0b" /> {tile.flag}
                </div>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Decision buttons */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <button
              onClick={() => decide(true)}
              style={{ padding: '0.9rem', backgroundColor: '#ef4444', color: '#fff', border: 'none', borderRadius: 'var(--radius-md)', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', transition: 'transform 0.15s ease', boxShadow: '0 4px 14px rgba(239,68,68,0.35)' }}
              onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-1px)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
            >
              <AlertTriangle size={18} /> Issue Exists
            </button>
            <button
              onClick={() => decide(false)}
              style={{ padding: '0.9rem', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: 'var(--radius-md)', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', transition: 'transform 0.15s ease', boxShadow: '0 4px 14px rgba(16,185,129,0.35)' }}
              onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-1px)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
            >
              <CheckCircle2 size={18} /> No Issue
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

// ── Summary Modal after all tiles reviewed ────────────────────────────────────
const SummaryModal = ({ decisions, tiles, onClose }) => {
  const issueCount = Object.values(decisions).filter(Boolean).length;
  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000 }}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20, opacity: 0 }} animate={{ scale: 1, y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 28 }}
        style={{ width: '100%', maxWidth: '500px', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-lg)', boxShadow: '0 32px 64px -16px rgba(0,0,0,0.5)', overflow: 'hidden' }}
      >
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', display: 'flex', justifyContent: 'space-between' }}>
          <h3 style={{ margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Verification Summary</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}><X size={20} /></button>
        </div>
        <div style={{ padding: '2rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ padding: '1.25rem', backgroundColor: issueCount > 0 ? 'rgba(239,68,68,0.08)' : 'var(--bg-secondary)', border: `1px solid ${issueCount > 0 ? 'rgba(239,68,68,0.3)' : 'var(--border-color)'}`, borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: issueCount > 0 ? '#ef4444' : 'var(--text-primary)' }}>{issueCount}</div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>Issues Flagged</div>
            </div>
            <div style={{ padding: '1.25rem', backgroundColor: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: '#10b981' }}>{tiles.length - issueCount}</div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>Cleared</div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.5rem' }}>
            {tiles.map(t => (
              <div key={t.id} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.65rem 0.875rem', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                {decisions[t.id] ? <AlertTriangle size={15} color="#ef4444" /> : <CheckCircle2 size={15} color="#10b981" />}
                <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{t.label}</span>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>{decisions[t.id] ? 'Issue' : 'Clear'}</span>
              </div>
            ))}
          </div>
          <button
            onClick={onClose}
            style={{ width: '100%', padding: '0.9rem', background: 'linear-gradient(135deg,var(--accent-primary),var(--accent-hover))', color: '#fff', border: 'none', borderRadius: 'var(--radius-md)', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 16px rgba(79,70,229,0.35)' }}
          >
            Download Annotated Map
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

// ── Main CoaxSection ──────────────────────────────────────────────────────────
export const CoaxSection = () => {
  const [dpi, setDpi] = useState(300);
  const [beforeNodeType, setBeforeNodeType] = useState('3x3'); // 3x3 | 4x4 | none
  const [phase, setPhase] = useState('idle'); // idle | analysis | tiles | summary
  const [decisions, setDecisions] = useState({});

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.05
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 260, damping: 20 } }
  };

  return (
    <motion.div 
      className="section-container" 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      style={{ display: 'flex', flexDirection: 'column', gap: '2rem', position: 'relative' }}
    >

      {/* Header */}
      <motion.div variants={itemVariants}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>Coax Analysis Engine</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Configure tracking parameters, assign node hierarchies, and map your coax infrastructure.</p>
      </motion.div>

      {/* Global Configuration */}
      <motion.div variants={itemVariants}>
        <Card style={{ backgroundColor: 'var(--bg-primary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
            <Settings2 size={18} className="text-accent" />
            <h3 style={{ fontWeight: 600, margin: 0 }}>Global Configuration</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
              <Input label="Prism ID" placeholder="e.g. PR-8492" />
              <Input label="Node Name" placeholder="e.g. ND-Alpha" />
              <Input label="Instance Identifier" placeholder="e.g. 01" />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
              <div>
                <label className="ui-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Resolution (DPI)</label>
                <div style={{ display: 'flex', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', padding: '0.25rem', border: '1px solid var(--border-color)' }}>
                  {[300, 600, 800].map(val => (
                    <button key={val} onClick={() => setDpi(val)} style={{ flex: 1, padding: '0.5rem', border: 'none', borderRadius: 'var(--radius-sm)', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', backgroundColor: dpi === val ? 'var(--accent-primary)' : 'transparent', color: dpi === val ? '#ffffff' : 'var(--text-secondary)', boxShadow: dpi === val ? 'var(--shadow-md)' : 'none', transition: 'all 0.2s ease' }}>
                      {val}
                    </button>
                  ))}
                </div>
                {/* DPI guidance hint */}
                <motion.div 
                  layout
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.3 }}
                  style={{
                    marginTop: '0.65rem',
                    padding: '0.6rem 0.875rem',
                    backgroundColor: dpi === 300 ? 'rgba(16,185,129,0.08)' : dpi === 600 ? 'rgba(79,70,229,0.08)' : 'rgba(245,158,11,0.08)',
                    border: `1px solid ${dpi === 300 ? 'rgba(16,185,129,0.25)' : dpi === 600 ? 'rgba(79,70,229,0.25)' : 'rgba(245,158,11,0.3)'}`,
                    borderRadius: 'var(--radius-sm)',
                    overflow: 'hidden'
                  }}
                >
                  <AnimatePresence mode="wait">
                    <motion.div 
                      key={dpi}
                      initial={{ opacity: 0, x: -5 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 5 }}
                      transition={{ duration: 0.2 }}
                      style={{ fontSize: '0.8rem', lineHeight: 1.5, color: 'var(--text-secondary)', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}
                    >
                      <Info size={14} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--accent-primary)' }} />
                      <span>
                        {dpi === 300 && <><strong style={{ color: '#059669' }}>Small map:</strong> 300 DPI is ideal for compact cable maps with fewer nodes and short spans.</>}
                        {dpi === 600 && <><strong style={{ color: 'var(--accent-primary)' }}>Medium map:</strong> 600 DPI balances detail and processing speed for moderately sized maps.</>}
                        {dpi === 800 && <><strong style={{ color: '#b45309' }}>Large map:</strong> 800 DPI is best for high-density maps with complex node structures and long cable runs.</>}
                      </span>
                    </motion.div>
                  </AnimatePresence>
                </motion.div>
              </div>
              <div>
                <label className="ui-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Base Node Grid</label>
                <div style={{ display: 'flex', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', padding: '0.25rem', border: '1px solid var(--border-color)' }}>
                  {['3x3', '4x4', 'none'].map(type => (
                    <button 
                      key={type} 
                      onClick={() => setBeforeNodeType(type)} 
                      style={{ 
                        flex: 1, 
                        padding: '0.5rem', 
                        border: 'none', 
                        borderRadius: 'var(--radius-sm)', 
                        fontWeight: 600, 
                        fontSize: '0.875rem', 
                        cursor: 'pointer', 
                        backgroundColor: beforeNodeType === type ? 'var(--accent-primary)' : 'transparent', 
                        color: beforeNodeType === type ? '#ffffff' : 'var(--text-secondary)', 
                        boxShadow: beforeNodeType === type ? 'var(--shadow-md)' : 'none', 
                        transition: 'all 0.2s ease',
                        textTransform: 'capitalize'
                      }}
                    >
                      {type === 'none' ? 'None' : `${type} Nodes`}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Before / After Split */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)', gap: '2rem' }}>
        {/* Before */}
        <motion.div variants={itemVariants}>
          <Card style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-tertiary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileImage size={18} className="text-secondary" />
                <h3 style={{ fontWeight: 600, margin: 0 }}>Before Map Layer</h3>
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Step 1</div>
            </div>
            <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', flexGrow: 1 }}>
              <motion.div 
                className="upload-card" 
                whileHover={{ y: -2, borderColor: 'var(--accent-primary)', backgroundColor: 'var(--accent-light)' }}
                whileTap={{ scale: 0.99 }}
                style={{ height: '200px', border: '2px dashed var(--border-color)', backgroundColor: 'var(--bg-primary)' }}
              >
                <div className="upload-icon" style={{ backgroundColor: 'var(--bg-secondary)', color: 'var(--text-secondary)' }}><Upload size={24} /></div>
                <div>
                  <div style={{ fontWeight: 500, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>Upload Before Map PDF</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Drag & Drop required</div>
                </div>
              </motion.div>
              <AnimatePresence mode="wait">
                {beforeNodeType !== 'none' ? (
                  <motion.div 
                    key="node-inputs"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '1rem' }}>
                      Source Nodes ({beforeNodeType === '3x3' ? '3' : '4'} Required)
                    </h4>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <Input placeholder="Node Name 1" />
                      <Input placeholder="Node Name 2" />
                      <Input placeholder="Node Name 3" />
                      {beforeNodeType === '4x4' && <Input placeholder="Node Name 4" />}
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    key="no-nodes"
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    style={{ 
                      padding: '1.25rem', 
                      backgroundColor: 'var(--bg-secondary)', 
                      borderRadius: 'var(--radius-md)', 
                      border: '1px dashed var(--border-color)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      color: 'var(--text-muted)'
                    }}
                  >
                    <CheckCircle2 size={18} className="text-success" />
                    <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>No node names required for this analysis.</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </Card>
        </motion.div>

        {/* After */}
        <motion.div variants={itemVariants}>
          <Card style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', border: '1px solid var(--border-focus)' }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-focus)', backgroundColor: 'var(--accent-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileImage size={18} className="text-accent" />
                <h3 style={{ fontWeight: 600, margin: 0, color: 'var(--accent-primary)' }}>After Map Overlay</h3>
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-primary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Step 2</div>
            </div>
            <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', flexGrow: 1 }}>
              <motion.div 
                className="upload-card" 
                whileHover={{ y: -2, borderColor: 'var(--accent-primary)', backgroundColor: 'var(--accent-light)' }}
                whileTap={{ scale: 0.99 }}
                style={{ height: '200px', border: '2px dashed var(--border-focus)', backgroundColor: 'transparent' }}
              >
                <div className="upload-icon" style={{ backgroundColor: 'var(--accent-light)', color: 'var(--accent-primary)' }}><Upload size={24} /></div>
                <div>
                  <div style={{ fontWeight: 500, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>Upload After Map PDF</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--accent-primary)' }}>Must process Before map first</div>
                </div>
              </motion.div>
              <AnimatePresence mode="wait">
                {beforeNodeType !== 'none' ? (
                  <motion.div 
                    key="after-node-inputs"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '1rem' }}>Destination Nodes (2 Required)</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <Input placeholder="After Node 1" /><Input placeholder="After Node 2" />
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    key="after-no-nodes"
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    style={{ 
                      padding: '1.25rem', 
                      backgroundColor: 'var(--bg-secondary)', 
                      borderRadius: 'var(--radius-md)', 
                      border: '1px dashed var(--border-color)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      color: 'var(--text-muted)'
                    }}
                  >
                    <CheckCircle2 size={18} className="text-success" />
                    <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>No destination nodes required.</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.div 
        variants={itemVariants}
        style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '2rem', borderTop: '1px solid var(--border-color)' }}
      >
        <Button size="lg" style={{ gap: '0.5rem', padding: '0.85rem 3rem' }} onClick={() => setPhase('analysis')}>
          <Play size={18} /> Start Sequence
        </Button>
      </motion.div>

      {/* Phase Modals */}
      <AnimatePresence>
        {phase === 'analysis' && <AnalysisModal onDone={() => setPhase('tiles')} />}
        {phase === 'tiles' && (
          <TileVerificationModal
            tiles={MOCK_TILES}
            onAllDone={(d) => { setDecisions(d); setPhase('summary'); }}
          />
        )}
        {phase === 'summary' && (
          <SummaryModal
            tiles={MOCK_TILES}
            decisions={decisions}
            onClose={() => setPhase('idle')}
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
};
