"use client";

import React from "react";
import { useApp, Role, Site, PRESET_PERSONAS } from "@/context/AppContext";

export const HeaderNav: React.FC = () => {
  const {
    currentUser,
    currentRole,
    currentSite,
    changePersona,
    switchSite,
    logout,
  } = useApp();

  return (
    <header className="flex justify-between items-center w-full px-6 py-3 bg-white/95 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-40 shadow-xs">
      {/* Left: Brand Logo & Title */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-emerald-50 border border-emerald-200/80 text-emerald-700 flex items-center justify-center font-bold shadow-xs">
          <span className="material-symbols-outlined text-lg">clinical_notes</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-900 font-bold text-base tracking-tight">
            AyuTrial-CTMS
          </span>
          <span className="text-slate-500 text-xs bg-slate-100 border border-slate-200/60 px-2 py-0.5 rounded-md font-medium">
            AIIA Apex Centre
          </span>
        </div>
      </div>

      {/* Center: Fixed Site Badge & Hidden Multi-Site Toggle */}
      <div className="hidden md:flex items-center">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs font-semibold text-emerald-800">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
          SITE-01: AIIA New Delhi (Apex Centre)
        </div>
        {/* HIDDEN FOR CORE DEMO: Multi-site interactive switch toggle
        <div className="flex items-center bg-slate-100 p-1 rounded-full border border-slate-200/80 shadow-xs ml-2">
          <button
            onClick={() => switchSite("SITE-01")}
            className={`px-3 py-1 text-xs rounded-full transition-all cursor-pointer ${
              currentSite === "SITE-01"
                ? "bg-white text-emerald-800 shadow-sm font-semibold"
                : "text-slate-600 hover:text-slate-900 font-medium"
            }`}
          >
            SITE-01 AIIA
          </button>
          <button
            onClick={() => switchSite("SITE-02")}
            className={`px-3 py-1 text-xs rounded-full transition-all cursor-pointer ${
              currentSite === "SITE-02"
                ? "bg-white text-emerald-800 shadow-sm font-semibold"
                : "text-slate-600 hover:text-slate-900 font-medium"
            }`}
          >
            SITE-02 Jamnagar
          </button>
        </div>
        */}
      </div>

      {/* Right: Latency Badge, Profile Pill & Sign Out */}
      <div className="flex items-center gap-2.5">
        {/* Latency Badge */}
        <div className="hidden lg:flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200/60 px-2.5 py-1 rounded-full font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>12ms ● TLS 1.3</span>
        </div>

        {/* Active Clinician Profile Pill */}
        <div className="flex items-center gap-2 border border-slate-200 bg-slate-50/80 px-3 py-1 rounded-full text-xs text-slate-800 font-medium shadow-xs">
          <div
            className={`w-5 h-5 rounded-full flex items-center justify-center font-bold text-[10px] ${
              currentUser?.avatarColor || "bg-emerald-100 text-emerald-800"
            }`}
          >
            <span className="material-symbols-outlined text-xs">
              {currentUser?.avatarIcon || "person"}
            </span>
          </div>

          <span className="hidden sm:inline font-semibold text-slate-900">
            {currentUser?.name || "Dr. Jayesh Rathi"}
          </span>

          <select
            value={currentRole}
            onChange={(e) => changePersona(e.target.value as Role)}
            className="bg-transparent border-0 text-xs font-semibold text-slate-600 hover:text-slate-900 focus:ring-0 cursor-pointer p-0 pr-4"
          >
            <option value="doctor" className="bg-white text-slate-900">PI / Doctor</option>
            <option value="coordinator" className="bg-white text-slate-900">CRC (Priya)</option>
            <option value="npvcc" className="bg-white text-slate-900">NPvCC Officer</option>
            <option value="auditor" className="bg-white text-slate-900">CDSCO Auditor</option>
            <option value="admin" className="bg-white text-slate-900">DSMB / Admin</option>
          </select>
        </div>

        {/* Minimal Sign Out Button */}
        <button
          onClick={logout}
          title="Sign Out / Switch Station"
          className="flex items-center gap-1 text-slate-600 hover:text-rose-700 bg-slate-100 hover:bg-rose-50 border border-slate-200 hover:border-rose-200 px-3 py-1.5 rounded-full text-xs font-medium transition-colors cursor-pointer"
        >
          <span className="material-symbols-outlined text-sm">logout</span>
          <span className="hidden sm:inline">Sign Out</span>
        </button>
      </div>
    </header>
  );
};

