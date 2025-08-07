"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function ConsultPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);

  useEffect(() => {
    if (!token) router.push("/login");
  }, [token, router]);

  if (!token) return null;

  const handleAsk = async () => {
    setAnswer(`You asked: "${question}"\n\n(Answer would appear here.)`);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Consult AI Agent</h1>
      <textarea
        className="w-full border rounded p-2 mb-4"
        placeholder="Type your question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button
        onClick={handleAsk}
        className="bg-blue-600 text-white px-4 py-2 rounded mb-6"
      >
        Ask
      </button>
      {answer && (
        <div className="bg-white p-4 border rounded whitespace-pre-wrap">
          {answer}
        </div>
      )}
    </div>
  );
}
