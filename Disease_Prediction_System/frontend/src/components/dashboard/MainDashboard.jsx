import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  IconButton,
  Button,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Timeline,
  ShowChart,
  Assessment,
  History,
  Notifications,
  MoreVert,
  Refresh,
  Download,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  BarElement,
  ArcElement,
} from 'chart.js';
import { useAuth } from '../../hooks/useAuth';
import { usePrediction } from '../../hooks/usePrediction';
import StatsCards from './StatsCards';
import ActivityFeed from './ActivityFeed';
import NotificationsPanel from './NotificationsPanel';
import api from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const MainDashboard = () => {
  const { user } = useAuth();
  const { getRecentPredictions } = usePrediction();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalPredictions: 0,
    accuracy: 0,
    patients: 0,
    activeUsers: 0,
  });
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [chartData, setChartData] = useState({});
  const [anchorEl, setAnchorEl] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, predictionsRes, chartRes] = await Promise.all([
        api.get('/api/stats'),
        api.get('/api/predictions/recent'),
        api.get('/api/analytics/charts'),
      ]);

      setStats(statsRes.data);
      setRecentPredictions(predictionsRes.data);
      setChartData(chartRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const predictionTrendData = {
    labels: chartData.labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Heart Disease',
        data: chartData.heart || [65, 59, 80, 81, 56, 55],
        borderColor: '#2196f3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Diabetes',
        data: chartData.diabetes || [28, 48, 40, 19, 86, 27],
        borderColor: '#f50057',
        backgroundColor: 'rgba(245, 0, 87, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Breast Cancer',
        data: chartData.cancer || [18, 30, 45, 27, 40, 35],
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const accuracyData = {
    labels: ['Logistic Regression', 'SVM', 'Random Forest', 'XGBoost'],
    datasets: [
      {
        label: 'Accuracy',
        data: [0.9649, 0.9737, 0.9737, 0.9649],
        backgroundColor: [
          'rgba(33, 150, 243, 0.8)',
          'rgba(245, 0, 87, 0.8)',
          'rgba(76, 175, 80, 0.8)',
          'rgba(255, 152, 0, 0.8)',
        ],
        borderRadius: 8,
      },
    ],
  };

  const diseaseDistribution = {
    labels: ['Heart Disease', 'Diabetes', 'Breast Cancer'],
    datasets: [
      {
        data: [42, 38, 20],
        backgroundColor: [
          'rgba(33, 150, 243, 0.8)',
          'rgba(245, 0, 87, 0.8)',
          'rgba(76, 175, 80, 0.8)',
        ],
        borderWidth: 0,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: { size: 12 },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0,0,0,0.8)',
        titleFont: { size: 14, weight: 'bold' },
        bodyFont: { size: 13 },
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          display: true,
          color: 'rgba(0,0,0,0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Welcome back, {user?.name || 'Doctor'}! 👋
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's what's happening with your disease prediction system today.
          </Typography>
        </Box>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchDashboardData}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={() => setAnchorEl(event.currentTarget)}
          >
            Export Report
          </Button>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
          >
            <MenuItem onClick={() => {}}>PDF Report</MenuItem>
            <MenuItem onClick={() => {}}>Excel Export</MenuItem>
            <MenuItem onClick={() => {}}>CSV Download</MenuItem>
          </Menu>
        </Box>
      </Box>

      {loading ? (
        <LinearProgress />
      ) : (
        <Grid container spacing={3}>
          {/* Stats Cards */}
          <Grid item xs={12}>
            <StatsCards stats={stats} />
          </Grid>

          {/* Charts Row 1 */}
          <Grid item xs={12} md={8}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Paper sx={{ p: 3, height: '100%' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" fontWeight="bold">
                    Prediction Trends
                  </Typography>
                  <IconButton size="small">
                    <MoreVert />
                  </IconButton>
                </Box>
                <Box sx={{ height: 300 }}>
                  <Line data={predictionTrendData} options={chartOptions} />
                </Box>
              </Paper>
            </motion.div>
          </Grid>

          <Grid item xs={12} md={4}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Paper sx={{ p: 3, height: '100%' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" fontWeight="bold">
                    Disease Distribution
                  </Typography>
                  <IconButton size="small">
                    <MoreVert />
                  </IconButton>
                </Box>
                <Box sx={{ height: 250 }}>
                  <Doughnut data={diseaseDistribution} options={chartOptions} />
                </Box>
              </Paper>
            </motion.div>
          </Grid>

          {/* Charts Row 2 */}
          <Grid item xs={12} md={6}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" fontWeight="bold">
                    Model Accuracy Comparison
                  </Typography>
                  <IconButton size="small">
                    <MoreVert />
                  </IconButton>
                </Box>
                <Box sx={{ height: 300 }}>
                  <Bar data={accuracyData} options={chartOptions} />
                </Box>
              </Paper>
            </motion.div>
          </Grid>

          <Grid item xs={12} md={6}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" fontWeight="bold">
                    Recent Activity
                  </Typography>
                  <Button size="small" endIcon={<History />}>
                    View All
                  </Button>
                </Box>
                <ActivityFeed predictions={recentPredictions} />
              </Paper>
            </motion.div>
          </Grid>

          {/* Notifications */}
          <Grid item xs={12}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" fontWeight="bold">
                    Notifications
                  </Typography>
                  <Chip
                    icon={<Notifications />}
                    label="3 new"
                    color="primary"
                    size="small"
                  />
                </Box>
                <NotificationsPanel />
              </Paper>
            </motion.div>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default MainDashboard;