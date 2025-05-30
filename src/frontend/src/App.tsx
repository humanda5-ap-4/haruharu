import { BrowserRouter, Routes, Route } from 'react-router-dom';
import WelcomePage from './pages/WelcomePage';
import ChatBotPage from "./pages/ChatBotPage";
import TopicSelectPage from "./pages/TopicSelectPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/chat" element={<ChatBotPage />} />
        <Route path="/topic-select" element={<TopicSelectPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;


// 예시 파일
// import SearchApp from "./SearchApp";

// function App() {
//   return (
//     <div className="App">
//       <SearchApp />
//     </div>
//   );
// }

// export default App;



