"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const HerbDrugMatrix: React.FC = () => {
  const { showToast, openCT16Modal } = useApp();

  const interactions = [
    {
      herb: "Guduchi (Tinospora cordifolia)",
      drug: "Aspirin (Acetylsalicylic acid)",
      severity: "CRITICAL",
      severityColor: "bg-[#ba1a1a] text-white",
      mechanism:
        "Synergistic antiplatelet inhibition + additive hepatotoxicity via CYP450 modulation. Causes acute ALT/AST elevation & scleral icterus.",
      incident: "Flagged in Patient AIIA-P089",
      active: true,
    },
    {
      herb: "Shuddha Guggulu (Commiphora mukul)",
      drug: "Warfarin (Coumadin)",
      severity: "CRITICAL",
      severityColor: "bg-[#ba1a1a] text-white",
      mechanism:
        "Guggulsterones displace warfarin from albumin binding sites, elevating INR > 4.5 and inducing severe spontaneous hemorrhagic risk.",
      incident: "Monitored in AIIA-GUG-2024",
      active: false,
    },
    {
      herb: "Haridra (Curcuma longa)",
      drug: "Low Molecular Weight Heparin",
      severity: "MODERATE",
      severityColor: "bg-[#fffbeb] text-[#d97706] border border-[#fde68a]",
      mechanism:
        "Curcumin inhibits thrombin-induced platelet aggregation; synergistic anticoagulation requires aPTT monitoring.",
      incident: "Theoretical Interaction",
      active: false,
    },
    {
      herb: "Ashwagandha (Withania somnifera)",
      drug: "Lorazepam / Benzodiazepines",
      severity: "MODERATE",
      severityColor: "bg-[#fffbeb] text-[#d97706] border border-[#fde68a]",
      mechanism:
        "Withanolides exert GABA-mimetic activity, potentiating central nervous system sedation and respiratory depression.",
      incident: "Monitored in AIIA-ASH-2025",
      active: false,
    },
  ];

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <div className="bg-white p-4 rounded border border-[#bfc9c3]/60 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded bg-[#064e3b] text-[#85f8c4] flex items-center justify-center font-bold text-sm">
            <span className="material-symbols-outlined text-2xl">medication_liquid</span>
          </div>
          <div>
            <h2 className="text-sm font-bold text-[#003527] leading-tight">
              Institutional Botanical &amp; Pharmaceutical Interaction Matrix
            </h2>
            <p className="text-[11px] text-[#404944]">
              National Pharmacovigilance Centre for Ayurveda (NPvCC) Herb-Drug Safety Engine
            </p>
          </div>
        </div>

        <button
          onClick={() =>
            showToast("Herb-Drug matrix refreshed with latest NPvCC clinical trial monographs.", "info")
          }
          className="bg-[#f2f3ff] hover:bg-[#eaedff] text-[#003527] px-3 py-1.5 rounded text-xs font-semibold border border-[#bfc9c3]/50 cursor-pointer"
        >
          Check Active Cohorts
        </button>
      </div>

      {/* Interactions Table */}
      <div className="bg-white rounded border border-[#bfc9c3]/60 shadow-xs overflow-hidden">
        <div className="p-3 bg-[#faf8ff] border-b border-[#bfc9c3]/40 flex items-center justify-between">
          <h3 className="text-xs font-bold text-[#003527] flex items-center gap-1.5">
            <span className="material-symbols-outlined text-sm text-[#ba1a1a]">
              warning
            </span>
            <span>Flagged Pharmacodynamic &amp; Pharmacokinetic Conflicts</span>
          </h3>
          <span className="text-[10px] font-mono text-neutral-500">
            4 Documented Interaction Pathways
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#f2f3ff] text-[#404944] border-b border-[#bfc9c3]/40 text-[11px] font-bold">
                <th className="p-2.5">Ayurvedic Botanical Formulation</th>
                <th className="p-2.5">Concomitant Allopathic Agent</th>
                <th className="p-2.5">Severity</th>
                <th className="p-2.5">Pharmacological Mechanism</th>
                <th className="p-2.5">Trial Correlation</th>
                <th className="p-2.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {interactions.map((i, idx) => (
                <tr
                  key={idx}
                  className={`hover:bg-[#faf8ff] transition-colors ${
                    i.active ? "bg-[#ffdad6]/20" : ""
                  }`}
                >
                  <td className="p-2.5 font-bold text-[#003527]">{i.herb}</td>
                  <td className="p-2.5 font-semibold text-neutral-800">{i.drug}</td>
                  <td className="p-2.5">
                    <span
                      className={`text-[9px] font-mono px-2 py-0.5 rounded font-bold ${i.severityColor}`}
                    >
                      {i.severity}
                    </span>
                  </td>
                  <td className="p-2.5 text-[11px] text-neutral-600 max-w-xs leading-relaxed">
                    {i.mechanism}
                  </td>
                  <td className="p-2.5 font-mono text-[11px]">
                    <span
                      className={
                        i.active ? "text-[#ba1a1a] font-bold" : "text-neutral-500"
                      }
                    >
                      {i.incident}
                    </span>
                  </td>
                  <td className="p-2.5 text-right">
                    {i.active && (
                      <button
                        onClick={openCT16Modal}
                        className="px-2 py-1 bg-[#ba1a1a] hover:bg-[#93000a] text-white rounded text-[10px] font-semibold cursor-pointer shadow-xs"
                      >
                        Form CT-16
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
