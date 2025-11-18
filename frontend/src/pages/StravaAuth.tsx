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
  const [selectedPlanId, setSelectedPlanId] = useState<number>(0);

  useEffect(() => {
    // Check if we're coming back from Strava with a code
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code && user) {
      handleCallback(code);
    }

    if (plans.length > 0 && selectedPlanId === 0) {
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
    if (!user?.token || selectedPlanId === 0) {
      setError('Please select a plan');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('Syncing runs from Strava...');

    try {
      const result = await strava.sync(user.id.toString(), selectedPlanId, user.token);
      setMessage(`✓ Successfully synced ${result.runs_imported} runs from Strava!`);
    } catch (err: any) {
      setError(err.message || 'Failed to sync runs. Make sure you have authorized Strava first.');
      setMessage('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onNavigate={onNavigate} />

      <div className="max-w-2xl mx-auto p-6">
        <button
          onClick={() => onNavigate('dashboard')}
          className="text-blue-600 hover:underline mb-4"
        >
          ← Back to Dashboard
        </button>

        <div className="bg-white p-8 rounded-lg shadow">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">
            Strava Integration
          </h1>

          <p className="text-gray-600 mb-6">
            Connect your Strava account to automatically sync your runs to your
            training plan.
          </p>

          {error && (
            <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
              {error}
            </div>
          )}

          {message && (
            <div className={`p-3 rounded mb-4 ${
              message.includes('✓')
                ? 'bg-green-100 text-green-700'
                : 'bg-blue-100 text-blue-700'
            }`}>
              {message}
            </div>
          )}

          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-3">Step 1: Authorize</h2>
              <p className="text-gray-600 mb-3">
                Click the button below to authorize this app to access your Strava
                activities.
              </p>
              <button
                onClick={handleGetAuthUrl}
                disabled={loading || isAuthorized}
                className="bg-orange-600 text-white px-6 py-3 rounded hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isAuthorized
                  ? '✓ Authorized with Strava'
                  : 'Authorize with Strava'}
              </button>
            </div>

            <div className="border-t pt-6">
              <h2 className="text-xl font-semibold mb-3">Step 2: Sync Runs</h2>
              <p className="text-gray-600 mb-3">
                Select a training plan and sync your recent Strava runs.
              </p>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  Select Training Plan
                </label>
                <select
                  value={selectedPlanId}
                  onChange={(e) => setSelectedPlanId(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={0}>-- Select a plan --</option>
                  {plans.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.name}
                    </option>
                  ))}
                </select>
                {plans.length === 0 && (
                  <p className="text-sm text-gray-500 mt-1">
                    No plans available.{' '}
                    <button
                      onClick={() => onNavigate('dashboard')}
                      className="text-blue-600 hover:underline"
                    >
                      Create a plan first
                    </button>
                  </p>
                )}
              </div>

              <button
                onClick={handleSync}
                disabled={loading || selectedPlanId === 0}
                className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Syncing...' : 'Sync Now'}
              </button>
            </div>

            <div className="border-t pt-6">
              <h2 className="text-xl font-semibold mb-3">How it works</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-2">
                <li>Authorize this app to access your Strava activities</li>
                <li>Recent runs from Strava will be synced to your selected plan</li>
                <li>Runs are matched by date and automatically added</li>
                <li>You can sync as many times as you want</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
