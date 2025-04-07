import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { DropzoneProps } from '../types';
import LoadingSpinner from './LoadingSpinner';

const FileUpload: React.FC<DropzoneProps> = ({ onFileAccepted }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    
    // Validar que sea un archivo CSV
    if (!file.name.endsWith('.csv')) {
      setError('Por favor, sube un archivo CSV válido');
      return;
    }

    // Validar tamaño del archivo (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('El archivo no debe superar los 5MB');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      await onFileAccepted(file);
    } catch (err) {
      setError('Error procesando el archivo');
      console.error('Error en FileUpload:', err);
    } finally {
      setIsLoading(false);
    }
  }, [onFileAccepted]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    disabled: isLoading
  });

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          dropzone
          ${isDragActive ? 'active border-blue-500 bg-blue-50' : ''}
          ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
          ${error ? 'border-red-500' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {isLoading ? (
          <div className="text-center">
            <LoadingSpinner size="md" color="blue" />
            <p className="mt-2 text-gray-600">Procesando archivo...</p>
          </div>
        ) : isDragActive ? (
          <div className="text-center">
            <i className="fas fa-cloud-upload-alt text-4xl text-blue-500 mb-4"></i>
            <p className="text-lg text-blue-600">Suelta el archivo aquí</p>
          </div>
        ) : (
          <div className="text-center">
            <i className="fas fa-file-csv text-4xl text-gray-400 mb-4"></i>
            <p className="text-lg text-gray-600 mb-2">
              Arrastra y suelta tu archivo CSV aquí, o haz clic para seleccionarlo
            </p>
            <p className="text-sm text-gray-500">
              El archivo debe contener las columnas: wallet_address, blockchain (opcional)
            </p>
          </div>
        )}

        {error && (
          <div className="mt-4 text-center text-red-500">
            <i className="fas fa-exclamation-circle mr-2"></i>
            {error}
          </div>
        )}
      </div>

      {/* Instrucciones adicionales */}
      <div className="mt-6 bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          <i className="fas fa-info-circle mr-2 text-blue-500"></i>
          Instrucciones
        </h3>
        <ul className="space-y-2 text-gray-600">
          <li className="flex items-start">
            <i className="fas fa-check-circle text-green-500 mt-1 mr-2"></i>
            <span>El archivo debe estar en formato CSV</span>
          </li>
          <li className="flex items-start">
            <i className="fas fa-check-circle text-green-500 mt-1 mr-2"></i>
            <span>Columna requerida: wallet_address</span>
          </li>
          <li className="flex items-start">
            <i className="fas fa-check-circle text-green-500 mt-1 mr-2"></i>
            <span>Columna opcional: blockchain (ethereum, bsc, polygon)</span>
          </li>
          <li className="flex items-start">
            <i className="fas fa-check-circle text-green-500 mt-1 mr-2"></i>
            <span>Tamaño máximo del archivo: 5MB</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default FileUpload;