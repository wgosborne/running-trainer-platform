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
    <header className="bg-blue-600 text-white shadow-md">
      <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-6">
          <button
            onClick={() => onNavigate('dashboard')}
            className="text-2xl font-bold hover:text-blue-100"
          >
            Running Tracker
          </button>

          <nav className="hidden md:flex space-x-4">
            <button
              onClick={() => onNavigate('dashboard')}
              className="hover:text-blue-100"
            >
              Dashboard
            </button>
            <button
              onClick={() => onNavigate('import-pdf')}
              className="hover:text-blue-100"
            >
              Import PDF
            </button>
            <button
              onClick={() => onNavigate('strava-auth')}
              className="hover:text-blue-100"
            >
              Strava
            </button>
          </nav>
        </div>

        <div className="flex items-center space-x-4">
          {user && (
            <>
              <span className="text-sm">{user.email}</span>
              <button
                onClick={handleLogout}
                className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded text-sm"
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
