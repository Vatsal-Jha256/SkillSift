import { useState } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  CircularProgress,
  Alert
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

interface ResumeUploadProps {
  onFileSelected: (file: File) => void;
  isUploading?: boolean;
  error?: string;
}

const ResumeUpload = ({ 
  onFileSelected, 
  isUploading = false, 
  error 
}: ResumeUploadProps) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      onFileSelected(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      onFileSelected(file);
    }
  };

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Paper
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        sx={{
          border: '2px dashed',
          borderColor: dragActive ? 'primary.main' : 'grey.300',
          borderRadius: 2,
          p: 3,
          textAlign: 'center',
          cursor: isUploading ? 'default' : 'pointer',
          backgroundColor: dragActive ? 'rgba(63, 81, 181, 0.04)' : 'inherit',
          opacity: isUploading ? 0.7 : 1,
          transition: 'all 0.2s ease',
        }}
      >
        <input
          type="file"
          id="resume-upload"
          accept=".pdf,.doc,.docx"
          onChange={handleFileChange}
          disabled={isUploading}
          style={{ display: 'none' }}
        />
        
        {isUploading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <CircularProgress size={40} />
            <Typography variant="body1" sx={{ mt: 2 }}>
              Processing Resume...
            </Typography>
          </Box>
        ) : (
          <>
            <UploadFileIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            
            <Typography variant="h6" gutterBottom>
              {selectedFile ? `Selected: ${selectedFile.name}` : 'Drag & Drop Your Resume'}
            </Typography>
            
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Supported formats: PDF, Word (.doc, .docx)
            </Typography>
            
            <Button
              component="label"
              htmlFor="resume-upload"
              variant="contained"
              sx={{ mt: 2 }}
            >
              Browse Files
            </Button>
          </>
        )}
      </Paper>
    </Box>
  );
};

export default ResumeUpload; 