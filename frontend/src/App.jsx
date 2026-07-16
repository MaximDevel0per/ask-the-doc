import { useEffect, useState } from "react";
import Chat from "./components/Chat.jsx";
import DocumentList from "./components/DocumentList.jsx";
import Upload from "./components/Upload.jsx";

export default function App() {
  const [documents, setDocuments] = useState([]);

  async function loadDocuments() {
    const res = await fetch("/api/documents");
    setDocuments(await res.json());
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <div className="app">
      <header>
        <h1>RAG Starter</h1>
        <p>Lade Dokumente hoch und stelle Fragen zu deren Inhalt.</p>
      </header>
      <div className="layout">
        <aside>
          <Upload onUploaded={loadDocuments} />
          <DocumentList documents={documents} onDeleted={loadDocuments} />
        </aside>
        <main>
          <Chat hasDocuments={documents.length > 0} />
        </main>
      </div>
    </div>
  );
}
