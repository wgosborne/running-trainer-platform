import { useStore } from '../store';

interface HeaderProps {
  onNavigate: (page: string) => void;
}

export default function Header({ onNavigate }: HeaderProps) {
  const user = useStore((state) => state.user);
  const logout = useStore((state) => state.logout);

  const handleLogout = () => {
    logout();
    window.location.reload();
  };

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-8">
          <button
            onClick={() => onNavigate('dashboard')}
            className="text-xl font-semibold text-gray-900 hover:text-primary-600 transition-colors"
          >
            Running Tracker
          </button>

          <nav className="hidden md:flex space-x-1">
            <button
              onClick={() => onNavigate('dashboard')}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md transition-colors"
            >
              Dashboard
            </button>
            <button
              onClick={() => onNavigate('import-pdf')}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md transition-colors"
            >
              Import PDF
            </button>
            <button
              onClick={() => onNavigate('strava-auth')}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md transition-colors"
            >
              Strava
            </button>
          </nav>
        </div>

        <div className="flex items-center space-x-4">
          {user && (
            <>
              <span className="text-sm text-gray-600">{user.email}</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-md transition-colors"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
