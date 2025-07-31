// frontend/app/login/page.tsx
"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { post } from "@/lib/api";
// ← Corrected import path to your _context folder
import { useAuth } from "../_context/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // OAuth2 form flow: username & password
      const { access_token, detail } = await post(
        "/auth/login",
        { username: email, password },
        { form: true }
      );
      if (access_token) {
        login(access_token);
        router.push("/consult");
      } else {
        alert(detail || "Login failed");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred during login");
    }
  };

  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Log In</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block mb-1">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            className="w-full border rounded p-2"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password" className="block mb-1">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            className="w-full border rounded p-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white rounded p-2"
        >
          Log In
        </button>
      </form>
    </div>
  );
}
