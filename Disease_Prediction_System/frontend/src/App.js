import React, { useState } from 'react';
import './App.css';

function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [diseaseType, setDiseaseType] = useState('heart');
  const [formData, setFormData] = useState({
    age: 55,
    sex: 1,
    cp: 0,
    trestbps: 140,
    chol: 240,
    fbs: 0,
    restecg: 1,
    thalach: 150,
    exang: 0,
    oldpeak: 2.3,
    slope: 1,
    ca: 0,
    thal: 2
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`http://localhost:5000/api/predict/${diseaseType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error('Error:', error);
      setPrediction({ error: 'Failed to get prediction' });
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch(level) {
      case 'High': return '#ff4444';
      case 'Medium': return '#ffbb33';
      case 'Low': return '#00C851';
      default: return '#33b5e5';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏥 Disease Prediction System</h1>
        <p>Machine Learning Powered Medical Diagnosis</p>
      </header>
      
      <div className="container">
        <div className="sidebar">
          <h3>Select Disease</h3>
          <button 
            className={diseaseType === 'heart' ? 'active' : ''} 
            onClick={() => setDiseaseType('heart')}
          >
            ❤️ Heart Disease
          </button>
          <button 
            className={diseaseType === 'diabetes' ? 'active' : ''} 
            onClick={() => setDiseaseType('diabetes')}
          >
            💉 Diabetes
          </button>
          <button 
            className={diseaseType === 'cancer' ? 'active' : ''} 
            onClick={() => setDiseaseType('cancer')}
          >
            🎗️ Breast Cancer
          </button>
        </div>
        
        <div className="main-content">
          <form onSubmit={handleSubmit}>
            <h2>{diseaseType.charAt(0).toUpperCase() + diseaseType.slice(1)} Prediction</h2>
            
            <div className="form-grid">
              {diseaseType === 'heart' && (
                <>
                  <div className="form-group">
                    <label>Age:</label>
                    <input 
                      type="number" 
                      value={formData.age} 
                      onChange={(e) => setFormData({...formData, age: parseInt(e.target.value)})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Sex:</label>
                    <select value={formData.sex} onChange={(e) => setFormData({...formData, sex: parseInt(e.target.value)})}>
                      <option value={0}>Female</option>
                      <option value={1}>Male</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Blood Pressure:</label>
                    <input 
                      type="number" 
                      value={formData.trestbps} 
                      onChange={(e) => setFormData({...formData, trestbps: parseInt(e.target.value)})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Cholesterol:</label>
                    <input 
                      type="number" 
                      value={formData.chol} 
                      onChange={(e) => setFormData({...formData, chol: parseInt(e.target.value)})}
                    />
                  </div>
                </>
              )}
              
              {diseaseType === 'diabetes' && (
                <>
                  <div className="form-group">
                    <label>Glucose:</label>
                    <input 
                      type="number" 
                      value={formData.glucose || 120} 
                      onChange={(e) => setFormData({...formData, glucose: parseInt(e.target.value)})}
                    />
                  </div>
                  <div className="form-group">
                    <label>BMI:</label>
                    <input 
                      type="number" 
                      value={formData.bmi || 25} 
                      onChange={(e) => setFormData({...formData, bmi: parseFloat(e.target.value)})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Age:</label>
                    <input 
                      type="number" 
                      value={formData.age} 
                      onChange={(e) => setFormData({...formData, age: parseInt(e.target.value)})}
                    />
                  </div>
                </>
              )}
              
              {diseaseType === 'cancer' && (
                <>
                  <div className="form-group">
                    <label>Radius Mean:</label>
                    <input 
                      type="number" 
                      value={formData.radius_mean || 15} 
                      onChange={(e) => setFormData({...formData, radius_mean: parseFloat(e.target.value)})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Texture Mean:</label>
                    <input 
                      type="number" 
                      value={formData.texture_mean || 20} 
                      onChange={(e) => setFormData({...formData, texture_mean: parseFloat(e.target.value)})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Perimeter Mean:</label>
                    <input 
                      type="number" 
                      value={formData.perimeter_mean || 90} 
                      onChange={(e) => setFormData({...formData, perimeter_mean: parseFloat(e.target.value)})}
                    />
                  </div>
                </>
              )}
            </div>
            
            <button type="submit" className="predict-btn" disabled={loading}>
              {loading ? 'Predicting...' : 'Predict'}
            </button>
          </form>
          
          {prediction && !prediction.error && (
            <div className="result-card">
              <h3>Prediction Result</h3>
              <div className="result-item">
                <strong>Risk Level:</strong>
                <span style={{color: getRiskColor(prediction.risk_level), fontWeight: 'bold'}}>
                  {' '}{prediction.risk_level}
                </span>
              </div>
              <div className="result-item">
                <strong>Probability:</strong> {(prediction.probability * 100).toFixed(1)}%
              </div>
              <div className="result-item">
                <strong>Status:</strong> {prediction.prediction === 1 ? '⚠️ Positive' : '✅ Negative'}
              </div>
              {prediction.tumor_type && (
                <div className="result-item">
                  <strong>Tumor Type:</strong> {prediction.tumor_type}
                </div>
              )}
            </div>
          )}
          
          {prediction && prediction.error && (
            <div className="error-card">
              Error: {prediction.error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;