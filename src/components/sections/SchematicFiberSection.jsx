import React, { useState } from 'react';
import { Upload, MapPin, Play } from 'lucide-react';
import { Card } from '../ui/Card';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { AnalysisProgressModal } from '../AnalysisProgressModal';

export const SchematicFiberSection = () => {
  const [showProgress, setShowProgress] = useState(false);

  return (
    <div style={{ animation: 'fadeIn 0.5s ease', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>Schematic Fiber Processing</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Provide metadata and upload the schematic maps for processing.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        
        {/* Left Side: Metadata Panel */}
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <Card style={{ height: '100%' }}>
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

        {/* Right Side: Map Uploads */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
          {/* Schematic Map 1 */}
          <Card style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '1rem' }}>
            <h3 style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem', textAlign: 'center', fontSize: '0.95rem' }}>Upload Schematic Map 1</h3>
            <div
              className="upload-card"
              style={{
                width: '100%', flex: 1,
                minHeight: '120px',
                border: '2px dashed var(--border-focus)',
                backgroundColor: 'var(--accent-light)',
                cursor: 'pointer',
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.5rem'
              }}
            >
              <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '0.75rem', borderRadius: '50%', boxShadow: 'var(--shadow-sm)' }}>
                <Upload size={24} style={{ color: 'var(--accent-primary)' }} />
              </div>
              <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>Drag and drop map file</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--accent-primary)' }}>Click to browse from computer</div>
            </div>
          </Card>

          {/* Schematic Map 2 */}
          <Card style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '1rem' }}>
            <h3 style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem', textAlign: 'center', fontSize: '0.95rem' }}>Upload Schematic Map 2</h3>
            <div
              className="upload-card"
              style={{
                width: '100%', flex: 1,
                minHeight: '120px',
                border: '2px dashed var(--border-focus)',
                backgroundColor: 'var(--accent-light)',
                cursor: 'pointer',
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.5rem'
              }}
            >
              <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '0.75rem', borderRadius: '50%', boxShadow: 'var(--shadow-sm)' }}>
                <Upload size={24} style={{ color: 'var(--accent-primary)' }} />
              </div>
              <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>Drag and drop map file</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--accent-primary)' }}>Click to browse from computer</div>
            </div>
          </Card>
        </div>

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
          onDownload={() => { console.log('Downloading schematic fiber map…'); setShowProgress(false); }}
        />
      )}
    </div>
  );
};
