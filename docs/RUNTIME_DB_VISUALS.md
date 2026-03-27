# Runtime DB Visuals

Generated ER-style visuals for runtime SQLite stores (history, vector, memory).

- generated_utc: 2026-03-27T17:49:38Z

## Runtime Data Flow (Cross-DB)

Logical relationships across runtime stores. These are application-level links, not SQLite foreign keys.

```mermaid
flowchart LR
  subgraph H["History DB"]
    H1["chats (0)"]
    H2["chat_messages (0)"]
    H3["eval_checkpoints (0)"]
    H1 --> H2
    H1 --> H3
  end

  subgraph V["Vector DB"]
    V1["message_vectors (0)"]
  end

  subgraph M["Memory DB"]
    M1["agent_sessions (0)"]
    M2["agent_messages (0)"]
    M1 --> M2
  end

  H2 -->|"message_id/session_id"| V1
  H1 -->|"session_id"| M1
```

## History DB (.polinko_history.db)

- status: present
- tables: 9

```mermaid
erDiagram
  chat_collaboration_state {
    string session_id PK
    string active_agent_id
    string active_role
    string objective
    int updated_at
    string updated_by
  }
  chat_handoffs {
    int id PK
    string session_id
    string from_agent_id
    string from_role
    string to_agent_id
    string to_role
    string objective
    string reason
    int created_at
    string created_by
  }
  chat_messages {
    int id PK
    string session_id
    string role
    string content
    int created_at
    string message_id
    string parent_message_id
  }
  chat_personalization {
    string session_id PK
    string memory_scope
    int updated_at
    string updated_by
  }
  chats {
    string session_id PK
    string title
    int created_at
    int updated_at
    string status
    int deprecated_at
  }
  eval_checkpoints {
    int id PK
    string checkpoint_id
    string session_id
    int total_count
    int pass_count
    int fail_count
    int other_count
    int created_at
  }
  ingest_dedup {
    int id PK
    string dedup_key
    string operation
    string session_id
    string response_json
    int created_at
  }
  message_feedback {
    int id PK
    string session_id
    string message_id
    string outcome
    string tags_json
    string note
    string recommended_action
    string action_taken
    string status
    int created_at
    int updated_at
  }
  ocr_runs {
    int id PK
    string run_id
    string session_id
    string source_name
    string mime_type
    string source_message_id
    string result_message_id
    string status
    string extracted_text
    int created_at
  }
  chats ||--o{ chat_collaboration_state : "session_id->session_id"
  chats ||--o{ chat_handoffs : "session_id->session_id"
  chats ||--o{ chat_messages : "session_id->session_id"
  chats ||--o{ chat_personalization : "session_id->session_id"
  chats ||--o{ eval_checkpoints : "session_id->session_id"
  chats ||--o{ ingest_dedup : "session_id->session_id"
  chats ||--o{ message_feedback : "session_id->session_id"
  chats ||--o{ ocr_runs : "session_id->session_id"
```

### Row Counts

- `chat_collaboration_state`: 0
- `chat_handoffs`: 0
- `chat_messages`: 0
- `chat_personalization`: 0
- `chats`: 0
- `eval_checkpoints`: 0
- `ingest_dedup`: 0
- `message_feedback`: 0
- `ocr_runs`: 0

## Vector DB (.polinko_vector.db)

- status: present
- tables: 1

```mermaid
erDiagram
  message_vectors {
    int id PK
    string vector_id
    string session_id
    string role
    string message_id
    string source_type
    string source_ref
    string metadata_json
    string content
    string embedding_json
    int created_at
    int active
  }
```

### Row Counts

- `message_vectors`: 0

## Memory DB (.polinko_memory.db)

- status: present
- tables: 2

```mermaid
erDiagram
  agent_messages {
    int id PK
    string session_id
    string message_data
    string created_at
  }
  agent_sessions {
    string session_id PK
    string created_at
    string updated_at
  }
  agent_sessions ||--o{ agent_messages : "session_id->session_id"
```

### Row Counts

- `agent_messages`: 0
- `agent_sessions`: 0
