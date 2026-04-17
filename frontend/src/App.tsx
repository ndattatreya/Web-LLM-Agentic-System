import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiService } from './services/api';
import Header from './components/Header';
import ProcessingForm from './components/ProcessingForm';
import ResultsView from './components/ResultsView';

type ActiveTab = 'processing' | 'results';

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('processing');
  const [processingResult, setProcessingResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiHealth, setApiHealth] = useState(false);

  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      await apiService.health();
      setApiHealth(true);
    } catch {
      setApiHealth(false);
    }
  };

  const handleProcessing = async (result: any) => {
    setProcessingResult(result);
    setActiveTab('results');
    setError(null);
  };

  const handleError = (errorMsg: string) => {
    setError(errorMsg);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Header apiHealth={apiHealth} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-100"
          >
            {error}
          </motion.div>
        )}

        {/* Navigation Tabs */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-8 flex gap-4 border-b border-slate-700"
        >
          <TabButton
            active={activeTab === 'processing'}
            onClick={() => setActiveTab('processing')}
            label="Process Document"
            icon="📄"
          />
          <TabButton
            active={activeTab === 'results'}
            onClick={() => setActiveTab('results')}
            label="View Results"
            icon="📊"
          />
        </motion.div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'processing' && (
            <ProcessingForm
              onSuccess={handleProcessing}
              onError={handleError}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          )}

          {activeTab === 'results' && (
            <ResultsView result={processingResult} />
          )}
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="mt-20 py-8 border-t border-slate-700 text-center text-slate-400">
        <p>Web-LLM Agentic System © 2026</p>
      </footer>
    </div>
  );
}

interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  label: string;
  icon: string;
}

function TabButton({ active, onClick, label, icon }: TabButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ y: -2 }}
      whileTap={{ y: 0 }}
      className={`px-6 py-3 font-medium text-sm transition-all flex items-center gap-2 ${
        active
          ? 'text-blue-400 border-b-2 border-blue-400'
          : 'text-slate-400 hover:text-slate-300'
      }`}
    >
      <span>{icon}</span>
      {label}
    </motion.button>
  );
}
