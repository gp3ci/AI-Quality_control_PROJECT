import React from 'react';
import { Routes, Route, Navigate, NavLink } from 'react-router-dom';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { MapEntryForm } from '../components/features/MapEntryForm';
import { HowToUse } from '../components/features/HowToUse';
import { Instructions } from '../components/features/Instructions';

const tabs = [
  { id: 'fiber', label: 'Fiber', path: '/dashboard/fiber' },
  { id: 'coax', label: 'Coaxial', path: '/dashboard/coax' },
];

const Dashboard = () => {
  return (
    <DashboardLayout>
      <div className="mb-10">
        <h1 className="text-4xl font-black text-[var(--card-foreground)] mb-6 tracking-tight">
          My Dashboard
        </h1>
        
        <div className="flex items-center gap-3 overflow-x-auto pb-2 custom-scrollbar">
          {tabs.map((tab) => (
            <NavLink
              key={tab.id}
              to={tab.path}
              className={({ isActive }) => `
                neu-button px-8 py-2.5 !text-sm whitespace-nowrap
                ${isActive 
                  ? '!bg-[var(--accent)] !text-white !shadow-none' 
                  : 'opacity-80 hover:opacity-100'}
              `}
            >
              {tab.label}
            </NavLink>
          ))}
        </div>
      </div>

      <div className="bg-[var(--secondary)]/30 rounded-[2rem] p-1 border border-[var(--glass-border)]">
        <div className="bg-[var(--card)] rounded-[1.8rem] p-8 shadow-sm">
          <Routes>
            <Route path="/" element={<Navigate to="fiber" replace />} />
            <Route path="fiber" element={<MapEntryForm title="Fiber Maps Analysis" variant="fiber" />} />
            <Route path="fiber-overview" element={<MapEntryForm title="Fiber Overview Analysis" variant="fiber-overview" />} />
            <Route path="coax" element={<MapEntryForm title="Coaxial Maps Analysis" variant="coax" />} />
            <Route path="instructions" element={<Instructions />} />
            <Route path="how-to-use" element={<HowToUse />} />
          </Routes>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
