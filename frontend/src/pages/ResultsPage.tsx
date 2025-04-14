import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Container, 
  Box, 
  Paper, 
  CircularProgress,
  Alert,
  Button
} from '@mui/material';
import { getResults, downloadPdfReport } from '../services/api';
import DownloadIcon from '@mui/icons-material/Download';

const ResultsPage = () => {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);

  useEffect(() => {
      const fetchResults = async () => {
          try {
              const data = await getResults(id || 'latest');
              setAnalysisData(data);
              setError('');
          } catch (err: any) {
              setError('Failed to load analysis results');
              console.error(err);
          } finally {
              setLoading(false);
          }
      };

      fetchResults();
  }, [id]);

  const handleDownload = async () => {
      setDownloading(true);
      setError('');
      
      try {
          await downloadPdfReport(analysisData?.analysis_id);
      } catch (err: any) {
          setError(err.message || 'Failed to download PDF report');
      } finally {
          setDownloading(false);
      }
  };

return (
    <Container>
        <Box sx={{ my: 4 }}>
            <Button
                variant="contained"
                onClick={handleDownload}
                disabled={downloading}
                startIcon={<DownloadIcon />}
                sx={{ mb: 2 }}
            >
                {downloading ? (
                    <>
                        Downloading... 
                        <CircularProgress size={20} sx={{ ml: 1 }} />
                    </>
                ) : 'Download PDF Report'}
            </Button>
            {error && (
                <Alert 
                    severity="error" 
                    sx={{ mb: 2 }}
                    onClose={() => setError('')}
                >
                    {error}
                </Alert>
            )}
        </Box>
    </Container>
);
};

export default ResultsPage;