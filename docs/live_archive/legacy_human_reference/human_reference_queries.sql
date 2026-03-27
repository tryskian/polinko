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

-- 7) Relationship map with human-readable titles
SELECT
  s.title AS source_title,
  s.path AS source_path,
  t.title AS target_title,
  t.path AS target_path,
  l.relation
FROM links l
JOIN documents s ON s.path = l.source_path
JOIN documents t ON t.path = l.target_path
ORDER BY source_path, target_path;

-- 8) Foreign key config (for ER viewer/debug)
PRAGMA foreign_key_list('links');
