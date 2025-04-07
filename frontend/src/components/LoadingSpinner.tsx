import React from 'react';
import { LoadingSpinnerProps } from '../types';

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md',
  color = 'blue'
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const colorClasses = {
    blue: 'border-blue-500',
    green: 'border-green-500',
    red: 'border-red-500',
    yellow: 'border-yellow-500',
    gray: 'border-gray-500'
  };

  return (
    <div className="flex items-center justify-center">
      <div
        className={`
          spinner
          ${sizeClasses[size]}
          ${colorClasses[color as keyof typeof colorClasses]}
          border-t-transparent
          animate-spin
          rounded-full
          border-4
        `}
        role="status"
        aria-label="Cargando..."
      >
        <span className="sr-only">Cargando...</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;