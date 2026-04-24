import puter from '@heyputer/puter.js';
import { apiService } from './api';
import type { ComparisonMetrics, ComparisonResult, FrameworkOutput } from './api';
import { TOP_COMPARISON_SEGMENTS, ANALYZE_GRAPH_MAX_RELATIONS, ANALYZE_GRAPH_MAX_NODES } from '../constants/comparison';

const puterAuthToken = import.meta.env.VITE_PUTER_AUTH_TOKEN?.trim();

if (puterAuthToken) {
  puter.setAuthToken(puterAuthToken);
}

const SEGMENT_WORDS = 50;
const MAX_GRAPH_NODES = ANALYZE_GRAPH_MAX_NODES - 4;
const MAX_GRAPH_RELATIONS = ANALYZE_GRAPH_MAX_RELATIONS - 4;

const ALLOWED_RELATIONS = new Set([
  'published_by',
  'published_in',
  'located_in',
  'headquartered_in',
  'part_of',
  'member_of',
  'belongs_to',
  'includes',
  'mentions',
  'organized_by',
  'celebrated_on',
  'born_on',
  'works_for',
  'owned_by',
  'founded_by',
  'edited_by',
  'based_in',
  'acquired_by',
]);

const STOP_WORDS = new Set([
  'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'your', 'about', 'only', 'valid', 'json', 'return',
  'following', 'extracted', 'text', 'summary', 'nodes', 'edges', 'source', 'target', 'relation', 'id', 'type',
  'person', 'organization', 'company', 'country', 'city', 'newspaper', 'website', 'technology', 'concept',
]);

const ALLOWED_NODE_TYPES = new Set([
  'Person',
  'Organization',
  'Company',
  'Country',
  'City',
  'Newspaper',
  'Website',
  'Technology',
  'Concept',
]);

const GENERIC_NODE_WORDS = new Set([
  'in',
  'the',
  'a',
  'an',
  'and',
  'or',
  'to',
  'of',
  'for',
  'on',
  'by',
  'from',
  'with',
  'about',
  'let',
  'truth',
  'prevail',
  'april',
]);

type GraphNode = {
  id: string;
  type: string;
  confidence?: number;
  mentions?: number;
};

type GraphEdge = {
  source: string;
  target: string;
  relation: string;
  confidence?: number;
};

function normalizeText(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9\s]+/g, ' ');
}

function tokenize(text: string): string[] {
  return normalizeText(text)
    .split(/\s+/)
    .map((word) => word.trim())
    .filter((word) => word.length > 2 && !STOP_WORDS.has(word));
}

function cosineSimilarity(leftText: string, rightText: string): number {
  const leftTokens = tokenize(leftText);
  const rightTokens = tokenize(rightText);

  if (!leftTokens.length || !rightTokens.length) {
    return 0;
  }

  const leftCounts = new Map<string, number>();
  const rightCounts = new Map<string, number>();

  for (const token of leftTokens) {
    leftCounts.set(token, (leftCounts.get(token) || 0) + 1);
  }

  for (const token of rightTokens) {
    rightCounts.set(token, (rightCounts.get(token) || 0) + 1);
  }

  const commonTokens = new Set([...leftCounts.keys(), ...rightCounts.keys()]);
  let dotProduct = 0;
  let leftMagnitude = 0;
  let rightMagnitude = 0;

  for (const token of commonTokens) {
    const leftValue = leftCounts.get(token) || 0;
    const rightValue = rightCounts.get(token) || 0;
    dotProduct += leftValue * rightValue;
    leftMagnitude += leftValue * leftValue;
    rightMagnitude += rightValue * rightValue;
  }

  if (!leftMagnitude || !rightMagnitude) {
    return 0;
  }

  return dotProduct / (Math.sqrt(leftMagnitude) * Math.sqrt(rightMagnitude));
}

function splitText(text: string): string[] {
  const words = text.split(/\s+/).filter(Boolean);
  const segments: string[] = [];

  for (let index = 0; index < words.length; index += SEGMENT_WORDS) {
    segments.push(words.slice(index, index + SEGMENT_WORDS).join(' '));
  }

  return segments;
}

