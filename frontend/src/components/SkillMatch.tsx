import {
  Box,
  Typography,
  Paper,
  LinearProgress,
  Chip,
  Divider
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { GridLegacy as Grid } from '@mui/material';
interface Skill {
  name: string;
  matched: boolean;
}

interface SkillMatchProps {
  overallScore: number;
  matchedSkills: Skill[];
  missingSkills: Skill[];
}

const SkillMatch = ({
  overallScore,
  matchedSkills,
  missingSkills
}: SkillMatchProps) => {
  // Function to determine color based on score
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'info.main';
    if (score >= 40) return 'warning.main';
    return 'error.main';
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Resume-Job Compatibility
      </Typography>
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2">Overall Match</Typography>
          <Typography
            variant="body2"
            fontWeight="bold"
            color={getScoreColor(overallScore)}
          >
            {overallScore}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={overallScore}
          color={
            overallScore >= 80 ? 'success' :
              overallScore >= 60 ? 'primary' :
                overallScore >= 40 ? 'warning' : 'error'
          }
          sx={{ height: 10, borderRadius: 5 }}
        />
      </Box>
      <Divider sx={{ my: 2 }} />
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CheckCircleIcon sx={{ color: 'success.main', mr: 1, fontSize: 18 }} />
              <Typography variant="subtitle1">Matched Skills</Typography>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {matchedSkills.length > 0 ? (
                matchedSkills.map((skill) => (
                  <Chip
                    key={skill.name}
                    label={skill.name}
                    color="success"
                    size="small"
                    variant="outlined"
                  />
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No matched skills found
                </Typography>
              )}
            </Box>
          </Box>
        </Grid>
        <Grid xs={12} md={6}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <ErrorIcon sx={{ color: 'error.main', mr: 1, fontSize: 18 }} />
              <Typography variant="subtitle1">Missing Skills</Typography>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {missingSkills.length > 0 ? (
                missingSkills.map((skill) => (
                  <Chip
                    key={skill.name}
                    label={skill.name}
                    color="error"
                    size="small"
                    variant="outlined"
                  />
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No missing skills found
                </Typography>
              )}
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default SkillMatch;