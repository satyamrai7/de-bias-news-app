import { useEffect, useState, useRef, useCallback } from "react";
import Navbar from "../components/Navbar";
import axios from "axios";
import placeholderImage from '../assets/placeholder.png';
import { BarChart3 } from "lucide-react";

function formatDate(utcString) {
  const date = new Date(utcString);
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

export default function News() {
  const [newscategory, setNewsCategory] = useState("world");
  const [newsArray, setNewsArray] = useState([]);
  const [cursor, setCursor] = useState("");
  const [hasMoreNews, setHasMoreNews] = useState(true);
  const [selectedNews, setSelectedNews] = useState(null); // for modal
  const [loading, setLoading] = useState(false);


  const observer = useRef();

  const lastNewsRef = useCallback(
    (node) => {
      if (!hasMoreNews || !node) return;
      if (observer.current) observer.current.disconnect();
      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
          LoadNewsFromCursor();
        }
      },
      {
        threshold: 1.0,
      });
      observer.current.observe(node);
    },
    [cursor, hasMoreNews]
  );

  useEffect(() => {
    const fetchNewsByCategory = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/news?category=${newscategory}`);
        const news_response = response.data.news;
        const curr = response.data.next_cursor;
        console.log(`cursor - ${curr}`)
        setCursor(curr);
        setHasMoreNews(!!curr);
        setNewsArray(news_response);
      } catch (error) {
        console.error("Error fetching categories:", error);
        setCursor(null);
        setHasMoreNews(false);
      }
    };
    fetchNewsByCategory();
  }, [newscategory]);

  async function LoadNewsFromCursor() {
    if (!cursor) {
      setHasMoreNews(false);
      return;
    }
    setLoading(true); // Show loader
    await new Promise((resolve) => setTimeout(resolve, 500)); // 0.5-second delay

    try {
        const response = await axios.get(`http://127.0.0.1:8000/news?category=${newscategory}&cursor=${cursor}`);
        const news_response = response.data.news;
        const newCursor = response.data.next_cursor;
        console.log(`newCursor - ${newCursor}`)
        setCursor(newCursor);
        setHasMoreNews(!!newCursor);
        setNewsArray((prev) => [...prev, ...news_response]);
    } catch (err) {
        console.error("Failed to load news:", err);
        setCursor(null);
        setHasMoreNews(false);
    } finally {
        setLoading(false); // Hide loader
    }
  }
  return (
    <div className="bg-gray-100 min-h-screen">
      <Navbar selected={newscategory} onSelect={setNewsCategory} />

      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6">
          {newsArray.map((news, index) => (
            <div
              key={news.news_id}
              ref={index === newsArray.length - 1 ? lastNewsRef : null}
              className="bg-white rounded-2xl shadow hover:shadow-lg transition-shadow overflow-hidden flex flex-col"
            >
              <img
                src={news.news_image_url || placeholderImage}
                alt={news.news_title}
                onError={(e) => { e.target.src = placeholderImage }}
                className="w-full h-48 object-cover"
              />
              <div className="p-4 flex flex-col flex-grow justify-between">
                <a
                  href={news.news_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block font-bold text-lg text-blue-700 hover:underline line-clamp-2"
                  style={{
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden"
                  }}
                >
                  {news.news_title}
                </a>

                <div className="mt-3 text-sm text-gray-600">
                  <p><strong>Author:</strong> {news.news_author || "Unknown"}</p>
                  <p><strong>Source:</strong> {news.website_name || "Unknown"}</p>
                  <p className="text-xs text-gray-500 mt-1">{formatDate(news.news_published)}</p>
                </div>

                <div className="mt-2 flex justify-end">
                  <button
                    className="text-gray-500 hover:text-indigo-600"
                    onClick={() => setSelectedNews(news)}
                    title="Analyze"
                  >
                    <BarChart3 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {hasMoreNews && (
        <div className="flex justify-center items-center mt-6 min-h-[100px]">
        {loading && (
            <svg className="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
        )}
        </div>
        )}

        {!hasMoreNews && (
          <div className="text-center mt-8 text-sm text-gray-500">
            You've reached the end! No more news available at the moment.
          </div>
        )}
      </div>

      {/* Modal */}
      {selectedNews && (
        <div className="fixed inset-0 bg-black bg-opacity-40 z-50 flex justify-center items-center">
          <div className="bg-white rounded-xl shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-3 right-4 text-gray-500 hover:text-black"
              onClick={() => setSelectedNews(null)}
            >
              ✕
            </button>
            <h2 className="text-xl font-bold mb-4">Article Analysis</h2>
            <p className="mb-3 text-sm text-gray-600"><strong>Summary:</strong> (Placeholder for summary API result)</p>
            <p className="mb-3 text-sm text-gray-600">
              <strong>Bias Tag:</strong>{" "}
              <span className="px-2 py-1 rounded-full bg-red-100 text-red-600 text-xs font-semibold">Very Left</span>
            </p>
            {/* Future: Add sentiment, credibility, etc */}
          </div>
        </div>
      )}
    </div>
  );
}
