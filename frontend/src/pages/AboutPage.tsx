import { Container, Typography, Box, Paper, Divider } from '@mui/material';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import WorkIcon from '@mui/icons-material/Work';
import SchoolIcon from '@mui/icons-material/School';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { GridLegacy as Grid } from '@mui/material';
const AboutPage = () => {
  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          About SkillSift
        </Typography>
        
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            What is SkillSift?
          </Typography>
          <Typography paragraph>
            SkillSift is an AI-powered resume analysis tool designed to help job seekers optimize 
            their resumes for specific job postings. By comparing your resume against job requirements,
            SkillSift identifies skill matches, gaps, and provides personalized recommendations to
            improve your chances of landing your dream job.
          </Typography>
          <Typography paragraph>
            Our advanced algorithms analyze both your resume and job descriptions to provide
            actionable insights, helping you stand out in competitive job markets.
          </Typography>
        </Paper>
        
        <Typography variant="h5" gutterBottom align="center" sx={{ mb: 3 }}>
          Key Features
        </Typography>
        
        <Grid container spacing={3}>
          <Grid xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AnalyticsIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Skill Matching
                </Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Typography>
                Sophisticated algorithms identify skills in your resume and match them against
                job requirements. Get a detailed breakdown of which skills you have and which
                ones you may need to develop.
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <WorkIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Personalized Recommendations
                </Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Typography>
                Receive targeted recommendations based on your skills, experience, and the specific
                job requirements. Learn how to highlight relevant experience and address potential
                skill gaps.
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SchoolIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Skill Development Roadmap
                </Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Typography>
                For identified skill gaps, SkillSift provides a customized development roadmap
                with resources and courses to help you enhance your qualifications and become
                a stronger candidate.
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Industry Insights
                </Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Typography>
                Get valuable industry-specific information including salary ranges, job market
                demand, and trends to help position yourself strategically in your job search.
              </Typography>
            </Paper>
          </Grid>
        </Grid>
        
        <Paper sx={{ p: 3, mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            How It Works
          </Typography>
          <Typography paragraph>
            1. <strong>Upload Your Resume</strong> - Start by uploading your resume in PDF or Word format.
          </Typography>
          <Typography paragraph>
            2. <strong>Enter Job Details</strong> - Provide the job title and description for the position you're interested in.
          </Typography>
          <Typography paragraph>
            3. <strong>Review Analysis</strong> - Receive a comprehensive analysis of how well your resume matches the job requirements.
          </Typography>
          <Typography paragraph>
            4. <strong>Apply Recommendations</strong> - Use our personalized recommendations to improve your resume and boost your chances.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};

export default AboutPage;