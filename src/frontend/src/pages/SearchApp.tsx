// src/pages/SearchApp.tsx
// import React, { useState } from "react";
import { useState } from "react"; 
import axios from "axios";

const SearchApp = () => {
  const [userInput, setUserInput] = useState("");
  const [result, setResult] = useState<any>(null);

  const detectCategory = (input: string): string => {
    const categories = ["축제", "공연", "관광지", "음식", "스포츠"];
    return categories.find((cat) => input.includes(cat)) || "";
  };

  const handleSearch = async () => {
    const detectedCategory = detectCategory(userInput);
    const query = userInput
      .replace(/알려줘|찾아줘|검색해줘/g, "")
      .trim()
      .replace(detectedCategory, "")
      .trim();

    if (!detectedCategory) {
      setResult({
        error:
          "지원하지 않는 주제입니다. 축제, 공연, 관광지, 음식, 스포츠 중 하나를 말씀해주세요.",
      });
      return;
    }

    try {
      const res = await axios.get("http://127.0.0.1:8000/api/search", {
        params: { category: detectedCategory, query },
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setResult({ error: "검색 중 오류 발생" });
    }
  };

  // ✅ 이 return은 컴포넌트 함수 내부에 있어야 함
  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-xl font-bold mb-2">정보 검색</h1>
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
        <div className="mt-4 bg-gray-100 p-4 rounded">
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
