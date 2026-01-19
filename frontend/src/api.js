// Use environment variable for API URL in production, proxy in development
const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function fetchCompanies(category = null) {
  const url = category
    ? `${API_BASE}/companies?category=${encodeURIComponent(category)}`
    : `${API_BASE}/companies`;
  const response = await fetch(url);
  const data = await response.json();
  return data.companies;
}

export async function searchCompanies(query) {
  const response = await fetch(`${API_BASE}/companies/search?q=${encodeURIComponent(query)}`);
  const data = await response.json();
  return data.companies;
}

export async function fetchCompanyNews(companyId, onlyRelevant = false) {
  const url = `${API_BASE}/companies/${companyId}/news?only_relevant=${onlyRelevant}`;
  const response = await fetch(url);
  return response.json();
}

export async function fetchNewsFeed(limit = 50, category = null) {
  let url = `${API_BASE}/news?limit=${limit}`;
  if (category) {
    url += `&category=${encodeURIComponent(category)}`;
  }
  const response = await fetch(url);
  const data = await response.json();
  return data.articles;
}

export async function fetchCategories() {
  const response = await fetch(`${API_BASE}/categories`);
  const data = await response.json();
  return data.categories;
}

export async function refreshCompany(companyId) {
  const response = await fetch(`${API_BASE}/refresh/${companyId}`, {
    method: 'POST',
  });
  return response.json();
}

export async function refreshAll() {
  const response = await fetch(`${API_BASE}/refresh-all`, {
    method: 'POST',
  });
  return response.json();
}

export async function fetchRefreshStatus() {
  const response = await fetch(`${API_BASE}/refresh-status`);
  return response.json();
}

export async function fetchStats() {
  const response = await fetch(`${API_BASE}/stats`);
  return response.json();
}

export async function fetchDigest() {
  const response = await fetch(`${API_BASE}/digest`);
  return response.json();
}

export async function refreshDigest() {
  const response = await fetch(`${API_BASE}/digest/refresh`, {
    method: 'POST',
  });
  return response.json();
}
