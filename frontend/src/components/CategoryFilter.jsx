export default function CategoryFilter({ categories, selected, onSelect }) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-sm text-gray-500">Filter:</span>
      <button
        onClick={() => onSelect(null)}
        className={`px-3 py-1 rounded-full text-sm ${
          selected === null
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        All
      </button>
      {categories.map((category) => (
        <button
          key={category}
          onClick={() => onSelect(category)}
          className={`px-3 py-1 rounded-full text-sm ${
            selected === category
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {category}
        </button>
      ))}
    </div>
  );
}
