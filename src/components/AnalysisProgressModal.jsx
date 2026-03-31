import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, Download, X } from 'lucide-react';

const STAGES = [
  { id: 'validate', label: 'Validating Inputs', detail: 'Checking metadata and file integrity…' },
  { id: 'extract', label: 'Extracting Symbols', detail: 'Running AI symbol detection on map tiles…' },
  { id: 'analyse', label: 'Analysing Network', detail: 'Building node topology and connectivity graph…' },
  { id: 'render', label: 'Rendering Output', detail: 'Compositing final annotated map…' },
];

export const AnalysisProgressModal = ({ onClose, onDownload }) => {
  const [currentStage, setCurrentStage] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (currentStage < STAGES.length) {
      const t = setTimeout(() => {
        if (currentStage < STAGES.length - 1) {
          setCurrentStage((s) => s + 1);
        } else {
          setDone(true);
        }
      }, 1400);
      return () => clearTimeout(t);
    }
  }, [currentStage]);

  const progress = done ? 100 : Math.round(((currentStage) / STAGES.length) * 100);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        style={{
          position: 'fixed', inset: 0,
          backgroundColor: 'rgba(0,0,0,0.6)',
          backdropFilter: 'blur(6px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 2000,
        }}
        onClick={done ? undefined : (e) => e.stopPropagation()}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 24 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 300, damping: 28 }}
          style={{
            width: '100%', maxWidth: '520px',
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-lg)',
            boxShadow: '0 32px 64px -16px rgba(0,0,0,0.5)',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div style={{
            padding: '1.25rem 1.5rem',
            borderBottom: '1px solid var(--border-color)',
            backgroundColor: 'var(--bg-secondary)',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <div>
              <h3 style={{ margin: 0, fontWeight: 700, color: 'var(--text-primary)', fontSize: '1rem' }}>
                {done ? '✅ Analysis Complete' : '⚙️ Analysis in Progress'}
              </h3>
              <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {done ? 'Your annotated map is ready to download.' : 'Please wait while your map is being processed…'}
              </p>
            </div>
            {done && (
              <button
                onClick={onClose}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}
              >
                <X size={20} />
              </button>
            )}
          </div>

          {/* Body */}
          <div style={{ padding: '2rem' }}>
            {/* Progress Bar */}
            <div style={{
              height: '8px', backgroundColor: 'var(--bg-tertiary)',
              borderRadius: 'var(--radius-pill)', overflow: 'hidden',
              marginBottom: '1.75rem',
            }}>
              <motion.div
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
                style={{
                  height: '100%',
                  borderRadius: 'var(--radius-pill)',
                  background: done
                    ? 'linear-gradient(90deg, #10b981, #34d399)'
                    : 'linear-gradient(90deg, var(--accent-primary), var(--accent-hover))',
                  boxShadow: done ? '0 0 12px rgba(16,185,129,0.4)' : '0 0 12px rgba(79,70,229,0.4)',
                }}
              />
            </div>

            {/* Stages List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {STAGES.map((stage, idx) => {
                const isCompleted = done || idx < currentStage;
                const isActive = !done && idx === currentStage;
                const isPending = !done && idx > currentStage;

                return (
                  <motion.div
                    key={stage.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.08 }}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '1rem',
                      padding: '0.85rem 1rem',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: isActive
                        ? 'var(--accent-light)'
                        : isCompleted ? 'transparent' : 'var(--bg-secondary)',
                      border: `1px solid ${isActive ? 'var(--border-focus)' : 'var(--border-color)'}`,
                      transition: 'all 0.3s ease',
                      opacity: isPending ? 0.4 : 1,
                    }}
                  >
                    {/* Icon */}
                    <div style={{ flexShrink: 0 }}>
                      {isCompleted ? (
                        <CheckCircle2 size={20} color="var(--success)" />
                      ) : isActive ? (
                        <Loader2 size={20} color="var(--accent-primary)" style={{ animation: 'spin 1s linear infinite' }} />
                      ) : (
                        <div style={{ width: 20, height: 20, borderRadius: '50%', border: '2px solid var(--border-color)' }} />
                      )}
                    </div>

                    {/* Labels */}
                    <div style={{ flex: 1 }}>
                      <div style={{
                        fontWeight: 600, fontSize: '0.9rem',
                        color: isActive ? 'var(--accent-primary)' : isCompleted ? 'var(--text-primary)' : 'var(--text-muted)',
                      }}>
                        {stage.label}
                      </div>
                      {isActive && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}
                        >
                          {stage.detail}
                        </motion.div>
                      )}
                    </div>

                    {/* Percentage badge for active */}
                    {isActive && (
                      <div style={{
                        fontSize: '0.75rem', fontWeight: 700,
                        color: 'var(--accent-primary)',
                        backgroundColor: 'var(--bg-secondary)',
                        padding: '0.2rem 0.6rem',
                        borderRadius: 'var(--radius-pill)',
                        border: '1px solid var(--border-focus)',
                      }}>
                        {progress}%
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>

            {/* Download button - appears when done */}
            <AnimatePresence>
              {done && (
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  style={{ marginTop: '1.75rem', display: 'flex', gap: '1rem' }}
                >
                  <button
                    onClick={onDownload}
                    style={{
                      flex: 1, padding: '0.9rem',
                      background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-hover))',
                      color: '#fff', border: 'none', borderRadius: 'var(--radius-md)',
                      fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
                      boxShadow: '0 4px 16px rgba(79,70,229,0.35)',
                      transition: 'transform 0.15s ease',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    <Download size={18} /> Download Map
                  </button>
                  <button
                    onClick={onClose}
                    style={{
                      padding: '0.9rem 1.5rem',
                      backgroundColor: 'var(--bg-secondary)',
                      color: 'var(--text-secondary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-md)',
                      fontWeight: 600, cursor: 'pointer',
                    }}
                  >
                    Close
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