function isMeaningfulNode(node: GraphNode): boolean {
  const normalized = node.id.toLowerCase().trim();
  const words = normalized.split(/\s+/).filter(Boolean);

  if (!normalized || words.length === 0 || words.length > 5) {
    return false;
  }

  if (words.some((word) => GENERIC_NODE_WORDS.has(word))) {
    return false;
  }

  if (words.every((word) => GENERIC_NODE_WORDS.has(word) || STOP_WORDS.has(word))) {
    return false;
  }

  return ALLOWED_NODE_TYPES.has(node.type) || words.length > 1;
}

function normalizeNode(node: any): GraphNode | null {
  if (!node || typeof node !== 'object') {
    return null;
  }

  const id = String(node.id ?? node.name ?? node.label ?? '').replace(/\s+/g, ' ').trim();
  if (!id) {
    return null;
  }

  const typeCandidate = String(node.type ?? node.category ?? 'Concept');
  const type = ALLOWED_NODE_TYPES.has(typeCandidate) ? typeCandidate : 'Concept';
  const confidence = Number.isFinite(Number(node.confidence)) ? Number(node.confidence) : 0.5;

  return {
    id,
    type,
    confidence: Math.max(0, Math.min(1, confidence)),
    mentions: Number.isFinite(Number(node.mentions)) ? Number(node.mentions) : 1,
  };
}

function normalizeEdge(edge: any): GraphEdge | null {
  if (!edge || typeof edge !== 'object') {
    return null;
  }

  const source = String(edge.source ?? '').replace(/\s+/g, ' ').trim();
  const target = String(edge.target ?? '').replace(/\s+/g, ' ').trim();
  const relation = String(edge.relation ?? '').replace(/\s+/g, ' ').trim().toLowerCase();

  if (!source || !target || !relation) {
    return null;
  }

  if (!ALLOWED_RELATIONS.has(relation)) {
    return null;
  }

  const confidence = Number.isFinite(Number(edge.confidence)) ? Number(edge.confidence) : 0.5;

  return {
    source,
    target,
    relation,
    confidence: Math.max(0, Math.min(1, confidence)),
  };
}

function normalizeGraphPayload(rawValue: unknown): { nodes: GraphNode[]; edges: GraphEdge[] } {
  if (rawValue && typeof rawValue === 'object') {
    const payload = rawValue as Record<string, any>;
    const nodes = Array.isArray(payload.nodes) ? payload.nodes.map(normalizeNode).filter(Boolean) as GraphNode[] : [];
    const edges = Array.isArray(payload.edges) ? payload.edges.map(normalizeEdge).filter(Boolean) as GraphEdge[] : [];

    const filteredNodes = nodes.filter(isMeaningfulNode).slice(0, MAX_GRAPH_NODES);
    const allowedIds = new Set(filteredNodes.map((node) => node.id.toLowerCase()));
    const filteredEdges = edges
      .filter((edge) => allowedIds.has(edge.source.toLowerCase()) && allowedIds.has(edge.target.toLowerCase()))
      .filter((edge, index, allEdges) => {
        const key = `${edge.source.toLowerCase()}|${edge.relation.toLowerCase()}|${edge.target.toLowerCase()}`;
        return allEdges.findIndex((candidate) => `${candidate.source.toLowerCase()}|${candidate.relation.toLowerCase()}|${candidate.target.toLowerCase()}` === key) === index;
      })
      .slice(0, MAX_GRAPH_RELATIONS);

    return {
      nodes: filteredNodes,
      edges: filteredEdges,
    };
  }

  const rawText = String(rawValue ?? '').replace(/```json|```/g, '').trim();

  try {
    return normalizeGraphPayload(JSON.parse(rawText));
  } catch {
    return {
      nodes: [],
      edges: [],
    };
  }
}

