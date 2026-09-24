"use client";

import React from "react";
import { useApp, Role, Site, Tab } from "@/context/AppContext";

export const HeaderNav: React.FC = () => {
  const {
    currentRole,
    currentSite,
    activeTab,
    changePersona,
    switchSite,
    switchTab,
  } = useApp();

  return (
    <header className="flex justify-between items-center w-full px-4 sm:px-6 h-14 bg-white border-b border-[#bfc9c3]/50 z-40 sticky top-0 shadow-xs">
      {/* Brand Anchor & Multi-Center Switcher */}
      <div className="flex items-center gap-4 sm:gap-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-[#064e3b] text-[#85f8c4] flex items-center justify-center font-bold shadow-sm">
            <span className="material-symbols-outlined text-lg">clinical_notes</span>
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-bold text-[#003527] tracking-tight leading-tight">
              AyuTrial-CTMS <span className="font-normal text-neutral-400">|</span> NPvCC Portal
            </h1>
            <p className="font-mono text-[10px] text-[#404944] flex items-center gap-1.5 flex-wrap">
              <span>AIIA New Delhi</span>
              <span className="text-[#bfc9c3]">•</span>
              <span className="text-[#006c4a] font-semibold">21 CFR Part 11</span>
              <span className="text-[#bfc9c3]">•</span>
              <span>GAMP 5 Cat.4</span>
              <span className="text-[#bfc9c3] hidden lg:inline">•</span>
              <span className="text-[#003527] font-medium hidden lg:inline">
                DPDP §6(4) Compliant
              </span>
            </p>
          </div>
        </div>

        {/* Site Switcher */}
        <div className="hidden lg:flex items-center bg-[#f2f3ff] rounded border border-[#bfc9c3]/60 p-0.5">
          <button
            onClick={() => switchSite("SITE-01")}
            className={`px-2 py-1 rounded text-xs font-semibold transition-colors cursor-pointer ${
              currentSite === "SITE-01"
                ? "bg-white text-[#003527] shadow-xs"
                : "text-[#404944] hover:text-[#003527]"
            }`}
          >
            SITE-01: AIIA New Delhi
          </button>
          <button
            onClick={() => switchSite("SITE-02")}
            className={`px-2 py-1 rounded text-xs font-semibold transition-colors cursor-pointer ${
              currentSite === "SITE-02"
                ? "bg-white text-[#003527] shadow-xs"
                : "text-[#404944] hover:text-[#003527]"
            }`}
          >
            SITE-02: IPGT&RA Jamnagar
          </button>
        </div>
      </div>

      {/* Center Navigation Links */}
      <nav className="hidden xl:flex items-center space-x-6 text-xs">
        <button
          onClick={() => switchTab("state_machine")}
          className={`pb-1 transition-colors flex items-center gap-1 cursor-pointer font-medium ${
            activeTab === "state_machine"
              ? "text-[#003527] border-b-2 border-[#003527] font-semibold"
              : "text-[#404944] hover:text-[#003527]"
          }`}
        >
          <span className="material-symbols-outlined text-sm">assignment</span>
          Active Trials
        </button>
        <button
          onClick={() => switchTab("ecrf_desk")}
          className={`pb-1 transition-colors flex items-center gap-1 cursor-pointer font-medium ${
            activeTab === "ecrf_desk"
              ? "text-[#003527] border-b-2 border-[#003527] font-semibold"
              : "text-[#404944] hover:text-[#003527]"
          }`}
        >
          <span className="material-symbols-outlined text-sm">table_chart</span>
          eCRF Matrix
        </button>
        <button
          onClick={() => switchTab("npvcc_desk")}
          className={`pb-1 transition-colors flex items-center gap-1 cursor-pointer font-medium ${
            activeTab === "npvcc_desk"
              ? "text-[#003527] border-b-2 border-[#003527] font-semibold"
              : "text-[#404944] hover:text-[#003527]"
          }`}
        >
          <span className="material-symbols-outlined text-sm">emergency</span>
          Safety Signals
          <span className="bg-[#ba1a1a] text-white text-[9px] font-mono px-1.5 py-0.2 rounded-full">
            1
          </span>
        </button>
        <button
          onClick={() => switchTab("alcoa_ledger")}
          className={`pb-1 transition-colors flex items-center gap-1 cursor-pointer font-medium ${
            activeTab === "alcoa_ledger"
              ? "text-[#003527] border-b-2 border-[#003527] font-semibold"
              : "text-[#404944] hover:text-[#003527]"
          }`}
        >
          <span className="material-symbols-outlined text-sm">verified_user</span>
          Regulatory Audit
        </button>
      </nav>

      {/* Global Telemetry & Persona Selector */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Latency & Encryption Status */}
        <div className="hidden 2xl:flex items-center gap-2 border-r border-[#bfc9c3]/60 pr-3 font-mono text-[10px]">
          <span className="flex items-center gap-1 text-[#006c4a] font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-[#006c4a]"></span> SUGAM: Encrypted
          </span>
          <span className="flex items-center gap-1 text-[#404944]">
            FastAPI: <span className="text-[#006c4a] font-semibold">14ms</span>
          </span>
        </div>

        {/* Persona Role Switcher */}
        <div className="flex items-center gap-1.5 bg-[#f2f3ff] px-2 py-1 rounded border border-[#bfc9c3]/60">
          <span className="material-symbols-outlined text-sm text-[#006c4a]">badge</span>
          <select
            value={currentRole}
            onChange={(e) => changePersona(e.target.value as Role)}
            className="bg-transparent border-0 text-xs font-semibold text-[#003527] focus:ring-0 cursor-pointer p-0 pr-6"
          >
            <option value="doctor">Dr. V. Sharma (PI - AIIA Delhi)</option>
            <option value="coordinator">Coord. R. Patel (CRC - Multi-Center)</option>
            <option value="npvcc">Dr. A. Joshi (NPvCC Medical Officer)</option>
            <option value="auditor">Inspector S. Rao (CDSCO Regulatory Auditor)</option>
          </select>
        </div>
      </div>
    </header>
  );
};
