import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import Notification from '../components/Notification';
import { walletApi } from '../services/api';
import type { UploadResponse } from '../types';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [notification, setNotification] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  const handleFileUpload = async (file: File) => {
    try {
      const response = await walletApi.uploadCsv(file);
      
      setNotification({
        type: 'success',
        message: `Archivo procesado correctamente. Analizando ${response.data.wallets_count} wallets...`
      });

      // Redirigir al análisis después de un breve delay
      setTimeout(() => {
        navigate(`/analysis/${response.data.analysis_id}`);
      }, 2000);

    } catch (error: any) {
      setNotification({
        type: 'error',
        message: error.message || 'Error procesando el archivo'
      });
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Análisis de Wallets con IA
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Analiza patrones y relaciones entre wallets en diferentes blockchains utilizando
          inteligencia artificial y visualización de datos.
        </p>
      </div>

      {/* Características principales */}
      <div className="grid md:grid-cols-3 gap-8 mb-12">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-blue-500 text-3xl mb-4">
            <i className="fas fa-chart-network"></i>
          </div>
          <h3 className="text-xl font-semibold mb-2">Análisis de Patrones</h3>
          <p className="text-gray-600">
            Detecta patrones de comportamiento y relaciones entre diferentes wallets.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-blue-500 text-3xl mb-4">
            <i className="fas fa-brain"></i>
          </div>
          <h3 className="text-xl font-semibold mb-2">IA Avanzada</h3>
          <p className="text-gray-600">
            Utiliza GPT-4 para generar insights y detectar posibles conexiones.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-blue-500 text-3xl mb-4">
            <i className="fas fa-file-pdf"></i>
          </div>
          <h3 className="text-xl font-semibold mb-2">Reportes Detallados</h3>
          <p className="text-gray-600">
            Genera informes completos en PDF y CSV con todas las métricas y hallazgos.
          </p>
        </div>
      </div>

      {/* Componente de carga de archivos */}
      <div className="mb-12">
        <FileUpload onFileAccepted={handleFileUpload} />
      </div>

      {/* Blockchains soportadas */}
      <div className="bg-white rounded-lg shadow p-8 mb-12">
        <h2 className="text-2xl font-semibold mb-6 text-center">
          Blockchains Soportadas
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="flex items-center space-x-4">
            <img 
              src="https://cryptologos.cc/logos/ethereum-eth-logo.png"
              alt="Ethereum"
              className="w-8 h-8"
            />
            <span className="font-medium">Ethereum</span>
          </div>
          <div className="flex items-center space-x-4">
            <img 
              src="https://cryptologos.cc/logos/bnb-bnb-logo.png"
              alt="BNB Chain"
              className="w-8 h-8"
            />
            <span className="font-medium">BNB Chain</span>
          </div>
          <div className="flex items-center space-x-4">
            <img 
              src="https://cryptologos.cc/logos/polygon-matic-logo.png"
              alt="Polygon"
              className="w-8 h-8"
            />
            <span className="font-medium">Polygon</span>
          </div>
        </div>
      </div>

      {/* Notificación */}
      {notification && (
        <Notification
          type={notification.type}
          message={notification.message}
          duration={5000}
          onClose={() => setNotification(null)}
        />
      )}
    </div>
  );
};

export default Home;