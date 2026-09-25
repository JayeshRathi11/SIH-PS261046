"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const ToastContainer: React.FC = () => {
  const { toasts } = useApp();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 pointer-events-none max-w-md w-full">
      {toasts.map((t) => {
        const isError = t.type === "error";
        const isSuccess = t.type === "success";

        const style = isError
          ? "bg-white text-rose-900 border-rose-200 shadow-lg"
          : isSuccess
          ? "bg-white text-slate-800 border-emerald-200 shadow-lg"
          : "bg-white text-slate-800 border-slate-200 shadow-lg";

        const iconColor = isError
          ? "text-rose-600"
          : isSuccess
          ? "text-emerald-600"
          : "text-slate-600";

        const icon = isError
          ? "error"
          : isSuccess
          ? "check_circle"
          : "info";

        return (
          <div
            key={t.id}
            className={`${style} backdrop-blur-md px-4 py-3 rounded-2xl border flex items-center gap-3 pointer-events-auto transition-all animate-in slide-in-from-bottom-2 duration-200`}
          >
            <span className={`material-symbols-outlined text-lg ${iconColor} shrink-0`}>
              {icon}
            </span>
            <div className="text-xs leading-snug font-sans flex-1 font-medium">
              {t.message}
            </div>
          </div>
        );
      })}
    </div>
  );
};

