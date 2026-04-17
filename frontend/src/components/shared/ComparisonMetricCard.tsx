import { ComparisonMetrics } from '../../services/api';

type CardTheme = 'green' | 'purple' | 'orange';

interface ComparisonMetricCardProps {
  title: string;
  data?: Partial<ComparisonMetrics> | null;
  theme?: CardTheme;
  variant?: 'dark' | 'light';
}

const DARK_THEME = {
  green: 'border-green-500/30 bg-green-500/10 text-green-300',
  purple: 'border-purple-500/30 bg-purple-500/10 text-purple-300',
  orange: 'border-orange-500/30 bg-orange-500/10 text-orange-300',
} as const;

const LIGHT_THEME = {
  green: 'border-green-200 bg-green-50',
  purple: 'border-purple-200 bg-purple-50',
  orange: 'border-orange-200 bg-orange-50',
} as const;

function asPercent(value: number | undefined) {
  return `${(((value || 0) * 100)).toFixed(1)}%`;
}

export default function ComparisonMetricCard({
  title,
  data,
  theme = 'green',
  variant = 'dark',
}: ComparisonMetricCardProps) {
  const segments = Array.isArray(data?.segments) ? [...data.segments].sort((left, right) => left - right) : [];
  const nodes = Array.isArray(data?.nodes) ? data.nodes : [];
  const edges = Array.isArray(data?.edges) ? data.edges : [];
  const segmentPrecision = data?.segment_precision ?? data?.segment_accuracy ?? 0;
  const segmentRecall = data?.segment_recall ?? data?.segment_accuracy ?? 0;
  const segmentF1 = data?.segment_f1 ?? data?.segment_accuracy ?? 0;
  const segmentMatches = data?.segment_matches ?? 0;
  const segmentExpected = data?.segment_expected ?? segments.length;
  const meaningfulNodes = data?.meaningful_nodes ?? nodes.length;
  const validRelations = data?.valid_relations ?? edges.length;
  const expectedRelations = data?.expected_relations ?? 0;
  const graphAccuracy = data?.graph_accuracy ?? 0;
  const semanticQuality = data?.semantic_quality ?? 0;
  const semanticSimilarity = data?.semantic_similarity ?? 0;
  const finalScore = data?.final_graph_score ?? data?.final_score ?? 0;

  const themeClass = variant === 'dark' ? DARK_THEME[theme] : LIGHT_THEME[theme];
  const textClass = variant === 'dark' ? 'text-slate-200' : 'text-sm';

  return (
    <div className={`rounded-lg border p-4 ${themeClass}`}>
      <h3 className="font-semibold mb-3">{title}</h3>
      <div className={`space-y-2 ${textClass}`}>
        <div>Relevant Segments: {segments.length ? segments.join(', ') : 'None'}</div>
        <div>Correct Matches: {segmentMatches} / {segmentExpected}</div>
        <div>Meaningful Nodes: {meaningfulNodes}</div>
        <div>Valid Relations: {validRelations}{expectedRelations ? ` / ${expectedRelations}` : ''}</div>
        <div>Segment Precision: {asPercent(segmentPrecision)}</div>
        <div>Segment Recall: {asPercent(segmentRecall)}</div>
        <div>Segment F1: {asPercent(segmentF1)}</div>
        <div>Graph Accuracy: {asPercent(graphAccuracy)}</div>
        <div>Semantic Quality: {asPercent(semanticQuality)}</div>
        <div>Semantic Similarity: {asPercent(semanticSimilarity)}</div>
        <div className="font-semibold">Weighted Evaluation Score: {asPercent(finalScore)}</div>
      </div>
    </div>
  );
}
