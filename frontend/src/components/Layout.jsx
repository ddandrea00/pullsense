import { Link } from "react-router-dom";
import { Brain } from "lucide-react";
import { useWebSocket } from "../hooks/useWebSocket";

const Layout = ({ children }) => {
  const { isConnected } = useWebSocket();

  return (
    <div className="min-h-screen bg-gray-50">
      {!isConnected && (
        <div className="bg-yellow-500 text-white text-center py-2 text-sm">
          🔌 Reconnecting to live updates...
        </div>
      )}

      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center">
              <Brain className="w-8 h-8 text-blue-600 mr-3" />
              <h1 className="text-xl font-semibold">PullSense</h1>
            </Link>
            <nav className="flex space-x-4">
              <Link
                to="/"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Dashboard
              </Link>
              <Link
                to="/settings"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Settings
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
};

export default Layout;
