// frontend/app/deep-dive/page.tsx
"use client";

import React, { useEffect } from "react";
import { useAuth } from "@/_context/AuthContext";
import { useRouter } from "next/navigation";

export default function DeepDivePage() {
  const { token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!token) router.push("/login");
  }, [token, router]);

  if (!token) return null;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Deep Dive</h1>
      <p>
        Explore detailed logs, analysis graphs, and system internals here.
      </p>
      {/* TODO: integrate charts, logs viewer, model inspection UI */}
    </div>
  );
}
