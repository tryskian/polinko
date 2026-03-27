# Runtime DB Visuals

Generated ER-style visuals for runtime SQLite stores (history, vector, memory).

- generated_utc: 2026-03-27T19:53:51Z

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

## History DB (.local/runtime_dbs/active/history.db)

- status: missing

## Vector DB (.local/runtime_dbs/active/vector.db)

- status: missing

## Memory DB (.local/runtime_dbs/active/memory.db)

- status: missing
