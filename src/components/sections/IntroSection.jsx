import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Info, FileImage } from 'lucide-react';
import { Card } from '../ui/Card';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import './sections.css';

export const IntroSection = ({ onStart }) => {
  const [userName] = useState("Engineer");

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 260, damping: 20 } }
  };

  return (
    <motion.div 
      className="section-container"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div className="section-header" variants={itemVariants}>
        <h2 className="section-title" style={{ fontSize: '2rem' }}>Welcome, {userName}</h2>
        <p className="section-subtitle">Start by initializing a new map analysis session.</p>
      </motion.div>

      <div className="grid grid-cols-2 gap-6" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <motion.div className="flex-col gap-4" style={{ display: 'flex' }} variants={itemVariants}>
          <Card>
            <h3 className="mb-4" style={{ marginBottom: '1rem', fontWeight: 600 }}>Session Details</h3>
            <Input label="Map Name" placeholder="e.g., North District Coax Area 5" />
            
            <div className="mt-4" style={{ marginTop: '1.5rem' }}>
              <label className="ui-label" style={{ marginBottom: '0.5rem', display: 'block' }}>Screenshot Upload</label>
              <motion.div 
                className="upload-card"
                whileHover={{ borderColor: 'var(--accent-primary)', backgroundColor: 'var(--accent-light)', y: -2 }}
                whileTap={{ scale: 0.99 }}
              >
                <div className="upload-icon">
                  <FileImage size={28} />
                </div>
                <div>
                  <div className="upload-text">Click to upload or drag & drop</div>
                  <div className="upload-subtext">PNG, JPG up to 10MB</div>
                </div>
              </motion.div>
            </div>
            
            <div className="mt-4" style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
              <Button onClick={onStart} style={{ gap: '0.5rem' }}>Start Session →</Button>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="h-full bg-accent-light" style={{ height: '100%', borderLeft: '4px solid var(--accent-primary)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <Info size={24} style={{ color: 'var(--accent-primary)' }} />
              <h3 style={{ fontWeight: 600 }}>Map Upload Instructions</h3>
            </div>
            <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.75rem', lineHeight: '1.6' }}>
              {[
                "Ensure the map is clearly visible and within the supported resolution boundaries.",
                "Upload only supported formats (PNG, JPEG, PDF) for the screenshot upload field.",
                "Before and After maps must correspond to the exact same geographical boundaries for accurate analysis.",
                "Use the specific Fiber/Coax tabs depending on the network infrastructure type.",
                "Review generated alerts carefully before exporting the final approved analytical map."
              ].map((text, i) => (
                <motion.li 
                  key={i}
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + (i * 0.1) }}
                >
                  {text}
                </motion.li>
              ))}
            </ul>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
};
