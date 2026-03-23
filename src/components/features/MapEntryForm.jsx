import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileText, CheckCircle2, Download, AlertCircle, ArrowRight, Image as ImageIcon } from 'lucide-react';
import { Button } from '../ui/Button';

export const MapEntryForm = ({ title, variant = "fiber" }) => {
  const [processingStatus, setProcessingStatus] = useState('idle'); // 'idle', 'uploading', 'validating', 'completed'
  const [progress, setProgress] = useState(0);
  const [isConnectedToHub, setIsConnectedToHub] = useState(false);
  const [rareTiles, setRareTiles] = useState([
    { id: 1, img: 'https://via.placeholder.com/150?text=Tile+A', handled: false, decision: null },
    { id: 2, img: 'https://via.placeholder.com/150?text=Tile+B', handled: false, decision: null }
  ]);

  const accentColorClass = "text-[var(--accent)]";
  const borderFocusClass = "focus:ring-[var(--accent)]/50";

  const handleStartProcessing = () => {
    setProcessingStatus('uploading');

    let curProgress = 0;
    const interval = setInterval(() => {
      curProgress += Math.random() * 15;
      if (curProgress >= 100) {
        clearInterval(interval);
        setProgress(100);
        setTimeout(() => {
          setProcessingStatus('validating');
        }, 1000);
      } else {
        setProgress(curProgress);
      }
    }, 400);
  };

  const handleTileDecision = (id, decision) => {
    setRareTiles(prev => prev.map(t => t.id === id ? { ...t, handled: true, decision } : t));
  };

  const allTilesHandled = rareTiles.every(t => t.handled);

  const finalizeProcessing = () => {
    setProcessingStatus('completed');
  };

  const resetForm = () => {
    setProcessingStatus('idle');
    setProgress(0);
    setRareTiles([
      { id: 1, img: 'https://via.placeholder.com/150?text=Tile+A', handled: false, decision: null },
      { id: 2, img: 'https://via.placeholder.com/150?text=Tile+B', handled: false, decision: null }
    ]);
  };

  return (
    <div className="w-full space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">

      {/* Description */}
      <div>
        <h2 className="text-xl font-bold text-[var(--card-foreground)] flex items-center gap-3">
          <div className="w-1.5 h-6 bg-[var(--accent)] rounded-full" />
          {title}
        </h2>
        <p className="text-slate-500 mt-2 text-sm max-w-2xl">
          Upload your network comparison map sets (PDF) and define the regional metadata for the target analysis zone.
        </p>
      </div>

      {/* Unified Audit Metadata Section */}
      <div className="bg-[var(--secondary)]/40 p-8 rounded-[2.5rem] border border-[var(--glass-border)] space-y-8">
        <h3 className="text-sm font-black uppercase text-slate-500 tracking-widest flex items-center gap-2">
          <FileText className="w-4 h-4 text-[var(--accent)]" />Metadata
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Prism ID */}
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase text-slate-400 ml-1">Prism ID</label>
            <input type="text" placeholder="e.g. PID:4365279" className="w-full bg-[var(--card)] border-none rounded-xl py-3 px-5 text-xs focus:ring-1 focus:ring-[var(--accent)] outline-none shadow-sm" />
          </div>

          {/* Map Type (Autofilled) */}
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase text-slate-400 ml-1">Map Type</label>
            <input
              type="text"
              readOnly
              value={variant === 'fiber' ? 'Fiber' : (variant === 'fiber-overview' ? 'Fiber Overview' : 'Coaxial')}
              className="w-full bg-[var(--secondary)] border-none rounded-xl py-3 px-5 text-xs text-slate-500 font-bold outline-none shadow-sm cursor-not-allowed"
            />
          </div>

          {/* Node Name */}
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase text-slate-400 ml-1">Node Name</label>
            <input type="text" placeholder="e.g.NODE:EA1335" className="w-full bg-[var(--card)] border-none rounded-xl py-3 px-5 text-xs focus:ring-1 focus:ring-[var(--accent)] outline-none shadow-sm" />
          </div>

          {/* Instance */}
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase text-slate-400 ml-1">Instance</label>
            <input type="text" placeholder="e.g. INSTANCE:TWKIWI" className="w-full bg-[var(--card)] border-none rounded-xl py-3 px-5 text-xs focus:ring-1 focus:ring-[var(--accent)] outline-none shadow-sm" />
          </div>
        </div>

        {/* Constant Design Note (Only for Coax) */}
        {variant === 'coax' && (
          <div className="bg-[var(--accent)]/5 border border-[var(--accent)]/20 p-5 rounded-2xl flex items-start gap-4">
            <AlertCircle className="w-5 h-5 text-[var(--accent)] mt-0.5" />
            <div className="space-y-1">
              <p className="text-[10px] font-black text-[var(--accent)] uppercase tracking-widest">Global Engineering Requirement</p>
              <p className="text-sm font-bold text-slate-600 dark:text-slate-300">
                DESIGN NOTE: CHECK ALL ACTIVITIES AND ENSURE THEY HAVE BEEN REBALNCED PROPERLY
              </p>
            </div>
          </div>
        )}

        {/* Hub Connectivity for Fiber Overview */}
        {variant === 'fiber-overview' && (
          <div className="pt-4 border-t border-[var(--glass-border)]">
            <div className="flex items-center justify-between">
              <label className="text-xs font-black uppercase text-slate-500 tracking-wider">Connected to Hub?</label>
              <div className="flex bg-[var(--card)] p-1 rounded-xl border border-[var(--glass-border)]">
                {['No', 'Yes'].map((choice) => (
                  <button
                    key={choice}
                    onClick={() => setIsConnectedToHub(choice === 'Yes')}
                    className={`px-4 py-1.5 text-[10px] font-black uppercase rounded-lg transition-all ${(isConnectedToHub && choice === 'Yes') || (!isConnectedToHub && choice === 'No')
                      ? 'bg-[var(--accent)] text-white'
                      : 'text-slate-500'
                      }`}
                  >
                    {choice}
                  </button>
                ))}
              </div>
            </div>

            {isConnectedToHub && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="grid grid-cols-2 gap-4 pt-6"
              >
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase text-slate-400">Hub Name</label>
                  <input type="text" placeholder="Hub-A" className="w-full bg-[var(--card)] border-none rounded-xl py-3 px-5 text-xs focus:ring-1 focus:ring-[var(--accent)] outline-none shadow-sm" />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase text-slate-400">Port/Panel</label>
                  <input type="text" placeholder="P1-S2" className="w-full bg-[var(--card)] border-none rounded-xl py-3 px-5 text-xs focus:ring-1 focus:ring-[var(--accent)] outline-none shadow-sm" />
                </div>
              </motion.div>
            )}
          </div>
        )}
      </div>



      {/* Project Documentation Section (Images) */}
      <div className="space-y-6">
        <h3 className="text-sm font-black uppercase text-slate-500 tracking-widest flex items-center gap-2">
          <ImageIcon className="w-4 h-4 text-[var(--accent)]" /> Project Documentation (Images)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Survey Info */}
          <div className="group relative cursor-pointer h-40 border-2 border-dashed border-[var(--glass-border)] hover:border-[var(--accent)] rounded-[2rem] flex flex-col items-center justify-center transition-all bg-[var(--secondary)]/40 hover:bg-[var(--secondary)]/60">
            <input type="file" accept="image/*" className="absolute inset-0 opacity-0 cursor-pointer" />
            <div className="p-3 bg-[var(--card)] rounded-xl shadow-sm group-hover:scale-110 transition-transform duration-500 mb-2">
              <ImageIcon className="w-5 h-5 text-[var(--accent)]" />
            </div>
            <p className="font-bold text-xs text-[var(--card-foreground)] uppercase">Survey Info</p>
            <p className="text-[10px] text-slate-400 mt-0.5 tracking-widest">Image Upload Required</p>
          </div>

          {/* Project Design */}
          <div className="group relative cursor-pointer h-40 border-2 border-dashed border-[var(--glass-border)] hover:border-[var(--accent)] rounded-[2rem] flex flex-col items-center justify-center transition-all bg-[var(--secondary)]/40 hover:bg-[var(--secondary)]/60">
            <input type="file" accept="image/*" className="absolute inset-0 opacity-0 cursor-pointer" />
            <div className="p-3 bg-[var(--card)] rounded-xl shadow-sm group-hover:scale-110 transition-transform duration-500 mb-2">
              <ImageIcon className="w-5 h-5 text-[var(--accent)]" />
            </div>
            <p className="font-bold text-xs text-[var(--card-foreground)] uppercase">Project Design</p>
            <p className="text-[10px] text-slate-400 mt-0.5 tracking-widest">Image Upload Required</p>
          </div>
        </div>
      </div>

      {/* Map File Upload Regions (PDFs) */}
      <div className="space-y-6">
        <h3 className="text-sm font-black uppercase text-slate-500 tracking-widest flex items-center gap-2">
          <UploadCloud className="w-4 h-4 text-[var(--accent)]" /> Map Datasets (PDF)
        </h3>
        <div className={`grid grid-cols-1 ${variant === 'fiber-overview' ? '' : 'md:grid-cols-2'} gap-8`}>
          <div className="group relative cursor-pointer h-52 border-2 border-dashed border-[var(--glass-border)] hover:border-[var(--accent)] rounded-[2rem] flex flex-col items-center justify-center transition-all bg-[var(--secondary)]/40 hover:bg-[var(--secondary)]/60">
            <div className="p-4 bg-[var(--card)] rounded-2xl shadow-sm group-hover:shadow-[var(--accent)]/20 transition-all mb-4">
              <UploadCloud className="w-8 h-8 text-[var(--accent)]" />
            </div>
            <p className="font-bold text-[var(--card-foreground)] uppercase text-xs">
              {variant === 'fiber-overview' ? 'Overview Map (PDF)' : 'Before Map (PDF)'}
            </p>
            <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-widest">PDF Format Only</p>
          </div>

          {variant !== 'fiber-overview' && (
            <div className="group relative cursor-pointer h-52 border-2 border-dashed border-[var(--glass-border)] hover:border-[var(--accent)] rounded-[2rem] flex flex-col items-center justify-center transition-all bg-[var(--secondary)]/40 hover:bg-[var(--secondary)]/60">
              <div className="p-4 bg-[var(--card)] rounded-2xl shadow-sm group-hover:shadow-[var(--accent)]/20 transition-all mb-4">
                <UploadCloud className="w-8 h-8 text-[var(--accent)]" />
              </div>
              <p className="font-bold text-[var(--card-foreground)] uppercase text-xs">After Map (PDF)</p>
              <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-widest">PDF Format Only</p>
            </div>
          )}
        </div>
      </div>

      {/* Node Name Configuration (only for Coax) */}
      {variant === 'coax' && (
        <div className="bg-[var(--secondary)]/40 border border-[var(--glass-border)] p-8 rounded-[2.5rem]">
          <h3 className="text-sm font-black uppercase tracking-widest text-[var(--accent)] mb-8 flex items-center gap-3">
            <div className="w-2 h-2 bg-[var(--accent)] rounded-full animate-pulse" />
            Node Name Configuration
          </h3>

          <div className="grid grid-cols-1 lg:grid-cols-7 gap-10">
            {/* Before Section (4 Nodes) */}
            <div className="lg:col-span-4 space-y-6">
              <h4 className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-4">Before Map (4 Nodes)</h4>
              {[1, 2, 3, 4].map((i) => (
                <div key={`before-node-${i}`} className="bg-[var(--card)]/50 p-3 rounded-2xl border border-[var(--glass-border)]/50">
                  <div className="space-y-1">
                    <label className="text-[9px] font-bold uppercase text-slate-400 ml-1">Node Name {i}</label>
                    <input
                      type="text"
                      placeholder="Enter Node Name"
                      className="w-full bg-[var(--card)] border-none rounded-xl py-2.5 px-4 text-xs focus:ring-1 focus:ring-[var(--accent)] outline-none"
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Divider */}
            <div className="hidden lg:flex flex-col items-center justify-center h-full pt-6">
              <div className="w-[1px] h-full bg-gradient-to-b from-transparent via-[var(--glass-border)] to-transparent" />
            </div>

            {/* After Section (2 Nodes) */}
            <div className="lg:col-span-2 space-y-6">
              <h4 className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-4">After Map (2 Nodes)</h4>
              {[1, 2].map((i) => (
                <div key={`after-node-${i}`} className="bg-[var(--card)]/50 p-3 rounded-2xl border border-[var(--glass-border)]/50">
                  <div className="space-y-1">
                    <label className="text-[9px] font-bold uppercase text-slate-400 ml-1">Node Identifier {i === 1 ? 'A' : 'B'}</label>
                    <input
                      type="text"
                      placeholder="Enter Identifier"
                      className="w-full bg-[var(--card)] border-none rounded-xl py-2.5 px-4 text-xs focus:ring-1 focus:ring-[var(--accent)] outline-none"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Action Section */}
      <div className="flex justify-center py-6 min-h-[120px]">
        <AnimatePresence mode="wait">
          {processingStatus === 'idle' && (
            <motion.div
              key="start-btn"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, y: 10 }}
              className="w-full max-w-sm"
            >
              <button
                onClick={handleStartProcessing}
                className="neu-button w-full h-14 !text-lg !rounded-2xl"
              >
                Start Analysis Scan
              </button>
            </motion.div>
          )}

          {/* Processing State with HITL Validation */}
          {processingStatus === 'uploading' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="py-20 flex flex-col items-center justify-center space-y-8"
            >
              <div className="relative w-32 h-32">
                <svg className="w-full h-full rotate-[-90deg]">
                  <circle cx="64" cy="64" r="60" fill="none" stroke="currentColor" strokeWidth="8" className="text-[var(--secondary)]" />
                  <circle cx="64" cy="64" r="60" fill="none" stroke="currentColor" strokeWidth="8" className="text-[var(--accent)]" strokeDasharray="377" strokeDashoffset={377 - (377 * progress) / 100} strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.4s ease-out' }} />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center text-xl font-black text-[var(--accent)]">
                  {Math.round(progress)}%
                </div>
              </div>
              <div className="text-center space-y-2">
                <h3 className="text-2xl font-black text-slate-800 dark:text-white uppercase tracking-tighter">Initializing Engines...</h3>
                <p className="text-slate-400 font-bold text-sm tracking-widest">Alignment + Tiling in Progress</p>
              </div>
            </motion.div>
          )}

          {processingStatus === 'validating' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="py-10 space-y-10"
            >
              <div className="text-center space-y-3">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/10 text-amber-500 text-[10px] font-black uppercase tracking-widest">
                  <AlertCircle className="w-3.5 h-3.5" />
                  Human Analysis Required
                </div>
                <h3 className="text-3xl font-black text-slate-800 dark:text-white">Rare Case Asset Validation</h3>
                <p className="text-slate-400 font-medium max-w-xl mx-auto">
                  The AI engine has identified potential anomalies in these tiles. Please verify them based on project specifications to complete the analysis.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                {rareTiles.map(tile => (
                  <div key={tile.id} className="bg-[var(--card)] border border-[var(--glass-border)] rounded-[2.5rem] p-8 space-y-6 shadow-xl relative overflow-hidden">
                    {tile.handled && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="absolute inset-0 z-20 bg-[var(--card)]/90 backdrop-blur-sm flex items-center justify-center animate-in fade-in zoom-in duration-300">
                        <div className="flex flex-col items-center gap-4">
                          <div className={`p-4 rounded-full ${tile.decision === 'yes' ? 'bg-emerald-500' : 'bg-red-500'} text-white`}>
                            {tile.decision === 'yes' ? <CheckCircle2 className="w-10 h-10" /> : <AlertCircle className="w-10 h-10" />}
                          </div>
                          <span className="text-xl font-black uppercase tracking-widest text-slate-500">{tile.decision === 'yes' ? 'Approved' : 'Rejected'}</span>
                        </div>
                      </motion.div>
                    )}

                    <div className="aspect-video bg-[var(--secondary)] rounded-2xl overflow-hidden shadow-inner border border-[var(--glass-border)] flex items-center justify-center text-slate-300">
                      <img src={tile.img} alt={`Rare case ${tile.id}`} className="w-full h-full object-cover" />
                    </div>

                    <div className="flex flex-col gap-4">
                      <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest text-slate-400">
                        <span>Tile Coordinate: Z12-A4</span>
                        <span>Confidence: 82%</span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 pt-2">
                        <button
                          onClick={() => handleTileDecision(tile.id, 'no')}
                          className="neu-button !py-4 !rounded-2xl !bg-red-500/5 hover:!bg-red-500 !text-red-500 hover:!text-white border-transparent"
                        >
                          Skip (No)
                        </button>
                        <button
                          onClick={() => handleTileDecision(tile.id, 'yes')}
                          className="neu-button !py-4 !rounded-2xl !bg-emerald-500/5 hover:!bg-emerald-500 !text-emerald-500 hover:!text-white border-transparent"
                        >
                          Confirm (Yes)
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-center pt-8">
                <button
                  onClick={finalizeProcessing}
                  disabled={!allTilesHandled}
                  className={`neu-button px-12 py-5 !text-lg !rounded-[2rem] transition-all ${allTilesHandled
                    ? '!bg-[var(--accent)] !text-white !shadow-xl !shadow-indigo-500/20'
                    : 'opacity-30 grayscale cursor-not-allowed'
                    }`}
                >
                  Complete Final Analysis
                  <ArrowRight className="ml-2 w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {processingStatus === 'completed' && (
            <motion.div
              key="done"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center gap-6"
            >
              <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center text-emerald-500 shadow-inner">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <div className="flex gap-4">
                <button className="neu-button px-8 py-3 !bg-emerald-500 !text-white !shadow-none !border-transparent">
                  <Download className="w-4 h-4" />
                  Download Results
                </button>
                <button onClick={resetForm} className="neu-button px-8 py-3 !bg-[var(--secondary)] !text-slate-500 !shadow-none !border-transparent">
                  Dismiss
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

    </div>
  );
};
