import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts';
import { Database, TrendingUp } from 'lucide-react';
import { ProcessingResult } from '../services/api';

interface DataAnalysisProps {
  result: ProcessingResult | null;
}

export default function DataAnalysis({ result }: DataAnalysisProps) {
  const analysis = useMemo(() => {
    if (!result) return null;

    const relevantCount = result.relevant_segments.length;
    const totalSegments = result.total_segments || 0;
    const irrelevantCount = Math.max(totalSegments - relevantCount, 0);

    const relevantPercentage =
      totalSegments > 0 ? (relevantCount / totalSegments) * 100 : 0;

    const avgConfidence =
      relevantCount > 0
        ? result.relevant_segments.reduce(
            (sum, segment) => sum + (segment.confidence || segment.relevance_score || 0),
            0
          ) / relevantCount
        : 0;

    return {
      totalSegments,
      relevantCount,
      irrelevantCount,
      relevantPercentage,
      avgConfidence
    };
  }, [result]);

  if (!result || !analysis) {
    return (
      <div className="bg-slate-800/40 border border-slate-700 rounded-xl p-8 text-center text-slate-400">
        Upload or process a URL to see live analysis
      </div>
    );
  }

  const pieData = [
    {
      name: 'Relevant',
      value: analysis.relevantCount,
      fill: '#22c55e'
    },
    {
      name: 'Irrelevant',
      value: analysis.irrelevantCount,
      fill: '#ef4444'
    }
  ];

  const confidenceData = result.relevant_segments.map((segment, index) => ({
    name: `Seg ${index + 1}`,
    confidence: Math.round(
      ((segment.confidence || segment.relevance_score || 0) * 100)
    )
  }));

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-600 to-blue-500 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2 text-blue-100">
            <Database className="w-5 h-5" />
            <span>Total Segments</span>
          </div>
          <p className="text-3xl font-bold text-white">
            {analysis.totalSegments}
          </p>
        </div>

        <div className="bg-gradient-to-br from-green-600 to-green-500 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2 text-green-100">
            <TrendingUp className="w-5 h-5" />
            <span>Relevant</span>
          </div>
          <p className="text-3xl font-bold text-white">
            {analysis.relevantCount}
          </p>
          <p className="text-sm text-green-100 mt-1">
            {analysis.relevantPercentage.toFixed(1)}%
          </p>
        </div>

        <div className="bg-slate-800/70 border border-slate-700 rounded-xl p-5">
          <p className="text-slate-400 text-sm mb-2">Irrelevant</p>
          <p className="text-3xl font-bold text-red-400">
            {analysis.irrelevantCount}
          </p>
        </div>

        <div className="bg-slate-800/70 border border-slate-700 rounded-xl p-5">
          <p className="text-slate-400 text-sm mb-2">Avg Confidence</p>
          <p className="text-3xl font-bold text-cyan-400">
            {(analysis.avgConfidence * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">
            Relevant vs Irrelevant
          </h3>

          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={90}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">
            Segment Confidence
          </h3>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={confidenceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="confidence" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.div>
  );
}