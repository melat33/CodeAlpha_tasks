import React, { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Alert,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  LinearProgress,
} from '@mui/material';
import {
  Favorite,
  Healing,
  TrendingUp,
  Science,
  Info,
  CheckCircle,
  Warning,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { usePrediction } from '../../hooks/usePrediction';
import { useNotification } from '../../context/NotificationContext';
import ResultsCard from './ResultsCard';
import ExplanationView from './ExplanationView';
import PredictionForm from './PredictionForm';

const steps = ['Patient Information', 'Clinical Measurements', 'Review & Predict'];

const HeartPrediction = () => {
  const [activeStep, setActiveStep] = useState(0);
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
    thal: 2,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [errors, setErrors] = useState({});

  const { predictHeartDisease, getExplanation } = usePrediction();
  const { showNotification } = useNotification();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.name === 'sex' || e.target.name === 'fbs' || 
                       e.target.name === 'exang' || e.target.name === 'cp' ||
                       e.target.name === 'restecg' || e.target.name === 'slope' ||
                       e.target.name === 'ca' || e.target.name === 'thal'
                       ? parseInt(e.target.value) 
                       : parseFloat(e.target.value),
    });
  };

  const handleSliderChange = (name) => (e, value) => {
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const validateStep = () => {
    const newErrors = {};
    
    if (activeStep === 0) {
      if (!formData.age || formData.age < 0 || formData.age > 120) {
        newErrors.age = 'Age must be between 0 and 120';
      }
      if (formData.sex === undefined) {
        newErrors.sex = 'Please select gender';
      }
    }
    
    if (activeStep === 1) {
      if (!formData.trestbps || formData.trestbps < 80 || formData.trestbps > 200) {
        newErrors.trestbps = 'Blood pressure must be between 80 and 200';
      }
      if (!formData.chol || formData.chol < 100 || formData.chol > 600) {
        newErrors.chol = 'Cholesterol must be between 100 and 600';
      }
      if (!formData.thalach || formData.thalach < 60 || formData.thalach > 220) {
        newErrors.thalach = 'Heart rate must be between 60 and 220';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep()) {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const predictionResult = await predictHeartDisease(formData);
      setResult(predictionResult);
      
      // Get SHAP explanation
      const explanationResult = await getExplanation('heart', formData);
      setExplanation(explanationResult);
      
      showNotification('Prediction completed successfully!', 'success');
    } catch (error) {
      showNotification('Prediction failed. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setActiveStep(0);
    setResult(null);
    setExplanation(null);
    setFormData({
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
      thal: 2,
    });
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Age"
                name="age"
                type="number"
                value={formData.age}
                onChange={handleChange}
                error={!!errors.age}
                helperText={errors.age}
                InputProps={{ inputProps: { min: 0, max: 120 } }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Gender</InputLabel>
                <Select
                  name="sex"
                  value={formData.sex}
                  onChange={handleChange}
                  label="Gender"
                  error={!!errors.sex}
                >
                  <MenuItem value={0}>Female</MenuItem>
                  <MenuItem value={1}>Male</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>Chest Pain Type</Typography>
              <FormControl fullWidth>
                <Select
                  name="cp"
                  value={formData.cp}
                  onChange={handleChange}
                >
                  <MenuItem value={0}>Typical Angina</MenuItem>
                  <MenuItem value={1}>Atypical Angina</MenuItem>
                  <MenuItem value={2}>Non-anginal Pain</MenuItem>
                  <MenuItem value={3}>Asymptomatic</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        );
      
      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Resting Blood Pressure: {formData.trestbps} mm Hg
              </Typography>
              <Slider
                value={formData.trestbps}
                onChange={handleSliderChange('trestbps')}
                min={80}
                max={200}
                step={1}
                marks={[
                  { value: 80, label: '80' },
                  { value: 120, label: '120' },
                  { value: 140, label: '140' },
                  { value: 200, label: '200' },
                ]}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Serum Cholesterol: {formData.chol} mg/dl
              </Typography>
              <Slider
                value={formData.chol}
                onChange={handleSliderChange('chol')}
                min={100}
                max={600}
                step={1}
                marks={[
                  { value: 100, label: '100' },
                  { value: 200, label: '200' },
                  { value: 240, label: '240' },
                  { value: 600, label: '600' },
                ]}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Maximum Heart Rate: {formData.thalach} bpm
              </Typography>
              <Slider
                value={formData.thalach}
                onChange={handleSliderChange('thalach')}
                min={60}
                max={220}
                step={1}
                marks={[
                  { value: 60, label: '60' },
                  { value: 150, label: '150' },
                  { value: 220, label: '220' },
                ]}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                ST Depression: {formData.oldpeak}
              </Typography>
              <Slider
                value={formData.oldpeak}
                onChange={handleSliderChange('oldpeak')}
                min={0}
                max={6.2}
                step={0.1}
                marks={[
                  { value: 0, label: '0' },
                  { value: 2, label: '2' },
                  { value: 4, label: '4' },
                  { value: 6.2, label: '6.2' },
                ]}
              />
            </Grid>
          </Grid>
        );
      
      case 2:
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Alert severity="info" icon={<Info />}>
                Please review the patient information before making the prediction.
              </Alert>
            </Grid>
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Patient Summary
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Age: {formData.age} years
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Gender: {formData.sex === 0 ? 'Female' : 'Male'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Chest Pain: {['Typical Angina', 'Atypical Angina', 'Non-anginal Pain', 'Asymptomatic'][formData.cp]}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Blood Pressure: {formData.trestbps} mm Hg
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Cholesterol: {formData.chol} mg/dl
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Heart Rate: {formData.thalach} bpm
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );
      
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Favorite sx={{ fontSize: 40, color: '#f50057', mr: 2 }} />
            <Box>
              <Typography variant="h4" fontWeight="bold">
                Heart Disease Prediction
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Enter patient details to assess risk of heart disease using our ML model
              </Typography>
            </Box>
          </Box>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          <AnimatePresence mode="wait">
            {!result ? (
              <motion.div
                key="form"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                {getStepContent(activeStep)}

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
                  <Button
                    disabled={activeStep === 0}
                    onClick={handleBack}
                  >
                    Back
                  </Button>
                  <Box>
                    {activeStep === steps.length - 1 ? (
                      <Button
                        variant="contained"
                        onClick={handleSubmit}
                        disabled={loading}
                        startIcon={<Science />}
                      >
                        Predict
                      </Button>
                    ) : (
                      <Button
                        variant="contained"
                        onClick={handleNext}
                      >
                        Next
                      </Button>
                    )}
                  </Box>
                </Box>
              </motion.div>
            ) : (
              <motion.div
                key="result"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <ResultsCard result={result} onReset={handleReset} />
                {explanation && <ExplanationView explanation={explanation} />}
              </motion.div>
            )}
          </AnimatePresence>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default HeartPrediction;