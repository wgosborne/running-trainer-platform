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
    <header className="bg-gradient-to-r from-spring-600 to-spring-500 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-6">
          <button
            onClick={() => onNavigate('dashboard')}
            className="text-2xl font-bold hover:text-spring-100 transition-colors flex items-center gap-2"
          >
            <span className="text-3xl">🏃</span>
            <span>Running Tracker</span>
          </button>

          <nav className="hidden md:flex space-x-2">
            <button
              onClick={() => onNavigate('dashboard')}
              className="px-4 py-2 rounded-lg hover:bg-spring-700 transition-colors font-medium"
            >
              Dashboard
            </button>
            <button
              onClick={() => onNavigate('import-pdf')}
              className="px-4 py-2 rounded-lg hover:bg-spring-700 transition-colors font-medium"
            >
              Import PDF
            </button>
            <button
              onClick={() => onNavigate('strava-auth')}
              className="px-4 py-2 rounded-lg hover:bg-spring-700 transition-colors font-medium"
            >
              Strava
            </button>
          </nav>
        </div>

        <div className="flex items-center space-x-4">
          {user && (
            <>
              <span className="text-sm font-medium text-spring-100">{user.email}</span>
              <button
                onClick={handleLogout}
                className="bg-spring-700 hover:bg-spring-800 px-5 py-2 rounded-lg text-sm font-semibold transition-colors shadow-md"
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
