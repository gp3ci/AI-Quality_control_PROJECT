import React from 'react';
import { 
  FileText, 
  AlertCircle, 
  MousePointer2, 
  Layers,
  Search,
  CheckCircle,
  HelpCircle,
  ShieldCheck
} from 'lucide-react';

const sections = [
  {
    icon: FileText,
    title: "Document Requirements",
    content: [
      "Supported Formats: PDF (Vector preferred), PNG, JPG, TIFF.",
      "Resolution: 300 DPI minimum for accurate OCR detection.",
      "Maximum File Size: 50MB per map upload.",
      "Orientation: Maps must be oriented identically for alignment."
    ]
  },
  {
    icon: Layers,
    title: "Node Configuration Grid",
    content: [
      "Sys: High-level System ID (e.g., HUB name or region core).",
      "Reg: Regional code used for network partitioning.",
      "Zone & Area: Localized identifiers for specific distribution points.",
      "After Map ID: Main ID and Sub ID are required for final callouts."
    ]
  },
  {
    icon: ShieldCheck,
    title: "Best Practices",
    content: [
      "Ensure legends and scale bars do not obscure node symbols.",
      "Use 'Extreme' callout detail for complex high-density areas.",
      "Calibrate sensitivity based on line thickness in original drawings.",
      "Always include a Reference map if the topography is non-standard."
    ]
  },
  {
    icon: AlertCircle,
    title: "Troubleshooting",
    content: [
      "Misalignment: Check if maps have different cropping or margins.",
      "Missing Nodes: Increase sensitivity in the 'Set Options' stage.",
      "OCR Failure: Ensure text is not rotated more than 45 degrees.",
      "Slow Processing: Large maps lead to longer tiling stages."
    ]
  }
];

export const Instructions = () => {
  return (
    <div className="max-w-6xl mx-auto py-12 px-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 mb-16 border-b border-[var(--glass-border)] pb-12">
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[var(--accent)]/10 text-[var(--accent)] text-xs font-black uppercase tracking-widest">
            <ShieldCheck className="w-4 h-4" />
            Official Documentation
          </div>
          <h1 className="text-5xl font-black tracking-tighter text-slate-800 dark:text-white">
            Technical <span className="opacity-40">Instructions</span>
          </h1>
          <p className="text-xl text-slate-500 font-medium max-w-xl">
            Detailed guidelines for operating the SpectraMap autonomous analysis engine and interpreting results.
          </p>
        </div>
        
        <div className="neu-button !rounded-3xl p-6 flex flex-col items-center gap-2 min-w-[200px]">
          <span className="text-3xl font-black text-[var(--accent)]">v2.4.0</span>
          <span className="text-[10px] uppercase font-bold text-slate-400 tracking-widest">Engine Version</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {sections.map((section, idx) => (
          <div 
            key={idx}
            className="group bg-[var(--secondary)]/20 border border-[var(--glass-border)] rounded-[2.5rem] p-10 hover:border-[var(--accent)]/30 transition-all duration-500"
          >
            <div className="flex items-start gap-6 mb-8">
              <div className="p-4 rounded-2xl bg-[var(--card)] shadow-sm text-[var(--accent)] group-hover:scale-110 transition-transform">
                <section.icon className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-black text-slate-800 dark:text-slate-100 pt-2">
                {section.title}
              </h3>
            </div>
            
            <ul className="space-y-4">
              {section.content.map((item, i) => (
                <li key={i} className="flex items-start gap-4 text-slate-500 dark:text-slate-400 font-medium leading-relaxed">
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]/40 mt-2.5 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="mt-20 p-12 neu-button !rounded-[3rem] !items-center !text-center flex-col space-y-6">
        <div className="p-4 rounded-full bg-[var(--accent)] text-white">
          <HelpCircle className="w-10 h-10" />
        </div>
        <h3 className="text-3xl font-black text-slate-800 dark:text-white mt-4">
           Still need assistance?
        </h3>
        <p className="text-lg text-slate-500 max-w-2xl mx-auto">
          For project-specific overrides or custom rule implementation, please reach out to the core engineering team.
        </p>
        <button className="neu-button !bg-[var(--accent)] !text-white px-12 py-4 mt-4 !text-lg !shadow-xl !shadow-indigo-500/20">
          Contact Support
        </button>
      </div>
    </div>
  );
};
