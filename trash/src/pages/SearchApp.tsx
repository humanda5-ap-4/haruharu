// src/frontend/src/pages/SearchApp.tsx

import React, { useState } from "react";
import axios from "axios";

const SearchApp = () => {
  const [userInput, setUserInput] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleSearch = async () => {
    // 임시 NLP 파싱 (정해진 category: 축제)
    const category = "축제";
    const query = userInput.replace(/알려줘|찾아줘|검색해줘/g, "").trim();

    try {
      const response = await axios.get(`http://localhost:8000/api/search`, {
        params: { category, query },
      });
      setResult(response.data);
    } catch (error) {
      console.error(error);
      setResult({ error: "검색 중 오류 발생" });
    }
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">축제 정보 검색</h1>
      <input
        type="text"
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        placeholder="예: 서울 장미 축제 알려줘"
        className="w-full border p-2 mb-2 rounded"
      />
      <button
        onClick={handleSearch}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        검색
      </button>

      {result && (
        <div className="mt-4 border p-4 rounded bg-gray-100">
          {result.error ? (
            <p className="text-red-500">{result.error}</p>
          ) : (
            <>
              <p>
                <strong>축제명:</strong> {result.festival_name}
              </p>
              <p>
                <strong>장소:</strong> {result.festival_loc}
              </p>
              <p>
                <strong>기간:</strong> {result.start_date} ~ {result.fin_date}
              </p>
              <p>
                <strong>거리:</strong> {result.distance}
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchApp;
