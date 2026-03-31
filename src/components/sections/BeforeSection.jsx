import React from 'react';
import { motion } from 'framer-motion';
import { Download, Upload, Baseline, Zap } from 'lucide-react';
import { Card } from '../ui/Card';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import './sections.css';

export const BeforeSection = () => {
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
        <h2 className="section-title">Before Map Processing</h2>
        <p className="section-subtitle">Provide details and upload the base infrastructure map.</p>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card className="mb-6" style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <Input label="Prism ID" placeholder="Enter Prism ID" />
            <Input label="Node Name" placeholder="Enter Node Name" />
            <Input label="Instance" placeholder="Enter Instance ID" />
          </div>
        </Card>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <motion.div variants={itemVariants}>
          <Card>
            <div style={{ padding: '1rem' }}>
              <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Baseline size={20} style={{ color: 'var(--accent-primary)' }} />
                Fiber Upload
              </h3>
              <motion.div 
                className="upload-card"
                whileHover={{ y: -2, borderColor: 'var(--accent-primary)', backgroundColor: 'var(--accent-light)' }}
                whileTap={{ scale: 0.99 }}
              >
                <div className="upload-icon">
                  <Upload size={24} />
                </div>
                <div className="upload-text">Upload Fiber Map</div>
                <Button variant="secondary" style={{ marginTop: '0.5rem' }}>Browse Files</Button>
              </motion.div>
              <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1.5rem' }}>
                <Button style={{ gap: '0.6rem', width: '100%', justifyContent: 'center' }}>
                  <Download size={18} /> Download Fiber Map Processed
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card>
            <div style={{ padding: '1rem' }}>
              <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Zap size={20} style={{ color: '#f59e0b' }} />
                Coax Upload
              </h3>
              <motion.div 
                className="upload-card"
                whileHover={{ y: -2, borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.05)' }}
                whileTap={{ scale: 0.99 }}
              >
                <div className="upload-icon" style={{ color: '#f59e0b' }}>
                  <Upload size={24} />
                </div>
                <div className="upload-text">Upload Coax Map</div>
                <Button variant="secondary" style={{ marginTop: '0.5rem' }}>Browse Files</Button>
              </motion.div>
              <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1.5rem' }}>
                <Button style={{ gap: '0.6rem', width: '100%', justifyContent: 'center', backgroundColor: '#f59e0b', borderColor: '#f59e0b' }}>
                  <Download size={18} /> Download Coax Map Processed
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>


    </motion.div>
  );
};
