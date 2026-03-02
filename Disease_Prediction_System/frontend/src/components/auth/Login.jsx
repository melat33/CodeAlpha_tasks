import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  Link,
  InputAdornment,
  IconButton,
  Divider,
} from '@mui/material';
import { Visibility, VisibilityOff, LockOutlined, EmailOutlined } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useNotification } from '../../context/NotificationContext';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const { login } = useAuth();
  const navigate = useNavigate();
  const { showNotification } = useNotification();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error for this field
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: '',
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = validateForm();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    try {
      await login(formData.email, formData.password);
      showNotification('Login successful!', 'success');
      navigate('/dashboard');
    } catch (error) {
      showNotification(error.response?.data?.message || 'Login failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Paper
            elevation={3}
            sx={{
              p: 4,
              width: '100%',
              borderRadius: 4,
              background: 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
            }}
          >
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <img
                src="/assets/logo.svg"
                alt="Logo"
                style={{ width: 60, height: 60, marginBottom: 16 }}
              />
              <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
                Welcome Back
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Sign in to continue to Disease Prediction System
              </Typography>
            </Box>

            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                margin="normal"
                label="Email Address"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                error={!!errors.email}
                helperText={errors.email}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailOutlined color="action" />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                margin="normal"
                label="Password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange}
                error={!!errors.password}
                helperText={errors.password}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockOutlined color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <Box sx={{ textAlign: 'right', mt: 1 }}>
                <Link
                  component={RouterLink}
                  to="/forgot-password"
                  variant="body2"
                  sx={{ textDecoration: 'none' }}
                >
                  Forgot Password?
                </Link>
              </Box>

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  mt: 3,
                  mb: 2,
                  py: 1.5,
                  background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #1976d2 30%, #1cb5e0 90%)',
                  },
                }}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>

              <Divider sx={{ my: 2 }}>OR</Divider>

              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Don't have an account?{' '}
                  <Link
                    component={RouterLink}
                    to="/register"
                    sx={{ textDecoration: 'none', fontWeight: 'bold' }}
                  >
                    Sign Up
                  </Link>
                </Typography>
              </Box>
            </form>
          </Paper>
        </Box>
      </motion.div>
    </Container>
  );
};

export default Login;