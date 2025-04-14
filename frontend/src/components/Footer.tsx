import { Box, Container, Typography, Link as MuiLink } from '@mui/material';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <Box 
      component="footer" 
      sx={{ 
        py: 3, 
        mt: 'auto', 
        backgroundColor: (theme) => theme.palette.grey[100] 
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {new Date().getFullYear()}
          {' '}
          <MuiLink 
            component={Link} 
            to="/" 
            color="inherit" 
            sx={{ textDecoration: 'none' }}
          >
            SkillSift
          </MuiLink>
          {' - AI-powered resume analysis'}
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
          <MuiLink 
            component={Link} 
            to="/about" 
            color="inherit" 
            sx={{ mx: 1 }}
          >
            About
          </MuiLink>
          |
          <MuiLink 
            href="#" 
            color="inherit" 
            sx={{ mx: 1 }}
          >
            Privacy Policy
          </MuiLink>
          |
          <MuiLink 
            href="#" 
            color="inherit" 
            sx={{ mx: 1 }}
          >
            Terms of Service
          </MuiLink>
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer; 