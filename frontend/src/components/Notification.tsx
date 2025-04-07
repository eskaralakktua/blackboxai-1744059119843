import React, { useEffect } from 'react';
import { NotificationProps } from '../types';

const Notification: React.FC<NotificationProps> = ({
  type,
  message,
  duration = 5000,
  onClose
}) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const getTypeStyles = () => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-green-500',
          icon: 'fas fa-check-circle'
        };
      case 'error':
        return {
          bg: 'bg-red-500',
          icon: 'fas fa-exclamation-circle'
        };
      case 'warning':
        return {
          bg: 'bg-yellow-500',
          icon: 'fas fa-exclamation-triangle'
        };
      case 'info':
      default:
        return {
          bg: 'bg-blue-500',
          icon: 'fas fa-info-circle'
        };
    }
  };

  const { bg, icon } = getTypeStyles();

  return (
    <div
      className={`
        fixed bottom-4 right-4 
        flex items-center 
        ${bg} text-white 
        px-4 py-3 rounded-lg shadow-lg
        transform transition-all duration-500 ease-in-out
        hover:scale-105
        z-50
      `}
      role="alert"
    >
      <div className="flex items-center">
        <i className={`${icon} text-xl mr-3`}></i>
        <p className="font-medium">{message}</p>
      </div>
      
      {onClose && (
        <button
          onClick={onClose}
          className="ml-6 focus:outline-none hover:opacity-75 transition-opacity"
          aria-label="Cerrar notificación"
        >
          <i className="fas fa-times"></i>
        </button>
      )}
    </div>
  );
};

export default Notification;