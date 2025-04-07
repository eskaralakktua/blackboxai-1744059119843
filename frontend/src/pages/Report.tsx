import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import { walletApi } from '../services/api';
import type { WalletStats, TokenInfo } from '../types';

const Report: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [stats, setStats] = useState<WalletStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWalletStats();
  }, [id]);

  const loadWalletStats = async () => {
    try {
      setLoading(true);
      const response = await walletApi.getAnalysisReport(id || '');
      const walletData = response.data.wallets_analyzed[0]; // Asumimos que queremos el primer wallet
      setStats(walletData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="lg" color="blue" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <i className="fas fa-exclamation-circle text-red-500 text-4xl mb-4"></i>
          <h2 className="text-xl font-semibold text-red-700 mb-2">Error cargando reporte</h2>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <i className="fas fa-info-circle text-yellow-500 text-4xl mb-4"></i>
          <h2 className="text-xl font-semibold text-yellow-700 mb-2">No hay datos disponibles</h2>
          <p className="text-yellow-600">No se encontraron estadísticas para esta wallet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Encabezado */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Reporte Detallado de Wallet
        </h1>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <p className="text-gray-600">
              <span className="font-semibold">Dirección:</span> {stats.address}
            </p>
            <p className="text-gray-600">
              <span className="font-semibold">Blockchain:</span> {stats.blockchain}
            </p>
          </div>
          <div>
            <p className="text-gray-600">
              <span className="font-semibold">Primera transacción:</span>{' '}
              {new Date(stats.first_transaction_date).toLocaleString()}
            </p>
            <p className="text-gray-600">
              <span className="font-semibold">Última transacción:</span>{' '}
              {new Date(stats.last_transaction_date).toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Estadísticas principales */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Total Enviado</h3>
          <p className="text-3xl font-bold text-green-600">
            ${stats.total_sent_usd.toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Total Recibido</h3>
          <p className="text-3xl font-bold text-blue-600">
            ${stats.total_received_usd.toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Transacciones</h3>
          <p className="text-3xl font-bold text-purple-600">
            {stats.transaction_count.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Tokens */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Tokens Únicos</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Token
                </th>
                <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Símbolo
                </th>
                <th className="px-6 py-3 bg-gray-50 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Valor Total (USD)
                </th>
                <th className="px-6 py-3 bg-gray-50 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Transacciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {stats.unique_tokens.map((token: TokenInfo) => (
                <tr key={token.address}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {token.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {token.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                    ${token.total_value_usd.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                    {token.transaction_count.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Contratos más frecuentes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Contratos Más Frecuentes</h2>
        <div className="space-y-2">
          {stats.most_frequent_contracts.map((contract, index) => (
            <div
              key={contract}
              className="flex items-center justify-between p-3 bg-gray-50 rounded"
            >
              <span className="text-gray-600 font-mono">{contract}</span>
              <span className="text-gray-500 text-sm">
                #{index + 1} más frecuente
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Report;