import React from 'react';
import { 
  MousePointer2, 
  Upload, 
  Settings2, 
  Play, 
  Layers, 
  Cpu, 
  CheckCircle2, 
  Download,
  ArrowRight
} from 'lucide-react';
import { motion } from 'framer-motion';

const steps = [
  {
    icon: MousePointer2,
    title: "Pick your map type",
    desc: "Choose between Fiber or Coaxial analysis tracks from the dashboard.",
    color: "bg-blue-500/10 text-blue-500"
  },
  {
    icon: Upload,
    title: "Upload Maps",
    desc: "Upload BEFORE map + AFTER map (optional Reference map support).",
    color: "bg-purple-500/10 text-purple-500"
  },
  {
    icon: Settings2,
    title: "Set Options",
    desc: "Configure tile collision, sensitivity, and callout detail levels.",
    color: "bg-indigo-500/10 text-indigo-500"
  },
  {
    icon: Play,
    title: "Start Analysis",
    desc: "One click to initiate the deep-scan processing engine.",
    color: "bg-emerald-500/10 text-emerald-500"
  }
];

const stages = [
  { icon: Layers, label: "Alignment + Tiling" },
  { icon: Cpu, label: "AI Detection + OCR" },
  { icon: CheckCircle2, label: "Rule Callouts + Match" }
];

export const HowToUse = () => {
  return (
    <div className="max-w-5xl mx-auto space-y-16 py-10">
      <div className="text-center space-y-4">
        <h2 className="text-4xl font-black tracking-tight text-slate-800 dark:text-white">
          Getting Started with <span className="text-[var(--accent)]">SpectraMap</span>
        </h2>
        <p className="text-slate-500 dark:text-slate-400 max-w-2xl mx-auto text-lg">
          Master the automated network analysis workflow in a few simple steps.
        </p>
      </div>

      {/* Main Workflow Steps */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {steps.map((step, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="neu-button flex-col !items-start !text-left p-8 space-y-4 h-full !rounded-[2rem]"
          >
            <div className={`p-3 rounded-2xl ${step.color}`}>
              <step.icon className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-black text-slate-800 dark:text-slate-200">
              {idx + 1}. {step.title}
            </h3>
            <p className="text-sm text-slate-500 leading-relaxed font-medium">
              {step.desc}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Processing Engine Visualization */}
      <div className="bg-[var(--secondary)]/30 border border-[var(--glass-border)] rounded-[3rem] p-12 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-[var(--accent)]/10 blur-[100px] pointer-events-none" />
        
        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h3 className="text-3xl font-black text-slate-800 dark:text-slate-100 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-[var(--accent)] text-white text-sm flex items-center justify-center">5</span>
              Autonomous Engine processing
            </h3>
            <p className="text-lg text-slate-500 font-medium">
              Our AI engine handles the heavy lifting through three specialized technical stages.
            </p>
          </div>

          <div className="flex flex-col gap-4">
             {stages.map((stage, i) => (
               <div key={i} className="flex items-center gap-6 group">
                 <div className="w-12 h-12 flex-shrink-0 bg-[var(--card)] rounded-xl flex items-center justify-center shadow-sm group-hover:bg-[var(--accent)] group-hover:text-white transition-all">
                    <stage.icon className="w-6 h-6" />
                 </div>
                 <div className="flex-1 h-[2px] bg-slate-200 dark:bg-slate-700 hidden md:block" />
                 <span className="text-sm font-bold tracking-widest uppercase text-slate-500 group-hover:text-[var(--accent)]">
                   {stage.label}
                 </span>
               </div>
             ))}
          </div>
        </div>
      </div>

      {/* Final Step */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center space-y-8"
      >
        <div className="flex items-center justify-center gap-4 text-slate-400">
          <ArrowRight className="w-6 h-6 animate-pulse" />
          <span className="text-sm font-black uppercase tracking-[0.3em]">Phase 6-7</span>
          <ArrowRight className="w-6 h-6 animate-pulse" />
        </div>
        
        <div className="inline-flex flex-col md:flex-row items-center gap-6 p-6 bg-emerald-500/5 border border-emerald-500/20 rounded-[2.5rem]">
          <div className="flex items-center gap-4 text-emerald-600 font-bold px-6 border-r border-emerald-500/10">
            <CheckCircle2 className="w-6 h-6" />
            Analysis Complete
          </div>
          <button className="neu-button !bg-emerald-500 !text-white !border-none !shadow-lg !shadow-emerald-500/20 px-10 py-4 !text-lg">
            <Download className="w-5 h-5" />
            Download Callouts
          </button>
        </div>
      </motion.div>
    </div>
  );
};
