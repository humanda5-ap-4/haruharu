import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatBotPage from "./pages/ChatBotPage";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ChatBotPage />} />
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



