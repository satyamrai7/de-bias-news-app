import { useNavigate } from "react-router-dom";
import {Symbol} from "../components/Logo"; // adjust the path as needed

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-200 to-pink-200 text-center px-4">
      
      {/* Logo + Heading Together */}
      <div className="flex items-center justify-center gap-3 mb-6">
        <Symbol className="w-12 h-12 text-blue-700" />
        <h1 className="text-5xl font-bold text-blue-700">De-Bias</h1>
      </div>

      {/* Subtext */}
      <p className="text-lg text-gray-700 mb-8 max-w-xl">
        Get unbiased news from all sides. Compare perspectives. <br/> Break out of your bubble.
        <br/> Powered by FastAPI + React!
      </p>

      {/* Button */}
      <button
        onClick={() => navigate("/news")}
        className="px-6 py-3 bg-indigo-600 text-white rounded-full shadow-lg hover:bg-indigo-700 transition"
      >
        Enter News Portal
      </button>
    </div>
  );
}
