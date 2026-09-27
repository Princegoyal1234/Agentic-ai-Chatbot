import { extractText } from "../services/api";

function Message({ message }) {

  const isUser = message.role === "user";
  // Safety net: never render an object directly -> would show "[object Object]"
  const text =
    typeof message.content === "string"
      ? message.content
      : extractText(message.content);

  return (
    <div
      className={`
        flex
        ${isUser ? "justify-end" : "justify-start"}
        mb-4
      `}
    >

      <div
        className={`
          max-w-[75%]
          px-4
          py-3
          rounded-2xl
          text-sm
          leading-6
          whitespace-pre-wrap

          ${isUser
            ? "bg-black text-white rounded-br-md"
            : message.isError
              ? "bg-red-50 text-red-700 border border-red-200 rounded-bl-md"
              : "bg-gray-100 text-gray-900 rounded-bl-md"
          }
        `}
      >
        {text}
        {/* Streaming cursor */}
        {message.streaming && (
          <span className="inline-block w-2 h-4 ml-1 align-middle bg-gray-500 animate-pulse">▍</span>
        )}
      </div>

    </div>
  );
}

export default Message;