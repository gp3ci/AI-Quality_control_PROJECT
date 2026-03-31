import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Download, AlertCircle, FileCheck, FileText, Upload, DownloadCloud } from 'lucide-react';

export const InstructionsSection = () => {
  const [activeScenario, setActiveScenario] = useState(1);

  const scenarios = [
    { id: 1, title: 'Network Hub Routing Issue', hasIssue: true, message: 'CRITICAL: The selected infrastructure lacks a direct path to the main Hub. Ensure you define Splice Can parameters in the After Section to maintain topology integrity.' },
    { id: 2, title: 'Fiber Loop Validation', hasIssue: false, message: 'Topology integrity verified. No issues detected in the primary or secondary fiber loops.' },
    { id: 3, title: 'Coax Signal Attenuation Alert', hasIssue: true, message: 'WARNING: Signal attenuation exceeds 4dB limit across 3 requested sectors. Verify DPI map quality and amplifier specs before exporting analysis.' },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.05
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 260, damping: 20 } }
  };

  const activeScenarioData = scenarios.find(s => s.id === activeScenario);

  return (
    <motion.div 
      className="section-container"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div 
        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}
        variants={itemVariants}
      >
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>Workflow Scenarios</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Interactive simulation of infrastructure validation outputs.</p>
        </div>
        <Button variant="secondary" style={{ gap: '0.5rem' }}>
          <DownloadCloud size={16} /> Export Report
        </Button>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(350px, 1fr) 2fr', gap: '2rem' }}>
        {/* Left Side: Scenario List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {scenarios.map(scenario => {
            const isActive = activeScenario === scenario.id;
            return (
              <motion.div key={scenario.id} variants={itemVariants}>
                <Card 
                  onClick={() => setActiveScenario(scenario.id)}
                  style={{
                    cursor: 'pointer',
                    padding: '1.25rem',
                    border: isActive ? '2px solid var(--accent-primary)' : '1px solid var(--border-color)',
                    backgroundColor: isActive ? 'var(--bg-secondary)' : 'var(--bg-primary)',
                    boxShadow: isActive ? 'var(--shadow-md)' : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                  whileHover={{ x: 5, backgroundColor: 'var(--bg-secondary)' }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isActive && (
                    <motion.div 
                      layoutId="activeIndicator"
                      style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '4px', backgroundColor: 'var(--accent-primary)' }}
                    />
                  )}
                  <div style={{ 
                    padding: '0.5rem', borderRadius: '50%', 
                    backgroundColor: scenario.hasIssue ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                    color: scenario.hasIssue ? 'var(--error)' : 'var(--success)'
                  }}>
                    {scenario.hasIssue ? <AlertCircle size={20} /> : <FileCheck size={20} />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-primary)' }}>{scenario.title}</h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>Click to view details</p>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* Right Side: Scenario Detail Panel */}
        <motion.div variants={itemVariants} style={{ height: '100%' }}>
          <Card style={{ backgroundColor: 'var(--bg-primary)', display: 'flex', flexDirection: 'column', height: '100%', minHeight: '400px' }}>
            <AnimatePresence mode="wait">
              {activeScenarioData ? (
                <motion.div 
                  key={activeScenario}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  style={{ padding: '1rem' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                    <motion.div 
                      initial={{ rotate: -10, scale: 0.9 }}
                      animate={{ rotate: 0, scale: 1 }}
                      style={{ 
                        padding: '1rem', borderRadius: 'var(--radius-lg)', 
                        backgroundColor: activeScenarioData.hasIssue ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                        color: activeScenarioData.hasIssue ? 'var(--error)' : 'var(--success)'
                      }}
                    >
                      {activeScenarioData.hasIssue ? <AlertCircle size={32} /> : <FileCheck size={32} />}
                    </motion.div>
                    <div>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {activeScenarioData.title}
                      </h3>
                      <div style={{ 
                        display: 'inline-block', marginTop: '0.5rem', padding: '0.25rem 0.75rem', borderRadius: 'var(--radius-pill)',
                        fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px',
                        backgroundColor: activeScenarioData.hasIssue ? 'var(--error)' : 'var(--success)', color: '#fff'
                      }}>
                        {activeScenarioData.hasIssue ? 'Action Required' : 'Validated'}
                      </div>
                    </div>
                  </div>
                  
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    style={{ padding: '1.5rem', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', lineHeight: 1.6, color: 'var(--text-secondary)' }}
                  >
                    {activeScenarioData.message}
                  </motion.div>

                  {activeScenarioData.hasIssue && (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                      style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}
                    >
                      <Button variant="primary">Resolve Issue Automatically</Button>
                      <Button variant="secondary">Ignore & Proceed</Button>
                    </motion.div>
                  )}
                </motion.div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                  <FileText size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                  <p>Select a scenario to view detailed output</p>
                </div>
              )}
            </AnimatePresence>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
};
