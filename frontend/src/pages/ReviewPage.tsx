import React, { useState } from 'react';
import axios from 'axios';

interface ReviewResult {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  score: number;
  summary: string;
  issues: Array<{
    severity: 'info' | 'warning' | 'error' | 'critical';
    category: string;
    message: string;
    line: number;
    suggestion: string;
  }>;
  metrics: {
    complexity: number;
    maintainability: number;
    security_score: number;
    performance_score: number;
  };
  suggestions: string[];
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ReviewPage: React.FC = () => {
  const [code, setCode] = useState('def hello():\n    print("world")');
  const [language, setLanguage] = useState('python');
  const [filename, setFilename] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [error, setError] = useState<string>('');

  const handleReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_URL}/api/v1/reviews`, {
        code,
        language,
        filename: filename || undefined,
      });

      const reviewId = response.data.id;

      // Poll for results
      let attempts = 0;
      const maxAttempts = 30; // 30 seconds max

      const pollResults = async () => {
        while (attempts < maxAttempts) {
          try {
            const resultResponse = await axios.get(
              `${API_URL}/api/v1/reviews/${reviewId}`
            );
            const resultData = resultResponse.data;

            if (resultData.status === 'completed' || resultData.status === 'failed') {
              setResult(resultData);
              setLoading(false);
              return;
            }

            attempts++;
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
          } catch (pollError) {
            console.error('Polling error:', pollError);
            attempts++;
          }
        }

        setError('Review timeout - please try again');
        setLoading(false);
      };

      pollResults();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to review code');
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'error': return 'text-red-500 bg-red-50';
      case 'warning': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-blue-600 bg-blue-50';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">AI Code Reviewer</h1>
          <p className="text-slate-400">Intelligent code analysis powered by Claude AI</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <div className="bg-slate-800 rounded-lg shadow-xl p-6 border border-slate-700">
            <form onSubmit={handleReview} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Programming Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="java">Java</option>
                  <option value="go">Go</option>
                  <option value="rust">Rust</option>
                  <option value="cpp">C++</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Filename (optional)
                </label>
                <input
                  type="text"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  placeholder="e.g., main.py"
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Code
                </label>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full h-96 bg-slate-700 border border-slate-600 rounded-md px-4 py-2 text-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Paste your code here..."
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                {loading ? 'Analyzing...' : 'Review Code'}
              </button>

              {error && (
                <div className="bg-red-900 border border-red-700 rounded-md p-3 text-red-200 text-sm">
                  {error}
                </div>
              )}
            </form>
          </div>

          {/* Results Panel */}
          <div className="bg-slate-800 rounded-lg shadow-xl p-6 border border-slate-700">
            {!result ? (
              <div className="flex items-center justify-center h-full text-slate-400">
                <div className="text-center">
                  <p className="text-lg">Submit code for review</p>
                  <p className="text-sm mt-2">Results will appear here</p>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Score */}
                <div className="bg-slate-700 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300">Overall Score</span>
                    <span className={`text-3xl font-bold ${getScoreColor(result.score)}`}>
                      {result.score.toFixed(1)}/10
                    </span>
                  </div>
                </div>

                {/* Summary */}
                {result.summary && (
                  <div>
                    <h3 className="font-semibold text-slate-200 mb-2">Summary</h3>
                    <p className="text-slate-400 text-sm">{result.summary}</p>
                  </div>
                )}

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-700 rounded-lg p-3">
                    <p className="text-xs text-slate-400">Complexity</p>
                    <p className="text-lg font-semibold text-slate-200">
                      {result.metrics.complexity}/10
                    </p>
                  </div>
                  <div className="bg-slate-700 rounded-lg p-3">
                    <p className="text-xs text-slate-400">Maintainability</p>
                    <p className="text-lg font-semibold text-slate-200">
                      {result.metrics.maintainability.toFixed(1)}/10
                    </p>
                  </div>
                  <div className="bg-slate-700 rounded-lg p-3">
                    <p className="text-xs text-slate-400">Security</p>
                    <p className="text-lg font-semibold text-slate-200">
                      {result.metrics.security_score.toFixed(1)}/10
                    </p>
                  </div>
                  <div className="bg-slate-700 rounded-lg p-3">
                    <p className="text-xs text-slate-400">Performance</p>
                    <p className="text-lg font-semibold text-slate-200">
                      {result.metrics.performance_score.toFixed(1)}/10
                    </p>
                  </div>
                </div>

                {/* Issues */}
                {result.issues.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-slate-200 mb-2">Issues Found</h3>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {result.issues.map((issue, idx) => (
                        <div
                          key={idx}
                          className={`rounded-lg p-3 text-sm ${getSeverityColor(
                            issue.severity
                          )}`}
                        >
                          <div className="font-semibold">
                            {issue.category} - {issue.severity}
                          </div>
                          <div className="mt-1">{issue.message}</div>
                          {issue.suggestion && (
                            <div className="mt-2 text-xs opacity-75">
                              💡 {issue.suggestion}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggestions */}
                {result.suggestions.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-slate-200 mb-2">Suggestions</h3>
                    <ul className="space-y-1">
                      {result.suggestions.map((suggestion, idx) => (
                        <li key={idx} className="text-slate-400 text-sm flex items-start">
                          <span className="mr-2">→</span>
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReviewPage;
