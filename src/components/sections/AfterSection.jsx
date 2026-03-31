import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiberOverviewSection } from './FiberOverviewSection';
import { FiberMapSection } from './FiberMapSection';
import './sections.css';

export const AfterSection = () => {
  const [activeTab, setActiveTab] = useState('fiber');

  const tabs = [
    { id: 'fiber', label: 'Fiber Map Processing' },
    { id: 'overview', label: 'Fiber Overview Processing' }
  ];

  return (
    <motion.div 
      className="section-container" 
      style={{ gap: '1rem' }}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
    >
      
      {/* Sub-navigation Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', marginBottom: '1.5rem', position: 'relative' }}>
        {tabs.map(tab => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                position: 'relative',
                padding: '0.875rem 1.75rem',
                background: 'transparent',
                border: 'none',
                color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.95rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'color 0.2s'
              }}
            >
              {tab.label}
              {isActive && (
                <motion.div 
                  layoutId="activeTab"
                  style={{
                    position: 'absolute',
                    bottom: -1,
                    left: 0,
                    right: 0,
                    height: '2px',
                    backgroundColor: 'var(--accent-primary)',
                    zIndex: 1
                  }}
                />
              )}
            </button>
          );
        })}
      </div>

      <div style={{ minHeight: '600px', position: 'relative' }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.25 }}
          >
            {activeTab === 'fiber' && <FiberMapSection />}
            {activeTab === 'overview' && <FiberOverviewSection />}
          </motion.div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
};
