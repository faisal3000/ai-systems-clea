// components/Header.tsx
"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function Header() {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const user = {
    name: "Faisal Khan",
    email: "f.khann@gmail.com",
    avatarUrl:
      "https://ui-avatars.com/api/?name=Faisal+Khan&background=0D8ABC&color=fff",
  };

  return (
    <header className="h-16 bg-white border-b px-6 flex items-center justify-between shadow-sm">
      <h1 className="text-lg font-semibold text-gray-800">
        AI Systems Engineering Agent
      </h1>
      <div className="flex items-center gap-4">
        {isAuthenticated ? (
          <>
            <div className="text-right hidden sm:block">
              <div className="font-medium text-sm text-gray-800">{user.name}</div>
              <div className="text-xs text-gray-500">{user.email}</div>
            </div>
            <img
              src={user.avatarUrl}
              alt="User Avatar"
              className="w-10 h-10 rounded-full border object-cover"
            />
            <button
              onClick={logout}
              className="text-sm text-gray-600 hover:text-red-600 transition"
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => router.push("/login")}
              className="text-sm text-blue-600 hover:underline"
            >
              Sign In
            </button>
            <button
              onClick={() => router.push("/auth")}
              className="text-sm text-white bg-blue-600 px-3 py-1 rounded hover:bg-blue-700"
            >
              Sign Up
            </button>
          </>
        )}
      </div>
    </header>
  );
}
