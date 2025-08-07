"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function KnowledgeBasePage() {
  const { token } = useAuth();
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<string[]>([]);

  useEffect(() => {
    if (!token) router.push("/login");
  }, [token, router]);

  if (!token) return null;

  const handleSearch = () => {
    setResults([
      `Result 1 for "${query}"`,
      `Result 2 for "${query}"`,
      `Result 3 for "${query}"`,
    ]);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Knowledge Base</h1>
      <div className="flex mb-4">
        <input
          type="text"
          className="flex-grow border rounded p-2 mr-2"
          placeholder="Search the KB..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          onClick={handleSearch}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Search
        </button>
      </div>
      <ul className="space-y-2">
        {results.map((r, i) => (
          <li key={i} className="bg-white p-3 border rounded">
            {r}
          </li>
        ))}
      </ul>
    </div>
  );
}
