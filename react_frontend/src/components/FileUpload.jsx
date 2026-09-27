import { useRef } from "react";
import { Paperclip } from "lucide-react";

function FileUpload({ onFilesSelected }) {

  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {

    const files = Array.from(event.target.files);

    if (files.length === 0) {
      return;
    }

    onFilesSelected(files);

    // Allow selecting the same file again
    event.target.value = "";
  };

  const openFilePicker = () => {
    fileInputRef.current.click();
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        hidden
        multiple
        accept=".pdf,application/pdf"
        onChange={handleFileChange}
      />

      <button
        type="button"
        onClick={openFilePicker}
        className="
          w-10
          h-10
          flex
          items-center
          justify-center
          rounded-lg
          text-gray-500
          hover:bg-gray-100
          hover:text-gray-800
          transition
        "
      >
        <Paperclip size={20} />
      </button>
    </>
  );
}

export default FileUpload;