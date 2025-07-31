// frontend/app/signup/page.tsx
"use client";

import React, { useState } from "react";
import { post } from "@/lib/api";

export default function SignUpPage() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // FastAPI expects form-encoded for /auth/register
      const { access_token, detail } = await post(
        "/auth/register",
        { username: email, password },
        { form: true }
      );
      if (access_token) {
        alert("Account created! You can now log in.");
      } else {
        alert(detail || "Signup failed");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred during signup");
    }
  };

  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Sign Up</h1>
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
          Create Account
        </button>
      </form>
    </div>
  );
}
