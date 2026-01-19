import NewsFeed from './components/NewsFeed';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="px-6 py-4 flex items-center gap-4">
          <img src="/logo.png" alt="Waylens" className="h-8" />
          <span className="text-gray-900 font-medium">Weekly Intelligence Digest</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        <NewsFeed />
      </main>
    </div>
  );
}

export default App;