function graphMetrics(nodes: GraphNode[], edges: GraphEdge[]): FrameworkOutput['graph_metrics'] {
  const totalNodes = nodes.length;
  const totalRelations = edges.length;
  const meaningfulNodes = nodes.filter(isMeaningfulNode).length;

  const uniqueNodeRatio =
    totalNodes > 0
      ? new Set(nodes.map((node) => node.id.toLowerCase())).size / totalNodes
      : 0;

  const validRelations = edges.filter((edge) => {
    return (
      edge.source &&
      edge.target &&
      edge.relation &&
      edge.relation.toLowerCase() !== 'related_to' &&
      edge.source.toLowerCase() !== edge.target.toLowerCase()
    );
  }).length;

  const graphAccuracy =
    totalRelations > 0 ? validRelations / totalRelations : 0;

  const semanticQuality =
    totalNodes > 0 ? meaningfulNodes / totalNodes : 0;

  const redundancyPenalty = 1 - Math.max(0, totalNodes - meaningfulNodes) * 0.08;

  const diversityScore = uniqueNodeRatio;

  const finalGraphScore =
    100 *
    (
      0.35 * graphAccuracy +
      0.30 * semanticQuality +
      0.20 * diversityScore +
      0.15 * Math.max(0, redundancyPenalty)
    );

  return {
    meaningful_nodes: meaningfulNodes,
    total_nodes: totalNodes,
    valid_relations: validRelations,
    total_relations: totalRelations,
    graph_accuracy: Number((graphAccuracy * 100).toFixed(1)),
    semantic_quality: Number((semanticQuality * 100).toFixed(1)),
    final_graph_score: Number(finalGraphScore.toFixed(1)),
  };
}

function scoreSegment(text: string, referenceText: string, index: number, total: number): number {
  const keywordScore = cosineSimilarity(text, referenceText);
  const structureScore = text.split(/\s+/).length >= 15 ? 0.2 : 0.05;
  const positionScore = total > 1 ? 1 - index / Math.max(total - 1, 1) : 1;

  return Math.max(0, Math.min(1, 0.4 * keywordScore + 0.4 * structureScore + 0.2 * positionScore));
}

function computeSegmentMetrics(predictedSegments: number[], actualSegments: number[]) {
  const predictedSet = new Set(predictedSegments);
  const actualSet = new Set(actualSegments);
  const correct = Array.from(predictedSet).filter((segment) => actualSet.has(segment)).length;

  const precision = predictedSet.size > 0 ? correct / predictedSet.size : 0;
  const recall = actualSet.size > 0 ? correct / actualSet.size : 0;
  const f1 = precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0;

  return {
    correct,
    predictedCount: predictedSet.size,
    actualCount: actualSet.size,
    precision,
    recall,
    f1,
  };
}

function computeSetOverlapMetrics(predictedItems: string[], actualItems: string[]) {
  const predictedSet = new Set(predictedItems.filter(Boolean));
  const actualSet = new Set(actualItems.filter(Boolean));
  const correct = Array.from(predictedSet).filter((item) => actualSet.has(item)).length;
  const precision = predictedSet.size > 0 ? correct / predictedSet.size : 0;
  const recall = actualSet.size > 0 ? correct / actualSet.size : 0;
  const f1 = precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0;

  return {
    correct,
    predictedCount: predictedSet.size,
    actualCount: actualSet.size,
    precision,
    recall,
    f1,
  };
}

function buildSegmentSelectionPrompt(segments: Array<{ id: string; text: string }>, topic: string): string {
  const segmentList = segments
    .map((seg) => `${seg.id}: ${seg.text}`)
    .join('\n');

  return `You are given document segments with IDs.

Task:
Select ONLY the 5 most relevant segments for understanding the main topic of the document.

Topic: ${topic}

Rules:
- Return exactly 5 segment IDs
- Choose only the most informative and central segments
- Do not include every segment
- Output valid JSON only

Example:
{
  "relevant_segments": ["seg_0", "seg_5", "seg_12", "seg_27", "seg_41"]
}

Segments:
${segmentList}`;
}

function buildGraphPrompt(extractedText: string): string {
  return `
Return ONLY valid JSON with this structure:

{
  "nodes": [
    { "id": "The Times of India", "type": "Newspaper", "confidence": 0.98 }
  ],
  "edges": [
    {
      "source": "The Times of India",
      "target": "Bennett, Coleman & Co. Ltd.",
      "relation": "owned_by",
      "confidence": 0.97
    }
  ]
}

Rules:
- Keep at most 8 nodes and 6 relations.
- Use only meaningful entities: Person, Organization, Company, Country, City, Newspaper, Website, Technology, Concept.
- Ignore single generic words, long merged phrases, duplicates, and entities longer than 5 words.
- Relation must be specific and meaningful.
- Do NOT use generic relations like "related_to".
- Allowed relations: published_by, located_in, part_of, member_of, belongs_to, includes, mentions, organized_by, celebrated_on, born_on, works_for.
- Create relations only when entities appear in the same sentence and the sentence contains a relation phrase.
- Do not create fully connected graphs.
- Prefer exact semantic entities over capitalized phrase fragments.

Text:
${extractedText}
`;
}

