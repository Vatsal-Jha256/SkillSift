// src/pages/AnalyzePage.tsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  CircularProgress,
  Alert
} from '@mui/material';
import ResumeUpload from '../components/ResumeUpload';
import { analyzeResume } from '../services/api';

const AnalyzePage = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
    }
  }, [navigate]);

  // This is the function that receives the file from ResumeUpload
  const handleFileSelected = (selectedFile: File) => {
    setFile(selectedFile);
  };
  
  // This is the function to handle the actual upload and analysis

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a resume file first');
      return;
    }
    
    try {
      setIsUploading(true);
      setError('');
      
      const analysisResult = await analyzeResume(file, jobDescription);
      
      if (!analysisResult) {
        throw new Error('No analysis results received');
      }

      // Navigate to results page with the analysis ID
      navigate(`/results/${analysisResult.analysis_id || 'latest'}`);
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.message || 'Failed to analyze resume. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };
  
  return (
    <Container maxWidth="md">
      <Typography variant="h4" component="h1" gutterBottom>
        Analyze Your Resume
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}
        
        <Typography variant="h6" gutterBottom>
          Upload Resume
        </Typography>
        
        <ResumeUpload 
          onFileSelected={handleFileSelected}
          isUploading={isUploading}
          error={error}
        />
        
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Job Description (Optional)
          </Typography>
          
          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="Paste job description here to compare your resume with job requirements"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            disabled={isUploading}
          />
        </Box>
        
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!file || isUploading}
            sx={{ minWidth: 150 }}
          >
            {isUploading ? (
              <>
                Analyzing...
                <CircularProgress size={20} sx={{ ml: 1 }} />
              </>
            ) : (
              'Analyze Resume'
            )}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};
export default AnalyzePage;