import { useMemo } from 'react';

export type GraphNode = {
  id: string;
  type?: string;
  confidence?: number;
  importance?: number;
  level?: string;
  mentions?: number;
  source_sentence?: string;
  aliases?: string[];
};

export type GraphEdge = {
  source: string;
  target: string;
  sourceId: string;
  targetId: string;
  relation?: string;
  confidence?: number;
  sentence?: string;
  sentence_index?: number;
};

function simplifyEntityKey(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

function formatRelationLabel(value: string): string {
  const cleaned = value.replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (!cleaned) {
    return 'Related To';
  }

  return cleaned
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ');
}

function inferVerbLikeRelationFromText(sourceId: string, targetId: string, text: string): string | null {
  if (!text) {
    return null;
  }

  const sourceKey = simplifyEntityKey(sourceId);
  const targetKey = simplifyEntityKey(targetId);
  if (!sourceKey || !targetKey) {
    return null;
  }

  const sentences = text
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean)
    .slice(0, 500);

  const sentence = sentences.find((entry) => {
    const normalized = simplifyEntityKey(entry);
    return normalized.includes(sourceKey) && normalized.includes(targetKey);
  });

  if (!sentence) {
    return null;
  }

  const sentenceLower = sentence.toLowerCase();
  const sourceIndex = sentenceLower.indexOf(sourceId.toLowerCase());
  const targetIndex = sentenceLower.indexOf(targetId.toLowerCase());

  let relationZone = sentenceLower;
  if (sourceIndex >= 0 && targetIndex >= 0 && sourceIndex !== targetIndex) {
    const start = Math.min(sourceIndex, targetIndex);
    const end = Math.max(sourceIndex, targetIndex);
    relationZone = sentenceLower.slice(start, end);
  }

  const phraseRules: Array<{ phrase: string; label: string; score: number }> = [
    { phrase: 'owned by', label: 'Owned By', score: 100 },
    { phrase: 'appointed by', label: 'Appointed By', score: 96 },
    { phrase: 'founded by', label: 'Founded By', score: 95 },
    { phrase: 'published by', label: 'Published By', score: 94 },
    { phrase: 'located in', label: 'Located In', score: 93 },
    { phrase: 'based in', label: 'Based In', score: 92 },
    { phrase: 'part of', label: 'Part Of', score: 91 },
    { phrase: 'belongs to', label: 'Belongs To', score: 90 },
    { phrase: 'filed by', label: 'Filed By', score: 89 },
    { phrase: 'ruled by', label: 'Ruled By', score: 88 },
    { phrase: 'supports', label: 'Supports', score: 82 },
    { phrase: 'opposes', label: 'Opposes', score: 82 },
    { phrase: 'criticized', label: 'Criticized', score: 82 },
    { phrase: 'praised', label: 'Praised', score: 82 },
    { phrase: 'visited', label: 'Visited', score: 81 },
    { phrase: 'announced', label: 'Announced', score: 80 },
    { phrase: 'reported', label: 'Reported', score: 70 },
    { phrase: 'said', label: 'Said', score: 25 },
    { phrase: 'says', label: 'Says', score: 25 },
    { phrase: 'say', label: 'Says', score: 25 },
  ];

  const phraseCandidates = phraseRules
    .filter((rule) => relationZone.includes(rule.phrase) || sentenceLower.includes(rule.phrase))
    .sort((a, b) => b.score - a.score);

  if (phraseCandidates.length > 0) {
    return phraseCandidates[0].label;
  }

  const words = relationZone.match(/[a-z]+/g) || sentenceLower.match(/[a-z]+/g) || [];
  const stopWords = new Set([
    'the', 'a', 'an', 'to', 'of', 'in', 'on', 'for', 'at', 'by', 'with', 'from', 'and', 'or', 'but',
    'that', 'this', 'these', 'those', 'as', 'it', 'its', 'their', 'his', 'her', 'our', 'your', 'they',
    'he', 'she', 'we', 'you', 'will', 'would', 'can', 'could', 'may', 'might', 'should',
  ]);
  const lowPriorityVerbs = new Set(['say', 'says', 'said', 'tell', 'tells', 'told']);

  const candidates = words.filter((word) => {
    if (stopWords.has(word) || word.length <= 3) {
      return false;
    }
    return /ed$|ing$|es$|s$/.test(word);
  });

  const bestCandidate = candidates.find((word) => !lowPriorityVerbs.has(word)) || candidates[0];
  if (!bestCandidate) {
    return null;
  }

  return formatRelationLabel(bestCandidate);
}

