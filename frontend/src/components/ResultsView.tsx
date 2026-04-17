import React, { useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Clock, Zap } from 'lucide-react';
import { ProcessingResult } from '../services/api';
import useSegments from '../hooks/useSegments';
import useComparison from '../hooks/useComparison';
import useKnowledgeGraph, { GraphEdge, GraphNode } from '../hooks/useKnowledgeGraph';
import SectionTabButton from './shared/SectionTabButton';
import ComparisonMetricCard from './shared/ComparisonMetricCard';
import ComparisonFormulaPanel from './shared/ComparisonFormulaPanel';

interface ResultsViewProps {
  result: ProcessingResult | null;
}

type ResultsSectionTab = 'overview' | 'segments' | 'graph' | 'comparison' | 'text';

export default function ResultsView({ result }: ResultsViewProps) {
  if (!result) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-12"
      >
        <div className="text-6xl mb-4">📋</div>
        <p className="text-slate-400">
          Process a document to see results here
        </p>
      </motion.div>
    );
  }

  const { relevancePercentage, sortedRelevantSegments } = useSegments(result);

  const [activeSectionTab, setActiveSectionTab] = useState<ResultsSectionTab>('overview');
  const {
    graphSource,
    graphNodes,
    graphEdges,
    renderedOurComparison,
    chatgptComparison,
    geminiComparison,
    hasAnyComparisonCard,
    frameworkComparisonScore,
  } = useComparison(result);
  const backendKnowledgeGraph = result.knowledge_graph || null;
  const { normalizedGraphNodes, normalizedGraphEdges } = useKnowledgeGraph(
    graphNodes,
    graphEdges,
    result.extracted_text || result.raw_text || ''
  );

  const formattedFrameworkScore = `${((frameworkComparisonScore > 1 ? frameworkComparisonScore : frameworkComparisonScore * 100)).toFixed(1)}%`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="grid md:grid-cols-4 gap-4">
        <SummaryCard
          icon={<Zap className="w-5 h-5" />}
          label="Source"
          value={result.source}
          subtitle={result.source_type}
        />
        <SummaryCard
          icon={<Clock className="w-5 h-5" />}
          label="Processing Time"
          value={`${result.processing_time.toFixed(2)}s`}
        />
        <SummaryCard
          icon={<CheckCircle className="w-5 h-5" />}
          label="Total Segments"
          value={result.total_segments.toString()}
        />
        <SummaryCard
          icon={<CheckCircle className="w-5 h-5" />}
          label="Relevant"
          value={`${result.relevant_segments.length}`}
          subtitle={`${relevancePercentage.toFixed(1)}% of total`}
        />
      </div>

      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-3">
        <div className="flex flex-wrap gap-2">
          <SectionTabButton
            active={activeSectionTab === 'overview'}
            onClick={() => setActiveSectionTab('overview')}
            label="Overview"
            variant="dark"
          />
          <SectionTabButton
            active={activeSectionTab === 'segments'}
            onClick={() => setActiveSectionTab('segments')}
            label={`Relevant Segments (${result.relevant_segments.length})`}
            variant="dark"
          />
          <SectionTabButton
            active={activeSectionTab === 'graph'}
            onClick={() => setActiveSectionTab('graph')}
            label="Knowledge Graph"
            variant="dark"
          />
          <SectionTabButton
            active={activeSectionTab === 'comparison'}
            onClick={() => setActiveSectionTab('comparison')}
            label="Comparison"
            variant="dark"
          />
          <SectionTabButton
            active={activeSectionTab === 'text'}
            onClick={() => setActiveSectionTab('text')}
            label="Extracted Text"
            variant="dark"
          />
        </div>
      </div>

      {activeSectionTab === 'overview' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4">Result Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-slate-300">
            <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-700">
              <p className="text-sm text-slate-400">Source</p>
              <p className="text-lg font-semibold text-white">{result.source}</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-700">
              <p className="text-sm text-slate-400">Source Type</p>
              <p className="text-lg font-semibold text-white">{result.source_type}</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-700">
              <p className="text-sm text-slate-400">Processing Time</p>
              <p className="text-lg font-semibold text-white">{result.processing_time.toFixed(2)}s</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-700">
              <p className="text-sm text-slate-400">Relevance Ratio</p>
              <p className="text-lg font-semibold text-white">{relevancePercentage.toFixed(1)}%</p>
            </div>
          </div>
        </motion.div>
      )}

      {activeSectionTab === 'segments' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>🔍</span> Relevant Segments ({result.relevant_segments.length})
          </h2>

          <div className="space-y-4 max-h-[600px] overflow-y-auto">
            {sortedRelevantSegments.length > 0 ? (
              sortedRelevantSegments.map((segment, idx) => (
                <motion.div
                  key={segment.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-4 bg-slate-700/50 border border-slate-600 rounded-lg hover:border-slate-500 transition-all"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3 flex-1">
                      <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-xs font-medium">
                        {segment.id}
                      </span>
                      {segment.relevance_score !== undefined && (
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-slate-600 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                              style={{ width: `${Math.min(segment.relevance_score * 100, 100)}%` }}
                            />
                          </div>
                          <span className="text-xs text-slate-400">
                            {(segment.relevance_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>
                    {segment.confidence !== undefined && (
                      <span className="text-xs text-slate-400">
                        Confidence: {(segment.confidence * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">
                    {segment.text}
                  </p>
                </motion.div>
              ))
            ) : (
              <div className="text-center py-8 text-slate-400">
                No relevant segments found
              </div>
            )}
          </div>
        </motion.div>
      )}

      {activeSectionTab === 'graph' && (
        (graphSource || renderedOurComparison) ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>🧠</span> Knowledge Graph
            </h2>
            <p className="mb-4 text-xs text-slate-400">
              Disconnected nodes are hidden in this view so the graph stays readable and focused on actual relations.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                <p className="text-sm text-green-300">Nodes</p>
                <p className="text-2xl font-bold text-white">{graphNodes.length || renderedOurComparison?.nodes?.length || 0}</p>
              </div>
              <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                <p className="text-sm text-green-300">Relations</p>
                <p className="text-2xl font-bold text-white">{graphEdges.length || renderedOurComparison?.edges?.length || 0}</p>
              </div>
              <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                <p className="text-sm text-green-300">Final Score</p>
                <p className="text-2xl font-bold text-white">
                  {formattedFrameworkScore}
                </p>
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-4">
              <div className="p-4 bg-slate-900/60 rounded-lg border border-slate-700 lg:col-span-2">
                <h3 className="text-sm font-semibold text-slate-200 mb-2">Graph Visualization</h3>
                <KnowledgeGraphCanvas
                  nodes={normalizedGraphNodes}
                  edges={normalizedGraphEdges}
                />
              </div>
              <div className="p-4 bg-slate-900/60 rounded-lg border border-slate-700">
                <h3 className="text-sm font-semibold text-slate-200 mb-2">Nodes (Raw)</h3>
                <div className="text-xs text-slate-300 font-mono max-h-48 overflow-auto whitespace-pre-wrap">
                  {JSON.stringify(normalizedGraphNodes || [], null, 2)}
                </div>
              </div>
              <div className="p-4 bg-slate-900/60 rounded-lg border border-slate-700">
                <h3 className="text-sm font-semibold text-slate-200 mb-2">Edges (Raw)</h3>
                <div className="text-xs text-slate-300 font-mono max-h-48 overflow-auto whitespace-pre-wrap">
                  {JSON.stringify(normalizedGraphEdges || [], null, 2)}
                </div>
              </div>
            </div>

            <div className="mt-4 p-4 bg-slate-900/60 rounded-lg border border-slate-700">
              <h3 className="text-sm font-semibold text-slate-200 mb-2">knowledge_representation.py Output</h3>
              <div className="text-xs text-slate-300 font-mono max-h-64 overflow-auto whitespace-pre-wrap">
                {JSON.stringify(backendKnowledgeGraph || graphSource || {}, null, 2)}
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 text-slate-400"
          >
            Knowledge graph data is not available for this result.
          </motion.div>
        )
      )}

      {activeSectionTab === 'comparison' && (
        hasAnyComparisonCard ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4">Comparison Cards</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <ComparisonMetricCard
                title="Our Framework"
                theme="green"
                data={renderedOurComparison}
                variant="dark"
              />
              <ComparisonMetricCard
                title="ChatGPT"
                theme="purple"
                data={chatgptComparison}
                variant="dark"
              />
              <ComparisonMetricCard
                title="Gemini"
                theme="orange"
                data={geminiComparison}
                variant="dark"
              />
            </div>
            <ComparisonFormulaPanel className="mt-4 rounded-lg border border-slate-700 bg-slate-900/40 p-4 text-sm text-slate-300" />
            <p className="mt-3 text-xs text-slate-400">
              Comparison uses the top 5 framework segments against the model-selected top segments for fairness.
            </p>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 text-slate-400"
          >
            Comparison metrics are not available for this result.
          </motion.div>
        )
      )}

      {activeSectionTab === 'text' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
        >
          <h3 className="text-lg font-bold text-white mb-4">📄 Extracted Text (Preview)</h3>
          <div className="p-4 bg-slate-900/50 rounded-lg font-mono text-sm text-slate-300 max-h-[300px] overflow-y-auto">
            {result.extracted_text || result.raw_text}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

interface SummaryCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  subtitle?: string;
}

function SummaryCard({ icon, label, value, subtitle }: SummaryCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition-all"
    >
      <div className="flex items-center gap-3 mb-2">
        <span className="text-blue-400">{icon}</span>
        <p className="text-slate-400 text-sm">{label}</p>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      {subtitle && (
        <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
      )}
    </motion.div>
  );
}

interface KnowledgeGraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

function KnowledgeGraphCanvas({ nodes, edges }: KnowledgeGraphCanvasProps) {
  if (!nodes.length) {
    return (
      <div className="h-72 rounded-lg border border-dashed border-slate-600 flex items-center justify-center text-sm text-slate-400">
        No nodes available to render the graph.
      </div>
    );
  }

  const width = 1600;
  const height = 920;
  const positioned = useMemo(() => buildKnowledgeGraphLayout(nodes, edges, width, height), [nodes, edges]);
  const positionedNodes = positioned.nodes;
  const positionedEdges = positioned.edges;
  const typeLegend = Array.from(new Set(positionedNodes.map((node) => node.type || 'Entity')));
  const visibleRelationLabels = useMemo(() => selectVisibleRelationLabels(positionedEdges), [positionedEdges]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(positionedNodes[0]?.id || null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const viewportRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setSelectedNodeId(positionedNodes[0]?.id || null);
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, [nodes, edges]);

  const selectedNode = positionedNodes.find((node) => node.id === selectedNodeId) || positionedNodes[0] || null;

  const clampZoom = (value: number) => Math.max(0.55, Math.min(1.8, Number(value.toFixed(2))));

  const adjustZoom = (delta: number) => {
    setZoom((current) => clampZoom(current + delta));
  };

  const shiftPan = (deltaX: number, deltaY: number) => {
    setPan((current) => ({
      x: Number((current.x + deltaX).toFixed(1)),
      y: Number((current.y + deltaY).toFixed(1)),
    }));
  };

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const focusViewport = () => {
    viewportRef.current?.focus();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const step = event.shiftKey ? 64 : 32;

    if (['INPUT', 'TEXTAREA'].includes((event.target as HTMLElement)?.tagName || '')) {
      return;
    }

    switch (event.key) {
      case 'ArrowUp':
      case 'w':
      case 'W':
        event.preventDefault();
        shiftPan(0, step);
        break;
      case 'ArrowDown':
      case 's':
      case 'S':
        event.preventDefault();
        shiftPan(0, -step);
        break;
      case 'ArrowLeft':
      case 'a':
      case 'A':
        event.preventDefault();
        shiftPan(step, 0);
        break;
      case 'ArrowRight':
      case 'd':
      case 'D':
        event.preventDefault();
        shiftPan(-step, 0);
        break;
      case '+':
      case '=':
        event.preventDefault();
        adjustZoom(0.12);
        break;
      case '-':
      case '_':
        event.preventDefault();
        adjustZoom(-0.12);
        break;
      case '0':
        event.preventDefault();
        resetView();
        break;
      default:
        break;
    }
  };

  const handleWheel = (event: React.WheelEvent<HTMLDivElement>) => {
    event.preventDefault();
    adjustZoom(event.deltaY > 0 ? -0.08 : 0.08);
  };

  return (
    <div
      ref={viewportRef}
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onWheel={handleWheel}
      onMouseDown={focusViewport}
      className="rounded-lg border border-slate-700 bg-slate-950/50 p-3 outline-none focus:ring-2 focus:ring-blue-400/40"
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => adjustZoom(0.12)}
            className="rounded-md border border-slate-600 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
          >
            Zoom In
          </button>
          <button
            type="button"
            onClick={() => adjustZoom(-0.12)}
            className="rounded-md border border-slate-600 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
          >
            Zoom Out
          </button>
          <button
            type="button"
            onClick={resetView}
            className="rounded-md border border-slate-600 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
          >
            Reset
          </button>
          <button
            type="button"
            onClick={() => shiftPan(0, 32)}
            className="rounded-md border border-slate-600 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
          >
            Move Up
          </button>
          <button
            type="button"
            onClick={() => shiftPan(0, -32)}
            className="rounded-md border border-slate-600 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
          >
            Move Down
          </button>
          <button
            type="button"
            onClick={() => shiftPan(32, 0)}
            className="rounded-md border border-slate-600 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
          >
            Move Left
          </button>
          <button
            type="button"
            onClick={() => shiftPan(-32, 0)}
            className="rounded-md border border-slate-600 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
          >
            Move Right
          </button>
        </div>
        <p className="text-xs text-slate-400">
          Click the graph, then use arrow keys or WASD to move, +/- to zoom, and 0 to reset.
        </p>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-[760px] block select-none">
        <defs>
          <marker
            id="graph-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
          <radialGradient id="graph-vignette" cx="50%" cy="45%" r="70%">
            <stop offset="0%" stopColor="#0b1533" />
            <stop offset="100%" stopColor="#030818" />
          </radialGradient>
          <pattern id="graph-grid" width="24" height="24" patternUnits="userSpaceOnUse">
            <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#1e293b" strokeWidth="1" />
          </pattern>
          <filter id="node-glow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="2.4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g transform={`translate(${pan.x} ${pan.y}) scale(${zoom})`}>
          <rect x="0" y="0" width={width} height={height} fill="url(#graph-vignette)" />
          <rect x="0" y="0" width={width} height={height} fill="url(#graph-grid)" fillOpacity="0.42" />

          {positionedEdges.map((edge, index) => (
            <g key={`${edge.source}-${edge.target}-${index}`}>
              <path
                d={edge.path}
                stroke={edge.stroke}
                strokeWidth={edge.strokeWidth}
                strokeOpacity={edge.strokeOpacity}
                fill="none"
                markerEnd="url(#graph-arrow)"
              />
              {edge.relation && visibleRelationLabels.has(edge.labelKey) && (
                <g>
                  <rect
                    x={edge.labelX - (edge.relation.length * 6 + 10) / 2}
                    y={edge.labelY - 9}
                    rx="4"
                    ry="4"
                    width={edge.relation.length * 6 + 10}
                    height="14"
                    fill="#0f172a"
                    fillOpacity="0.9"
                    stroke="#334155"
                  />
                  <text
                    x={edge.labelX}
                    y={edge.labelY + 2}
                    fill="#cbd5e1"
                    fontSize="10"
                    textAnchor="middle"
                  >
                    {edge.relation.length > 24 ? `${edge.relation.slice(0, 24)}...` : edge.relation}
                  </text>
                </g>
              )}
            </g>
          ))}

          {positionedNodes.map((node) => {
            const isSelected = selectedNode?.id === node.id;

            return (
            <g
              key={node.id}
              style={{ cursor: 'pointer' }}
              onClick={() => setSelectedNodeId(node.id)}
            >
              <circle
                cx={node.sx + node.sr * 0.22}
                cy={node.sy + node.sr * 0.28}
                r={node.sr}
                fill="#020617"
                fillOpacity={isSelected ? 0.76 : 0.5}
              />
              <circle
                cx={node.sx}
                cy={node.sy}
                r={node.sr * 1.06}
                fill={node.color}
                fillOpacity={isSelected ? 0.34 : 0.22}
                filter="url(#node-glow)"
              />
              <circle
                cx={node.sx}
                cy={node.sy}
                r={node.radius}
                fill={node.color}
                fillOpacity={isSelected ? 1 : 0.95}
                stroke={isSelected ? '#ffffff' : '#e2e8f0'}
                strokeOpacity={isSelected ? 0.82 : 0.3}
                strokeWidth={isSelected ? 2 : 1}
                filter="url(#node-glow)"
              />
              <circle
                cx={node.sx - node.sr * 0.28}
                cy={node.sy - node.sr * 0.24}
                r={Math.max(2, node.sr * 0.28)}
                fill="#ffffff"
                fillOpacity="0.45"
              />
              {node.level ? (
                <text
                  x={node.sx}
                  y={node.sy - node.sr - 10}
                  fill="#cbd5e1"
                  fontSize="9"
                  textAnchor="middle"
                  letterSpacing="0.08em"
                >
                  {(node.level || node.type || 'Entity').toUpperCase()}
                </text>
              ) : null}
              <text
                x={node.sx}
                y={node.sy + node.sr + 14}
                fill="#e2e8f0"
                fontSize="11"
                textAnchor="middle"
              >
                {node.id.length > 20 ? `${node.id.slice(0, 20)}...` : node.id}
              </text>
            </g>
            );
          })}
        </g>
      </svg>

      <div className="mt-3 grid gap-3 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="flex flex-wrap gap-3 px-1">
          {typeLegend.map((type) => (
            <div key={type} className="flex items-center gap-2 text-xs text-slate-300">
              <span
                className="inline-block h-3 w-3 rounded-full"
                style={{ backgroundColor: nodeTypeColor(type) }}
              />
              <span>{type}</span>
            </div>
          ))}
        </div>

        <div className="rounded-lg border border-slate-700 bg-slate-900/70 p-4 text-sm text-slate-200">
          {selectedNode ? (
            <>
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Selected Node</p>
                  <h4 className="text-base font-semibold text-white">{selectedNode.id}</h4>
                </div>
                <span
                  className="rounded-full px-2 py-1 text-[11px] font-semibold uppercase tracking-wide text-slate-900"
                  style={{ backgroundColor: selectedNode.color }}
                >
                  {(selectedNode.level || selectedNode.type || 'Entity').toString()}
                </span>
              </div>
              <div className="mt-3 space-y-2 text-slate-300">
                <div>Confidence: {selectedNode.confidence != null ? `${Math.round(selectedNode.confidence * 100)}%` : 'N/A'}</div>
                <div>Importance: {selectedNode.importance != null ? selectedNode.importance.toFixed(2) : 'N/A'}</div>
                <div>Mentions: {selectedNode.mentions ?? 0}</div>
                <div>Aliases: {selectedNode.aliases?.length ? selectedNode.aliases.join(', ') : 'None'}</div>
                <div>Source sentence: {selectedNode.source_sentence || 'Not provided'}</div>
              </div>
            </>
          ) : (
            <p className="text-slate-400">Click a node to inspect its metadata and supporting sentence.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function nodeTypeColor(type?: string): string {
  const normalized = (type || 'entity').toLowerCase();

  if (normalized.includes('person')) return '#22c55e';
  if (normalized.includes('org') || normalized.includes('company')) return '#38bdf8';
  if (normalized.includes('country') || normalized.includes('city') || normalized.includes('location')) return '#f59e0b';
  if (normalized.includes('concept') || normalized.includes('technology')) return '#a78bfa';
  return '#0ea5e9';
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

type PositionedNode = GraphNode & {
  x: number;
  y: number;
  z: number;
  sx: number;
  sy: number;
  sr: number;
  radius: number;
  color: string;
  degree: number;
};

type PositionedEdge = GraphEdge & {
  sourceNode: PositionedNode;
  targetNode: PositionedNode;
  path: string;
  labelX: number;
  labelY: number;
  labelKey: string;
  stroke: string;
  strokeWidth: number;
  strokeOpacity: number;
};

function buildKnowledgeGraphLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  width: number,
  height: number
): { nodes: PositionedNode[]; edges: PositionedEdge[] } {
  const centerX = width / 2;
  const centerY = height / 2;
  const boundedNodes = nodes.slice(0, 48);
  const validNodeIds = new Set(boundedNodes.map((node) => node.id));
  const boundedEdges = edges
    .filter((edge) => validNodeIds.has(edge.sourceId) && validNodeIds.has(edge.targetId))
    .slice(0, 120);

  const degreeMap = new Map<string, number>();
  boundedNodes.forEach((node) => degreeMap.set(node.id, 0));
  boundedEdges.forEach((edge) => {
    degreeMap.set(edge.sourceId, (degreeMap.get(edge.sourceId) || 0) + 1);
    degreeMap.set(edge.targetId, (degreeMap.get(edge.targetId) || 0) + 1);
  });

  const connectedNodes = boundedNodes.filter((node) => (degreeMap.get(node.id) || 0) > 0 || boundedEdges.length === 0);

  const levelOrder = ['main topic', 'subtopic', 'entity', 'supporting detail'];
  const tierGroups = new Map<number, GraphNode[]>();
  connectedNodes
    .slice()
    .sort((left, right) => {
      const leftLevel = (left.level || left.type || 'entity').toLowerCase();
      const rightLevel = (right.level || right.type || 'entity').toLowerCase();
      const leftTier = Math.max(0, levelOrder.indexOf(leftLevel));
      const rightTier = Math.max(0, levelOrder.indexOf(rightLevel));
      if (leftTier !== rightTier) {
        return leftTier - rightTier;
      }
      const leftImportance = Number(left.importance || 0);
      const rightImportance = Number(right.importance || 0);
      if (rightImportance !== leftImportance) {
        return rightImportance - leftImportance;
      }
      return (degreeMap.get(right.id) || 0) - (degreeMap.get(left.id) || 0);
    })
    .forEach((node) => {
      const level = (node.level || node.type || 'entity').toLowerCase();
      const tier = Math.max(0, levelOrder.indexOf(level));
      const current = tierGroups.get(tier) || [];
      current.push(node);
      tierGroups.set(tier, current);
    });

  const tierRadii = [0, 180, 320, 470];
  const tierOffsets = [22, 18, 12, 8];
  const positionedNodes: PositionedNode[] = [];

  tierGroups.forEach((group, tier) => {
    const count = group.length;
    const radius = tierRadii[tier] || 320 + tier * 70;
    const angleStep = count > 0 ? (Math.PI * 2) / count : 0;
    const offset = tierOffsets[tier] || 10;

    group.forEach((node, index) => {
      const degree = degreeMap.get(node.id) || 0;
      const importance = Number(node.importance || 0);
      const angle = count <= 1 ? 0 : index * angleStep;
      const jitter = ((index % 3) - 1) * offset;
      const ringRadius = Math.max(0, radius + jitter - Math.min(48, importance * 18));
      const x = tier === 0 ? centerX : centerX + ringRadius * Math.cos(angle);
      const y = tier === 0 ? centerY : centerY + ringRadius * Math.sin(angle);

      positionedNodes.push({
        ...node,
        x,
        y,
        z: ((index % 7) - 3) * 10 + Math.max(0, 3 - tier) * 10,
        degree,
        radius: Math.min(22, 10 + degree * 1.2 + importance * 5),
        color: nodeTypeColor(node.type),
        sx: 0,
        sy: 0,
        sr: 0,
      });
    });
  });

  positionedNodes.sort((left, right) => {
    const leftLevel = (left.level || left.type || 'entity').toLowerCase();
    const rightLevel = (right.level || right.type || 'entity').toLowerCase();
    const leftTier = Math.max(0, levelOrder.indexOf(leftLevel));
    const rightTier = Math.max(0, levelOrder.indexOf(rightLevel));
    if (leftTier !== rightTier) {
      return leftTier - rightTier;
    }
    return (right.importance || 0) - (left.importance || 0);
  });

  const byId = new Map(positionedNodes.map((node) => [node.id, node]));

  for (let iteration = 0; iteration < 220; iteration++) {
    for (let i = 0; i < positionedNodes.length; i++) {
      for (let j = i + 1; j < positionedNodes.length; j++) {
        const a = positionedNodes[i];
        const b = positionedNodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const distSq = dx * dx + dy * dy + 0.01;
        const force = 2200 / distSq;
        const fx = (dx / Math.sqrt(distSq)) * force;
        const fy = (dy / Math.sqrt(distSq)) * force;
        a.x += fx;
        a.y += fy;
        b.x -= fx;
        b.y -= fy;
      }
    }

    boundedEdges.forEach((edge) => {
      const source = byId.get(edge.sourceId);
      const target = byId.get(edge.targetId);
      if (!source || !target) {
        return;
      }

      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const distance = Math.sqrt(dx * dx + dy * dy) || 1;
      const desired = Math.min(480, 180 + Math.max(0, positionedNodes.length - 8) * 10);
      const pull = (distance - desired) * 0.014;
      const fx = (dx / distance) * pull;
      const fy = (dy / distance) * pull;
      source.x += fx;
      source.y += fy;
      target.x -= fx;
      target.y -= fy;
    });

    positionedNodes.forEach((node) => {
      const level = (node.level || node.type || 'entity').toLowerCase();
      const tier = Math.max(0, levelOrder.indexOf(level));
      const centerPull = tier === 0 ? 0.0038 : 0.0018;
      node.x += (centerX - node.x) * centerPull;
      node.y += (centerY - node.y) * centerPull;
      node.x = Math.max(58, Math.min(width - 58, node.x));
      node.y = Math.max(58, Math.min(height - 70, node.y));
    });
  }

  positionedNodes.forEach((node) => {
    const depth = node.z + Math.min(36, node.degree * 4);
    node.sx = node.x + depth * 0.45;
    node.sy = node.y - depth * 0.3;
    node.sr = Math.max(8, node.radius + depth * 0.05);
  });

  const pairCounter = new Map<string, number>();
  boundedEdges.forEach((edge) => {
    const key = `${edge.sourceId}|${edge.targetId}`;
    pairCounter.set(key, (pairCounter.get(key) || 0) + 1);
  });
  const pairOffsetCounter = new Map<string, number>();

  const positionedEdges: PositionedEdge[] = boundedEdges
    .map((edge) => {
      const sourceNode = byId.get(edge.sourceId);
      const targetNode = byId.get(edge.targetId);
      if (!sourceNode || !targetNode) {
        return null;
      }

      const key = `${edge.sourceId}|${edge.targetId}`;
      const total = pairCounter.get(key) || 1;
      const used = pairOffsetCounter.get(key) || 0;
      pairOffsetCounter.set(key, used + 1);

      const spread = 24;
      const curveOffset = total === 1 ? 0 : (used - (total - 1) / 2) * spread;

      const mx = (sourceNode.x + targetNode.x) / 2;
      const my = (sourceNode.y + targetNode.y) / 2;
      const dx = targetNode.sx - sourceNode.sx;
      const dy = targetNode.sy - sourceNode.sy;
      const length = Math.sqrt(dx * dx + dy * dy) || 1;
      const nx = -dy / length;
      const ny = dx / length;
      const cx = mx + nx * curveOffset;
      const cy = my + ny * curveOffset;

      const depthMix = (sourceNode.z + targetNode.z) / 2;
      const strokeOpacity = Math.max(0.42, Math.min(0.92, 0.62 + depthMix * 0.01));
      const strokeWidth = Math.max(1.2, Math.min(2.4, 1.3 + Math.abs(curveOffset) * 0.01));

      return {
        ...edge,
        sourceNode,
        targetNode,
        relation: edge.relation ? formatRelationLabel(edge.relation) : undefined,
        path: `M ${sourceNode.sx} ${sourceNode.sy} Q ${cx} ${cy} ${targetNode.sx} ${targetNode.sy}`,
        labelX: (sourceNode.sx + 2 * cx + targetNode.sx) / 4,
        labelY: (sourceNode.sy + 2 * cy + targetNode.sy) / 4,
        labelKey: `${edge.sourceId}->${edge.targetId}:${formatRelationLabel(edge.relation || '')}`,
        stroke: '#93a4bf',
        strokeWidth,
        strokeOpacity,
      };
    })
    .filter((edge): edge is PositionedEdge => Boolean(edge));

  positionedNodes.sort((a, b) => a.z - b.z);

  return {
    nodes: positionedNodes,
    edges: positionedEdges,
  };
}

function selectVisibleRelationLabels(edges: PositionedEdge[]): Set<string> {
  const selected = new Set<string>();
  const placed: Array<{ x: number; y: number }> = [];

  edges.forEach((edge) => {
    if (!edge.relation) {
      return;
    }

    const tooClose = placed.some((point) => {
      const dx = point.x - edge.labelX;
      const dy = point.y - edge.labelY;
      return dx * dx + dy * dy < 34 * 34;
    });

    if (!tooClose) {
      selected.add(edge.labelKey);
      placed.push({ x: edge.labelX, y: edge.labelY });
    }
  });

  return selected;
}

