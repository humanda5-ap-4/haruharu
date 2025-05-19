import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatBotPage from "./pages/ChatBotPage";
import QuotePage from './pages/QuotePage';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ChatBotPage />} />
        <Route path="/QuotePage" element={<QuotePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

// import ChatBotPage from "./pages/ChatBotPage";

// function App() {
//   return (
//     <div>
//       <ChatBotPage />
//     </div>
//   );
// }

// export default App;


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



