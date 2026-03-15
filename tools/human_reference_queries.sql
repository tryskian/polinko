-- Human-reference quick queries (for DB viewer)

-- 1) Latest human docs by captured date / modified date
SELECT *
FROM v_human_reference_latest
LIMIT 100;

-- 2) Category totals
SELECT category, COUNT(*) AS total_docs
FROM documents
GROUP BY category
ORDER BY total_docs DESC, category ASC;

-- 3) Latest transcript captures
SELECT title, path, captured_on, modified_utc, word_count
FROM documents
WHERE category = 'transcripts'
ORDER BY COALESCE(captured_on, modified_utc) DESC
LIMIT 50;

-- 4) Latest key points
SELECT title, path, captured_on, modified_utc, word_count
FROM documents
WHERE category = 'key_points'
ORDER BY COALESCE(captured_on, modified_utc) DESC
LIMIT 50;

-- 5) Latest theory notes
SELECT title, path, captured_on, modified_utc, word_count
FROM documents
WHERE category = 'theory_notes'
ORDER BY COALESCE(captured_on, modified_utc) DESC
LIMIT 50;

-- 6) Cross-references (source -> target)
SELECT source_path, target_path, relation
FROM links
ORDER BY source_path, target_path;

