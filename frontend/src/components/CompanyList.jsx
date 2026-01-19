import { useState, useEffect } from 'react';
import ArticleCard from './ArticleCard';
import { fetchCompanies, searchCompanies, fetchCompanyNews, refreshCompany } from '../api';

export default function CompanyList({ category, searchQuery, onRefreshComplete }) {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedCompany, setExpandedCompany] = useState(null);
  const [companyNews, setCompanyNews] = useState({});
  const [refreshingCompany, setRefreshingCompany] = useState(null);

  useEffect(() => {
    loadCompanies();
  }, [category]);

  useEffect(() => {
    if (searchQuery && searchQuery.length >= 2) {
      searchForCompanies();
    } else if (!searchQuery) {
      loadCompanies();
    }
  }, [searchQuery]);

  async function loadCompanies() {
    setLoading(true);
    try {
      const data = await fetchCompanies(category);
      setCompanies(data);
    } catch (error) {
      console.error('Failed to load companies:', error);
    }
    setLoading(false);
  }

  async function searchForCompanies() {
    try {
      const data = await searchCompanies(searchQuery);
      setCompanies(data);
    } catch (error) {
      console.error('Search failed:', error);
    }
  }

  async function handleExpand(companyId) {
    if (expandedCompany === companyId) {
      setExpandedCompany(null);
      return;
    }
    setExpandedCompany(companyId);
    if (!companyNews[companyId]) {
      const data = await fetchCompanyNews(companyId, true);
      setCompanyNews((prev) => ({ ...prev, [companyId]: data.articles }));
    }
  }

  async function handleRefresh(e, companyId) {
    e.stopPropagation();
    setRefreshingCompany(companyId);
    try {
      await refreshCompany(companyId);
      const data = await fetchCompanyNews(companyId, true);
      setCompanyNews((prev) => ({ ...prev, [companyId]: data.articles }));
      onRefreshComplete?.();
    } catch (error) {
      console.error('Refresh failed:', error);
    }
    setRefreshingCompany(null);
  }

  // Group companies by category
  const groupedCompanies = companies.reduce((acc, company) => {
    const cat = company.category;
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(company);
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {Object.entries(groupedCompanies).map(([categoryName, categoryCompanies]) => (
        <div key={categoryName}>
          <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
            {categoryName}
            <span className="text-sm font-normal text-gray-400">
              ({categoryCompanies.length})
            </span>
          </h2>
          <div className="bg-white rounded-lg border border-gray-200 divide-y">
            {categoryCompanies.map((company) => (
              <div key={company.id}>
                <div
                  onClick={() => handleExpand(company.id)}
                  className="px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <svg
                      className={`w-4 h-4 text-gray-400 transition-transform ${
                        expandedCompany === company.id ? 'rotate-90' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                    <span className="font-medium text-gray-900">{company.name}</span>
                  </div>
                  <button
                    onClick={(e) => handleRefresh(e, company.id)}
                    disabled={refreshingCompany === company.id}
                    className={`px-3 py-1 rounded text-sm ${
                      refreshingCompany === company.id
                        ? 'bg-gray-100 text-gray-400'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {refreshingCompany === company.id ? (
                      <span className="flex items-center gap-1">
                        <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                            fill="none"
                          />
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                          />
                        </svg>
                        Refreshing...
                      </span>
                    ) : (
                      'Refresh'
                    )}
                  </button>
                </div>
                {expandedCompany === company.id && (
                  <div className="px-4 py-3 bg-gray-50 border-t">
                    {companyNews[company.id]?.length > 0 ? (
                      <div className="space-y-3">
                        {companyNews[company.id].map((article) => (
                          <ArticleCard
                            key={article.id}
                            article={article}
                            showCompany={false}
                          />
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 py-4 text-center">
                        No relevant news yet. Click "Refresh" to fetch news.
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
