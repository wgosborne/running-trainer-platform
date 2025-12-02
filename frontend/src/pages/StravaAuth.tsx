import { useState, useEffect } from 'react';
import { strava } from '../api';
import { useStore } from '../store';
import Header from '../components/Header';

interface StravaAuthProps {
  onNavigate: (page: string) => void;
}

export default function StravaAuth({ onNavigate }: StravaAuthProps) {
  const user = useStore((state) => state.user);
  const plans = useStore((state) => state.plans);

  const [isAuthorized, setIsAuthorized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [selectedPlanId, setSelectedPlanId] = useState<string>('');

  useEffect(() => {
    // Check if we're coming back from Strava with a code
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code && user) {
      handleCallback(code);
    }

    if (plans.length > 0 && selectedPlanId === '') {
      setSelectedPlanId(plans[0].id);
    }
  }, []);

  const handleGetAuthUrl = async () => {
    setLoading(true);
    setError('');

    try {
      const redirectUri = `${window.location.origin}/strava-callback`;
      const response = await strava.getAuthUrl(redirectUri);
      setMessage('Opening Strava authorization in new window...');

      // Open in new window
      window.open(response.auth_url, '_blank', 'width=600,height=700');
    } catch (err: any) {
      setError(err.message || 'Failed to get Strava auth URL');
    } finally {
      setLoading(false);
    }
  };

  const handleCallback = async (code: string) => {
    if (!user) return;

    setLoading(true);
    setError('');

    try {
      await strava.handleCallback(code, user.id.toString());
      setIsAuthorized(true);
      setMessage('✓ Successfully authorized with Strava! You can now sync your runs.');

      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } catch (err: any) {
      setError(err.message || 'Failed to handle callback');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    if (selectedPlanId === '') {  // Removed !user?.token check
      setError('Please select a plan');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('Syncing runs from Strava...');

    try {
      const result = await strava.sync(
        user?.id.toString() || '1',  // Default user ID if not available
        selectedPlanId
        // user.token  // Removed token parameter
      );
      setMessage(`✓ Successfully synced ${result.runs_imported} runs from Strava!`);
    } catch (err: any) {
      setError(err.message || 'Failed to sync runs. Make sure you have authorized Strava first.');
      setMessage('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onNavigate={onNavigate} />

      <div className="max-w-3xl mx-auto p-6">
        <button
          onClick={() => onNavigate('dashboard')}
          className="text-primary-600 hover:text-primary-700 font-medium mb-4 flex items-center gap-2 transition-colors"
        >
          <span>←</span> Back to Dashboard
        </button>

        <div className="bg-white p-10 rounded-lg shadow-sm border border-gray-200">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-3">
              Strava Integration
            </h1>
            <p className="text-gray-600">
              Connect your Strava account to automatically sync your runs to your
              training plan
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          {message && (
            <div className={`p-4 rounded-lg mb-6 border ${
              message.includes('✓') || message.includes('Successfully')
                ? 'bg-primary-50 border-primary-200 text-primary-700'
                : 'bg-blue-50 border-blue-200 text-blue-700'
            }`}>
              {message}
            </div>
          )}

          <div className="space-y-6">
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-gray-900 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  1
                </div>
                <h2 className="text-xl font-semibold text-gray-900">Authorize</h2>
              </div>
              <p className="text-gray-600 mb-4">
                Click the button below to authorize this app to access your Strava
                activities
              </p>
              <button
                onClick={handleGetAuthUrl}
                disabled={loading || isAuthorized}
                className="bg-primary-600 text-white px-5 py-2.5 rounded-md text-sm font-medium hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isAuthorized
                  ? 'Authorized with Strava'
                  : 'Authorize with Strava'}
              </button>
            </div>

            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-gray-900 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  2
                </div>
                <h2 className="text-xl font-semibold text-gray-900">Sync Runs</h2>
              </div>
              <p className="text-gray-600 mb-4">
                Select a training plan and sync your recent Strava runs
              </p>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Training Plan
                </label>
                <select
                  value={selectedPlanId}
                  onChange={(e) => setSelectedPlanId(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value={''}>-- Select a plan --</option>
                  {plans.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.name}
                    </option>
                  ))}
                </select>
                {plans.length === 0 && (
                  <p className="text-sm text-gray-600 mt-2">
                    No plans available.{' '}
                    <button
                      onClick={() => onNavigate('dashboard')}
                      className="text-primary-600 hover:text-primary-700 font-medium"
                    >
                      Create a plan first
                    </button>
                  </p>
                )}
              </div>

              <button
                onClick={handleSync}
                disabled={loading || selectedPlanId === ''}
                className="bg-primary-600 text-white px-5 py-2.5 rounded-md text-sm font-medium hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Syncing...' : 'Sync Now'}
              </button>
            </div>

            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                How it works
              </h2>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 font-bold mt-0.5">•</span>
                  <span>Authorize this app to access your Strava activities</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 font-bold mt-0.5">•</span>
                  <span>Recent runs from Strava will be synced to your selected plan</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 font-bold mt-0.5">•</span>
                  <span>Runs are matched by date and automatically added</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 font-bold mt-0.5">•</span>
                  <span>You can sync as many times as you want</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
