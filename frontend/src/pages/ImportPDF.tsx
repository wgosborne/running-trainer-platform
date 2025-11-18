import { useState, useEffect } from 'react';
import { pdf as pdfApi, plans as plansApi } from '../api';
import { useStore } from '../store';
import Header from '../components/Header';

interface ImportPDFProps {
  onNavigate: (page: string, planId?: number) => void;
}

export default function ImportPDF({ onNavigate }: ImportPDFProps) {
  const user = useStore((state) => state.user);
  const plans = useStore((state) => state.plans);
  const setPlans = useStore((state) => state.setPlans);

  const [file, setFile] = useState<File | null>(null);
  const [selectedPlanId, setSelectedPlanId] = useState<string>('');
  const [planStartDate, setPlanStartDate] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [progress, setProgress] = useState('');

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    if (!user?.token) return;

    try {
      const data = await plansApi.getAll(user.token);
      setPlans(data);
      if (data.length > 0 && selectedPlanId === '') {
        setSelectedPlanId(data[0].id);
        // Auto-populate start date from selected plan
        if (data[0].start_date) {
          setPlanStartDate(data[0].start_date);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load plans');
    }
  };

  const handlePlanChange = (planId: string) => {
    setSelectedPlanId(planId);
    // Auto-populate start date from selected plan
    const selectedPlan = plans.find(p => p.id === planId);
    if (selectedPlan?.start_date) {
      setPlanStartDate(selectedPlan.start_date);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
      setSuccess('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !user?.token || !selectedPlanId || !planStartDate) {
      setError('Please select a file, plan, and start date');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    setProgress('Uploading PDF...');

    try {
      const result = await pdfApi.upload(
        file,
        selectedPlanId,
        planStartDate,
        user.token
      );
      setProgress('Creating workouts...');

      setTimeout(() => {
        setProgress('');
        setSuccess(
          `✓ ${result.workouts_created} workouts created successfully!` +
          (result.workouts_failed > 0 ? ` (${result.workouts_failed} failed)` : '')
        );
        setFile(null);

        // Reset file input
        const fileInput = document.getElementById('pdf-file') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      }, 500);
    } catch (err: any) {
      setError(err.message || 'Failed to import PDF');
      setProgress('');
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
            Import Training Plan from PDF
          </h1>

          <p className="text-gray-600 mb-6">
            Upload a PDF training plan to automatically extract workouts and add
            them to your selected plan.
          </p>

          {error && (
            <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-100 text-green-700 p-3 rounded mb-4">
              {success}
            </div>
          )}

          {progress && (
            <div className="bg-blue-100 text-blue-700 p-3 rounded mb-4">
              {progress}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                Select Training Plan
              </label>
              <select
                value={selectedPlanId}
                onChange={(e) => handlePlanChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">-- Select a plan --</option>
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
                    type="button"
                    onClick={() => onNavigate('dashboard')}
                    className="text-blue-600 hover:underline"
                  >
                    Create a plan first
                  </button>
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Plan Start Date
              </label>
              <input
                type="date"
                value={planStartDate}
                onChange={(e) => setPlanStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                This should match the first week in your PDF (e.g., the Monday of "21-Jul")
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Upload PDF File
              </label>
              <input
                id="pdf-file"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              {file && (
                <p className="text-sm text-gray-600 mt-1">
                  Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || !file || !selectedPlanId || !planStartDate}
              className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Importing...' : 'Import PDF'}
            </button>
          </form>

          {success && (
            <div className="mt-6 text-center">
              <button
                onClick={() => onNavigate('plan-detail', selectedPlanId)}
                className="text-blue-600 hover:underline"
              >
                View plan details →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
