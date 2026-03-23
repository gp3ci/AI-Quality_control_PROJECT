import React, { useState } from 'react';
import { Search, Bell, Calculator, User, X, Upload, FileSpreadsheet, PlusCircle } from 'lucide-react';
import * as XLSX from 'xlsx';
import { ThemeToggle } from '../ui/ThemeToggle';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '../ui/Button';

export const Navbar = () => {
  const [isCalcOpen, setIsCalcOpen] = useState(false);
  const [results, setResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsAnalyzing(true);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });

        const results = {
          coaxTapsCount: 0,
          coaxTapsUpgrade: 0,
          coaxActivesUpgrade: 0,
          coaxActivesUpgradeDesign: 0
        };

        const sheetNames = workbook.SheetNames;

        // Helper to find sheet name case-insensitively
        const findSheet = (name) => sheetNames.find(s => s.toLowerCase().replace(/\s/g, '') === name.toLowerCase());

        const processSheetData = (sheetName, isActives = false) => {
          const targetName = findSheet(sheetName);
          if (!targetName) return;

          const sheet = workbook.Sheets[targetName];
          const json = XLSX.utils.sheet_to_json(sheet);

          json.forEach(row => {
            const count = parseFloat(row['COUNT']) || 0;
            const upgrade = parseFloat(row['UPGRADE']) || 0;
            const design = parseFloat(row['DESIGN']) || 0;

            if (!isActives) {
              results.coaxTapsCount += count;
              results.coaxTapsUpgrade += upgrade;
            } else {
              results.coaxActivesUpgrade += upgrade;
              results.coaxActivesUpgradeDesign += (upgrade + design);
            }
          });
        };

        processSheetData('CoaxTaps');
        processSheetData('CoaxActives', true);

        setResults(results);
      } catch (err) {
        console.error("BOM Parsing Error:", err);
        alert("Failed to parse BOM file. Please ensure it follows the standard ENRGY TECH schema.");
      } finally {
        setIsAnalyzing(false);
      }
    };
    reader.readAsArrayBuffer(file);
  };

  return (
    <header className="relative z-30 flex h-20 w-full items-center justify-between px-8 bg-transparent">
      {/* Logo Section */}
      <div className="flex items-center gap-3 min-w-[200px]">
        <div className="w-10 h-10 bg-[var(--accent)] rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
        <span className="text-2xl font-bold tracking-tight text-[var(--card-foreground)]">
          ENERGY Vision
        </span>
      </div>



      {/* Right Side Actions */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <button className="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-[var(--secondary)] transition-colors text-slate-400 hover:text-[var(--accent)]">
            <Bell className="w-5 h-5" />
          </button>
          <button
            onClick={() => setIsCalcOpen(true)}
            className={`w-10 h-10 flex items-center justify-center rounded-xl transition-all duration-300 ${isCalcOpen ? 'bg-[var(--accent)] text-white shadow-lg' : 'hover:bg-[var(--secondary)] text-slate-400 hover:text-[var(--accent)]'}`}
          >
            <Calculator className="w-5 h-5" />
          </button>
          <div className="h-6 w-[1px] bg-[var(--glass-border)] mx-1" />
          <ThemeToggle />
        </div>

        <div className="flex items-center gap-3 cursor-pointer group">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-bold text-[var(--card-foreground)]">Hi Matt !</p>
          </div>
          <div className="w-10 h-10 rounded-xl overflow-hidden shadow-md group-hover:ring-2 ring-[var(--accent)] transition-all">
            <img
              src="https://api.dicebear.com/9.x/toon-head/svg?seed=George"
              alt="User profile"
              className="w-full h-full object-cover bg-slate-100 dark:bg-slate-800"
            />
          </div>
        </div>
      </div>

      {/* CSV Analysis Modal */}
      <AnimatePresence>
        {isCalcOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsCalcOpen(false)}
              className="absolute inset-0 bg-slate-900/40 backdrop-blur-md"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-xl bg-[var(--card)] border border-[var(--glass-border)] rounded-[2.5rem] p-10 shadow-2xl overflow-hidden"
            >
              {/* Background Glow */}
              <div className="absolute -top-24 -right-24 w-48 h-48 bg-[var(--accent)]/10 blur-[100px] rounded-full pointer-events-none" />

              <div className="flex justify-between items-start mb-10">
                <div className="space-y-1">
                  <h2 className="text-2xl font-black text-[var(--card-foreground)] uppercase tracking-tighter flex items-center gap-3">
                    <Calculator className="w-6 h-6 text-[var(--accent)]" />
                    BOM Calculator
                  </h2>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">ENRGY TECH BOM Analysis Tool</p>
                </div>
                <button
                  onClick={() => { setIsCalcOpen(false); setResults(null); }}
                  className="p-2 hover:bg-[var(--secondary)] rounded-xl transition-all text-slate-400"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {!results ? (
                <label className="group relative flex flex-col items-center justify-center h-64 border-2 border-dashed border-[var(--glass-border)] hover:border-[var(--accent)] rounded-[2rem] transition-all cursor-pointer bg-[var(--secondary)]/40 hover:bg-[var(--secondary)]/60 overflow-hidden">
                  <input type="file" accept=".csv, .xlsx, .xlsm" onChange={handleFileUpload} className="hidden" />
                  <div className="p-5 bg-[var(--card)] rounded-2xl shadow-sm mb-4 group-hover:scale-110 transition-transform duration-500">
                    <Upload className="w-8 h-8 text-[var(--accent)]" />
                  </div>
                  <p className="font-black text-[var(--card-foreground)] tracking-tight">Upload BOM File</p>
                  <p className="text-[10px] font-bold text-slate-400 mt-1 uppercase tracking-widest text-center px-8">Supports CSV, XLSX, and XLSM formats</p>

                  {isAnalyzing && (
                    <div className="absolute inset-0 bg-[var(--card)]/80 backdrop-blur-sm flex items-center justify-center">
                      <div className="flex flex-col items-center gap-3">
                        <div className="w-8 h-8 border-4 border-[var(--accent)]/20 border-t-[var(--accent)] rounded-full animate-spin" />
                        <span className="text-[10px] font-black uppercase text-[var(--accent)] tracking-widest">Parsing Data...</span>
                      </div>
                    </div>
                  )}
                </label>
              ) : (
                <div className="space-y-6">
                  {/* CoaxTaps Analysis */}
                  <div className="bg-[var(--secondary)]/60 p-8 rounded-[2rem] border border-[var(--glass-border)] relative overflow-hidden">
                    <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                      <FileSpreadsheet className="w-3.5 h-3.5" /> CoaxTaps Analysis
                    </h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-[var(--card)] p-5 rounded-2xl border border-[var(--glass-border)] space-y-1">
                        <span className="text-[8px] font-bold text-slate-500 uppercase tracking-tight">Sum of COUNT</span>
                        <p className="text-2xl font-black text-[var(--accent)] tracking-tighter">{results.coaxTapsCount.toLocaleString()}</p>
                      </div>
                      <div className="bg-[var(--card)] p-5 rounded-2xl border border-[var(--glass-border)] space-y-1">
                        <span className="text-[8px] font-bold text-slate-500 uppercase tracking-tight">Sum of UPGRADE</span>
                        <p className="text-2xl font-black text-[var(--accent)] tracking-tighter">{results.coaxTapsUpgrade.toLocaleString()}</p>
                      </div>
                    </div>
                  </div>

                  {/* CoaxActives Analysis */}
                  <div className="bg-[var(--accent)]/5 p-8 rounded-[2rem] border border-[var(--accent)]/20 relative overflow-hidden">
                    <div className="absolute -left-10 -bottom-10 w-32 h-32 bg-[var(--accent)]/10 blur-[50px] rounded-full pointer-events-none" />
                    <h4 className="text-[10px] font-black text-[var(--accent)] uppercase tracking-widest mb-6 flex items-center gap-2">
                      <PlusCircle className="w-3.5 h-3.5" /> CoaxActives Analysis
                    </h4>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center bg-[var(--card)] p-4 rounded-2xl border border-[var(--glass-border)] shadow-sm">
                        <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">Sum of UPGRADE Column</span>
                        <span className="text-lg font-black text-[var(--card-foreground)]">{results.coaxActivesUpgrade.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between items-center bg-[var(--card)] p-4 rounded-2xl border border-[var(--glass-border)] shadow-sm border-l-4 border-l-[var(--accent)]">
                        <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">Sum of UPGRADE & DESIGN Columns</span>
                        <span className="text-lg font-black text-[var(--accent)]">{results.coaxActivesUpgradeDesign.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => setResults(null)}
                    className="w-full py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-[var(--accent)] transition-colors"
                  >
                    Reset and Scan New BOM
                  </button>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </header>
  );
};
