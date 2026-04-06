import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Clock, Zap } from 'lucide-react';
import { ProcessingResult } from '../services/api';

interface ResultsViewProps {
  result: ProcessingResult | null;
}

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

  const relevancePercentage = useMemo(() => {
    if (result.total_segments === 0) return 0;
    return (result.relevant_segments.length / result.total_segments) * 100;
  }, [result]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Summary Cards */}
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

      {/* Segments Section */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
      >
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span>🔍</span> Relevant Segments ({result.relevant_segments.length})
        </h2>
        
        <div className="space-y-4 max-h-[600px] overflow-y-auto">
          {result.relevant_segments.length > 0 ? (
            result.relevant_segments.map((segment, idx) => (
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

      {/* Raw Text Preview */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
      >
        <h3 className="text-lg font-bold text-white mb-4">📄 Raw Text (Preview)</h3>
        <div className="p-4 bg-slate-900/50 rounded-lg font-mono text-sm text-slate-300 max-h-[300px] overflow-y-auto">
          {result.raw_text}
        </div>
      </motion.div>
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
