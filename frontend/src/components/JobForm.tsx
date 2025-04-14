import { useState } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper 
} from '@mui/material';
import WorkIcon from '@mui/icons-material/Work';

interface JobFormProps {
  onSubmit: (jobTitle: string, jobDescription: string) => void;
  loading?: boolean;
}

const JobForm = ({ onSubmit, loading = false }: JobFormProps) => {
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [titleError, setTitleError] = useState('');
  const [descriptionError, setDescriptionError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    let isValid = true;
    
    if (!jobTitle.trim()) {
      setTitleError('Job title is required');
      isValid = false;
    } else {
      setTitleError('');
    }
    
    if (!jobDescription.trim()) {
      setDescriptionError('Job description is required');
      isValid = false;
    } else {
      setDescriptionError('');
    }
    
    if (isValid) {
      onSubmit(jobTitle, jobDescription);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
        <WorkIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">Job Details</Typography>
      </Box>
      
      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="Job Title"
          variant="outlined"
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
          error={!!titleError}
          helperText={titleError}
          disabled={loading}
          margin="normal"
          placeholder="e.g. Frontend Developer, Data Scientist, Project Manager"
        />
        
        <TextField
          fullWidth
          label="Job Description"
          variant="outlined"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          error={!!descriptionError}
          helperText={descriptionError}
          disabled={loading}
          margin="normal"
          multiline
          rows={6}
          placeholder="Paste the job description here including skills, qualifications, and responsibilities..."
        />
        
        <Button 
          type="submit" 
          variant="contained" 
          fullWidth 
          disabled={loading}
          sx={{ mt: 2 }}
        >
          {loading ? 'Processing...' : 'Match Resume to Job'}
        </Button>
      </form>
    </Paper>
  );
};

export default JobForm; 