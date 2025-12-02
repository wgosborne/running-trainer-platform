import { useState } from 'react';
// import { auth } from '../api';  // Auth disabled
import { useStore } from '../store';

interface LoginProps {
  onLoginSuccess: () => void;
}

export default function Login({ onLoginSuccess }: LoginProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const setUser = useStore((state) => state.setUser);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Auth disabled - simulate login
      setUser({
        id: 1,
        email: email,
        token: 'guest',
      });
      onLoginSuccess();
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-spring-50 to-sky-50">
      <div className="bg-white p-10 rounded-2xl shadow-2xl w-full max-w-md border-2 border-spring-200">
        <div className="text-center mb-8">
          <div className="text-6xl mb-3">🏃</div>
          <h1 className="text-4xl font-bold text-spring-600 mb-2">
            Running Tracker
          </h1>
          <p className="text-gray-600">Track your training, achieve your goals</p>
        </div>

        <h2 className="text-2xl font-bold mb-6 text-center text-spring-700">
          {isLogin ? 'Welcome Back!' : 'Create Account'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-spring-500 focus:border-spring-500 transition-colors"
              placeholder="your@email.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-spring-500 focus:border-spring-500 transition-colors"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className={`text-sm p-4 rounded-lg border-2 ${
              error.includes('successful')
                ? 'bg-spring-50 border-spring-400 text-spring-700'
                : 'bg-coral-50 border-coral-400 text-coral-700'
            }`}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-spring-500 to-spring-600 text-white py-3 rounded-lg font-semibold hover:from-spring-600 hover:to-spring-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
          >
            {loading ? 'Loading...' : isLogin ? 'Login' : 'Register'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
            className="text-spring-600 hover:text-spring-700 font-semibold text-sm transition-colors"
          >
            {isLogin
              ? "Don't have an account? Register"
              : 'Already have an account? Login'}
          </button>
        </div>
      </div>
    </div>
  );
}
