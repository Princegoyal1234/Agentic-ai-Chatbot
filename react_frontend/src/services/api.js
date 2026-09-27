const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const USER_ID = "user1";
export const getThreads = async () => {
  const r = await fetch(`${API_URL}/threads/?user_id=${USER_ID}`);
  const d = await r.json();
  if(!d.success) throw new Error(d.error);
  return d.threads; // {threadId: title}
};

// Backend can send content as string OR array of blocks
// e.g. "hello" OR [{type:"text", text:"hello"}] (Gemini/LangChain content blocks)
// If we do `full += object` JS coerces to "[object Object]" — that's the bug.
export function extractText(content) {
  if (content == null) return "";
  if (typeof content === "string") return content;
  if (Array.isArray(content)) return content.map(extractText).join("");
  if (typeof content === "object") {
    if (typeof content.text === "string") return content.text;
    if (Array.isArray(content.text)) return content.text.map(extractText).join("");
    if (typeof content.content === "string") return content.content;
    return ""; // tool payloads / images etc. -> render nothing, not "[object Object]"
  }
  return String(content);
}

// Backend returns LangChain messages: [{content, type: "human"/"ai"/"tool", ...}]
// Normalize to [{id, role: "user"/"assistant", content}]
// Mirrors frontend/sidebar_module.py load_chat_history() + chat_module.py display_chat_history() filter
function normalizeHistory(history) {
  return (history || [])
    .map((msg, idx) => {
      const rawType = msg?.type ?? msg?.id?.at?.(-1) ?? "";
      const type = String(rawType).toLowerCase();
      // Skip tool messages and empty content (same as Streamlit filter)
      if (type.includes("tool")) return null;
      const content = extractText(msg?.content);
      if (!content.trim()) return null;
      const role = type.includes("human") ? "user" : "assistant";
      return { id: `${idx}-${Date.now()}`, role, content };
    })
    .filter(Boolean);
}

export const getHistory = async (threadId) => {
  const r = await fetch(`${API_URL}/threads/${threadId}?user_id=${USER_ID}`);
  const d = await r.json();
  if (!d.success) throw new Error(d.error || "Failed to load chat history");
  return normalizeHistory(d.history);
};

// Upload one PDF to existing backend POST /files/upload.
// Backend expects Form(thread_id, file) with content_type ==
// "application/pdf" and returns {success, filename, chunks}.
// Frontend never decides RAG — it only indexes, then chats;
// backend LLM decides whether pdf_rag tool is needed.
export const uploadPdf = async (threadId, file) => {
  if (!file) throw new Error("No file selected.");
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    throw new Error(`Only PDF files are allowed (got "${file.name}").`);
  }
  const MAX_MB = 20;
  if (file.size > MAX_MB * 1024 * 1024) {
    throw new Error(
      `"${file.name}" is ${(file.size / 1024 / 1024).toFixed(1)} MB — max is ${MAX_MB} MB.`
    );
  }

  const form = new FormData();
  form.append("thread_id", threadId);
  // Force application/pdf so backend content_type check passes
  const pdfBlob = new Blob([file], { type: "application/pdf" });
  form.append("file", pdfBlob, file.name);

  const r = await fetch(`${API_URL}/files/upload`, {
    method: "POST",
    body: form,
  });
  let d;
  try {
    d = await r.json();
  } catch {
    throw new Error(`Upload failed for "${file.name}": HTTP ${r.status}`);
  }
  // Backend success: {success:true,...}; backend 400: {error} (no success flag)
  if (!r.ok || d.success === false || d.error) {
    throw new Error(d.error || `Upload failed for "${file.name}".`);
  }
  return d;
};

// Streams POST /chat/ NDJSON (one JSON object per line).
// Mirrors frontend/chat_module.py get_chat_stream() + stream_response().
// Events: {mode:"messages", event:"token", content}
//         {mode:"messages", event:"tool_call", tool_calls/tool_call_chunks}
//         {mode:"updates", event:"graph_update", data}
//         {mode:"error", error}
export const streamChat = async (message, threadId, callbacks = {}) => {
  const { onToken, onTool } = callbacks;
  const res = await fetch(`${API_URL}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      thread_id: threadId,
      user_id: USER_ID,
    }),
  });
  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  let full = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const lines = buf.split("\n");
    buf = lines.pop(); // keep incomplete line

    for (const line of lines) {
      if (!line.trim()) continue;
      let evt;
      try {
        evt = JSON.parse(line);
      } catch {
        continue; // skip malformed chunk (same as Streamlit JSONDecodeError continue)
      }

      if (evt.mode === "error") {
        throw new Error(evt.error || "Streaming error");
      }

      if (evt.mode === "messages") {
        if (evt.event === "token") {
          const text = extractText(evt.content);
          if (!text) continue; // skip empty blocks
          full += text;
          onToken?.(full);
        } else if (evt.event === "tool_call") {
          const name =
            evt.tool_calls?.[0]?.name ||
            evt.tool_call_chunks?.[0]?.name ||
            "tool";
          onTool?.(name);
        }
      } else if (evt.mode === "updates" && evt.event === "graph_update") {
        // Tool finished -> clear indicator (Streamlit: st.status complete)
        if (evt.data?.tools) {
          onTool?.(null);
        }
      }
    }
  }

  onTool?.(null);
  return full;
};

