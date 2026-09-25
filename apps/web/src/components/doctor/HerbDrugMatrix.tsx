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
      severityClass: "bg-rose-500/15 text-rose-300 border-rose-500/40 shadow-[0_0_12px_rgba(244,63,94,0.2)]",
      mechanism:
        "Synergistic antiplatelet inhibition + additive hepatotoxicity via CYP450 modulation. Causes acute ALT/AST elevation & scleral icterus.",
      incident: "Flagged in Patient AIIA-P089",
      active: true,
    },
    {
      herb: "Shuddha Guggulu (Commiphora mukul)",
      drug: "Warfarin (Coumadin)",
      severity: "CRITICAL",
      severityClass: "bg-rose-500/15 text-rose-300 border-rose-500/40 shadow-[0_0_12px_rgba(244,63,94,0.2)]",
      mechanism:
        "Guggulsterones displace warfarin from albumin binding sites, elevating INR > 4.5 and inducing severe spontaneous hemorrhagic risk.",
      incident: "Monitored in AIIA-GUG-2024",
      active: false,
    },
    {
      herb: "Haridra (Curcuma longa)",
      drug: "Low Molecular Weight Heparin",
      severity: "MODERATE",
      severityClass: "bg-amber-500/15 text-amber-300 border-amber-500/30",
      mechanism:
        "Curcumin inhibits thrombin-induced platelet aggregation; synergistic anticoagulation requires aPTT monitoring.",
      incident: "Theoretical Interaction",
      active: false,
    },
    {
      herb: "Ashwagandha (Withania somnifera)",
      drug: "Lorazepam / Benzodiazepines",
      severity: "MODERATE",
      severityClass: "bg-amber-500/15 text-amber-300 border-amber-500/30",
      mechanism:
        "Withanolides exert GABA-mimetic activity, potentiating central nervous system sedation and respiratory depression.",
      incident: "Monitored in AIIA-ASH-2025",
      active: false,
    },
  ];

  return (
    <div className="space-y-4">
      {/* Header Banner Bento */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-center justify-center font-bold text-sm shadow-xs">
            <span className="material-symbols-outlined text-2xl">medication_liquid</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-semibold tracking-wider text-emerald-800 bg-emerald-50/80 px-2.5 py-0.5 rounded-full border border-emerald-200/60 inline-flex items-center gap-1.5">
                ▪ Interoperability Safety Matrix
              </span>
              <span className="bg-slate-100 text-slate-700 border border-slate-200 text-[9px] font-mono px-2 py-0.5 rounded-full font-bold">
                NPvCC MONOGRAPHS
              </span>
            </div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight mt-1">
              Institutional Botanical &amp; Pharmaceutical Interaction Matrix
            </h2>
            <p className="text-[11px] text-slate-500">
              National Pharmacovigilance Centre for Ayurveda (NPvCC) Herb-Drug Safety Engine
            </p>
          </div>
        </div>

        <button
          onClick={() =>
            showToast("Herb-Drug matrix refreshed with latest NPvCC clinical trial monographs.", "info")
          }
          className="bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 px-4 py-2 rounded-xl text-xs font-semibold cursor-pointer transition-all active:scale-95 shadow-2xs flex items-center gap-1.5"
        >
          <span className="material-symbols-outlined text-sm text-emerald-600">sync</span>
          <span>Check Active Cohorts</span>
        </button>
      </div>

      {/* Interactions Table Bento */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 bg-slate-50/60 border-b border-slate-200/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-sm text-rose-600">
              warning
            </span>
            <h3 className="text-xs font-bold text-slate-900 tracking-tight">
              Flagged Pharmacodynamic &amp; Pharmacokinetic Conflicts
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-500 bg-white border border-slate-200 px-2.5 py-0.5 rounded-full shadow-2xs">
            4 Documented Interaction Pathways
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 border-b border-slate-200 text-[10px] uppercase font-mono tracking-wider">
                <th className="p-3">Ayurvedic Botanical Formulation</th>
                <th className="p-3">Concomitant Allopathic Agent</th>
                <th className="p-3">Severity</th>
                <th className="p-3">Pharmacological Mechanism</th>
                <th className="p-3">Trial Correlation</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {interactions.map((i, idx) => (
                <tr
                  key={idx}
                  className={`hover:bg-slate-50/80 transition-colors ${
                    i.active ? "bg-rose-50/40 border-l-4 border-rose-500" : ""
                  }`}
                >
                  <td className="p-3 font-semibold text-emerald-800">{i.herb}</td>
                  <td className="p-3 font-bold text-slate-900">{i.drug}</td>
                  <td className="p-3">
                    <span
                      className={`text-[9px] font-mono px-2.5 py-0.5 rounded-full font-bold border ${
                        i.severity === "CRITICAL"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : "bg-amber-50 text-amber-800 border border-amber-200"
                      }`}
                    >
                      {i.severity}
                    </span>
                  </td>
                  <td className="p-3 text-[11px] text-slate-600 max-w-xs leading-relaxed">
                    {i.mechanism}
                  </td>
                  <td className="p-3 font-mono text-[11px]">
                    <span
                      className={
                        i.active ? "text-rose-700 font-bold flex items-center gap-1" : "text-slate-500"
                      }
                    >
                      {i.active && <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span>}
                      {i.incident}
                    </span>
                  </td>
                  <td className="p-3 text-right">
                    {i.active && (
                      <button
                        onClick={openCT16Modal}
                        className="px-3 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-lg text-[10px] font-mono font-bold cursor-pointer shadow-2xs transition-all active:scale-95 flex items-center gap-1 ml-auto"
                      >
                        <span className="material-symbols-outlined text-xs">assignment_late</span>
                        <span>Form CT-16</span>
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

