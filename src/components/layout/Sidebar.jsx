import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Database, 
  Zap, 
  BookOpen,
  HelpCircle,
  LogOut
} from 'lucide-react';

const navItems = [
  { icon: Zap, label: 'Fiber', path: '/dashboard/fiber' },
  { icon: BookOpen, label: 'Fiber Overview', path: '/dashboard/fiber-overview' },
  { icon: Database, label: 'Coaxial', path: '/dashboard/coax' },
  { icon: BookOpen, label: 'Instructions', path: '/dashboard/instructions' },
  { icon: HelpCircle, label: 'How to Use', path: '/dashboard/how-to-use' },
];

export const Sidebar = () => {
  return (
    <aside className="w-64 flex flex-col py-8 bg-transparent border-r border-[var(--glass-border)] h-full">
      <div className="flex-1 flex flex-col gap-3 px-4">
        {navItems.map((item, index) => (
          <NavLink
            key={index}
            to={item.path}
            className={({ isActive }) => `
              neu-button w-full justify-start gap-4 transition-all duration-300
              ${isActive 
                ? 'opacity-100 !bg-[var(--accent)] !text-white !shadow-none' 
                : 'opacity-70 hover:opacity-100'}
            `}
          >
            <item.icon className="w-6 h-6 flex-shrink-0" />
            <span className="text-sm font-bold tracking-wide">
              {item.label}
            </span>
          </NavLink>
        ))}
      </div>

      <div className="px-4 mt-auto">
        <button className="w-full flex items-center gap-4 px-5 py-4 rounded-2xl text-slate-400 hover:bg-red-500/10 hover:text-red-500 transition-all">
          <LogOut className="w-6 h-6" />
          <span className="text-sm font-bold tracking-wide">Logout</span>
        </button>
      </div>
    </aside>
  );
};
