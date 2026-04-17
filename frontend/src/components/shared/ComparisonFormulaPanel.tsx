import { COMPARISON_FORMULA_TEXT, COMPARISON_METRIC_GUIDE } from '../../constants/comparison';

interface ComparisonFormulaPanelProps {
  className?: string;
}

export default function ComparisonFormulaPanel({ className }: ComparisonFormulaPanelProps) {
  return (
    <div className={className || 'mt-4 rounded-lg border border-slate-700 bg-slate-900/40 p-4 text-sm text-slate-300'}>
      <p className="font-medium text-slate-200 mb-2">Scoring formula</p>
      <p className="font-mono text-xs mb-3">{COMPARISON_FORMULA_TEXT}</p>
      <p className="mb-2 text-slate-400">Metric guide</p>
      <ul className="space-y-1 text-slate-300">
        {COMPARISON_METRIC_GUIDE.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
    </div>
  );
}
