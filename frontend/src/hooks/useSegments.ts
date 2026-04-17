import { useMemo } from 'react';
import { ProcessingResult } from '../services/api';

export default function useSegments(result: ProcessingResult | null) {
  const relevancePercentage = useMemo(() => {
    if (!result || result.total_segments === 0) {
      return 0;
    }
    return (result.relevant_segments.length / result.total_segments) * 100;
  }, [result]);

  const sortedRelevantSegments = useMemo(() => {
    if (!result) {
      return [];
    }

    return [...result.relevant_segments].sort((left, right) => {
      const leftScore = left.confidence ?? left.relevance_score ?? 0;
      const rightScore = right.confidence ?? right.relevance_score ?? 0;
      return rightScore - leftScore;
    });
  }, [result]);

  return {
    relevancePercentage,
    sortedRelevantSegments,
  };
}