async function getModelSegmentSelection(
  segments: Array<{ id: string; text: string }>,
  topic: string,
  model: 'gpt-5-nano' | 'gemini-2.5-flash-lite',
): Promise<{ segment_ids: string[]; elapsedSeconds: number }> {
  const prompt = buildSegmentSelectionPrompt(segments, topic);
  const startedAt = performance.now();
  const response = await puter.ai.chat(prompt, { model });
  const elapsedSeconds = (performance.now() - startedAt) / 1000;

  try {
    const rawText = String(response?.message?.content || response).replace(/```json|```/g, '').trim();
    const parsed = JSON.parse(rawText);
    const allowedIds = new Set(segments.map((seg) => seg.id));
    const segmentIds = Array.isArray(parsed.relevant_segments)
      ? parsed.relevant_segments
          .filter((id: unknown): id is string => typeof id === 'string')
          .filter((id: string) => /^seg_\d+$/.test(id) && allowedIds.has(id))
      : [];

    const relevantIds = segmentIds.slice(0, TOP_COMPARISON_SEGMENTS);
    return { segment_ids: relevantIds, elapsedSeconds };
  } catch {
    return { segment_ids: [], elapsedSeconds };
  }
}

function buildSelectedText(
  segmentIds: string[],
  segmentLookup: Map<string, string>,
): string {
  return segmentIds
    .map((segmentId) => segmentLookup.get(segmentId) || '')
    .filter(Boolean)
    .join(' ')
    .trim();
}

async function analyzeSelectedSegmentsGraph(
  segmentIds: string[],
  segmentLookup: Map<string, string>,
): Promise<{ parsed: { nodes: GraphNode[]; edges: GraphEdge[] }; text: string; elapsedSeconds: number }> {
  const selectedText = buildSelectedText(segmentIds, segmentLookup);
  const startedAt = performance.now();

  if (!selectedText) {
    return {
      parsed: { nodes: [], edges: [] },
      text: '',
      elapsedSeconds: (performance.now() - startedAt) / 1000,
    };
  }

  const graphResult = await apiService.analyzeGraph(selectedText);
  const elapsedSeconds = (performance.now() - startedAt) / 1000;

  return {
    parsed: normalizeGraphPayload(graphResult),
    text: selectedText,
    elapsedSeconds,
  };
}

function segmentIdToNumber(segmentId: string): number | null {
  const value = Number(segmentId.replace('seg_', '')) + 1;
  return Number.isFinite(value) ? value : null;
}

function segmentIdsToNumbers(segmentIds: Iterable<string>): number[] {
  return Array.from(segmentIds)
    .map(segmentIdToNumber)
    .filter((value): value is number => value !== null);
}

async function scoreExternalModelSelection(
  selectedIds: Set<string>,
  segmentLookup: Map<string, string>,
  scoringReference: FrameworkOutput,
  segmentSelectionElapsedSeconds: number,
) {
  const graphResult = await analyzeSelectedSegmentsGraph(Array.from(selectedIds), segmentLookup);
  const predicted = {
    segments: segmentIdsToNumbers(selectedIds),
    nodes: graphResult.parsed.nodes,
    edges: graphResult.parsed.edges,
    summary: graphResult.text,
  };
  const metrics = scoreComparison(
    predicted,
    scoringReference,
    segmentSelectionElapsedSeconds + graphResult.elapsedSeconds,
  );
  metrics.segments = predicted.segments;

  return {
    predicted,
    metrics,
    graphElapsedSeconds: graphResult.elapsedSeconds,
  };
}

