"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/context/AppContext";
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
import { ExecutiveDashboard } from "@/components/analytics/ExecutiveDashboard";

const MainWorkspaceContent: React.FC = () => {
  const { activeTab, currentRole, currentSite, currentUser } = useApp();

  const roleTitles: Record<string, string> = {
    doctor: "Principal Investigator (PI) Bedside Examination Desk",
    coordinator: "Clinical Research Coordinator (CRC) Study Operations",
    npvcc: "National Pharmacovigilance Centre for Ayurveda (NPvCC) Incident Triage",
    auditor: "CDSCO Regulatory Auditor & ALCOA+ Cryptographic Ledger",
    admin: "Executive DSMB & Multi-Center Analytics Desk",
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#FBFBFA] text-slate-800">
      {/* Workspace Sub-header */}
      <div className="bg-white border-b border-slate-200/80 px-4 sm:px-6 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs shadow-xs">
        <div className="flex items-center gap-2.5 flex-wrap">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-bold text-slate-900 tracking-tight">
            {roleTitles[currentRole] || roleTitles.doctor}
          </span>
          <span className="text-slate-300">|</span>
          <span className="text-[11px] font-mono text-slate-500">
            Active Clinician: <strong className="text-slate-800">{currentUser?.name || "Dr. Jayesh Rathi"}</strong> ({currentUser?.roleHeader || "DOCTOR"})
          </span>
          <span className="text-slate-300">•</span>
          <span className="text-[11px] font-mono text-slate-500">
            Scope: <span className="text-emerald-700 font-semibold">{currentSite === "SITE-01" ? "AIIA New Delhi" : "IPGT&RA Jamnagar"}</span>
          </span>
        </div>

        <div className="flex items-center gap-2 text-[10px] font-mono">
          <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-0.5 rounded-full font-semibold">
            Protocol: AIIA-GUD-2026
          </span>
          <span className="bg-teal-50 text-teal-800 border border-teal-200 px-2.5 py-0.5 rounded-full font-semibold">
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
        {activeTab === "analytics" && <ExecutiveDashboard />}
      </main>

      {/* Regulatory Footer */}
      <footer className="bg-white border-t border-slate-200/80 px-4 sm:px-6 py-3 text-[11px] text-slate-500 flex flex-wrap items-center justify-between gap-2 shadow-2xs">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>CDSCO SUGAM Gateway: <strong className="text-slate-800">Connected (TLS 1.3)</strong></span>
          </span>
          <span className="text-slate-300">•</span>
          <span>Session Hash: <strong className="font-mono text-emerald-700">SHA256: 7d84a...93fcb</strong></span>
        </div>
        <div className="flex items-center gap-2">
          <span>Validated Under US FDA 21 CFR Part 11 &amp; GAMP 5 Category 4</span>
          <span className="text-slate-300">•</span>
          <strong className="text-emerald-700">AIIA &amp; NPvCC Platform</strong>
        </div>
      </footer>

      {/* Global Modals & Notifications */}
      <CT16Modal />
      <ToastContainer />
    </div>
  );
};

export default function Home() {
  const { isAuthenticated, isMounted } = useApp();
  const router = useRouter();

  useEffect(() => {
    if (isMounted && !isAuthenticated) {
      router.push("/login");
    }
  }, [isMounted, isAuthenticated, router]);

  if (!isMounted || !isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#FBFBFA] flex items-center justify-center text-slate-700 font-mono text-sm">
        <div className="flex items-center gap-3 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <span className="w-5 h-5 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></span>
          <span>Authenticating AyuTrial-CTMS Session...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#FBFBFA]">
      <StatutoryBanner />
      <HeaderNav />
      <PitchStepper />
      <div className="flex-1 flex overflow-hidden">
        <SideNav />
        <MainWorkspaceContent />
      </div>
    </div>
  );
}

