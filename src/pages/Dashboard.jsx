import React from 'react';
import { Routes, Route, Navigate, NavLink } from 'react-router-dom';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { MapEntryForm } from '../components/features/MapEntryForm';
import { HowToUse } from '../components/features/HowToUse';
import { Instructions } from '../components/features/Instructions';



const Dashboard = () => {
  return (
    <DashboardLayout>
      <div className="mb-10">
        <h1 className="text-4xl font-black text-[var(--card-foreground)] mb-6 tracking-tight">
          My Dashboard
        </h1>
        

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
