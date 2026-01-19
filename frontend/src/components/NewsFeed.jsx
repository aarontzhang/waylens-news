import { useState, useEffect } from 'react';
import { fetchDigest, refreshDigest, fetchRefreshStatus } from '../api';

// Parse markdown-style bold (**text**) to JSX
function parseMarkdown(text) {
  if (!text) return null;
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

// Determine which step we're on based on status
function getProgressStep(progress) {
  if (!progress?.current) return { step: 1, label: 'Initializing', detail: '' };
  const { current, progress: prog, total } = progress;

  if (current.includes('Complete')) {
    return { step: 4, label: 'Complete', detail: 'Loading digest...' };
  }
  if (current.includes('Generating')) {
    return { step: 3, label: 'Generating Summary', detail: 'Writing your intelligence brief' };
  }
  if (current.includes('Scoring')) {
    return { step: 2, label: 'Analyzing Articles', detail: 'Evaluating significance' };
  }
  if (current.includes('Fetching')) {
    const company = current.replace('Fetching: ', '');
    return { step: 1, label: 'Collecting News', detail: company, prog, total };
  }
  return { step: 1, label: 'Initializing', detail: '' };
}

// Animated loading dots component
function LoadingDots() {
  return (
    <span className="inline-flex items-center gap-1 ml-2">
      <span className="loading-dot w-1.5 h-1.5 rounded-full" style={{ backgroundColor: 'rgba(255,255,255,0.9)' }}></span>
      <span className="loading-dot w-1.5 h-1.5 rounded-full" style={{ backgroundColor: 'rgba(255,255,255,0.9)' }}></span>
      <span className="loading-dot w-1.5 h-1.5 rounded-full" style={{ backgroundColor: 'rgba(255,255,255,0.9)' }}></span>
    </span>
  );
}

export default function NewsFeed() {
  const [digest, setDigest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshProgress, setRefreshProgress] = useState(null);
  const [sourcesExpanded, setSourcesExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (digest?.summary) {
      navigator.clipboard.writeText(digest.summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  useEffect(() => {
    loadDigest();
  }, []);

  useEffect(() => {
    let interval;
    if (refreshing) {
      interval = setInterval(async () => {
        const status = await fetchRefreshStatus();
        setRefreshProgress(status);
        if (!status.running) {
          setRefreshing(false);
          loadDigest();
        }
      }, 500);
    }
    return () => clearInterval(interval);
  }, [refreshing]);

  async function loadDigest() {
    setLoading(true);
    try {
      const data = await fetchDigest();
      setDigest(data);
    } catch (error) {
      console.error('Failed to load digest:', error);
    }
    setLoading(false);
  }

  async function handleRefresh() {
    if (refreshing) return;
    setRefreshing(true);
    setRefreshProgress({ current: 'Starting...', progress: 0, total: 0, running: true });
    try {
      await refreshDigest();
    } catch (error) {
      console.error('Failed to refresh digest:', error);
      setRefreshing(false);
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    // SQLite returns UTC timestamps without timezone indicator
    // Add 'Z' to ensure JavaScript parses it as UTC
    const utcDateStr = dateStr.includes('Z') ? dateStr : dateStr.replace(' ', 'T') + 'Z';
    const date = new Date(utcDateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-6 w-6 border-2 border-brand-orange border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div>
      {/* Digest Card */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {digest?.generated_at ? (
                <p className="text-sm text-gray-500">Last generated {formatDate(digest.generated_at)}</p>
              ) : (
                <p className="text-sm text-gray-500">No digest generated yet</p>
              )}
              {digest?.summary && (
                <button
                  onClick={handleCopy}
                  className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded"
                  title={copied ? 'Copied!' : 'Copy summary'}
                >
                  {copied ? (
                    <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  )}
                </button>
              )}
            </div>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="px-4 py-2 rounded-md text-sm font-medium transition-colors"
              style={{
                backgroundColor: refreshing ? '#e5e7eb' : '#111827',
                color: refreshing ? '#9ca3af' : '#ffffff',
                cursor: refreshing ? 'not-allowed' : 'pointer',
              }}
              onMouseEnter={(e) => !refreshing && (e.target.style.backgroundColor = '#374151')}
              onMouseLeave={(e) => !refreshing && (e.target.style.backgroundColor = '#111827')}
            >
              {refreshing ? 'Generating...' : 'Generate Digest'}
            </button>
          </div>
        </div>

        {/* Progress indicator */}
        {refreshing && (
          <div className="px-6 py-5 bg-gray-50 border-b border-gray-200">
            {(() => {
              const { step, label, detail, prog, total } = getProgressStep(refreshProgress);
              const steps = [
                { num: 1, name: 'Collect' },
                { num: 2, name: 'Analyze' },
                { num: 3, name: 'Generate' },
              ];

              return (
                <div className="space-y-4">
                  {/* Step indicators */}
                  <div className="flex items-center gap-2">
                    {steps.map((s, i) => (
                      <div key={s.num} className="flex items-center">
                        <div
                          className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-colors"
                          style={{
                            backgroundColor: step > s.num ? 'rgba(240, 90, 40, 0.1)' : step === s.num ? '#F05A28' : '#f3f4f6',
                            color: step > s.num ? '#F05A28' : step === s.num ? '#ffffff' : '#9ca3af'
                          }}
                        >
                          {step > s.num ? (
                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <span>{s.num}</span>
                          )}
                          <span>{s.name}</span>
                          {step === s.num && <LoadingDots />}
                        </div>
                        {i < steps.length - 1 && (
                          <div
                            className="w-8 h-px mx-1"
                            style={{ backgroundColor: step > s.num ? 'rgba(240, 90, 40, 0.3)' : '#e5e7eb' }}
                          />
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Status detail */}
                  <div className="flex items-center justify-between">
                    <div>
                      {step === 1 && detail && (
                        <p className="text-sm text-gray-600">
                          {prog !== undefined && total > 0
                            ? `${detail} (${prog}/${total})`
                            : detail
                          }
                        </p>
                      )}
                      {step === 1 && prog !== undefined && total > 0 && (
                        <div className="mt-2 w-64 h-1 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-300"
                            style={{ width: `${(prog / total) * 100}%`, backgroundColor: '#F05A28' }}
                          />
                        </div>
                      )}
                      {(step === 2 || step === 3) && (
                        <p className="text-sm text-gray-600">{detail}</p>
                      )}
                    </div>
                    {(step === 2 || step === 3) && (
                      <span className="text-xs text-gray-400">Usually 30-60 seconds</span>
                    )}
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* Summary */}
        <div className="px-6 py-6">
          {!digest?.summary || digest.summary.includes('No digest available') ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No digest available yet.</p>
              <p className="text-gray-400 text-sm mt-1">Click "Generate Digest" to create your first report.</p>
            </div>
          ) : (
            <div className="space-y-5">
              {digest.summary.split('\n\n').map((paragraph, i) => (
                <div
                  key={i}
                  className="pl-4 border-l-2 border-gray-200 transition-colors"
                  style={{ borderColor: undefined }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = '#F05A28'}
                  onMouseLeave={(e) => e.currentTarget.style.borderColor = '#e5e7eb'}
                >
                  <p className="text-[15px] text-gray-700 leading-relaxed">
                    {parseMarkdown(paragraph)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sources */}
        {digest?.sources?.length > 0 && (
          <div className="border-t border-gray-200">
            <button
              onClick={() => setSourcesExpanded(!sourcesExpanded)}
              className="w-full px-6 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <span className="text-sm text-gray-500">
                {digest.sources.length} Sources
              </span>
              <svg
                className={`w-4 h-4 text-gray-400 transition-transform ${sourcesExpanded ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {sourcesExpanded && (
              <div className="px-6 pb-4 space-y-2">
                {digest.sources.map((article, i) => (
                  <a
                    key={article.id || i}
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block py-2 px-3 -mx-3 rounded hover:bg-gray-50 transition-colors group"
                  >
                    <div className="flex items-start gap-3">
                      <span className="flex-shrink-0 text-xs text-gray-400 mt-0.5 w-4">
                        {i + 1}.
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-700 group-hover:text-gray-900 transition-colors line-clamp-1">
                          {article.title}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-500">
                            {article.company_name}
                          </span>
                          {article.news_type && article.news_type !== 'UNKNOWN' && (
                            <span className="text-xs text-gray-400">
                              {article.news_type.replace('_', ' ')}
                            </span>
                          )}
                        </div>
                      </div>
                      <svg className="w-4 h-4 text-gray-300 flex-shrink-0 mt-0.5 transition-colors group-hover:text-[#F05A28]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </div>
                  </a>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
