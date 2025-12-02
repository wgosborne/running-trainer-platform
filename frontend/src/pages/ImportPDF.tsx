import { useState, useEffect } from 'react';
import { pdf as pdfApi, plans as plansApi } from '../api';
import { useStore } from '../store';
import Header from '../components/Header';

interface ImportPDFProps {
  onNavigate: (page: string, planId?: string) => void;
}

export default function ImportPDF({ onNavigate }: ImportPDFProps) {
  // const user = useStore((state) => state.user);  // Auth removed
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
    // if (!user?.token) return;  // Auth removed for easier deployment

    try {
      const data = await plansApi.getAll();  // Removed token parameter
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
    if (!file || !selectedPlanId || !planStartDate) {  // Removed !user?.token check
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
        planStartDate
        // user.token  // Removed token parameter
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
              Import Training Plan
            </h1>
            <p className="text-gray-600">
              Upload a PDF training plan to automatically extract workouts and add
              them to your selected plan
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-primary-50 border border-primary-200 text-primary-700 p-4 rounded-lg mb-6">
              {success}
            </div>
          )}

          {progress && (
            <div className="bg-blue-50 border border-blue-200 text-blue-700 p-4 rounded-lg mb-6">
              {progress}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Training Plan
              </label>
              <select
                value={selectedPlanId}
                onChange={(e) => handlePlanChange(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
                <p className="text-sm text-gray-600 mt-2">
                  No plans available.{' '}
                  <button
                    type="button"
                    onClick={() => onNavigate('dashboard')}
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Create a plan first
                  </button>
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Plan Start Date
              </label>
              <input
                type="date"
                value={planStartDate}
                onChange={(e) => setPlanStartDate(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
              />
              <p className="text-sm text-gray-600 mt-2">
                This should match the first week in your PDF (e.g., the Monday of "21-Jul")
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload PDF File
              </label>
              <input
                id="pdf-file"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-primary-50 file:text-primary-700 file:font-medium hover:file:bg-primary-100"
                required
              />
              {file && (
                <p className="text-sm text-gray-700 mt-2">
                  Selected: <span className="font-medium">{file.name}</span> ({(file.size / 1024).toFixed(1)} KB)
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || !file || !selectedPlanId || !planStartDate}
              className="w-full bg-primary-600 text-white py-3 rounded-md font-medium hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Importing...' : 'Import PDF'}
            </button>
          </form>

          {success && (
            <div className="mt-6 text-center">
              <button
                onClick={() => onNavigate('plan-detail', selectedPlanId)}
                className="text-primary-600 hover:text-primary-700 font-medium flex items-center justify-center gap-2 mx-auto transition-colors"
              >
                <span>View plan details</span>
                <span>→</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