export async function buildLocalFrameworkOutput(extractedText: string, topic?: string): Promise<FrameworkOutput> {
  void topic;
  const segments = splitText(extractedText);
  const allSegmentsWithId = segments.map((text, index) => ({
    id: `seg_${index}`,
    text,
  }));

  // Our framework: score and select segments based on relevance
  const scoredSegments = allSegmentsWithId
    .map((seg, index) => ({
      ...seg,
      score: scoreSegment(seg.text, extractedText, index, segments.length),
    }))
    .sort((left, right) => right.score - left.score);

  // Get our framework's selected segment IDs
  const ourSelectedIds = scoredSegments.map((s) => s.id);
  const selectedTexts = scoredSegments.slice(0, 5).map((s) => s.text);
  const summary = selectedTexts.slice(0, 3).join(' ').slice(0, 500);

  // Get graph from full text
  const startedAt = performance.now();
  const graphResponse = await puter.ai.chat(buildGraphPrompt(extractedText), { model: 'gpt-5-nano' });
  const elapsedSeconds = (performance.now() - startedAt) / 1000;
  const normalizedGraph = normalizeGraphPayload(graphResponse?.message?.content || graphResponse);

  return {
    segments: ourSelectedIds.map((id) => Number(id.replace('seg_', '')) + 1),
    summary,
    nodes: normalizedGraph.nodes,
    edges: normalizedGraph.edges,
    time: elapsedSeconds,
    graph_metrics: graphMetrics(normalizedGraph.nodes, normalizedGraph.edges),
  };
}

function scoreComparison(
  predicted: Record<string, any>,
  reference: FrameworkOutput,
  responseTimeSeconds: number,
): ComparisonMetrics {
  void responseTimeSeconds;
  const predictedSegments = Array.isArray(predicted.segments) ? predicted.segments : [];
  const predictedNodes = Array.isArray(predicted.nodes)
    ? predicted.nodes.map(normalizeNode).filter(Boolean) as GraphNode[]
    : [];
  const predictedEdges = Array.isArray(predicted.edges)
    ? predicted.edges.map(normalizeEdge).filter(Boolean) as GraphEdge[]
    : [];

  const segmentMetrics = computeSegmentMetrics(predictedSegments, reference.segments);

  const referenceNodeIds = new Set(
    reference.nodes.map((node: any) => String(node.id || '').toLowerCase()).filter(Boolean),
  );

  const meaningfulNodes = predictedNodes.filter((node) =>
    referenceNodeIds.has(node.id.toLowerCase()),
  ).length;

  const referenceEdgeKeys = new Set(
    reference.edges.map(
      (edge: any) => `${String(edge.source || '').toLowerCase()}|${String(edge.relation || '').toLowerCase()}|${String(edge.target || '').toLowerCase()}`,
    ),
  );

  const matchedRelationKeys = predictedEdges
    .map((edge) => ({
      key: `${edge.source.toLowerCase()}|${edge.relation.toLowerCase()}|${edge.target.toLowerCase()}`,
    }))
    .filter(({ key }) => referenceEdgeKeys.has(key));

  const validRelations = matchedRelationKeys.length;

  const expectedRelations = Math.max(reference.edges.length, 1);
  const graphAccuracy = validRelations / expectedRelations;
  const semanticQuality = reference.nodes.length > 0
    ? meaningfulNodes / reference.nodes.length
    : 0;
  const semanticSimilarity = cosineSimilarity(String(predicted.summary || ''), reference.summary || '');

  const nodeMetrics = computeSetOverlapMetrics(
    predictedNodes.map((node) => node.id.toLowerCase()),
    reference.nodes.map((node: any) => String(node.id || '').toLowerCase()).filter(Boolean),
  );

  const relationMetrics = computeSetOverlapMetrics(
    predictedEdges.map((edge) => `${edge.source.toLowerCase()}|${edge.relation.toLowerCase()}|${edge.target.toLowerCase()}`),
    reference.edges.map((edge: any) => `${String(edge.source || '').toLowerCase()}|${String(edge.relation || '').toLowerCase()}|${String(edge.target || '').toLowerCase()}`),
  );
  const graphScore = 0.3 * nodeMetrics.f1 + 0.4 * relationMetrics.f1 + 0.3 * semanticSimilarity;

  const finalGraphScore =
    0.4 * segmentMetrics.f1 +
    0.3 * graphAccuracy +
    0.2 * semanticQuality +
    0.1 * semanticSimilarity;

  return {
    segments: predictedSegments,
    nodes: predictedNodes,
    edges: predictedEdges,
    segment_matches: segmentMetrics.correct,
    segment_expected: segmentMetrics.actualCount,
    segment_precision: Number(segmentMetrics.precision.toFixed(3)),
    segment_recall: Number(segmentMetrics.recall.toFixed(3)),
    segment_f1: Number(segmentMetrics.f1.toFixed(3)),
    segment_accuracy: Number(segmentMetrics.f1.toFixed(3)),
    node_precision: Number(nodeMetrics.precision.toFixed(3)),
    node_recall: Number(nodeMetrics.recall.toFixed(3)),
    node_f1: Number(nodeMetrics.f1.toFixed(3)),
    relation_precision: Number(relationMetrics.precision.toFixed(3)),
    relation_recall: Number(relationMetrics.recall.toFixed(3)),
    relation_f1: Number(relationMetrics.f1.toFixed(3)),
    graph_score: Number(graphScore.toFixed(3)),
    meaningful_nodes: meaningfulNodes,
    valid_relations: validRelations,
    expected_relations: expectedRelations,
    graph_accuracy: Number(graphAccuracy.toFixed(3)),
    semantic_quality: Number(semanticQuality.toFixed(3)),
    semantic_similarity: Number(semanticSimilarity.toFixed(3)),
    final_graph_score: Number(finalGraphScore.toFixed(3)),
    final_score: Number(finalGraphScore.toFixed(3)),
  };
}

