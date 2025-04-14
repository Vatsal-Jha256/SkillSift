import { Container, Typography, Box, Button, Paper } from '@mui/material';
import { Link } from 'react-router-dom';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { GridLegacy as Grid } from '@mui/material';

const Home = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to SkillSift
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          AI-powered resume analysis to match your skills with job requirements
        </Typography>
        <Button
          component={Link}
          to="/analyze"
          variant="contained"
          size="large"
          startIcon={<UploadFileIcon />}
          sx={{ mt: 2 }}
        >
          Analyze Your Resume
        </Button>
        <Grid container spacing={3} sx={{ mt: 4 }}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h5" gutterBottom>
                Skill Matching
              </Typography>
              <Typography>
                Identify how well your skills match job requirements with AI-powered analysis.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h5" gutterBottom>
                Get Recommendations
              </Typography>
              <Typography>
                Receive personalized recommendations to improve your resume and close skill gaps.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h5" gutterBottom>
                Detailed Reports
              </Typography>
              <Typography>
                Access comprehensive reports showing your compatibility with job postings.
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Home;