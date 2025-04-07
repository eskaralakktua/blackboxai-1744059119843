import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600';
  };

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo y título */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <i className="fas fa-chart-network text-blue-600 text-2xl mr-2"></i>
              <span className="font-bold text-xl text-gray-800">
                Wallet Analysis
              </span>
            </Link>
          </div>

          {/* Enlaces de navegación */}
          <div className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className={`${isActive('/')} transition-colors duration-200 font-medium`}
            >
              <i className="fas fa-home mr-2"></i>
              Inicio
            </Link>

            <a 
              href="https://github.com/yourusername/wallet-analysis"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-blue-600 transition-colors duration-200 font-medium"
            >
              <i className="fab fa-github mr-2"></i>
              GitHub
            </a>

            <a 
              href="/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-blue-600 transition-colors duration-200 font-medium"
            >
              <i className="fas fa-book mr-2"></i>
              Documentación
            </a>
          </div>

          {/* Botón de menú móvil */}
          <div className="md:hidden flex items-center">
            <button
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
              aria-expanded="false"
            >
              <span className="sr-only">Abrir menú principal</span>
              <i className="fas fa-bars"></i>
            </button>
          </div>
        </div>
      </div>

      {/* Menú móvil */}
      <div className="hidden md:hidden">
        <div className="px-2 pt-2 pb-3 space-y-1">
          <Link
            to="/"
            className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
          >
            <i className="fas fa-home mr-2"></i>
            Inicio
          </Link>

          <a
            href="https://github.com/yourusername/wallet-analysis"
            target="_blank"
            rel="noopener noreferrer"
            className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
          >
            <i className="fab fa-github mr-2"></i>
            GitHub
          </a>

          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
          >
            <i className="fas fa-book mr-2"></i>
            Documentación
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;