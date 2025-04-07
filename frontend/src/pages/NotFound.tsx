import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <i className="fas fa-exclamation-triangle text-6xl text-yellow-500 mb-4"></i>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            404 - Página no encontrada
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Lo sentimos, la página que estás buscando no existe o ha sido movida.
          </p>
        </div>
        
        <div className="mt-8">
          <Link
            to="/"
            className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <i className="fas fa-home mr-2"></i>
            Volver al inicio
          </Link>
        </div>

        <div className="mt-6">
          <p className="text-sm text-gray-500">
            Si crees que esto es un error, por favor{' '}
            <a
              href="mailto:support@example.com"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              contáctanos
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default NotFound;