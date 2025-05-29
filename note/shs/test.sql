use haruharu;

CREATE TABLE shs_test (
    id INT PRIMARY KEY,
    category VARCHAR(20),         -- 축제, 공연, 관광지 등
    festival_name VARCHAR(255),
    festival_loc VARCHAR(255),
    start_date DATE,
    fin_date DATE,
    distance VARCHAR(20),
    region VARCHAR(50),
    source_api VARCHAR(100)
);
INSERT INTO shs_test (
    id, category, festival_name, festival_loc,
    start_date, fin_date, distance, region, source_api
) VALUES
(
    1, '축제', '서울 장미 축제', '서울 중랑구 중화체육공원',
    '2025-05-20', '2025-05-26', '3.2km', '서울', 'TourAPI 4.0'
),
(
    2, '축제', '부산 바다 축제', '부산 해운대 해수욕장',
    '2025-08-01', '2025-08-06', '7.8km', '부산', 'KOPIS 축제정보API'
),
(
    101, '공연', '뮤지컬 캣츠', '서울 예술의전당',
    '2025-06-10', '2025-06-25', '4.1km', '서울', 'KOPIS 공연API'
);
select *from shs_test;
