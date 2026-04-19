import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, AlertTriangle, Send, Loader2 } from 'lucide-react';

const FraudForm = () => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  const [formData, setFormData] = useState({
    Make: 'Honda',
    AccidentArea: 'Urban',
    Sex: 'Male',
    MaritalStatus: 'Single',
    Fault: 'Policy Holder',
    VehicleCategory: 'Sedan',
    VehiclePrice: '20000 to 29000',
    Year: '1994',
    DriverRating: 1,
    Days_Policy_Accident: 'more than 30',
    Days_Policy_Claim: 'more than 30',
    PastNumberOfClaims: 'none',
    AgeOfVehicle: '3 years',
    AgeOfPolicyHolder: '26 to 30',
    PoliceReportFiled: 'No',
    WitnessPresent: 'No',
    AgentType: 'External',
    NumberOfSuppliments: 'none',
    AddressChange_Claim: 'no change',
    NumberOfCars: '1 vehicle',
    BasePolicy: 'Liability'
  });

  const options = {
    Make: ['Accura', 'BMW', 'Chevrolet', 'Dodge', 'Ferrari', 'Ford', 'Honda', 'Jaguar', 'Lexus', 'Mazda', 'Mecedes', 'Mercury', 'Nisson', 'Pontiac', 'Porche', 'Saab', 'Saturn', 'Toyota', 'VW'],
    AccidentArea: ['Rural', 'Urban'],
    Sex: ['Female', 'Male'],
    MaritalStatus: ['Divorced', 'Married', 'Single', 'Widow'],
    Fault: ['Policy Holder', 'Third Party'],
    VehicleCategory: ['Sedan', 'Sport', 'Utility'],
    VehiclePrice: ['20000 to 29000', '30000 to 39000', '40000 to 59000', '60000 to 69000', 'less than 20000', 'more than 69000'],
    Year: ['1994', '1995', '1996'],
    AgeOfVehicle: ['2 years', '3 years', '4 years', '5 years', '6 years', '7 years', 'more than 7', 'new'],
    AgeOfPolicyHolder: ['16 to 17', '18 to 20', '21 to 25', '26 to 30', '31 to 35', '36 to 40', '41 to 50', '51 to 65', 'over 65'],
    BasePolicy: ['All Perils', 'Collision', 'Liability'],
    PoliceReportFiled: ['No', 'Yes'],
    WitnessPresent: ['No', 'Yes'],
    AgentType: ['External', 'Internal'],
    Days_Policy_Accident: ['1 to 7', '15 to 30', '8 to 15', 'more than 30', 'none'],
    Days_Policy_Claim: ['15 to 30', '8 to 15', 'more than 30', 'none'],
    PastNumberOfClaims: ['1', '2 to 4', 'more than 4', 'none'],
    NumberOfSuppliments: ['1 to 2', '3 to 5', 'more than 5', 'none'],
    AddressChange_Claim: ['1 year', '2 to 3 years', '4 to 8 years', 'no change', 'under 6 months'],
    NumberOfCars: ['1 vehicle', '2 vehicles', '3 to 4', '5 to 8', 'more than 8'],
    DriverRating: [1, 2, 3, 4]
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await axios.post('http://localhost:5000/predict', formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResult(res.data);
    } catch (err) {
      alert('Prediction request failed.');
    } finally {
      setLoading(false);
    }
  };

  const renderField = (name, label) => (
    <div className="form-group" key={name}>
      <label>{label}</label>
      <select 
        className="form-input"
        value={formData[name]}
        onChange={(e) => setFormData({...formData, [name]: e.target.value})}
      >
        {options[name].map(opt => <option key={opt} value={opt}>{opt}</option>)}
      </select>
    </div>
  );

  return (
    <div className="container" style={{ padding: '3rem 0' }}>
      <h1 style={{ marginBottom: '2rem' }}>New Fraud Analysis</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem', alignItems: 'start' }}>
        <form onSubmit={handleSubmit} className="glass-panel" style={{ padding: '2rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="section">
              <h3 style={{ borderBottom: '1px solid var(--glass-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Vehicle Information</h3>
              {renderField('Make', 'Car Make')}
              {renderField('VehicleCategory', 'Category')}
              {renderField('VehiclePrice', 'Price Range')}
              {renderField('Year', 'Manufacturing Year')}
              {renderField('AgeOfVehicle', 'Vehicle Age')}
              {renderField('NumberOfCars', 'Other Cars Involved')}
            </div>
            
            <div className="section">
              <h3 style={{ borderBottom: '1px solid var(--glass-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Policy & Driver</h3>
              {renderField('Sex', 'Gender')}
              {renderField('MaritalStatus', 'Marital Status')}
              {renderField('AgeOfPolicyHolder', 'Policy Holder Age')}
              {renderField('DriverRating', 'Driver Rating')}
              {renderField('BasePolicy', 'Base Policy Type')}
              {renderField('AgentType', 'Agent Type')}
            </div>
          </div>
          
          <div className="section" style={{ marginTop: '2rem' }}>
            <h3 style={{ borderBottom: '1px solid var(--glass-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Claim Details</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
              {renderField('AccidentArea', 'Accident Area')}
              {renderField('Fault', 'Fault Party')}
              {renderField('PoliceReportFiled', 'Police Report?')}
              {renderField('WitnessPresent', 'Witness?')}
              {renderField('Days_Policy_Accident', 'Policy Days (Accident)')}
              {renderField('Days_Policy_Claim', 'Policy Days (Claim)')}
              {renderField('PastNumberOfClaims', 'Past Claims')}
              {renderField('NumberOfSuppliments', 'Supplements')}
              {renderField('AddressChange_Claim', 'Address Change')}
            </div>
          </div>

          <button type="submit" className="btn-primary" style={{ width: '100%', marginTop: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }} disabled={loading}>
            {loading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
            {loading ? 'Analyzing Data...' : 'Analyze Claim Risk'}
          </button>
        </form>

        <div className="result-side">
          {result && (
            <div className={`glass-panel ${result.is_fraud === 1 ? 'risk-high' : 'risk-low'}`} style={{ 
              padding: '2rem', 
              textAlign: 'center', 
              border: result.is_fraud === 1 ? '2px solid var(--danger)' : '2px solid var(--success)',
              position: 'sticky',
              top: '2rem'
            }}>
              {result.is_fraud === 1 ? (
                <AlertTriangle size={64} color="var(--danger)" style={{ marginBottom: '1rem' }} />
              ) : (
                <ShieldCheck size={64} color="var(--success)" style={{ marginBottom: '1rem' }} />
              )}
              <h2 style={{ color: result.is_fraud === 1 ? 'var(--danger)' : 'var(--success)', marginBottom: '1rem' }}>
                {result.is_fraud === 1 ? 'High Fraud Risk' : 'Secure Claim'}
              </h2>
              <p style={{ color: 'var(--text-dim)', marginBottom: '1.5rem' }}>
                The AI model has detected {result.is_fraud === 1 ? 'potentially fraudulent indicators' : 'no immediate red flags'} in this claim.
              </p>
              <div style={{ fontSize: '2.5rem', fontWeight: '800' }}>
                {(result.probability * 100).toFixed(1)}%
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-dim)' }}>
                Fraud Risk Score
              </div>
            </div>
          )}
          {!result && !loading && (
            <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-dim)' }}>
              <p>Enter claim details and click analyze to see the risk assessment.</p>
            </div>
          )}
          {loading && (
             <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-dim)' }}>
                <Loader2 className="animate-spin" style={{ margin: '0 auto 1rem' }} size={40} />
                <p>Synthesizing claim data with neural patterns...</p>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FraudForm;
