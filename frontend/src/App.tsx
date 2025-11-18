import { useState } from 'react';
import { useStore } from './store';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import PlanDetail from './pages/PlanDetail';
import ImportPDF from './pages/ImportPDF';
import StravaAuth from './pages/StravaAuth';

type Page = 'login' | 'dashboard' | 'plan-detail' | 'import-pdf' | 'strava-auth';

function App() {
  const user = useStore((state) => state.user);
  const [currentPage, setCurrentPage] = useState<Page>('login');
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);

  const handleNavigate = (page: string, planId?: number) => {
    setCurrentPage(page as Page);
    if (planId !== undefined) {
      setSelectedPlanId(planId);
    }
  };

  const handleLoginSuccess = () => {
    setCurrentPage('dashboard');
  };

  // If user is not logged in, always show login page
  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

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
