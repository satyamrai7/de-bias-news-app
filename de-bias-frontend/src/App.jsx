import { BrowserRouter, Routes, Route } from "react-router-dom"
import Landing from "./pages/Landing"
import News from "./pages/News";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element = {<Landing/>}></Route>
        <Route path="/news" element={<News />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App