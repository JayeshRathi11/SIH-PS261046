"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const ToastContainer: React.FC = () => {
  const { toasts } = useApp();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none max-w-md w-full">
      {toasts.map((t) => {
        const bg =
          t.type === "error"
            ? "bg-[#ba1a1a] text-white border-[#ffdad6]/40"
            : t.type === "success"
            ? "bg-[#064e3b] text-white border-[#85f8c4]/40"
            : "bg-neutral-900 text-neutral-100 border-neutral-700";

        const icon =
          t.type === "error"
            ? "error"
            : t.type === "success"
            ? "check_circle"
            : "info";

        return (
          <div
            key={t.id}
            className={`${bg} px-4 py-2.5 rounded-lg shadow-xl text-xs font-sans border flex items-center gap-2 pointer-events-auto transition-all animate-in slide-in-from-bottom-2 duration-150`}
          >
            <span className="material-symbols-outlined text-base">{icon}</span>
            <span className="leading-snug flex-1">{t.message}</span>
          </div>
        );
      })}
    </div>
  );
};
