// frontend/app/admin/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { post } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";


type User = {
  id: number;
  email: string;
  is_active: boolean;
  is_admin: boolean;
};

export default function AdminPage() {
  const { token } = useAuth();
  const [pending, setPending] = useState<User[]>([]);

  useEffect(() => {
    if (!token) return;
    fetch("http://127.0.0.1:8000/admin/users/pending", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setPending(data));
  }, [token]);

  const approve = async (id: number) => {
    await post(`/admin/approve/${id}`, {}, { token });
    setPending((prev) => prev.filter((u) => u.id !== id));
  };

  if (!token) return <p>Please log in as an admin first.</p>;

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
      {pending.length === 0 ? (
        <p>No pending users to approve.</p>
      ) : (
        <ul className="space-y-2">
          {pending.map((user) => (
            <li key={user.id} className="flex justify-between">
              <span>{user.email}</span>
              <button
                className="bg-green-600 text-white px-2 rounded"
                onClick={() => approve(user.id)}
              >
                Approve
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