function resolveRelationLabel(
  originalRelation: string | undefined,
  sourceId: string,
  targetId: string,
  contextText: string,
): string | undefined {
  const cleaned = (originalRelation || '').trim();
  const generic = !cleaned || /^mentions?$/i.test(cleaned) || /^related\s*to$/i.test(cleaned);

  if (!generic) {
    return formatRelationLabel(cleaned);
  }

  const inferred = inferVerbLikeRelationFromText(sourceId, targetId, contextText);
  if (inferred) {
    return inferred;
  }

  return cleaned ? formatRelationLabel(cleaned) : 'Related To';
}

function normalizeGraphNodes(nodes: any[]): GraphNode[] {
  if (!Array.isArray(nodes)) {
    return [];
  }

  return nodes
    .map((node, index) => {
      if (!node || typeof node !== 'object') {
        return { id: `Node ${index + 1}` };
      }

      const rawId = node.id ?? node.name ?? node.label ?? `Node ${index + 1}`;
      return {
        id: String(rawId),
        type: node.type ? String(node.type) : undefined,
        confidence: Number.isFinite(Number(node.confidence)) ? Number(node.confidence) : undefined,
        importance: Number.isFinite(Number(node.importance)) ? Number(node.importance) : undefined,
        level: node.level ? String(node.level) : undefined,
        mentions: Number.isFinite(Number(node.mentions)) ? Number(node.mentions) : undefined,
        source_sentence: node.source_sentence ? String(node.source_sentence) : undefined,
        aliases: Array.isArray(node.aliases) ? node.aliases.map((alias: unknown) => String(alias)) : undefined,
      };
    })
    .filter((node) => node.id.trim().length > 0);
}

function normalizeGraphEdges(edges: any[], nodes: GraphNode[], contextText: string): GraphEdge[] {
  if (!Array.isArray(edges)) {
    return [];
  }

  const canonicalBySimpleKey = new Map<string, string>();
  nodes.forEach((node) => {
    canonicalBySimpleKey.set(simplifyEntityKey(node.id), node.id);
  });

  const resolveNodeId = (value: unknown): string | null => {
    if (value === undefined || value === null) {
      return null;
    }

    const raw = String(value).trim();
    if (!raw) {
      return null;
    }

    const direct = canonicalBySimpleKey.get(simplifyEntityKey(raw));
    return direct || raw;
  };

  return edges
    .map((edge) => {
      if (!edge || typeof edge !== 'object') {
        return null;
      }

      const source = edge.source ?? edge.from;
      const target = edge.target ?? edge.to;
      if (source === undefined || target === undefined) {
        return null;
      }

      const sourceId = resolveNodeId(source);
      const targetId = resolveNodeId(target);
      if (!sourceId || !targetId || sourceId === targetId) {
        return null;
      }

      return {
        source: String(source),
        target: String(target),
        sourceId,
        targetId,
        relation: resolveRelationLabel(
          edge.relation ? String(edge.relation) : undefined,
          sourceId,
          targetId,
          contextText,
        ),
        confidence: Number.isFinite(Number(edge.confidence)) ? Number(edge.confidence) : undefined,
        sentence: edge.sentence ? String(edge.sentence) : undefined,
        sentence_index: Number.isFinite(Number(edge.sentence_index)) ? Number(edge.sentence_index) : undefined,
      };
    })
    .filter((edge): edge is GraphEdge => Boolean(edge));
}

export default function useKnowledgeGraph(nodes: any[], edges: any[], contextText: string) {
  const normalizedGraphNodes = useMemo(() => normalizeGraphNodes(nodes), [nodes]);
  const normalizedGraphEdges = useMemo(
    () => normalizeGraphEdges(edges, normalizedGraphNodes, contextText),
    [edges, normalizedGraphNodes, contextText],
  );

  return {
    normalizedGraphNodes,
    normalizedGraphEdges,
  };
}
