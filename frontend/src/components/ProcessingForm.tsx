import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Link as LinkIcon, Loader } from 'lucide-react';
import { apiService } from '../services/api';

interface ProcessingFormProps {
  onSuccess: (result: any) => void;
  onError: (error: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export default function ProcessingForm({
  onSuccess,
  onError,
  isLoading,
  setIsLoading
}: ProcessingFormProps) {
  const [url, setUrl] = useState('');
  const [processingMode, setProcessingMode] = useState<'url' | 'file'>('url');
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleProcessURL = async () => {
  if (!url.trim()) return;

  try {
    setIsLoading(true);

    const response = await apiService.processURL(url);

    console.log("API Response:", response);

    // Normalize backend response so ResultsView always receives
    // result.relevant_segments correctly
    const normalizedResult = {
      source: response.source || url,
      source_type: response.source_type || "url",
      raw_text: response.raw_text || "",
      total_segments:
        response.total_segments ||
        response.segments?.length ||
        0,

      relevant_segments:
        response.relevant_segments ||
        response.results?.relevant_segments ||
        response.filtered_segments ||
        response.segments?.filter(
          (segment: any) =>
            segment.is_relevant ||
            (segment.relevance_score ?? 0) >= 0.25 ||
            (segment.confidence ?? 0) >= 0.25
        ) ||
        [],

      entities: response.entities || [],
      key_points: response.key_points || [],
      processing_time: response.processing_time || 0,
    };

    console.log(
      "Normalized relevant segments:",
      normalizedResult.relevant_segments
    );

    onSuccess(normalizedResult);
  } catch (error) {
    console.error("Error processing URL:", error);
    onError(error instanceof Error ? error.message : 'Error processing URL');
  } finally {
    setIsLoading(false);
  }
};

  const handleProcessFile = async (file: File) => {
    if (!file) return;

    setIsLoading(true);
    try {
      const result = await apiService.processFile(file);
      onSuccess(result);
      setSelectedFile(null);
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Error processing file');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      setSelectedFile(files[0]);
      setProcessingMode('file');
    }
  };

  return (
    <div className="space-y-8">
      {/* Mode Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid md:grid-cols-2 gap-4"
      >
        <ModeCard
          icon={<LinkIcon className="w-8 h-8" />}
          title="Process URL"
          description="Analyze content from a web URL"
          active={processingMode === 'url'}
          onClick={() => setProcessingMode('url')}
        />
        <ModeCard
          icon={<Upload className="w-8 h-8" />}
          title="Upload File"
          description="Process PDF, Audio, or Document Files"
          active={processingMode === 'file'}
          onClick={() => setProcessingMode('file')}
        />
      </motion.div>

      {/* Processing Area */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-8"
      >
        {processingMode === 'url' ? (
          <form onSubmit={handleProcessURL} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Enter URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 disabled:from-slate-600 disabled:to-slate-600 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : (
                'Process URL'
              )}
            </button>
          </form>
        ) : (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-all ${
              dragActive
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-slate-600 hover:border-slate-500'
            }`}
          >
            {selectedFile ? (
              <div className="space-y-4">
                <div className="text-green-400">✓ File selected</div>
                <p className="text-slate-300">{selectedFile.name}</p>
                <button
                  type="button"
                  onClick={() => handleProcessFile(selectedFile)}
                  disabled={isLoading}
                  className="mx-auto block py-2 px-6 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 disabled:from-slate-600 disabled:to-slate-600 text-white font-medium rounded-lg transition-all flex items-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    'Process File'
                  )}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="w-12 h-12 mx-auto text-slate-400" />
                <div>
                  <p className="text-slate-300 font-medium">
                    Drag & drop your file here
                  </p>
                  <p className="text-slate-500 text-sm mt-1">
                    or click to browse
                  </p>
                </div>
                <input
                  type="file"
                  onChange={(e) => {
                    if (e.target.files?.[0]) {
                      setSelectedFile(e.target.files[0]);
                    }
                  }}
                  accept=".pdf,.mp3,.wav,.m4a,.txt,.html"
                  className="hidden"
                  id="file-input"
                  disabled={isLoading}
                />
                <label htmlFor="file-input" className="cursor-pointer">
                  <span className="text-blue-400 hover:text-blue-300">
                    Select file
                  </span>
                </label>
              </div>
            )}
          </div>
        )}
      </motion.div>

      {/* Info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-slate-800/30 border border-slate-700 rounded-lg p-4 text-sm text-slate-400"
      >
        <p className="font-medium text-slate-300 mb-2">Supported Formats:</p>
        <ul className="space-y-1 ml-4">
          <li>• Web URLs (HTTP/HTTPS)</li>
          <li>• PDF Documents</li>
          <li>• Audio Files (MP3, WAV, M4A)</li>
          <li>• Text Documents (TXT, HTML)</li>
        </ul>
      </motion.div>
    </div>
  );
}

interface ModeCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  active: boolean;
  onClick: () => void;
}

function ModeCard({ icon, title, description, active, onClick }: ModeCardProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`p-6 rounded-xl border-2 transition-all text-left ${
        active
          ? 'bg-blue-500/10 border-blue-500'
          : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
      }`}
    >
      <div className={active ? 'text-blue-400' : 'text-slate-400'}>
        {icon}
      </div>
      <h3 className="font-semibold text-white mt-3">{title}</h3>
      <p className="text-slate-400 text-sm mt-1">{description}</p>
    </motion.button>
  );
}
