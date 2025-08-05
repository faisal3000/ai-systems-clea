
"use client";

import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Rocket, Brain, Search, FileText } from "lucide-react";
import { motion } from "framer-motion";

/**
 * A polished landing / dashboard screen with Tailwind, shadcn/ui buttons,
 * subtle motion, and an info grid describing each section.
 */
export default function HomePage() {
  return (
    <div className="w-full max-w-5xl mx-auto px-4 md:px-8 py-10 space-y-16">
      {/* ── Hero ──────────────────────────────────────────────────── */}
      <section className="text-center space-y-6">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl md:text-6xl font-extrabold tracking-tight"
        >
          AI Systems Engineering Agent
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-2xl mx-auto text-lg md:text-xl text-gray-600"
        >
          Accelerate your engineering workflow with AI‑powered consulting, deep‑dive
          analyses, and an ever‑growing knowledge base.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex flex-col sm:flex-row justify-center gap-4"
        >
          <Link href="/consult">
            <Button size="lg" className="rounded-2xl px-8 text-base font-semibold">
              Get Started
            </Button>
          </Link>
          <Link href="/knowledge-base">
            <Button
              variant="outline"
              size="lg"
              className="rounded-2xl px-8 text-base"
            >
              Browse Knowledge Base
            </Button>
          </Link>
        </motion.div>
      </section>

      {/* ── Feature grid ───────────────────────────────────────────── */}
      <section className="grid gap-8 md:grid-cols-3">
        <FeatureCard
          icon={Rocket}
          title="Dashboard"
          description="Your personalized overview with project status, AI insights and quick actions all in one place."
          href="/dashboard"
        />
        <FeatureCard
          icon={Brain}
          title="Consult"
          description="Chat with an engineering‑focused AI assistant that understands your requirements and tech stack."
          href="/consult"
        />
        <FeatureCard
          icon={Search}
          title="Deep Dive"
          description="Generate architecture diagrams, risk analyses and optimisation plans in minutes—powered by GPT‑4o."
          href="/deep-dive"
        />
        <FeatureCard
          icon={FileText}
          title="Knowledge Base"
          description="Curated best practices, design docs and troubleshooting guides searchable in natural language."
          href="/knowledge-base"
        />
        <FeatureCard
          icon={Rocket}
          title="Admin"
          description="Approve new users, manage roles and monitor system metrics (Admins only)."
          href="/admin"
        />
      </section>
    </div>
  );
}

/** Card component */
function FeatureCard({
  icon: Icon,
  title,
  description,
  href,
}: {
  icon: typeof Rocket;
  title: string;
  description: string;
  href: string;
}) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="group rounded-2xl border bg-white p-6 shadow-sm transition-shadow hover:shadow-lg"
    >
      <Link href={href} className="flex flex-col h-full gap-4">
        <div className="flex items-center justify-center h-12 w-12 rounded-xl bg-blue-100 text-blue-600">
          <Icon size={24} />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 group-hover:underline">
          {title}
        </h3>
        <p className="flex-1 text-sm text-gray-600">{description}</p>
        <span className="text-sm font-medium text-blue-600 group-hover:underline">
          Explore →
        </span>
      </Link>
    </motion.div>
  );
}
