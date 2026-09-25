"use client";

import React from "react";
import { useApp, Tab } from "@/context/AppContext";

export const SideNav: React.FC = () => {
  const { activeTab, switchTab, currentRole, currentSite } = useApp();

  const operationsItems: Array<{
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
      id: "herb_drug",
      icon: "medication_liquid",
      label: "Herb-Drug Safety Matrix",
      sublabel: "Guduchi + Aspirin Alert",
    },
  ];

  const governanceItems: Array<{
    id: Tab;
    icon: string;
    label: string;
    sublabel: string;
    badge?: string;
  }> = [
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
  ];

  const intelligenceItems: Array<{
    id: Tab;
    icon: string;
    label: string;
    sublabel: string;
    badge?: string;
  }> = [
    {
      id: "analytics",
      icon: "monitoring",
      label: "Executive DSMB Analytics",
      sublabel: "Multi-Center KPIs & SPC",
      badge: "DSMB",
    },
    {
      id: "regulatory_export",
      icon: "cloud_sync",
      label: "Interoperability & Export",
      sublabel: "CDISC SDTM & HL7 FHIR",
    },
  ];

  const roleDisplay: Record<string, string> = {
    doctor: "Principal Investigator",
    coordinator: "Research Coordinator",
    npvcc: "NPvCC Medical Officer",
    auditor: "CDSCO Auditor",
    admin: "Executive DSMB Chair",
  };

  const renderNavGroup = (title: string, items: typeof operationsItems) => (
    <div className="space-y-1">
      <div className="px-3 py-1.5 text-[10px] font-semibold tracking-wider text-slate-400 uppercase">
        {title}
      </div>
      {items.map((item) => {
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => switchTab(item.id)}
            className={`w-full text-left flex items-start gap-2.5 px-3 py-2 rounded-xl text-xs transition-all duration-150 cursor-pointer ${
              isActive
                ? "bg-white text-emerald-800 font-semibold shadow-xs border border-slate-200/80"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80 border border-transparent"
            }`}
          >
            <span
              className={`material-symbols-outlined text-base mt-0.5 transition-colors ${
                isActive ? "text-emerald-700" : "text-slate-400"
              }`}
            >
              {item.icon}
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-1">
                <span className="truncate">{item.label}</span>
                {item.badge && (
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.2 rounded-full font-bold ${
                      item.badge.includes("SAE")
                        ? "bg-rose-50 text-rose-700 border border-rose-200"
                        : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </div>
              <p className="text-[10px] truncate text-slate-500 font-normal">
                {item.sublabel}
              </p>
            </div>
          </button>
        );
      })}
    </div>
  );

  return (
    <aside className="w-64 bg-[#F8FAFC] border-r border-slate-200/80 flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)] p-3 select-none">
      {/* Navigation Sections */}
      <div className="space-y-4">
        {renderNavGroup("▪ Operations", operationsItems)}
        {renderNavGroup("▪ Governance", governanceItems)}
        {renderNavGroup("▪ Intelligence", intelligenceItems)}
      </div>

      {/* User Session Footer */}
      <div className="pt-3 border-t border-slate-200">
        <div className="flex items-center gap-2.5 p-2.5 rounded-xl bg-white border border-slate-200/80 shadow-xs">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold text-xs border border-emerald-200 shadow-xs">
            {currentRole.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-semibold text-slate-900 truncate">
              {roleDisplay[currentRole]}
            </div>
            <div className="text-[10px] font-mono text-emerald-700 font-medium truncate">
              {currentSite === "SITE-01" ? "SITE-01: DELHI" : "SITE-02: JAMNAGAR"}
            </div>
          </div>
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
        </div>
      </div>
    </aside>
  );
};

