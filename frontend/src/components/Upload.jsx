import { useRef, useState } from "react";

// Fehlerantworten sind nicht immer JSON: unbehandelte Server-Fehler
// liefern "Internal Server Error" als reinen Text.
async function readError(res) {
  const body = await res.text();
  try {
    return JSON.parse(body).detail || body;
  } catch {
    return body || `Upload fehlgeschlagen (HTTP ${res.status})`;
  }
}

export default function Upload({ onUploaded }) {
  const inputRef = useRef();
  const [status, setStatus] = useState("");

  async function handleUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setStatus("Wird verarbeitet…");
    try {
      const res = await fetch("/api/documents", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        throw new Error(await readError(res));
      }
      const result = await res.json();
      setStatus(`✓ ${result.filename} (${result.chunks} Chunks)`);
      onUploaded();
    } catch (e) {
      setStatus(`Fehler: ${e.message}`);
    } finally {
      inputRef.current.value = "";
    }
  }

  return (
    <section className="upload">
      <h2>Dokument hochladen</h2>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt,.md"
        onChange={handleUpload}
      />
      {status && <p className="status">{status}</p>}
    </section>
  );
}
