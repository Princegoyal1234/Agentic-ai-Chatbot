function Sidebar({ chats, activeChatId, loading, error, onNewChat, onSelectChat, onDeleteChat }) {
  return (
    <aside className="w-64 h-screen bg-gray-50 border-r border-gray-200 flex flex-col p-4">

      {/* Header */}
      <div className="mb-5">
        <h2 className="text-xl font-semibold">
          RAG Chat
        </h2>
      </div>

      {/* New Chat */}
      <button
        className="
          w-full
          px-4 py-3
          rounded-lg
          border border-gray-300
          bg-white
          hover:bg-gray-100
          transition
          text-sm
          font-medium
        "
        onClick={onNewChat}
      >
        + New Chat
      </button>

      {/* Chat History */}
      <div className="mt-8">

        <p className="text-xs text-gray-500 mb-2">
          CHATS
        </p>

        <div className="space-y-1">
          {loading && (
            <p className="text-sm text-gray-500 px-3 py-2">Loading chats...</p>
          )}

          {!loading && error && (
            <p className="text-sm text-red-500 px-3 py-2">Failed: {error}</p>
          )}

          {!loading && !error && chats.length === 0 && (
            <p className="text-sm text-gray-500 px-3 py-2">
              No chats yet. Click New Chat.
            </p>
          )}

          {!loading &&
            !error &&
            chats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                className={`
                px-3
                py-2
                rounded-lg
                cursor-pointer
                text-sm
                transition

                ${activeChatId === chat.id
                    ? "bg-gray-200 font-medium"
                    : "hover:bg-gray-200"
                  }
              `}
              >
                {chat.title}
                {/* Delete */}

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  className="
                                ml-2
                                px-2
                                text-gray-400
                                hover:text-red-500
                                hover:bg-gray-300
                                rounded
                                transition
                              "
                >
                  🗑️
                </button>
              </div>
            ))}
        </div>

      </div>
      <div className="border-t border-gray-200 p-4">

        <p className="text-xs text-gray-500">
          RAG Assistant
        </p>

      </div>

    </aside>
  );
}

export default Sidebar;