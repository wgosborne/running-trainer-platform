import { useState } from 'react';
// import { useStore } from './store';  // Auth commented out for easier deployment
// import Login from './pages/Login';  // Auth commented out for easier deployment
import Dashboard from './pages/Dashboard';
import PlanDetail from './pages/PlanDetail';
import ImportPDF from './pages/ImportPDF';
import StravaAuth from './pages/StravaAuth';

type Page = 'login' | 'dashboard' | 'plan-detail' | 'import-pdf' | 'strava-auth';

function App() {
  // const user = useStore((state) => state.user);  // Auth commented out for easier deployment
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');  // Changed from 'login' to 'dashboard'
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);

  const handleNavigate = (page: string, planId?: string) => {
    setCurrentPage(page as Page);
    if (planId !== undefined) {
      setSelectedPlanId(planId);
    }
  };

  // const handleLoginSuccess = () => {  // Auth commented out for easier deployment
  //   setCurrentPage('dashboard');
  // };

  // AUTH COMMENTED OUT - Direct access to plans without login
  // If user is not logged in, always show login page
  // if (!user) {
  //   return <Login onLoginSuccess={handleLoginSuccess} />;
  // }

  // Render current page based on state
  switch (currentPage) {
    case 'dashboard':
      return <Dashboard onNavigate={handleNavigate} />;

    case 'plan-detail':
      return selectedPlanId ? (
        <PlanDetail planId={selectedPlanId} onNavigate={handleNavigate} />
      ) : (
        <Dashboard onNavigate={handleNavigate} />
      );

    case 'import-pdf':
      return <ImportPDF onNavigate={handleNavigate} />;

    case 'strava-auth':
      return <StravaAuth onNavigate={handleNavigate} />;

    default:
      return <Dashboard onNavigate={handleNavigate} />;
  }
}

export default App;
