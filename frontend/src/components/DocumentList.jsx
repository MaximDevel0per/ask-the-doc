export default function DocumentList({ documents, onDeleted }) {
  async function handleDelete(id) {
    await fetch(`/api/documents/${id}`, { method: "DELETE" });
    onDeleted();
  }

  return (
    <section className="documents">
      <h2>Dokumente ({documents.length})</h2>
      {documents.length === 0 && <p>Noch keine Dokumente.</p>}
      <ul>
        {documents.map((doc) => (
          <li key={doc.id}>
            <span title={`${doc.chunks} Chunks`}>{doc.filename}</span>
            <button onClick={() => handleDelete(doc.id)} title="Löschen">
              ×
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
