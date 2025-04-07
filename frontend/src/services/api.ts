import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { useState, useEffect, useRef } from 'react';
import { 
  APIResponse, 
  UploadResponse, 
  AnalysisStatus, 
  AnalysisReport, 
  GraphData 
} from '../types';

// Crear instancia de axios con configuración base
const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: any) => {
    const message = error.response?.data?.detail || 'Ha ocurrido un error';
    return Promise.reject({ message });
  }
);

// Servicios de API
export const walletApi = {
  // Subir archivo CSV
  uploadCsv: async (file: File): Promise<APIResponse<UploadResponse>> => {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse = await api.post('/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  // Obtener estado del análisis
  getAnalysisStatus: async (analysisId: string): Promise<APIResponse<AnalysisStatus>> => {
    const response: AxiosResponse = await api.get(`/analysis/${analysisId}/status`);
    return response.data;
  },

  // Obtener reporte completo
  getAnalysisReport: async (analysisId: string): Promise<APIResponse<AnalysisReport>> => {
    const response: AxiosResponse = await api.get(`/analysis/${analysisId}/report`);
    return response.data;
  },

  // Obtener datos del grafo
  getAnalysisGraph: async (analysisId: string): Promise<APIResponse<GraphData>> => {
    const response: AxiosResponse = await api.get(`/analysis/${analysisId}/graph`);
    return response.data;
  },

  // Descargar reporte en formato específico
  downloadReport: async (analysisId: string, format: 'pdf' | 'csv'): Promise<Blob> => {
    const response: AxiosResponse = await api.get(
      `/analysis/${analysisId}/download/${format}`,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },
};

// Hook personalizado para polling del estado del análisis
export const useAnalysisPolling = (
  analysisId: string,
  interval: number = 5000
): { 
  status: AnalysisStatus | null;
  error: string | null;
  stopPolling: () => void;
} => {
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollInterval = useRef<number>();

  const stopPolling = () => {
    if (pollInterval.current) {
      clearInterval(pollInterval.current);
    }
  };

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await walletApi.getAnalysisStatus(analysisId);
        setStatus(response.data);
        
        // Detener polling si el análisis está completo o hay un error
        if (response.data.status === 'completed' || response.data.status === 'error') {
          stopPolling();
        }
      } catch (err: any) {
        setError(err.message);
        stopPolling();
      }
    };

    // Iniciar polling
    pollStatus();
    pollInterval.current = window.setInterval(pollStatus, interval);

    // Cleanup
    return () => {
      stopPolling();
    };
  }, [analysisId, interval]);

  return { status, error, stopPolling };
};

export default walletApi;