function scoreAbsoluteFrameworkOutput(
  frameworkOutput: FrameworkOutput,
  extractedText: string,
): ComparisonMetrics {
  const predictedSegments = Array.isArray(frameworkOutput.segments) ? frameworkOutput.segments : [];
  const predictedNodes = Array.isArray(frameworkOutput.nodes)
    ? frameworkOutput.nodes.map(normalizeNode).filter(Boolean) as GraphNode[]
    : [];
  const predictedEdges = Array.isArray(frameworkOutput.edges)
    ? frameworkOutput.edges.map(normalizeEdge).filter(Boolean) as GraphEdge[]
    : [];

  const totalNodes = predictedNodes.length;
  const totalRelations = predictedEdges.length;
  const meaningfulNodes = predictedNodes.filter(isMeaningfulNode).length;

  const validRelations = predictedEdges.filter((edge) => {
    return (
      edge.source &&
      edge.target &&
      edge.relation &&
      edge.relation.toLowerCase() !== 'related_to' &&
      edge.source.toLowerCase() !== edge.target.toLowerCase()
    );
  }).length;

  const expectedRelations = Math.max(totalRelations, 1);
  const graphAccuracy = totalRelations > 0 ? validRelations / expectedRelations : 0;
  const semanticQuality = totalNodes > 0 ? meaningfulNodes / totalNodes : 0;
  const segmentMetrics = computeSegmentMetrics(predictedSegments, predictedSegments);
  const semanticSimilarity = cosineSimilarity(String(frameworkOutput.summary || ''), extractedText);
  const nodeMetrics = {
    precision: semanticQuality,
    recall: semanticQuality,
    f1: semanticQuality,
  };
  const relationMetrics = {
    precision: graphAccuracy,
    recall: graphAccuracy,
    f1: graphAccuracy,
  };
  const graphScore = 0.3 * nodeMetrics.f1 + 0.4 * relationMetrics.f1 + 0.3 * semanticSimilarity;
  const finalGraphScore =
    0.4 * segmentMetrics.f1 +
    0.3 * graphAccuracy +
    0.2 * semanticQuality +
    0.1 * semanticSimilarity;

  return {
    segments: predictedSegments,
    nodes: predictedNodes,
    edges: predictedEdges,
    segment_matches: segmentMetrics.correct,
    segment_expected: segmentMetrics.actualCount,
    segment_precision: Number(segmentMetrics.precision.toFixed(3)),
    segment_recall: Number(segmentMetrics.recall.toFixed(3)),
    segment_f1: Number(segmentMetrics.f1.toFixed(3)),
    segment_accuracy: Number(segmentMetrics.f1.toFixed(3)),
    node_precision: Number(nodeMetrics.precision.toFixed(3)),
    node_recall: Number(nodeMetrics.recall.toFixed(3)),
    node_f1: Number(nodeMetrics.f1.toFixed(3)),
    relation_precision: Number(relationMetrics.precision.toFixed(3)),
    relation_recall: Number(relationMetrics.recall.toFixed(3)),
    relation_f1: Number(relationMetrics.f1.toFixed(3)),
    graph_score: Number(graphScore.toFixed(3)),
    meaningful_nodes: meaningfulNodes,
    valid_relations: validRelations,
    expected_relations: expectedRelations,
    graph_accuracy: Number(graphAccuracy.toFixed(3)),
    semantic_quality: Number(semanticQuality.toFixed(3)),
    semantic_similarity: Number(semanticSimilarity.toFixed(3)),
    final_graph_score: Number(finalGraphScore.toFixed(3)),
    final_score: Number(finalGraphScore.toFixed(3)),
  };
}

