import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
// Add authorization interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Resume analysis
export const analyzeResume = async (file: File, jobDescription?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (jobDescription) {
    formData.append('job_description', jobDescription);
  }

  try {
    const response = await api.post('/resume/analyze-resume/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });

    // Store analysis ID for later use
    if (response.data?.analysis_id) {
      localStorage.setItem('lastAnalysisId', response.data.analysis_id);
    }

    return response.data; // Return just the data, not the whole response
  } catch (error: any) {
    console.error('Analysis error:', error.response || error);
    throw new Error(error.response?.data?.detail || 'Failed to analyze resume');
  }
};

// Get analysis results
export const getResults = async (id: string) => {
  const token = localStorage.getItem('token');
  return api.post(`/resume/generate-html-report/`, { analysis_id: id }, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
  });
};

// Generate cover letter
export const generateCoverLetter = async (data: any) => {
  return api.post('/cover-letter/generate', data); // Removed the redundant '/api' prefix
};

// Get cover letter templates
export const getCoverLetterTemplates = async () => {
  return api.get('/cover-letter/templates');
};

// Auth endpoints
export const login = async (email: string, password: string) => {
  try {
    const response = await api.post('/token', {
      username: email,
      password: password,
    });
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

// Privacy routes
export const getPrivacyPolicy = async () => {
  return api.get('/privacy/privacy-policy');
};

export const exportUserData = async () => {
  return api.post('/api/privacy/export-data');
};

export const deleteUserData = async () => {
  return api.post('/api/privacy/delete-data');
};

export const downloadPdfReport = async (analysisId?: string): Promise<void> => {
  // Use stored analysis ID if none provided
  const id = analysisId || localStorage.getItem('lastAnalysisId') || 'latest';
  
  try {
      const response = await api.get(
          `/resume/generate-pdf-report/?analysis_id=${id}`,
          {
              responseType: 'blob',
              headers: {
                  'Accept': 'application/pdf'
              }
          }
      );

      // Handle download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `resume_analysis_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
  } catch (error: any) {
      if (error.response?.status === 404) {
          throw new Error('Please analyze your resume first before downloading the report.');
      }
      throw error;
  }
};

export default api;