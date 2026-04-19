import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { AlertCircle, CheckCircle, Clock, X, User, Car, FileText, MapPin, Shield, AlertTriangle } from 'lucide-react';

const Dashboard = () => {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, fraud, secure
  const [selectedClaim, setSelectedClaim] = useState(null);
  const { token } = useAuth();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await axios.get('http://localhost:5000/history', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setClaims(res.data);
      } catch (err) {
        console.error('Failed to fetch history', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [token]);

  const filteredClaims = claims.filter(claim => {
    if (filter === 'fraud') return claim.prediction === 1;
    if (filter === 'secure') return claim.prediction === 0;
    return true;
  });

  const DetailItem = ({ label, value, icon: Icon }) => (
    <div className="detail-item">
      <label>{label}</label>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        {Icon && <Icon size={14} style={{ color: 'var(--accent)' }} />}
        <span>{value || 'N/A'}</span>
      </div>
    </div>
  );

  return (
    <div className="container" style={{ paddingTop: '3rem', paddingBottom: '5rem' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>Claim History</h1>
          <div className="glass-panel" style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
            Total Claims: {claims.length}
          </div>
        </div>
        
        <div className="tabs">
          <button 
            className={`tab-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All Claims
          </button>
          <button 
            className={`tab-btn ${filter === 'fraud' ? 'active' : ''}`}
            onClick={() => setFilter('fraud')}
          >
            High Risk
          </button>
          <button 
            className={`tab-btn ${filter === 'secure' ? 'active' : ''}`}
            onClick={() => setFilter('secure')}
          >
            Low Risk
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <p>Loading history...</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '1rem' }}>
          {filteredClaims.length === 0 ? (
            <p style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '3rem' }}>
              No {filter !== 'all' ? filter : ''} claims found.
            </p>
          ) : filteredClaims.map((claim) => (
            <div 
              key={claim.id} 
              className="glass-panel claim-card" 
              onClick={() => setSelectedClaim(claim)}
              style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
            >
              <div>
                <h3 style={{ marginBottom: '0.5rem' }}>{claim.make} - {claim.year}</h3>
                <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.875rem', color: 'var(--text-dim)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Car size={14}/> {claim.vehicle_category}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><User size={14}/> {claim.sex}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Shield size={14}/> {claim.base_policy}</span>
                </div>
              </div>
              
              <div style={{ textAlign: 'right' }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.5rem', 
                  color: claim.prediction === 1 ? 'var(--danger)' : 'var(--success)', 
                  fontWeight: '700',
                  fontSize: '1.1rem',
                  marginBottom: '0.25rem'
                }}>
                  {claim.prediction === 1 ? <AlertCircle size={20} /> : <CheckCircle size={20} />}
                  {claim.prediction === 1 ? 'High Fraud Risk' : 'Low Risk'}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  <Clock size={12} style={{ marginRight: '0.25rem' }} />
                  {new Date(claim.claim_date).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {selectedClaim && (
        <div className="modal-overlay" onClick={() => setSelectedClaim(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ 
                  width: '3rem', 
                  height: '3rem', 
                  borderRadius: '1rem', 
                  background: selectedClaim.prediction === 1 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(34, 197, 94, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: selectedClaim.prediction === 1 ? 'var(--danger)' : 'var(--success)'
                }}>
                  {selectedClaim.prediction === 1 ? <AlertTriangle size={24} /> : <Shield size={24} />}
                </div>
                <div>
                  <h2 style={{ fontSize: '1.25rem' }}>Claim Details</h2>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-dim)' }}>Claim ID: #{selectedClaim.id}</p>
                </div>
              </div>
              <button className="close-btn" onClick={() => setSelectedClaim(null)}>
                <X size={24} />
              </button>
            </div>
            
            <div className="modal-body">
              <div style={{ 
                background: 'var(--glass)', 
                padding: '1.5rem', 
                borderRadius: '1rem', 
                marginBottom: '2rem',
                border: selectedClaim.prediction === 1 ? '1px solid rgba(239, 68, 68, 0.2)' : '1px solid rgba(34, 197, 94, 0.2)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>AI Prediction Result</div>
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: '800', 
                    color: selectedClaim.prediction === 1 ? 'var(--danger)' : 'var(--success)' 
                  }}>
                    {selectedClaim.prediction === 1 ? 'High Potential for Fraud' : 'Authenticated Secure Claim'}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '2rem', fontWeight: '800' }}>
                    {(selectedClaim.probability * 100).toFixed(1)}%
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Fraud Risk Score</div>
                </div>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', fontSize: '1rem', color: 'var(--primary)' }}>
                  <Car size={18} /> Vehicle & Policy Profile
                </h3>
                <div className="detail-grid">
                  <DetailItem label="Make" value={selectedClaim.make} />
                  <DetailItem label="Category" value={selectedClaim.vehicle_category} />
                  <DetailItem label="Price Range" value={selectedClaim.vehicle_price} />
                  <DetailItem label="Year" value={selectedClaim.year} />
                  <DetailItem label="Vehicle Age" value={selectedClaim.age_of_vehicle} />
                  <DetailItem label="Policy Type" value={selectedClaim.base_policy} />
                  <DetailItem label="Agent Type" value={selectedClaim.agent_type} />
                  <DetailItem label="Other Cars Involved" value={selectedClaim.number_of_cars} />
                </div>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', fontSize: '1rem', color: 'var(--primary)' }}>
                  <User size={18} /> Policy Holder Details
                </h3>
                <div className="detail-grid">
                  <DetailItem label="Gender" value={selectedClaim.sex} />
                  <DetailItem label="Marital Status" value={selectedClaim.marital_status} />
                  <DetailItem label="Age Group" value={selectedClaim.age_of_policy_holder} />
                  <DetailItem label="Driver Rating" value={`${selectedClaim.driver_rating} / 4`} />
                </div>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', fontSize: '1rem', color: 'var(--primary)' }}>
                  <FileText size={18} /> Incident & Claim Information
                </h3>
                <div className="detail-grid">
                  <DetailItem label="Accident Area" value={selectedClaim.accident_area} icon={MapPin} />
                  <DetailItem label="Fault Party" value={selectedClaim.fault} />
                  <DetailItem label="Police Report" value={selectedClaim.police_report_filed} />
                  <DetailItem label="Witness Present" value={selectedClaim.witness_present} />
                  <DetailItem label="Policy (Accident)" value={selectedClaim.days_policy_accident} />
                  <DetailItem label="Policy (Claim)" value={selectedClaim.days_policy_claim} />
                  <DetailItem label="Past Claims" value={selectedClaim.past_number_of_claims} />
                  <DetailItem label="Supplements" value={selectedClaim.number_of_suppliments} />
                  <DetailItem label="Address Change" value={selectedClaim.address_change_claim} />
                  <DetailItem label="Analysis Date" value={new Date(selectedClaim.claim_date).toLocaleDateString()} icon={Clock} />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
