"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const BlockDrawer: React.FC = () => {
  const { activeBlockDrawer, closeBlockDrawer, isTampered } = useApp();

  if (activeBlockDrawer === null) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-sm">
      <div className="bg-white w-full max-w-md h-full shadow-2xl p-6 overflow-y-auto space-y-4 border-l border-slate-200 animate-in slide-in-from-right duration-200 text-slate-800">
        {/* Drawer Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700">
              <span className="material-symbols-outlined text-lg">fingerprint</span>
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 tracking-tight">
                Forensic Block Inspector #{activeBlockDrawer}
              </h2>
              <div className="text-[10px] font-mono text-slate-500">
                21 CFR Part 11 Electronic Record Detail
              </div>
            </div>
          </div>
          <button
            onClick={closeBlockDrawer}
            className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-900 flex items-center justify-center text-xs font-bold cursor-pointer border border-slate-200 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Block Integrity Badge */}
        {activeBlockDrawer === 3 && isTampered ? (
          <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-2xl text-xs space-y-1.5 shadow-xs">
            <div className="flex items-center gap-2 font-bold text-rose-800">
              <span className="material-symbols-outlined text-base text-rose-600 animate-pulse">cancel</span>
              <span>SHA-256 HASH COMPROMISED (TAMPERED)</span>
            </div>
            <p className="text-[11px] text-rose-700 leading-relaxed">
              The ALT transaminase field was modified directly in PostgreSQL from 165 U/L to 35 U/L. The recomputed leaf hash fails the isolated Merkle witness proof!
            </p>
          </div>
        ) : (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-2xl text-xs flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-emerald-800">
              <span className="material-symbols-outlined text-base text-emerald-600">
                check_circle
              </span>
              <span>Cryptographic Integrity Valid</span>
            </div>
            <span className="text-[10px] font-mono bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full border border-emerald-200 font-bold">
              ALCOA+ VERIFIED
            </span>
          </div>
        )}

        {/* Metadata Grid */}
        <div className="space-y-2 text-xs">
          <div className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Block Header Attributes:</div>
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2 font-mono text-[11px]">
            <div>
              <span className="text-slate-500">Height:</span>{" "}
              <strong className="text-slate-900">#{activeBlockDrawer}</strong>
            </div>
            <div>
              <span className="text-slate-500">Timestamp:</span>{" "}
              <span className="text-slate-700">2026-01-29T14:30:00.000Z</span>
            </div>
            <div>
              <span className="text-slate-500">Signer Identity:</span>{" "}
              <strong className="text-emerald-700">
                CN=Dr. V. Sharma, O=AIIA, C=IN
              </strong>
            </div>
            <div>
              <span className="text-slate-500">Merkle Path:</span>{" "}
              <strong className={activeBlockDrawer === 3 && isTampered ? "text-rose-700" : "text-emerald-700"}>
                {activeBlockDrawer === 3 && isTampered ? "BROKEN (Mismatch at Node #3)" : "Valid [L -> R -> Root]"}
              </strong>
            </div>
          </div>
        </div>

        {/* Raw Payload JSON */}
        <div className="space-y-1.5">
          <div className="font-semibold text-slate-500 text-[10px] uppercase tracking-wider flex justify-between">
            <span>Raw Database Payload (JSON):</span>
            {activeBlockDrawer === 3 && isTampered && (
              <span className="text-[10px] text-rose-700 font-mono font-bold animate-pulse">
                ⚠️ MUTATED BY DBA
              </span>
            )}
          </div>
          <pre
            className={`p-3.5 rounded-xl text-[11px] font-mono overflow-x-auto border ${
              activeBlockDrawer === 3 && isTampered
                ? "bg-slate-950 border-rose-300 text-rose-400 shadow-xs"
                : "bg-slate-950 border-slate-800 text-emerald-400"
            }`}
          >
            {activeBlockDrawer === 3
              ? JSON.stringify(
                  {
                    subject_id: "AIIA-P089",
                    visit: "Day 14",
                    biomarkers: {
                      alt_sgpt: isTampered ? 35 : 165,
                      ast_sgot: 142,
                      total_bilirubin: 3.4,
                    },
                    signed_by: "PI-8891",
                    status: isTampered ? "MUTATED_BY_DBA" : "VALIDATED",
                    timestamp: "2026-01-29T14:30:00Z",
                  },
                  null,
                  2
                )
              : JSON.stringify(
                  {
                    block_height: activeBlockDrawer,
                    protocol: "AIIA-GUD-2026",
                    attestation: "US FDA 21 CFR §11.50 Compliant",
                    timestamp: "2026-01-29T10:00:00Z",
                  },
                  null,
                  2
                )}
          </pre>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            onClick={closeBlockDrawer}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 cursor-pointer transition-colors border border-slate-200"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
