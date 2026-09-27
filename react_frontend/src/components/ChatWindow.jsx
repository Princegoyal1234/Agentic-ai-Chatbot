import { useEffect, useRef } from "react";
import Message from "./Message";
import ChatInput from "./ChatInput";

function ChatWindow({
  messages,
  loadingHistory,
  historyError,
  isStreaming,
  toolStatus,
  uploadedFiles = [],
  uploading = false,
  uploadError = null,
  onSendMessage,
}) {
  const bottomRef = useRef(null);

  // Auto-scroll on new tokens (replaces Streamlit's auto-rerender)
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, toolStatus]);

  return (
    <main className="flex-1 flex flex-col">

      {/* Header */}

      <div
        className="
          h-14
          border-b
          border-gray-200
          flex
          items-center
          px-6
        "
      >

        <h1 className="font-semibold">
          RAG Assistant
        </h1>

      </div>


      {/* Indexed-files banner: files already POSTed to /files/upload
          for this thread, so backend pdf_rag can retrieve them.
          Frontend only displays; backend LLM decides tool use. */}
      {(uploading || uploadedFiles.length > 0 || uploadError) && (
        <div className="max-w-3xl mx-auto w-full mb-3">
          {uploadedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-2">
              {uploadedFiles.map((name) => (
                <span
                  key={name}
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 border border-gray-200 rounded-lg text-gray-700"
                >
                  📄 {name}
                </span>
              ))}
            </div>
          )}
          {uploading && (
            <p className="text-xs text-amber-700 animate-pulse">
              📄 Indexing PDF(s)...
            </p>
          )}
          {uploadError && (
            <p className="text-xs text-red-600">Upload error: {uploadError}</p>
          )}
        </div>
      )}

      {/* Messages */}

      <div className="flex-1 overflow-y-auto px-6 py-6">

        <div className="max-w-3xl mx-auto">

          {loadingHistory ? (
            <div className="h-full flex items-center justify-center">
              <p className="text-gray-500 text-sm">Loading chat history...</p>
            </div>
          ) : historyError ? (
            <div className="h-full flex items-center justify-center">
              <p className="text-red-500 text-sm">Failed to load history: {historyError}</p>
            </div>
          ) : messages.length === 0 ? (

            <div className="h-full flex items-center justify-center">

              <div className="text-center">

                <h2 className="text-3xl font-semibold mb-2">
                  RAG Assistant
                </h2>

                <p className="text-gray-500">
                  Ask questions about your documents
                </p>

              </div>

            </div>

          ) : (

            <>
              {messages.map((message) => (
                <Message key={message.id} message={message} />
              ))}

              {/* Tool indicator (replaces st.status in chat_module.py) */}
              {toolStatus && (
                <div className="flex justify-start mb-4">
                  <div className="max-w-[75%] px-4 py-2 rounded-2xl rounded-bl-md bg-amber-50 border border-amber-200 text-amber-800 text-sm animate-pulse">
                    🔧 Calling `{toolStatus}`...
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </>

          )}

        </div>

      </div>


      {/* Input */}

      <ChatInput onSend={onSendMessage} disabled={isStreaming || uploading || loadingHistory} />

    </main>
  );
}

export default ChatWindow;