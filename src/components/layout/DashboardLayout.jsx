import React from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import SoftAurora from '../ui/SoftAurora';

export const DashboardLayout = ({ children }) => {
  return (
    <div className="relative min-h-screen bg-[var(--background)] text-[var(--foreground)] transition-colors duration-300 flex overflow-hidden">
      
      {/* Background SoftAurora - Subtler for context */}
      <div className="fixed inset-0 z-0 overflow-hidden opacity-20 pointer-events-none">
        <SoftAurora
          speed={0.8}
          scale={1.2}
          brightness={1.2}
          color1="#4D9FFF"
          color2="#6D28D9"
          noiseFrequency={3}
          noiseAmplitude={1.2}
          enableMouseInteraction={false}
        />
      </div>

      {/* Main Dashboard Frame (Full Viewport) */}
      <div className="relative z-10 w-full h-screen bg-[var(--card)] flex flex-col shadow-none overflow-hidden">
        
        {/* Top Edge Glow (Full Width) */}
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[var(--accent)] to-transparent opacity-30 shadow-[0_0_20px_var(--accent)]" />
        <div className="absolute top-[-150px] left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-[var(--accent)] opacity-[0.05] blur-[120px] rounded-full pointer-events-none" />

        <Navbar />
        
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto p-4 md:p-8 lg:p-12 custom-scrollbar">
            <div className="w-full">
              {children}
            </div>
          </main>
        </div>
      </div>

    </div>
  );
};
