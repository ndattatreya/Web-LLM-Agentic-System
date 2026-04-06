import React from 'react';
import { motion } from 'framer-motion';

interface HeaderProps {
  apiHealth: boolean;
}

export default function Header({ apiHealth }: HeaderProps) {
  return (
    <header className="bg-gradient-to-r from-slate-900 to-slate-800 border-b border-slate-700 shadow-lg">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6"
      >
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Web-LLM Agentic System
            </h1>
            <p className="text-slate-400 mt-1">
              Advanced Document Processing & Analysis Platform
            </p>
          </div>
          
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              apiHealth
                ? 'bg-green-500/10 border border-green-500/30'
                : 'bg-red-500/10 border border-red-500/30'
            }`}
          >
            <div
              className={`w-3 h-3 rounded-full ${
                apiHealth ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}
            />
            <span className={apiHealth ? 'text-green-400' : 'text-red-400'}>
              {apiHealth ? 'API Connected' : 'API Offline'}
            </span>
          </motion.div>
        </div>
      </motion.div>
    </header>
  );
}
