import { useMemo } from 'react';
import { ComparisonMetrics, ProcessingResult } from '../services/api';

function getComparisonBlock(comparison: any, kind: 'our' | 'chatgpt' | 'gemini'): Partial<ComparisonMetrics> | null {
  if (!comparison || typeof comparison !== 'object') {
    return null;
  }

  if (kind === 'our') {
    return comparison.our_model || comparison.our_system || null;
  }
  if (kind === 'chatgpt') {
    return comparison.chatgpt || comparison.gpt || null;
  }
  return comparison.gemini || null;
}

export default function useComparison(result: ProcessingResult) {
  return useMemo(() => {
    const ourComparison = getComparisonBlock(result.comparison, 'our');
    const chatgptComparison = getComparisonBlock(result.comparison, 'chatgpt');
    const geminiComparison = getComparisonBlock(result.comparison, 'gemini');
    const graphSource = result.knowledge_graph || result.framework_output || null;
    const graphNodes = Array.isArray(graphSource?.nodes) ? graphSource.nodes : ourComparison?.nodes || [];
    const graphEdges = Array.isArray(graphSource?.edges) ? graphSource.edges : ourComparison?.edges || [];
    const graphMetrics = graphSource?.graph_metrics || null;

    const renderedOurComparison = ourComparison
      ? {
          ...ourComparison,
          nodes: graphNodes.length ? graphNodes : ourComparison.nodes || [],
          edges: graphEdges.length ? graphEdges : ourComparison.edges || [],
          meaningful_nodes: graphMetrics?.meaningful_nodes ?? ourComparison.meaningful_nodes ?? graphNodes.length,
          valid_relations: graphMetrics?.valid_relations ?? ourComparison.valid_relations ?? graphEdges.length,
          graph_accuracy: graphMetrics ? graphMetrics.graph_accuracy / 100 : ourComparison.graph_accuracy,
          semantic_quality: graphMetrics ? graphMetrics.semantic_quality / 100 : ourComparison.semantic_quality,
          final_graph_score: ourComparison.final_graph_score,
        }
      : null;

    return {
      graphSource,
      graphNodes,
      graphEdges,
      renderedOurComparison,
      chatgptComparison,
      geminiComparison,
      hasAnyComparisonCard: Boolean(renderedOurComparison || chatgptComparison || geminiComparison),
      frameworkComparisonScore: renderedOurComparison?.final_graph_score ?? 0,
    };
  }, [result]);
}
