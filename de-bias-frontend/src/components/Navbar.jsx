import { useEffect, useState } from "react";
import Logo from "./Logo";
import axios from "axios";

export default function Navbar({ selected, onSelect }) {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/news/categories");
        setCategories(response.data.categories); // assuming { categories: [...] }
      } catch (error) {
        console.error("Error fetching categories:", error);
      }
    };
    fetchCategories();
  }, []);

  return (
    <nav className="bg-white shadow px-4 py-3 sticky top-0 z-50">
      <div className="max-w-screen-xl mx-auto flex justify-between items-center">
        {/* Left: Logo */}
        <Logo />

        {/* Center: Categories */}
        <div className="flex gap-4 overflow-x-auto justify-center flex-1 mx-4">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => onSelect(cat.toLowerCase())}
              className={`text-sm px-3 py-1 rounded-full whitespace-nowrap ${
                selected === cat.toLowerCase()
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Right: User Icon */}
        <div className="cursor-pointer">
          <svg
            className="w-8 h-8 text-gray-500"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.5 20.25a8.25 8.25 0 1115 0H4.5z"
            />
          </svg>
        </div>
      </div>
    </nav>
  );
}
