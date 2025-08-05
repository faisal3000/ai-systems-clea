// app/ClientLayout.tsx
"use client";

import React, { ReactNode } from "react";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import { AuthProvider } from "@/context/AuthContext";

export default function ClientLayout({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <aside className="w-64 bg-gray-100 border-r">
          <Sidebar />
        </aside>

        {/* Main content area */}
        <div className="flex flex-col flex-1 min-w-0">
          <Header />
          <main className="flex-1 p-6 bg-gray-50">{children}</main>
        </div>
      </div>
    </AuthProvider>
  );
}
