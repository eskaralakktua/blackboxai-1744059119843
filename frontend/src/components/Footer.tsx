import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-800 text-white mt-auto">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Columna 1: Logo e información */}
          <div className="space-y-4">
            <div className="flex items-center">
              <i className="fas fa-chart-network text-blue-400 text-2xl mr-2"></i>
              <span className="font-bold text-xl">Wallet Analysis</span>
            </div>
            <p className="text-gray-300 text-sm">
              Analiza patrones y relaciones entre wallets en diferentes blockchains utilizando
              inteligencia artificial y visualización de datos.
            </p>
          </div>

          {/* Columna 2: Enlaces rápidos */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Enlaces Rápidos</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-300 hover:text-white transition-colors">
                  Inicio
                </Link>
              </li>
              <li>
                <Link to="/docs" className="text-gray-300 hover:text-white transition-colors">
                  Documentación
                </Link>
              </li>
              <li>
                <a 
                  href="https://github.com/yourusername/wallet-analysis"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  GitHub
                </a>
              </li>
            </ul>
          </div>

          {/* Columna 3: Redes sociales */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Síguenos</h3>
            <div className="flex space-x-4">
              <a
                href="https://twitter.com/yourusername"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-white transition-colors"
              >
                <i className="fab fa-twitter text-2xl"></i>
              </a>
              <a
                href="https://github.com/yourusername"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-white transition-colors"
              >
                <i className="fab fa-github text-2xl"></i>
              </a>
              <a
                href="https://linkedin.com/in/yourusername"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-white transition-colors"
              >
                <i className="fab fa-linkedin text-2xl"></i>
              </a>
            </div>
          </div>
        </div>

        {/* Línea divisoria */}
        <div className="border-t border-gray-700 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            {/* Copyright */}
            <p className="text-gray-300 text-sm">
              © {currentYear} Wallet Analysis. Todos los derechos reservados.
            </p>

            {/* Enlaces legales */}
            <div className="flex space-x-4 mt-4 md:mt-0">
              <Link 
                to="/privacy" 
                className="text-gray-300 hover:text-white text-sm transition-colors"
              >
                Política de Privacidad
              </Link>
              <Link 
                to="/terms" 
                className="text-gray-300 hover:text-white text-sm transition-colors"
              >
                Términos de Uso
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;