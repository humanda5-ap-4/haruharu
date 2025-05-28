<<<<<<< HEAD
// src/pages/SearchApp.tsx
// import React, { useState } from "react";
import { useState } from "react"; 
import axios from "axios";


const API_BASE_URL = "http://localhost:8000";


=======
import { useState } from 'react';
import axios from "axios";


>>>>>>> origin/v1_sjy
const SearchApp = () => {
  const [userInput, setUserInput] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const detectCategory = (input: string): string => {
    const categories = ["축제", "공연", "관광지", "음식", "스포츠", "주식"];
    return categories.find((cat) => input.includes(cat)) || "";
  };

  const handleSearch = async () => {
    const detectedCategory = detectCategory(userInput);
  
    let query = userInput
      .replace(/알려줘|찾아줘|검색해줘/g, "")
      .trim()
      .replace(detectedCategory, "")
      .trim();
  
    if (!detectedCategory) {
      setResult({
        error:
          "지원하지 않는 주제입니다. 축제, 공연, 관광지, 음식, 스포츠, 주식 중 하나를 포함해 입력해주세요.",
      });
      return;
    }
  
    if (!query) {
      setResult({
        error: "검색어가 비어 있습니다. 좀 더 구체적으로 입력해주세요.",
      });
      return;
    }
  
    setLoading(true);
  
    try {
      // 통합 호출: category와 query를 모두 넘김
      const res = await axios.get(`${API_BASE_URL}/api/search`, {
        params: { category: detectedCategory, query },
      });
  
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setResult({ error: "검색 중 오류가 발생했습니다." });
    } finally {
      setLoading(false);
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
        placeholder="예: 서울 장미 축제 알려줘, 삼성전자 주가 알려줘"
        className="w-full border p-2 mb-2 rounded"
      />
      <button
        onClick={handleSearch}
        className="bg-blue-500 text-white px-4 py-2 rounded"
        disabled={loading}

      >
        {loading ? "검색중..." : "검색"}
      </button>

      {result && (
  <div className="mt-4 bg-gray-100 p-4 rounded">
    {result.error ? (
      <p className="text-red-500">{result.error}</p>
    ) : result.stock_name ? (
      <>
        <p><strong>종목명:</strong> {result.stock_name}</p>
        <p><strong>현재가:</strong> {result.stock_price}원</p>
        <p><strong>등락률:</strong> {result.change}%</p>
        <p><strong>거래량:</strong> {result.volume}</p>
      </>
    ) : result.festival_name ? (
      <>
        <p><strong>축제명:</strong> {result.festival_name}</p>
        <p><strong>장소:</strong> {result.festival_loc}</p>
        <p><strong>기간:</strong> {result.start_date} ~ {result.fin_date}</p>
        <p><strong>거리:</strong> {result.distance}</p>
      </>
    ) : (
      <p>검색 결과가 없습니다.</p>
    )}
  </div>
)}

    </div>
  );
};

export default SearchApp;
