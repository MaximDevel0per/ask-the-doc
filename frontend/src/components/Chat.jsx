import { useState } from "react";

export default function Chat({ hasDocuments }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendQuestion(event) {
    event.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error("Anfrage fehlgeschlagen");
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.answer, sources: data.sources },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Fehler: ${e.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="chat">
      <div className="messages">
        {messages.length === 0 && (
          <p className="hint">
            {hasDocuments
              ? "Stelle eine Frage zu deinen Dokumenten."
              : "Lade zuerst ein Dokument hoch."}
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <p>{msg.text}</p>
            {msg.sources?.length > 0 && (
              <details>
                <summary>Quellen ({msg.sources.length})</summary>
                <ul>
                  {msg.sources.map((s, j) => (
                    <li key={j}>
                      {s.filename} – Abschnitt {s.chunk_index} (Ähnlichkeit:{" "}
                      {s.similarity})
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        ))}
        {loading && <div className="message assistant">Denke nach…</div>}
      </div>
      <form onSubmit={sendQuestion}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Deine Frage…"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Senden
        </button>
      </form>
    </section>
  );
}
