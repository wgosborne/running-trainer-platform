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
    if (!user?.token || selectedPlanId === '') {
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
    <div className="min-h-screen bg-gradient-to-br from-spring-50 to-sky-50">
      <Header onNavigate={onNavigate} />

      <div className="max-w-3xl mx-auto p-6">
        <button
          onClick={() => onNavigate('dashboard')}
          className="text-spring-600 hover:text-spring-700 font-semibold mb-4 flex items-center gap-2 transition-colors"
        >
          <span>←</span> Back to Dashboard
        </button>

        <div className="bg-white p-10 rounded-2xl shadow-2xl border-2 border-spring-200">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">🏃</div>
            <h1 className="text-4xl font-bold text-spring-700 mb-3">
              Strava Integration
            </h1>
            <p className="text-gray-600 text-lg">
              Connect your Strava account to automatically sync your runs to your
              training plan.
            </p>
          </div>

          {error && (
            <div className="bg-coral-50 border-2 border-coral-400 text-coral-700 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          {message && (
            <div className={`p-4 rounded-lg mb-6 border-2 ${
              message.includes('✓')
                ? 'bg-spring-50 border-spring-400 text-spring-700'
                : 'bg-sky-50 border-sky-400 text-sky-700'
            }`}>
              {message}
            </div>
          )}

          <div className="space-y-8">
            <div className="bg-peach-50 p-6 rounded-xl border-2 border-peach-200">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-peach-500 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  1
                </div>
                <h2 className="text-2xl font-bold text-peach-800">Authorize</h2>
              </div>
              <p className="text-gray-700 mb-4">
                Click the button below to authorize this app to access your Strava
                activities.
              </p>
              <button
                onClick={handleGetAuthUrl}
                disabled={loading || isAuthorized}
                className="bg-peach-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-peach-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors shadow-md"
              >
                {isAuthorized
                  ? '✓ Authorized with Strava'
                  : '🔗 Authorize with Strava'}
              </button>
            </div>

            <div className="bg-sky-50 p-6 rounded-xl border-2 border-sky-200">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-sky-500 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  2
                </div>
                <h2 className="text-2xl font-bold text-sky-800">Sync Runs</h2>
              </div>
              <p className="text-gray-700 mb-4">
                Select a training plan and sync your recent Strava runs.
              </p>

              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Select Training Plan
                </label>
                <select
                  value={selectedPlanId}
                  onChange={(e) => setSelectedPlanId(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-spring-500 focus:border-spring-500"
                >
                  <option value={''}>-- Select a plan --</option>
                  {plans.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.name}
                    </option>
                  ))}
                </select>
                {plans.length === 0 && (
                  <p className="text-sm text-gray-600 mt-2 bg-sunshine-50 p-3 rounded-lg border-l-4 border-sunshine-400">
                    No plans available.{' '}
                    <button
                      onClick={() => onNavigate('dashboard')}
                      className="text-spring-600 hover:text-spring-700 font-semibold"
                    >
                      Create a plan first
                    </button>
                  </p>
                )}
              </div>

              <button
                onClick={handleSync}
                disabled={loading || selectedPlanId === ''}
                className="bg-spring-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-spring-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors shadow-md"
              >
                {loading ? '⏳ Syncing...' : '🔄 Sync Now'}
              </button>
            </div>

            <div className="bg-spring-50 p-6 rounded-xl border-2 border-spring-200">
              <h2 className="text-2xl font-bold text-spring-800 mb-4 flex items-center gap-2">
                <span>ℹ️</span> How it works
              </h2>
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-start gap-3">
                  <span className="text-spring-600 font-bold">→</span>
                  <span>Authorize this app to access your Strava activities</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-spring-600 font-bold">→</span>
                  <span>Recent runs from Strava will be synced to your selected plan</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-spring-600 font-bold">→</span>
                  <span>Runs are matched by date and automatically added</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-spring-600 font-bold">→</span>
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
