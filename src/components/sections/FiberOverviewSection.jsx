import React, { useState } from 'react';
import { Upload, Focus, Network, Server, Play } from 'lucide-react';
import { Card } from '../ui/Card';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { AnalysisProgressModal } from '../AnalysisProgressModal';

export const FiberOverviewSection = () => {
  const [isConnected, setIsConnected] = useState('yes');
  const [showProgress, setShowProgress] = useState(false);

  return (
    <div style={{ animation: 'fadeIn 0.5s ease', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>Fiber Overview Map</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Upload the overview map and configure hub connectivity parameters.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '2rem' }}>
        {/* Left Col: Map Metadata & Upload */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <Card>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
              <Focus size={18} className="text-accent" />
              <h3 style={{ fontWeight: 600, margin: 0 }}>Map Details</h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <Input label="Prism ID" placeholder="Enter Prism ID" />
              <Input label="Node Name" placeholder="Enter Node Name" />
              <Input label="Instance" placeholder="Enter Instance ID" />
            </div>

            <div style={{ marginTop: '2rem' }}>
              <label className="ui-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Upload Fiber Map</label>
              <div
                className="upload-card"
                style={{ border: '2px dashed var(--border-color)', backgroundColor: 'var(--bg-primary)', padding: '2rem', height: 'auto' }}
              >
                <Upload size={24} style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }} />
                <div style={{ fontSize: '0.875rem', color: 'var(--text-primary)' }}>Drag & drop map file here</div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Col: Connectivity & Actions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <Card style={{ flexGrow: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
              <Network size={18} className="text-accent" />
              <h3 style={{ fontWeight: 600, margin: 0 }}>Connectivity</h3>
            </div>
            
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Connected to Hub?</p>
            
            <div style={{ display: 'flex', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', padding: '0.35rem', border: '1px solid var(--border-color)', marginBottom: '2rem' }}>
              <button
                onClick={() => setIsConnected('yes')}
                style={{
                  flex: 1, padding: '0.75rem', border: 'none', borderRadius: 'var(--radius-sm)',
                  fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s',
                  backgroundColor: isConnected === 'yes' ? 'var(--accent-primary)' : 'transparent',
                  color: isConnected === 'yes' ? '#ffffff' : 'var(--text-secondary)',
                  boxShadow: isConnected === 'yes' ? 'var(--shadow-md)' : 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                  <Server size={16} /> Yes
                </div>
              </button>
              <button
                onClick={() => setIsConnected('no')}
                style={{
                  flex: 1, padding: '0.75rem', border: 'none', borderRadius: 'var(--radius-sm)',
                  fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s',
                  backgroundColor: isConnected === 'no' ? 'var(--accent-primary)' : 'transparent',
                  color: isConnected === 'no' ? '#ffffff' : 'var(--text-secondary)',
                  boxShadow: isConnected === 'no' ? 'var(--shadow-md)' : 'none',
                }}
              >
                No
              </button>
            </div>

            {/* Conditional Inputs */}
            {isConnected === 'yes' ? (
              <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', backgroundColor: 'var(--bg-primary)', padding: '1.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                <Input label="Hub Name" placeholder="Enter Hub Name" />
                <Input label="Port / Panel Name" placeholder="Enter Port or Panel" />
              </div>
            ) : (
              <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', backgroundColor: 'var(--bg-primary)', padding: '1.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                <Input label="Name of Splice Can" placeholder="Enter Splice Can Name" />
              </div>
            )}
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
          onDownload={() => { console.log('Downloading fiber overview map…'); setShowProgress(false); }}
        />
      )}
    </div>
  );
};
