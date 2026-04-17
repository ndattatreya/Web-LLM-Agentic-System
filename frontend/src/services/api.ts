import axios from 'axios';
import { ANALYZE_GRAPH_MAX_NODES, ANALYZE_GRAPH_MAX_RELATIONS } from '../constants/comparison';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  }
});

async function getData<T>(url: string): Promise<T> {
  const response = await api.get(url);
  return response.data as T;
}

async function postData<T>(url: string, data?: unknown, config?: Record<string, unknown>): Promise<T> {
  const response = await api.post(url, data, config);
  return response.data as T;
}

export interface Segment {
  id: string;
  text: string;
  is_relevant?: boolean;
  relevance_score?: number;
  confidence?: number;
}

export interface ComparisonMetrics {
  segments: number[];
  nodes: Array<Record<string, any>>;
  edges: Array<Record<string, any>>;
  segment_matches: number;
  segment_expected: number;
  segment_precision: number;
  segment_recall: number;
  segment_f1: number;
  segment_accuracy: number;
  node_precision: number;
  node_recall: number;
  node_f1: number;
  relation_precision: number;
  relation_recall: number;
  relation_f1: number;
  graph_score: number;
  meaningful_nodes: number;
  valid_relations: number;
  expected_relations?: number;
  graph_accuracy: number;
  semantic_quality: number;
  semantic_similarity: number;
  final_graph_score: number;
  final_score: number;
}

export interface ComparisonResult {
  our_model: ComparisonMetrics;
  chatgpt: ComparisonMetrics;
  gemini: ComparisonMetrics;
}

export interface FrameworkOutput {
  segments: number[];
  summary: string;
  nodes: Array<Record<string, any>>;
  edges: Array<Record<string, any>>;
  time?: number;
  graph_metrics?: {
    meaningful_nodes: number;
    total_nodes: number;
    valid_relations: number;
    total_relations: number;
    graph_accuracy: number;
    semantic_quality: number;
    final_graph_score: number;
  };
}

export interface ProcessingResult {
  source: string;
  source_type: string;
  raw_text: string;
  extracted_text?: string;
  total_segments: number;
  relevant_segments: Segment[];
  entities: string[];
  key_points: string[];
  processing_time: number;
  framework_output?: FrameworkOutput;
  knowledge_graph?: {
    nodes: Array<Record<string, any>>;
    edges: Array<Record<string, any>>;
    graph_metrics?: {
      meaningful_nodes: number;
      total_nodes: number;
      valid_relations: number;
      total_relations: number;
      graph_accuracy: number;
      semantic_quality: number;
      final_graph_score: number;
    };
  };
  comparison?: ComparisonResult;
}

export interface GraphAnalysisResult {
  nodes: Array<Record<string, any>>;
  edges: Array<Record<string, any>>;
  graph_metrics?: {
    meaningful_nodes: number;
    total_nodes: number;
    valid_relations: number;
    total_relations: number;
    graph_accuracy: number;
    semantic_quality: number;
    final_graph_score: number;
  };
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

  processURL: async (url: string): Promise<ProcessingResult> => {
    return postData<ProcessingResult>('/process/url', null, {
      params: { url }
    });
  },

  processFile: async (file: File): Promise<ProcessingResult> => {
    const formData = new FormData();
    formData.append('file', file);

    return postData<ProcessingResult>('/process/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
  },

  getDatasetStatistics: async (): Promise<DatasetStatistics> => {
    return getData<DatasetStatistics>('/data/dataset');
  },

  getModelComparison: async () => {
    return getData('/data/model-comparison');
  },

  getModelComparisonSummary: async (): Promise<ModelComparison> => {
    return getData<ModelComparison>('/data/model-comparison/summary');
  },

  analyzeGraph: async (text: string) => {
    return postData<GraphAnalysisResult>('/graph/analyze', {
      text,
      max_nodes: ANALYZE_GRAPH_MAX_NODES,
      max_relations: ANALYZE_GRAPH_MAX_RELATIONS,
    });
  },

  listResults: async () => {
    return getData('/results');
  },

  getResult: async (resultId: string) => {
    return getData(`/results/${resultId}`);
  }
};
