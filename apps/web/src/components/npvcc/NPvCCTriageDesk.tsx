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
      {/* Triage Desk Header Bento */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-rose-50 border border-rose-200 text-rose-600 flex items-center justify-center font-bold text-sm shadow-xs">
            <span className="material-symbols-outlined text-2xl animate-sae-pulse">emergency</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-semibold tracking-wider text-rose-800 bg-rose-50/80 px-2.5 py-0.5 rounded-full border border-rose-200/60 inline-flex items-center gap-1.5">
                ▪ Pharmacovigilance Triage
              </span>
              <span className="bg-slate-100 text-slate-700 border border-slate-200 text-[9px] font-mono px-2 py-0.5 rounded-full font-bold">
                NPvCC APEX GATE
              </span>
            </div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight mt-1">
              National Pharmacovigilance Centre for Ayurveda Incident Triage
            </h2>
            <p className="text-[11px] text-slate-500">
              Real-time Adverse Event Triage, BioBERT NLP MedDRA Coding &amp; CDSCO Form CT-16 Expedited Gate
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="bg-rose-50 text-rose-700 px-3.5 py-1.5 rounded-full text-xs font-mono font-semibold border border-rose-200 flex items-center gap-2 shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
            <span>T-24h Statutory Clock: {slaCountdown}</span>
          </div>
          <button
            onClick={openCT16Modal}
            className="bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-xs transition-all active:scale-95 cursor-pointer"
          >
            <span className="material-symbols-outlined text-sm font-bold">assignment_late</span>
            <span>Compile Form CT-16</span>
          </button>
        </div>
      </div>

      {/* HIDDEN FOR CORE DEMO: Semantic Case Similarity Search Bar & Vector Clustering
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-sm text-sky-600">travel_explore</span>
            <h3 className="text-xs font-bold text-slate-900 tracking-tight">
              BioBERT Semantic Case Similarity &amp; Historical Signal Search
            </h3>
          </div>
          <span className="text-[10px] font-mono text-sky-800 bg-sky-50 border border-sky-200 px-2.5 py-0.5 rounded-full font-semibold">
            Cosine Vector Space (768-dim)
          </span>
        </div>
        <div className="relative">
          <input
            type="text"
            placeholder="Search similar multicenter adverse events via BioBERT embeddings..."
            className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none"
          />
        </div>
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500">
          Historical similar cases (AIIA-GUD-2024, IPGTRA-2025) clustered via cosine similarity &gt; 0.85
        </div>
      </div>
      */}

      {/* BioBERT MedDRA Coding Pipeline Bento */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-sm text-emerald-600">
              psychology
            </span>
            <h3 className="text-xs font-bold text-slate-900 tracking-tight">
              BioBERT NLP MedDRA Autonomous Coding Pipeline
            </h3>
          </div>
          <span className="text-[10px] font-mono text-emerald-800 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full font-semibold">
            Bilingual Clinical NLP Active
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 border-b border-slate-200 text-[10px] uppercase font-mono tracking-wider">
                <th className="p-3">Ayurvedic Clinical Dictation Term</th>
                <th className="p-3">MedDRA Preferred Term (PT)</th>
                <th className="p-3">PT Code</th>
                <th className="p-3">System Organ Class (SOC)</th>
                <th className="p-3">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {meddraTokens.map((t) => (
                <tr key={t.code} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-3 font-semibold text-emerald-800">{t.ayur}</td>
                  <td className="p-3 text-slate-900 font-bold">{t.pt}</td>
                  <td className="p-3 font-mono text-slate-500">{t.code}</td>
                  <td className="p-3 text-slate-700">{t.soc}</td>
                  <td className="p-3 font-mono text-emerald-700 font-bold">
                    <span className="bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                      {t.confidence}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Causality Assessment Engine (Naranjo Algorithm) Bento */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-sm text-emerald-600">
              calculate
            </span>
            <h3 className="text-xs font-bold text-slate-900 tracking-tight">
              Ayurvedic Adverse Drug Reaction Causality Assessment (WHO-UMC / Naranjo Scale)
            </h3>
          </div>
          <span className="text-xs font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full font-mono shadow-2xs">
            Score: +{naranjoScore} (PROBABLE CAUSALITY)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200 space-y-1.5">
            <div className="font-bold text-slate-900">1. Temporal Sequence</div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Adverse reaction appeared at Day 14 following concomitant Aspirin initiation with Guduchi.
            </p>
            <div className="text-[10px] font-mono text-emerald-700 font-bold pt-1">+2 Points</div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200 space-y-1.5">
            <div className="font-bold text-slate-900">2. De-challenge Response</div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Discontinuation of botanical formulation followed by downward titration of transaminases.
            </p>
            <div className="text-[10px] font-mono text-emerald-700 font-bold pt-1">+2 Points</div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200 space-y-1.5">
            <div className="font-bold text-slate-900">3. Alternative Etiology</div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Viral hepatitis markers (HBsAg, Anti-HCV) negative. No other hepatotoxic agents.
            </p>
            <div className="text-[10px] font-mono text-emerald-700 font-bold pt-1">+2 Points</div>
          </div>
        </div>

        <div className="flex justify-end pt-3 border-t border-slate-100">
          <button
            onClick={() =>
              showToast(
                "Causality assessment verified & locked to trial safety ledger.",
                "success"
              )
            }
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl text-xs font-semibold transition-all active:scale-95 cursor-pointer shadow-xs"
          >
            Lock Causality Adjudication
          </button>
        </div>
      </div>
    </div>
  );
};
