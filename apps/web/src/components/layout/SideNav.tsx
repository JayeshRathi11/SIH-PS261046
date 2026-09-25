"use client";

import React from "react";
import { useApp, Tab } from "@/context/AppContext";

export const SideNav: React.FC = () => {
  const { activeTab, switchTab, currentRole, currentSite } = useApp();

  const navItems: Array<{
    id: Tab;
    icon: string;
    label: string;
    sublabel: string;
    badge?: string;
  }> = [
    {
      id: "state_machine",
      icon: "account_tree",
      label: "Protocol State Machine",
      sublabel: "CTRI Regex & IEC Gates",
    },
    {
      id: "ecrf_desk",
      icon: "fact_check",
      label: "Doctor Desk eCRF",
      sublabel: "P-089 Day 14 Bedside Visit",
      badge: "LIVE",
    },
    {
      id: "npvcc_desk",
      icon: "warning_amber",
      label: "NPvCC Safety Desk",
      sublabel: "BioBERT MedDRA & CT-16",
      badge: "1 SAE",
    },
    {
      id: "alcoa_ledger",
      icon: "lock_reset",
      label: "ALCOA+ Ledger & Tamper",
      sublabel: "SHA-256 Merkle Enclave",
    },
    {
      id: "herb_drug",
      icon: "medication_liquid",
      label: "Herb-Drug Safety Matrix",
      sublabel: "Guduchi + Aspirin Alert",
    },
    {
      id: "regulatory_export",
      icon: "cloud_sync",
      label: "Interoperability & Export",
      sublabel: "CDISC SDTM & HL7 FHIR",
    },
    {
      id: "analytics",
      icon: "monitoring",
      label: "Executive DSMB Analytics",
      sublabel: "Multi-Center KPIs & SPC",
      badge: "DSMB",
    },
  ];

  const roleDisplay: Record<string, string> = {
    doctor: "Principal Investigator",
    coordinator: "Research Coordinator",
    npvcc: "NPvCC Medical Officer",
    auditor: "CDSCO Auditor",
    admin: "Executive DSMB Chair",
  };

  return (
    <aside className="w-64 bg-white border-r border-[#bfc9c3]/50 flex flex-col justify-between shrink-0 min-h-[calc(100vh-8rem)]">
      {/* Navigation Links */}
      <div className="p-3 space-y-1">
        <div className="px-3 py-1.5 text-[10px] font-bold text-neutral-400 uppercase tracking-wider">
          Clinical Operations
        </div>

        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => switchTab(item.id)}
              className={`w-full text-left flex items-start gap-2.5 px-3 py-2 rounded text-xs transition-all cursor-pointer ${
                isActive
                  ? "bg-[#064e3b] text-white border-l-4 border-[#85f8c4] shadow-xs"
                  : "text-[#404944] hover:bg-[#f2f3ff] hover:text-[#003527]"
              }`}
            >
              <span
                className={`material-symbols-outlined text-base mt-0.5 ${
                  isActive ? "text-[#85f8c4]" : "text-[#707974]"
                }`}
              >
                {item.icon}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="font-semibold truncate">{item.label}</span>
                  {item.badge && (
                    <span
                      className={`text-[9px] font-mono px-1 py-0.2 rounded font-bold ${
                        item.badge.includes("SAE")
                          ? "bg-[#ba1a1a] text-white"
                          : "bg-[#006c4a] text-[#85f8c4]"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </div>
                <p
                  className={`text-[10px] truncate ${
                    isActive ? "text-[#80bea6]" : "text-[#707974]"
                  }`}
                >
                  {item.sublabel}
                </p>
              </div>
            </button>
          );
        })}
      </div>

      {/* User Session Footer */}
      <div className="p-3 border-t border-[#bfc9c3]/40 bg-[#f2f3ff]/60">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-[#064e3b] text-white flex items-center justify-center font-bold text-xs">
            {currentRole.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-semibold text-[#003527] truncate">
              {roleDisplay[currentRole]}
            </div>
            <div className="text-[10px] font-mono text-[#404944] truncate">
              {currentSite === "SITE-01" ? "SITE-01: DELHI" : "SITE-02: JAMNAGAR"}
            </div>
          </div>
          <span className="w-2 h-2 rounded-full bg-[#006c4a]"></span>
        </div>
      </div>
    </aside>
  );
};
