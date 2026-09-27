import { useState } from "react";
import { Send, X, FileText } from "lucide-react";
import FileUpload from "./FileUpload";

function ChatInput({ onSend, disabled }) {

  const [message, setMessage] = useState("");

  const [selectedFiles, setSelectedFiles] = useState([]);


  // =========================
  // FILE SELECTED
  // =========================

  const handleFilesSelected = (files) => {

    setSelectedFiles((currentFiles) => [
      ...currentFiles,
      ...files,
    ]);

  };


  // =========================
  // REMOVE FILE
  // =========================

  const removeFile = (index) => {

    setSelectedFiles((currentFiles) =>
      currentFiles.filter(
        (_, fileIndex) => fileIndex !== index
      )
    );

  };


  // =========================
  // SEND MESSAGE
  // =========================

  const handleSubmit = (e) => {

    e.preventDefault();

    if (
      !message.trim() &&
      selectedFiles.length === 0
    ) {
      return;
    }

    onSend(
      message,
      selectedFiles
    );

    setMessage("");
    setSelectedFiles([]);

  };


  return (

    <form
      onSubmit={handleSubmit}
      className="
        w-full
        max-w-3xl
        mx-auto
        px-4
        pb-5
      "
    >

      {/* Selected Files */}

      {selectedFiles.length > 0 && (

        <div className="mb-2 space-y-2">

          {selectedFiles.map((file, index) => (

            <div
              key={`${file.name}-${index}`}
              className="
                flex
                items-center
                justify-between
                px-3
                py-2
                bg-gray-50
                border
                border-gray-200
                rounded-lg
              "
            >

              <div className="flex items-center gap-2 min-w-0">
                <FileText
                  size={18}
                  className="text-gray-500 shrink-0"
                />

                <span className="text-sm truncate">
                  {file.name}
                </span>

              </div>


              <button
                type="button"
                onClick={() => removeFile(index)}
                className="
                  p-1
                  text-gray-400
                  hover:text-red-500
                  rounded
                "
              >
                <X size={16} />
              </button>

            </div>

          ))}

        </div>

      )}


      {/* Input Box */}

      <div
        className="
          flex
          items-center
          border
          border-gray-300
          rounded-xl
          p-1
          shadow-sm
          bg-white
        "
      >

        {/* File Upload */}

        <FileUpload
          onFilesSelected={handleFilesSelected}
        />


        {/* Text Input */}

        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={disabled ? "Waiting for response..." : "Ask anything..."}
          disabled={disabled}
          className="
            flex-1
            px-3
            py-3
            outline-none
            text-sm
          "
        />


        {/* Send */}

        <button
          type="submit"
          disabled={disabled}
          className="
            w-10
            h-10
            flex
            items-center
            justify-center
            rounded-lg
            bg-black
            text-white
            hover:bg-gray-800
            transition
            disabled:opacity-50
          "
        >
          <Send size={18} />
        </button>

      </div>

    </form>

  );
}

export default ChatInput;