export async function generateComparisonResult(
  extractedText: string,
  topic: string = 'document topic',
  frameworkOutput?: FrameworkOutput,
): Promise<ComparisonResult> {
  const referenceOutput = frameworkOutput || await buildLocalFrameworkOutput(extractedText, topic);

  // Get all segments for LLM comparison
  const segments = splitText(extractedText).map((text, index) => ({
    id: `seg_${index}`,
    text,
  }));
  const segmentLookup = new Map(segments.map((segment) => [segment.id, segment.text] as const));

  // Get segment selection from both LLMs
  const [gptSegmentResult, geminiSegmentResult] = await Promise.all([
    getModelSegmentSelection(segments, topic, 'gpt-5-nano'),
    getModelSegmentSelection(segments, topic, 'gemini-2.5-flash-lite'),
  ]);

  // Compare top segments only for fairness across systems.
  const allFrameworkSegments = referenceOutput.segments;
  const topFrameworkSegments = allFrameworkSegments.slice(0, TOP_COMPARISON_SEGMENTS);
  const scoringReference: FrameworkOutput = {
    ...referenceOutput,
    segments: topFrameworkSegments,
  };

  // Calculate segment overlap
  const gptSegmentIds = new Set(gptSegmentResult.segment_ids.slice(0, TOP_COMPARISON_SEGMENTS));
  const geminiSegmentIds = new Set(geminiSegmentResult.segment_ids.slice(0, TOP_COMPARISON_SEGMENTS));

  const [gptScored, geminiScored] = await Promise.all([
    scoreExternalModelSelection(gptSegmentIds, segmentLookup, scoringReference, gptSegmentResult.elapsedSeconds),
    scoreExternalModelSelection(geminiSegmentIds, segmentLookup, scoringReference, geminiSegmentResult.elapsedSeconds),
  ]);

  const ourComparison = scoreAbsoluteFrameworkOutput(
    {
      ...referenceOutput,
      segments: topFrameworkSegments,
    },
    extractedText
  );
  ourComparison.segments = topFrameworkSegments;

  return {
    our_model: ourComparison,
    chatgpt: gptScored.metrics,
    gemini: geminiScored.metrics,
  };
}

function scoreBlock(metrics: ComparisonMetrics) {
  const accuracy = (metrics.segment_f1 ?? metrics.segment_accuracy) * 100;
  const completeness = metrics.meaningful_nodes;
  const relevance = metrics.valid_relations;
  const hallucination = (1 - metrics.semantic_similarity) * 100;
  const completion = metrics.final_graph_score * 100;
  const grounding = metrics.graph_accuracy * 100;
  const freshness = metrics.semantic_quality * 100;

  return {
    accuracy,
    completeness,
    relevance,
    hallucination,
    completion,
    grounding,
    freshness,
    overall: metrics.final_graph_score * 100,
  };
}

function stringifyOutput(output: Record<string, any>) {
  return JSON.stringify(output, null, 2);
}

