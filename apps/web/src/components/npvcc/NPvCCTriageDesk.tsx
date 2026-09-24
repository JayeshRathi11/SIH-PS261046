"use client";

import React, { useState } from "react";
import { useApp } from "@/context/AppContext";

export const NPvCCTriageDesk: React.FC = () => {
  const { slaCountdown, openCT16Modal, showToast } = useApp();
  const [naranjoScore, setNaranjoScore] = useState<number>(6);

  const meddraTokens = [
    {
      ayur: "netra-peetata (नेत्र-पीतता)",
      pt: "Jaundice ocular",
      code: "10023126",
      soc: "Hepatobiliary disorders",
      confidence: "98.4%",
    },
    {
      ayur: "amlapitta (अम्लपित्त)",
      pt: "Hyperacidity / Dyspepsia",
      code: "10020639",
      soc: "Gastrointestinal disorders",
      confidence: "96.1%",
    },
    {
      ayur: "yakrit shotha (यकृत शोथ)",
      pt: "Drug-induced liver injury",
      code: "10072268",
      soc: "Hepatobiliary disorders",
      confidence: "94.8%",
    },
  ];

  return (
    <div className="space-y-4">
      {/* Triage Desk Header */}
      <div className="bg-white p-4 rounded border border-[#bfc9c3]/60 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded bg-[#ba1a1a] text-white flex items-center justify-center font-bold text-sm">
            <span className="material-symbols-outlined text-2xl">emergency</span>
          </div>
          <div>
            <h2 className="text-sm font-bold text-[#003527] leading-tight">
              National Pharmacovigilance Centre for Ayurveda (NPvCC) Incident Triage
            </h2>
            <p className="text-[11px] text-[#404944]">
              Real-time Adverse Event Triage, BioBERT NLP MedDRA Coding &amp; CDSCO Form CT-16 Expedited Gate
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="bg-[#ffdad6] text-[#ba1a1a] px-3 py-1.5 rounded text-xs font-mono font-bold border border-[#ba1a1a]/30 flex items-center gap-1.5">
            <span className="material-symbols-outlined text-sm animate-spin">
              timer
            </span>
            <span>T-24h Statutory Clock: {slaCountdown}</span>
          </div>
          <button
            onClick={openCT16Modal}
            className="bg-[#ba1a1a] hover:bg-[#93000a] text-white px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-1 shadow-sm transition-transform active:scale-95 cursor-pointer"
          >
            <span className="material-symbols-outlined text-sm">assignment_late</span>
            <span>Compile Form CT-16</span>
          </button>
        </div>
      </div>

      {/* BioBERT MedDRA Coding Pipeline */}
      <div className="bg-white p-4 rounded border border-[#bfc9c3]/60 shadow-xs space-y-3">
        <div className="flex items-center justify-between border-b border-[#bfc9c3]/30 pb-2">
          <h3 className="text-xs font-bold text-[#003527] flex items-center gap-1.5">
            <span className="material-symbols-outlined text-sm text-[#006c4a]">
              psychology
            </span>
            <span>BioBERT NLP MedDRA Autonomous Coding Pipeline</span>
          </h3>
          <span className="text-[10px] font-mono text-[#006c4a] bg-[#82f5c1]/30 px-2 py-0.5 rounded font-semibold">
            Bilingual Clinical NLP Active
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#f2f3ff] text-[#404944] border-b border-[#bfc9c3]/40 text-[11px] font-bold">
                <th className="p-2.5">Ayurvedic Clinical Dictation Term</th>
                <th className="p-2.5">MedDRA Preferred Term (PT)</th>
                <th className="p-2.5">PT Code</th>
                <th className="p-2.5">System Organ Class (SOC)</th>
                <th className="p-2.5">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {meddraTokens.map((t) => (
                <tr key={t.code} className="hover:bg-[#faf8ff]">
                  <td className="p-2.5 font-semibold text-[#003527]">{t.ayur}</td>
                  <td className="p-2.5 text-neutral-800 font-bold">{t.pt}</td>
                  <td className="p-2.5 font-mono text-neutral-600">{t.code}</td>
                  <td className="p-2.5 text-neutral-600">{t.soc}</td>
                  <td className="p-2.5 font-mono text-[#006c4a] font-bold">
                    {t.confidence}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Causality Assessment Engine (Naranjo Algorithm) */}
      <div className="bg-white p-4 rounded border border-[#bfc9c3]/60 shadow-xs space-y-3">
        <div className="flex items-center justify-between border-b border-[#bfc9c3]/30 pb-2">
          <h3 className="text-xs font-bold text-[#003527] flex items-center gap-1.5">
            <span className="material-symbols-outlined text-sm text-[#006c4a]">
              calculate
            </span>
            <span>Ayurvedic Adverse Drug Reaction Causality Assessment (WHO-UMC / Naranjo Scale)</span>
          </h3>
          <span className="text-xs font-bold text-[#006c4a] bg-[#82f5c1]/30 px-2 py-0.5 rounded font-mono">
            Score: +{naranjoScore} (PROBABLE CAUSALITY)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded bg-neutral-50 border border-neutral-200 space-y-1">
            <div className="font-bold text-[#003527]">1. Temporal Sequence</div>
            <p className="text-[11px] text-neutral-600">
              Adverse reaction appeared at Day 14 following concomitant Aspirin initiation with Guduchi.
            </p>
            <div className="text-[10px] font-mono text-[#006c4a] font-bold">+2 Points</div>
          </div>

          <div className="p-3 rounded bg-neutral-50 border border-neutral-200 space-y-1">
            <div className="font-bold text-[#003527]">2. De-challenge Response</div>
            <p className="text-[11px] text-neutral-600">
              Discontinuation of botanical formulation followed by downward titration of transaminases.
            </p>
            <div className="text-[10px] font-mono text-[#006c4a] font-bold">+2 Points</div>
          </div>

          <div className="p-3 rounded bg-neutral-50 border border-neutral-200 space-y-1">
            <div className="font-bold text-[#003527]">3. Alternative Etiology</div>
            <p className="text-[11px] text-neutral-600">
              Viral hepatitis markers (HBsAg, Anti-HCV) negative. No other hepatotoxic agents.
            </p>
            <div className="text-[10px] font-mono text-[#006c4a] font-bold">+2 Points</div>
          </div>
        </div>

        <div className="flex justify-end pt-2 border-t border-neutral-100">
          <button
            onClick={() =>
              showToast(
                "Causality assessment verified & locked to trial safety ledger.",
                "success"
              )
            }
            className="bg-[#003527] hover:bg-[#064e3b] text-white px-3 py-1.5 rounded text-xs font-semibold cursor-pointer"
          >
            Lock Causality Adjudication
          </button>
        </div>
      </div>
    </div>
  );
};
