"use client";

import React from "react";
import { AppProvider, useApp } from "@/context/AppContext";
import { StatutoryBanner } from "@/components/layout/StatutoryBanner";
import { HeaderNav } from "@/components/layout/HeaderNav";
import { SideNav } from "@/components/layout/SideNav";
import { PitchStepper } from "@/components/demo/PitchStepper";
import { ToastContainer } from "@/components/layout/ToastContainer";
import { CT16Modal } from "@/components/doctor/CT16Modal";
import { DynamicECRF } from "@/components/doctor/DynamicECRF";
import { ProtocolStateMachine } from "@/components/coordinator/ProtocolStateMachine";
import { NPvCCTriageDesk } from "@/components/npvcc/NPvCCTriageDesk";
import { TamperSimulator } from "@/components/auditor/TamperSimulator";
import { HerbDrugMatrix } from "@/components/doctor/HerbDrugMatrix";
import { ExportHub } from "@/components/export/ExportHub";

const MainWorkspaceContent: React.FC = () => {
  const { activeTab, currentRole, currentSite } = useApp();

  const roleTitles: Record<string, string> = {
    doctor: "Principal Investigator (PI) Bedside Examination Desk",
    coordinator: "Clinical Research Coordinator (CRC) Study Operations",
    npvcc: "National Pharmacovigilance Centre for Ayurveda (NPvCC) Incident Triage",
    auditor: "CDSCO Regulatory Auditor & ALCOA+ Cryptographic Ledger",
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#faf8ff]">
      {/* Workspace Sub-header */}
      <div className="bg-white border-b border-[#bfc9c3]/50 px-4 sm:px-6 py-2 flex flex-wrap items-center justify-between gap-2 shadow-xs">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#006c4a]"></span>
          <span className="text-xs font-bold text-[#003527]">
            {roleTitles[currentRole]}
          </span>
          <span className="text-neutral-300">|</span>
          <span className="text-[11px] font-mono text-neutral-500">
            Scope: {currentSite === "SITE-01" ? "AIIA New Delhi" : "IPGT&RA Jamnagar"}
          </span>
        </div>

        <div className="flex items-center gap-2 text-[10px] font-mono text-neutral-500">
          <span className="bg-[#b0f0d6] text-[#002117] px-2 py-0.5 rounded font-semibold">
            Protocol: AIIA-GUD-2026
          </span>
          <span className="bg-[#82f5c1] text-[#00714e] px-2 py-0.5 rounded font-semibold">
            Status: RECRUITING
          </span>
        </div>
      </div>

      {/* Dynamic Tab Body */}
      <main className="flex-1 p-4 sm:p-6 overflow-y-auto max-w-7xl w-full mx-auto">
        {activeTab === "state_machine" && <ProtocolStateMachine />}
        {activeTab === "ecrf_desk" && <DynamicECRF />}
        {activeTab === "npvcc_desk" && <NPvCCTriageDesk />}
        {activeTab === "alcoa_ledger" && <TamperSimulator />}
        {activeTab === "herb_drug" && <HerbDrugMatrix />}
        {activeTab === "regulatory_export" && <ExportHub />}
      </main>

      {/* Regulatory Footer */}
      <footer className="bg-white border-t border-[#bfc9c3]/50 px-4 sm:px-6 py-3 text-[11px] text-[#404944] flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[#006c4a]"></span>
            <span>CDSCO SUGAM Gateway: <strong>Connected (TLS 1.3)</strong></span>
          </span>
          <span>•</span>
          <span>Session Hash: <strong className="font-mono">SHA256: 7d84a...93fcb</strong></span>
        </div>
        <div className="flex items-center gap-2">
          <span>Validated Under US FDA 21 CFR Part 11 &amp; GAMP 5 Category 4</span>
          <span>•</span>
          <strong className="text-[#003527]">AIIA &amp; NPvCC Platform</strong>
        </div>
      </footer>

      {/* Global Modals & Notifications */}
      <CT16Modal />
      <ToastContainer />
    </div>
  );
};

export default function Home() {
  return (
    <AppProvider>
      <div className="flex flex-col min-h-screen">
        <StatutoryBanner />
        <HeaderNav />
        <PitchStepper />
        <div className="flex-1 flex overflow-hidden">
          <SideNav />
          <MainWorkspaceContent />
        </div>
      </div>
    </AppProvider>
  );
}
