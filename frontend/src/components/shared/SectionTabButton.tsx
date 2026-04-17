interface SectionTabButtonProps {
  active: boolean;
  onClick: () => void;
  label: string;
  variant?: 'dark' | 'light';
}

const VARIANT_CLASS: Record<NonNullable<SectionTabButtonProps['variant']>, string> = {
  dark: 'bg-slate-700/40 text-slate-300 border border-slate-600 hover:bg-slate-700/60',
  light: 'bg-gray-100 text-gray-700 hover:bg-gray-200',
};

const ACTIVE_CLASS: Record<NonNullable<SectionTabButtonProps['variant']>, string> = {
  dark: 'bg-blue-500/20 text-blue-300 border border-blue-500/40',
  light: 'bg-blue-600 text-white',
};

export default function SectionTabButton({ active, onClick, label, variant = 'dark' }: SectionTabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        active ? ACTIVE_CLASS[variant] : VARIANT_CLASS[variant]
      }`}
    >
      {label}
    </button>
  );
}
