import React, { useState } from 'react';
import { Upload, MapPin, Play } from 'lucide-react';
import { Card } from '../ui/Card';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { AnalysisProgressModal } from '../AnalysisProgressModal';

export const FiberMapSection = () => {
  const [showProgress, setShowProgress] = useState(false);

  return (
    <div style={{ animation: 'fadeIn 0.5s ease', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>Detail Fiber Map</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Provide metadata and upload the target fiber map for processing.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 2fr', gap: '2rem' }}>
        
        {/* Left Side: Metadata Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <Card>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
              <MapPin size={18} className="text-accent" />
              <h3 style={{ fontWeight: 600, margin: 0 }}>Map Details</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <Input label="Prism ID" placeholder="Enter Prism ID" />
              <Input label="Node Name" placeholder="Enter Node Name" />
              <Input label="Instance" placeholder="Enter Instance ID" />
            </div>
          </Card>
        </div>

        {/* Right Side: Map Upload */}
        <Card style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '3rem' }}>
          <h3 style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '1.5rem', textAlign: 'center' }}>Upload Target Fiber Map</h3>
          <div
            className="upload-card"
            style={{
              width: '100%', height: '240px',
              border: '2px dashed var(--border-focus)',
              backgroundColor: 'var(--accent-light)',
              cursor: 'pointer',
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1rem'
            }}
          >
            <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '1rem', borderRadius: '50%', boxShadow: 'var(--shadow-sm)' }}>
              <Upload size={32} style={{ color: 'var(--accent-primary)' }} />
            </div>
            <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>Drag and drop map file</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--accent-primary)' }}>Click to browse from computer</div>
          </div>
        </Card>

      </div>

      {/* Footer Actions */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem', paddingTop: '2rem', borderTop: '1px solid var(--border-color)' }}>
        <Button size="lg" style={{ gap: '0.5rem', padding: '0.85rem 3rem' }} onClick={() => setShowProgress(true)}>
          <Play size={18} /> Start Analysing
        </Button>
      </div>

      {showProgress && (
        <AnalysisProgressModal
          onClose={() => setShowProgress(false)}
          onDownload={() => { console.log('Downloading fiber map…'); setShowProgress(false); }}
        />
      )}
    </div>
  );
};
