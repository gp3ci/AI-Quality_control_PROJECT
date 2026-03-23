import React from 'react';
import { Search, Bell, Settings, User } from 'lucide-react';
import { ThemeToggle } from '../ui/ThemeToggle';

export const Navbar = () => {
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
          SpectraMap
        </span>
      </div>

      {/* Centered Search Bar */}
      <div className="hidden md:flex flex-1 max-w-md mx-8 relative group">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-[var(--accent)] transition-colors" />
        <input 
          type="text" 
          placeholder="Search bar"
          className="w-full bg-[var(--secondary)] border-none rounded-2xl py-2.5 pl-11 pr-4 text-sm focus:ring-1 focus:ring-[var(--accent)] transition-all outline-none"
        />
      </div>

      {/* Right Side Actions */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <button className="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-[var(--secondary)] transition-colors text-slate-400 hover:text-[var(--accent)]">
            <Bell className="w-5 h-5" />
          </button>
          <button className="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-[var(--secondary)] transition-colors text-slate-400 hover:text-[var(--accent)]">
            <Settings className="w-5 h-5" />
          </button>
          <div className="h-6 w-[1px] bg-[var(--glass-border)] mx-1" />
          <ThemeToggle />
        </div>

        <div className="flex items-center gap-3 cursor-pointer group">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-bold text-[var(--card-foreground)]">Hi Devid!</p>
          </div>
          <div className="w-10 h-10 rounded-xl overflow-hidden shadow-md group-hover:ring-2 ring-[var(--accent)] transition-all">
             <img 
               src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" 
               alt="User profile"
               className="w-full h-full object-cover bg-slate-100 dark:bg-slate-800"
             />
          </div>
        </div>
      </div>
    </header>
  );
};
