export default function ArticleCard({ article, showCompany = true }) {
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {showCompany && article.company_name && (
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                {article.company_name}
              </span>
              {article.company_category && (
                <span className="text-xs text-gray-400">
                  {article.company_category}
                </span>
              )}
            </div>
          )}
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-900 font-medium hover:text-blue-600 line-clamp-2"
          >
            {article.title}
          </a>
          {article.summary && (
            <p className="mt-2 text-sm text-gray-600 line-clamp-3">
              {article.summary}
            </p>
          )}
          {article.relevance_reason && !article.summary && (
            <p className="mt-2 text-sm text-gray-500 italic">
              {article.relevance_reason}
            </p>
          )}
          <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
            {article.source && <span>{article.source}</span>}
            {article.published_at && <span>{formatDate(article.published_at)}</span>}
          </div>
        </div>
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 p-2 text-gray-400 hover:text-blue-600"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
            />
          </svg>
        </a>
      </div>
    </div>
  );
}