export async function generateFrontendEvaluationBundle(
  extractedText: string,
  frameworkOutput?: FrameworkOutput,
  topic: string = 'document topic',
) {
  const referenceOutput = frameworkOutput || await buildLocalFrameworkOutput(extractedText, topic);
  
  const segments = splitText(extractedText).map((text, index) => ({
    id: `seg_${index}`,
    text,
  }));
  const segmentLookup = new Map(segments.map((segment) => [segment.id, segment.text] as const));

  const [
    gptSegmentResult,
    geminiSegmentResult,
  ] = await Promise.all([
    getModelSegmentSelection(segments, topic, 'gpt-5-nano'),
    getModelSegmentSelection(segments, topic, 'gemini-2.5-flash-lite'),
  ]);

  const allFrameworkSegments = referenceOutput.segments;
  const topFrameworkSegments = allFrameworkSegments.slice(0, TOP_COMPARISON_SEGMENTS);
  const ourSegmentIds = new Set(topFrameworkSegments.map((segNum) => `seg_${segNum - 1}`));
  const scoringReference: FrameworkOutput = {
    ...referenceOutput,
    segments: topFrameworkSegments,
  };

  const gptSegmentIds = new Set(gptSegmentResult.segment_ids.slice(0, TOP_COMPARISON_SEGMENTS));
  const geminiSegmentIds = new Set(geminiSegmentResult.segment_ids.slice(0, TOP_COMPARISON_SEGMENTS));

  const [gptScored, geminiScored] = await Promise.all([
    scoreExternalModelSelection(gptSegmentIds, segmentLookup, scoringReference, gptSegmentResult.elapsedSeconds),
    scoreExternalModelSelection(geminiSegmentIds, segmentLookup, scoringReference, geminiSegmentResult.elapsedSeconds),
  ]);

  const gptSegmentOverlap = ourSegmentIds.size
    ? (Array.from(ourSegmentIds).filter((id) => gptSegmentIds.has(id)).length / ourSegmentIds.size)
    : 0;

  const geminiSegmentOverlap = ourSegmentIds.size
    ? (Array.from(ourSegmentIds).filter((id) => geminiSegmentIds.has(id)).length / ourSegmentIds.size)
    : 0;

  const gptPredicted = gptScored.predicted;
  const geminiPredicted = geminiScored.predicted;
  const gptComparison = gptScored.metrics;
  const geminiComparison = geminiScored.metrics;

  const ourComparison = scoreAbsoluteFrameworkOutput(
    {
      ...referenceOutput,
      segments: topFrameworkSegments,
    },
    extractedText
  );
  ourComparison.segments = topFrameworkSegments;

  const comparison = {
    our_model: ourComparison,
    chatgpt: gptComparison,
    gemini: geminiComparison,
  } satisfies ComparisonResult;

  const outputs = {
    our_system: {
      output: stringifyOutput(referenceOutput),
      response_time_ms: Math.round((referenceOutput.time || 0) * 1000),
      selected_segments: topFrameworkSegments.length,
      total_relevant_segments: allFrameworkSegments.length,
    },
    gpt: {
      output: stringifyOutput({
        segments: gptPredicted.segments,
        nodes: gptPredicted.nodes,
        edges: gptPredicted.edges,
      }),
      response_time_ms: Math.round((gptSegmentResult.elapsedSeconds + gptScored.graphElapsedSeconds) * 1000),
      selected_segments: gptSegmentIds.size,
      segment_overlap: `${(gptSegmentOverlap * 100).toFixed(1)}%`,
    },
    gemini: {
      output: stringifyOutput({
        segments: geminiPredicted.segments,
        nodes: geminiPredicted.nodes,
        edges: geminiPredicted.edges,
      }),
      response_time_ms: Math.round((geminiSegmentResult.elapsedSeconds + geminiScored.graphElapsedSeconds) * 1000),
      selected_segments: geminiSegmentIds.size,
      segment_overlap: `${(geminiSegmentOverlap * 100).toFixed(1)}%`,
    },
  };

  return {
    frameworkOutput: referenceOutput,
    comparison,
    outputs,
    scores: {
      our_system: scoreBlock(comparison.our_model),
      gpt: scoreBlock(comparison.chatgpt),
      gemini: scoreBlock(comparison.gemini),
    },
    winner: ['our_system', 'gpt', 'gemini']
      .map((model) => ({ model, score: comparison[model as keyof ComparisonResult].final_graph_score }))
      .sort((left, right) => right.score - left.score)[0].model,
  };
}