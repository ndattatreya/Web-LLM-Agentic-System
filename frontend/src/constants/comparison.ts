export const COMPARISON_FORMULA_TEXT =
  'Overall Score = 0.4 × Segment F1 + 0.3 × Graph Accuracy + 0.2 × Semantic Quality + 0.1 × Semantic Similarity';

export const COMPARISON_METRIC_GUIDE = [
  'Segment F1: quality of retrieved relevant segments',
  'Graph Accuracy: correctness of extracted relations',
  'Semantic Quality: richness and usefulness of nodes',
  'Semantic Similarity: closeness to the reference graph',
] as const;

export const TOP_COMPARISON_SEGMENTS = 5;
export const ANALYZE_GRAPH_MAX_NODES = 12;
export const ANALYZE_GRAPH_MAX_RELATIONS = 10;
