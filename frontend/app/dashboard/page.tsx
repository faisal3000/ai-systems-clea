"use client";

import React, { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";

import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const { token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.push("/login");
    }
  }, [token, router]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Welcome to your Dashboard</h1>
      {/* Your dashboard content goes here */}
    </div>
  );
}
