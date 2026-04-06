import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  }
});

export interface Segment {
  id: string;
  text: string;
  is_relevant?: boolean;
  relevance_score?: number;
  confidence?: number;
}

export interface ProcessingResult {
  source: string;
  source_type: string;
  raw_text: string;
  total_segments: number;
  relevant_segments: Segment[];
  entities: string[];
  key_points: string[];
  processing_time: number;
}

export interface DatasetStatistics {
  total_samples: number;
  relevant_count: number;
  irrelevant_count: number;
  relevant_percentage: number;
}

export interface ModelComparison {
  model_a: string;
  model_b: string;
  total_comparisons: number;
  model_a_avg_time: number;
  model_b_avg_time: number;
  faster_model: string;
  time_difference_percent: number;
}

export const apiService = {
  health: async () => {
    return api.get('/health');
  },

  processURL: async (url: string) => {
    try {
      const response = await api.post('/process/url', null, {
        params: { url }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  processFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await api.post('/process/file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getDatasetStatistics: async (): Promise<DatasetStatistics> => {
    try {
      const response = await api.get('/data/dataset');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getModelComparison: async () => {
    try {
      const response = await api.get('/data/model-comparison');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getModelComparisonSummary: async (): Promise<ModelComparison> => {
    try {
      const response = await api.get('/data/model-comparison/summary');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  listResults: async () => {
    try {
      const response = await api.get('/results');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getResult: async (resultId: string) => {
    try {
      const response = await api.get(`/results/${resultId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};
