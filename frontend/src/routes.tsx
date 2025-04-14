   // src/routes.tsx
   import { Routes, Route } from 'react-router-dom';
   import Home from './pages/Home';
   import AnalyzePage from './pages/AnalyzePage';
   import ResultsPage from './pages/ResultsPage';
   import AboutPage from './pages/AboutPage';
   import Login from './components/Login';
   import ProtectedRoute from './components/ProtectedRoute'; // Import the ProtectedRoute component

   const AppRoutes = () => {
     return (
       <Routes>
         <Route path="/" element={<Home />} />
         <Route path="/login" element={<Login />} />
         <Route 
           path="/analyze" 
           element={
             <ProtectedRoute>
               <AnalyzePage />
             </ProtectedRoute>
           } 
         />
         <Route 
           path="/results/:id" 
           element={
             <ProtectedRoute>
               <ResultsPage />
             </ProtectedRoute>
           } 
         />
         <Route path="/about" element={<AboutPage />} />
       </Routes>
     );
   };

   export default AppRoutes;