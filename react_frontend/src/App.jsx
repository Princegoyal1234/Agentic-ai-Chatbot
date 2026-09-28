import { useEffect, useState } from "react";

import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import { getThreads, getHistory, streamChat, uploadPdf } from "./services/api";

function App() {

  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [loadingThreads, setLoadingThreads] = useState(true);
  const [threadsError, setThreadsError] = useState(null);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [historyError, setHistoryError] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [toolStatus, setToolStatus] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  // =========================
  // LOAD HISTORY FOR ONE THREAD
  // =========================
  const loadHistory = async (threadId) => {
    try {
      console.log(threadId);
      setLoadingHistory(true);
      setHistoryError(null);
      const messages = await getHistory(threadId);
      setChats((current) =>
        current.map((c) =>
          c.id === threadId ? { ...c, messages, messagesLoaded: true } : c
        )
      );
    } catch (err) {
      setHistoryError(err.message);
    } finally {
      setLoadingHistory(false);
    }
  };

  // =========================
  // LOAD THREADS ON MOUNT
  // =========================
  useEffect(() => {
    const loadThreads = async () => {
      try {
        setLoadingThreads(true);
        setThreadsError(null);
        // Backend returns {threadId: title} dict
        const threadsDict = await getThreads();
        const threadsArray = Object.entries(threadsDict || {}).map(
          ([id, title]) => ({
            id,
            title,
            messages: [],
            messagesLoaded: false,
            uploadedFiles: [],
          })
        );
        setChats(threadsArray);
        if (threadsArray.length > 0) {
          setActiveChatId(threadsArray[0].id);
          // Auto-load history for first thread (Streamlit did this on select)
          loadHistory(threadsArray[0].id);
        }
      } catch (err) {
        setThreadsError(err.message);
      } finally {
        setLoadingThreads(false);
      }
    };

    loadThreads();
  }, []);


  // =========================
  // NEW CHAT
  // =========================

  const createNewChat = () => {

    const newChat = {
      id: crypto.randomUUID(),
      title: "New Chat",
      messages: [],
      messagesLoaded: true, // new thread, nothing to fetch
      uploadedFiles: [],
    };

    setChats((currentChats) => [
      newChat,
      ...currentChats,
    ]);

    setActiveChatId(newChat.id);
  };


  // =========================
  // SELECT CHAT (+ fetch history if needed)
  // Replaces sidebar_module.py load_chat_history()
  // =========================

  const selectChat = (chatId) => {
    setActiveChatId(chatId);
    setHistoryError(null);
    const target = chats.find((c) => c.id === chatId);
    if (target && !target.messagesLoaded) {
      loadHistory(chatId);
    }
  };


  // =========================
  // SEND MESSAGE
  // =========================
  const activeChat = chats.find(
    (chat) => chat.id === activeChatId
  );

  const deleteChat = (chatId) => {
    const remaining = chats.filter((chat) => chat.id !== chatId);
    setChats(remaining);
    // If deleting active chat, switch to first remaining and load its history
    if (chatId === activeChatId) {
      if (remaining.length > 0) {
        setActiveChatId(remaining[0].id);
        if (!remaining[0].messagesLoaded) {
          loadHistory(remaining[0].id);
        }
      } else {
        setActiveChatId(null);
      }
    }
  };

  // =========================
  // SEND MESSAGE (upload PDFs first, then stream chat)
  // Frontend never decides RAG — it only calls POST /files/upload
  // so backend FAISS index exists, then POST /chat/;
  // backend LLM decides whether pdf_rag tool is needed.
  // Replaces chat_module.py render_chat() + sidebar_module.py handle_pdf_upload()
  // =========================
  const sendMessage = async (content, files = []) => {
    const text = (content || "").trim();
    if ((!text && files.length === 0) || !activeChatId || isStreaming || uploading) return;

    const threadId = activeChatId;
    setUploadError(null);

    // 1. Upload PDFs sequentially (backend appends to same FAISS index)
    if (files.length > 0) {
      setUploading(true);
      for (const file of files) {
        const statusId = `s-${Date.now()}-${file.name}`;
        setChats((current) =>
          current.map((chat) =>
            chat.id !== threadId
              ? chat
              : {
                ...chat,
                messages: [
                  ...chat.messages,
                  {
                    id: statusId,
                    role: "assistant",
                    content: `📄 Indexing "${file.name}"...`,
                    streaming: true,
                  },
                ],
              }
          )
        );
        try {
          const result = await uploadPdf(threadId, file);
          const shownName = result.filename || file.name;
          const chunks = result.chunks ?? "?";
          setChats((current) =>
            current.map((chat) => {
              if (chat.id !== threadId) return chat;
              const merged = Array.from(
                new Set([...(chat.uploadedFiles || []), shownName])
              );
              return {
                ...chat,
                uploadedFiles: merged,
                messages: chat.messages.map((m) =>
                  m.id === statusId
                    ? {
                      ...m,
                      content: `✅ "${shownName}" indexed (${chunks} chunks). You can now ask questions about it.`,
                      streaming: false,
                    }
                    : m
                ),
              };
            })
          );
        } catch (err) {
          setUploadError(err.message);
          setChats((current) =>
            current.map((chat) =>
              chat.id !== threadId
                ? chat
                : {
                  ...chat,
                  messages: chat.messages.map((m) =>
                    m.id === statusId
                      ? { ...m, content: `❌ Upload failed for "${file.name}": ${err.message}`, streaming: false, isError: true }
                      : m
                  ),
                }
            )
          );
        }
      }
      setUploading(false);
      if (!text) return; // file-only send: don't call LLM
    }

    const userMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: text,
    };
    const assistantId = `a-${Date.now()}`;

    // 2. Optimistic update: add user msg + empty assistant placeholder, update title
    setChats((current) =>
      current.map((chat) => {
        if (chat.id !== threadId) return chat;
        const newTitle =
          chat.messages.length === 0 && chat.title === "New Chat"
            ? text.length > 30
              ? text.substring(0, 30) + "..."
              : text
            : chat.title;
        return {
          ...chat,
          title: newTitle,
          messages: [
            ...chat.messages,
            userMessage,
            { id: assistantId, role: "assistant", content: "", streaming: true },
          ],
        };
      })
    );

    const patchAssistant = (patch) => {
      setChats((current) =>
        current.map((chat) => {
          if (chat.id !== threadId) return chat;
          return {
            ...chat,
            messages: chat.messages.map((m) =>
              m.id === assistantId ? { ...m, ...patch } : m
            ),
          };
        })
      );
    };

    // 3. Stream tokens from backend
    try {
      setIsStreaming(true);
      setToolStatus(null);
      const full = await streamChat(text, threadId, {
        onToken: (text) => patchAssistant({ content: text, streaming: true }),
        onTool: (name) => setToolStatus(name), // null = completed
      });
      patchAssistant({ content: full || "No response.", streaming: false });
    } catch (err) {
      patchAssistant({
        content: `Error: ${err.message}`,
        streaming: false,
        isError: true,
      });
    } finally {
      setIsStreaming(false);
      setToolStatus(null);
    }
  };


  return (

    <div className="flex h-screen bg-white">

      {/* Sidebar */}

      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        loading={loadingThreads}
        error={threadsError}
        onNewChat={createNewChat}
        onSelectChat={selectChat}
        onDeleteChat={deleteChat}
      />
      {activeChat ? <ChatWindow
        messages={activeChat?.messages || []}
        loadingHistory={loadingHistory}
        historyError={historyError}
        isStreaming={isStreaming}
        toolStatus={toolStatus}
        uploadedFiles={activeChat?.uploadedFiles || []}
        uploading={uploading}
        uploadError={uploadError}
        onSendMessage={sendMessage}
      /> :
        (

          <div className="flex-1 flex items-center justify-center">

            <div className="text-center">

              <h2 className="text-2xl font-semibold">
                No chat selected
              </h2>

              <p className="text-gray-500 mt-2">
                Create a new chat to get started.
              </p>

            </div>
          </div>)
      }
    </div>
  );
}

export default App;
