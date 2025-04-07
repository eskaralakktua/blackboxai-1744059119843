import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import Notification from '../components/Notification';
import GraphViewer from '../components/GraphViewer';
import { walletApi, useAnalysisPolling } from '../services/api';
import type { AnalysisReport, GraphData } from '../types';

const Analysis: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Usar el hook de polling para obtener actualizaciones del estado
  const { status, error: pollingError, stopPolling } = useAnalysisPolling(
    id || '',
    5000
  );

  useEffect(() => {
    if (status?.status === 'completed') {
      loadReport();
    } else if (status?.status === 'error') {
      setError(status.error || 'Error en el análisis');
      stopPolling();
    }
  }, [status]);

  const loadReport = async () => {
    try {
      const response = await walletApi.getAnalysisReport(id || '');
      setReport(response.data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDownload = async (format: 'pdf' | 'csv') => {
    try {
      const blob = await walletApi.downloadReport(id || '', format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `wallet-analysis-${id}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <i className="fas fa-exclamation-circle text-red-500 text-4xl mb-4"></i>
          <h2 className="text-xl font-semibold text-red-700 mb-2">Error en el análisis</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
          >
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  if (!status || status.status === 'processing') {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <LoadingSpinner size="lg" color="blue" />
          <h2 className="text-xl font-semibold mt-4 mb-2">
            Analizando wallets...
          </h2>
          <p className="text-gray-600 mb-4">
            {status?.message || 'Procesando datos...'}
          </p>
          <div className="w-full max-w-md mx-auto bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${status?.progress || 0}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Progreso: {status?.progress || 0}%
          </p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="container mx-auto px-4 py-8">
        <LoadingSpinner size="lg" color="blue" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Encabezado */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Resultados del Análisis
        </h1>
        <div className="flex justify-between items-center">
          <p className="text-gray-600">
            {new Date(report.timestamp).toLocaleString()}
          </p>
          <div className="space-x-4">
            <button
              onClick={() => handleDownload('pdf')}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
            >
              <i className="fas fa-file-pdf mr-2"></i>
              Descargar PDF
            </button>
            <button
              onClick={() => handleDownload('csv')}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors"
            >
              <i className="fas fa-file-csv mr-2"></i>
              Descargar CSV
            </button>
          </div>
        </div>
      </div>

      {/* Resumen */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Resumen</h2>
        <p className="text-gray-600 whitespace-pre-line">{report.summary}</p>
      </div>

      {/* Grafo de relaciones */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Grafo de Relaciones</h2>
        <div className="h-[600px]">
          <GraphViewer
            data={report.graph_data}
            onNodeClick={(nodeId) => console.log('Node clicked:', nodeId)}
            onEdgeClick={(edge) => console.log('Edge clicked:', edge)}
          />
        </div>
      </div>

      {/* Insights de IA */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Insights de IA</h2>
        <div className="space-y-4">
          {report.ai_insights.map((insight, index) => (
            <div
              key={index}
              className="border-l-4 border-blue-500 pl-4 py-2"
            >
              <h3 className="font-semibold mb-2">
                Wallet: {insight.wallet_address}
              </h3>
              <p className="text-gray-600 mb-2">
                Patrón: {insight.behavior_pattern}
              </p>
              <p className="text-gray-600 mb-2">
                Tipo de entidad: {insight.entity_type}
              </p>
              <div className="flex items-center mb-2">
                <span className="text-gray-600 mr-2">Score de riesgo:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
                  <div
                    className="bg-red-500 h-2 rounded-full"
                    style={{ width: `${insight.risk_score * 100}%` }}
                  ></div>
                </div>
                <span className="ml-2 text-sm text-gray-500">
                  {(insight.risk_score * 100).toFixed(1)}%
                </span>
              </div>
              <ul className="list-disc list-inside text-gray-600">
                {insight.observations.map((obs, i) => (
                  <li key={i}>{obs}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Analysis;