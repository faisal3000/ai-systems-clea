// components/Sidebar.tsx
"use client";

import React from "react";
import Link from "next/link";

export default function Sidebar() {
  return (
    <nav className="p-6 space-y-4 text-gray-800 text-sm">
      <h2 className="font-bold text-lg">Navigation</h2>
      <ul className="space-y-2">
        <li>
          <Link href="/dashboard" className="hover:text-blue-600">
            Dashboard
          </Link>
        </li>
        <li>
          <Link href="/consult" className="hover:text-blue-600">
            Consult
          </Link>
        </li>
        <li>
          <Link href="/deep-dive" className="hover:text-blue-600">
            Deep Dive
          </Link>
        </li>
        <li>
          <Link href="/knowledge-base" className="hover:text-blue-600">
            Knowledge Base
          </Link>
        </li>
      </ul>
    </nav>
  );
}
