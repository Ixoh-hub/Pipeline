-- Q1: Top Inventors
SELECT i.name, COUNT(DISTINCT r.patent_id) AS patents
FROM inventors AS i
JOIN relationships AS r ON i.inventor_id = r.inventor_id
GROUP BY i.name
ORDER BY patents DESC, i.name
LIMIT 10;

-- Q2: Top Companies
SELECT c.name, COUNT(DISTINCT r.patent_id) AS patents
FROM companies AS c
JOIN relationships AS r ON c.company_id = r.company_id
GROUP BY c.name
ORDER BY patents DESC, c.name
LIMIT 10;

-- Q3: Countries
SELECT i.country AS country, COUNT(DISTINCT r.patent_id) AS patents
FROM inventors AS i
JOIN relationships AS r ON i.inventor_id = r.inventor_id
GROUP BY i.country
ORDER BY patents DESC, i.country;

-- Q4: Trends Over Time
SELECT year, COUNT(*) AS patents
FROM patents
GROUP BY year
ORDER BY year;

-- Q5: JOIN Query
SELECT p.patent_id,
       p.title,
       i.name AS inventor_name,
       c.name AS company_name,
       p.year
FROM patents AS p
JOIN relationships AS r ON p.patent_id = r.patent_id
JOIN inventors AS i ON i.inventor_id = r.inventor_id
JOIN companies AS c ON c.company_id = r.company_id
ORDER BY p.year, p.patent_id
LIMIT 50;

-- Q6: CTE Query (WITH statement)
WITH inventor_counts AS (
    SELECT i.name,
           COUNT(DISTINCT r.patent_id) AS patents
    FROM inventors AS i
    JOIN relationships AS r ON i.inventor_id = r.inventor_id
    GROUP BY i.name
)
SELECT name, patents
FROM inventor_counts
WHERE patents >= 1
ORDER BY patents DESC, name;

-- Q7: Ranking Query
WITH inventor_counts AS (
    SELECT i.name,
           COUNT(DISTINCT r.patent_id) AS patents
    FROM inventors AS i
    JOIN relationships AS r ON i.inventor_id = r.inventor_id
    GROUP BY i.name
)
SELECT name,
       patents,
       RANK() OVER (ORDER BY patents DESC) AS rank
FROM inventor_counts
ORDER BY rank, name;
