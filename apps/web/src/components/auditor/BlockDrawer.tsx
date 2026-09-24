"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const BlockDrawer: React.FC = () => {
  const { activeBlockDrawer, closeBlockDrawer, isTampered } = useApp();

  if (activeBlockDrawer === null) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs">
      <div className="bg-white w-full max-w-md h-full shadow-2xl p-5 overflow-y-auto space-y-4 border-l border-neutral-300 animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="flex items-center justify-between border-b border-neutral-200 pb-3">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[#006c4a] text-xl">
              fingerprint
            </span>
            <div>
              <h2 className="text-sm font-bold text-[#003527]">
                Forensic Block Inspector #{activeBlockDrawer}
              </h2>
              <div className="text-[10px] font-mono text-neutral-500">
                21 CFR Part 11 Electronic Record Detail
              </div>
            </div>
          </div>
          <button
            onClick={closeBlockDrawer}
            className="text-neutral-400 hover:text-neutral-700 text-lg cursor-pointer"
          >
            ✕
          </button>
        </div>

        {/* Block Integrity Badge */}
        {activeBlockDrawer === 3 && isTampered ? (
          <div className="p-3 bg-[#ffdad6]/40 border-2 border-[#ba1a1a] rounded text-xs space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-[#ba1a1a]">
              <span className="material-symbols-outlined text-base">cancel</span>
              <span>SHA-256 HASH COMPROMISED (TAMPERED)</span>
            </div>
            <p className="text-[11px] text-[#93000a]">
              The ALT transaminase field was modified directly in the database table from
              165 U/L to 35 U/L. The recomputed leaf hash fails the isolated Merkle witness proof!
            </p>
          </div>
        ) : (
          <div className="p-2.5 bg-[#ecfdf5] border border-[#059669] rounded text-xs flex items-center justify-between">
            <div className="flex items-center gap-1.5 font-bold text-[#064e3b]">
              <span className="material-symbols-outlined text-base text-[#059669]">
                check_circle
              </span>
              <span>Cryptographic Integrity Valid</span>
            </div>
            <span className="text-[10px] font-mono bg-white px-2 py-0.5 rounded border border-[#059669] font-bold text-[#059669]">
              ALCOA+ VERIFIED
            </span>
          </div>
        )}

        {/* Metadata Grid */}
        <div className="space-y-2 text-xs">
          <div className="font-semibold text-neutral-700">Block Header Attributes:</div>
          <div className="bg-neutral-50 p-3 rounded border border-neutral-200 space-y-1.5 font-mono text-[11px]">
            <div>
              <span className="text-neutral-500">Height:</span>{" "}
              <strong>#{activeBlockDrawer}</strong>
            </div>
            <div>
              <span className="text-neutral-500">Timestamp:</span>{" "}
              <span>2026-01-29T14:30:00.000Z</span>
            </div>
            <div>
              <span className="text-neutral-500">Signer Identity:</span>{" "}
              <strong className="text-[#003527]">
                CN=Dr. V. Sharma, O=AIIA, C=IN
              </strong>
            </div>
            <div>
              <span className="text-neutral-500">Merkle Path:</span>{" "}
              <strong className={activeBlockDrawer === 3 && isTampered ? "text-[#ba1a1a]" : "text-[#059669]"}>
                {activeBlockDrawer === 3 && isTampered ? "BROKEN (Mismatch at Node #3)" : "Valid [L -> R -> Root]"}
              </strong>
            </div>
          </div>
        </div>

        {/* Raw Payload JSON */}
        <div className="space-y-1.5">
          <div className="font-semibold text-neutral-700 text-xs flex justify-between">
            <span>Raw Database Payload (JSON):</span>
            {activeBlockDrawer === 3 && isTampered && (
              <span className="text-[10px] text-[#ba1a1a] font-mono font-bold">
                ⚠️ MUTATED BY DBA
              </span>
            )}
          </div>
          <pre
            className={`p-3 rounded text-[11px] font-mono overflow-x-auto border ${
              activeBlockDrawer === 3 && isTampered
                ? "bg-[#ffdad6]/20 border-[#ba1a1a] text-[#93000a]"
                : "bg-neutral-900 border-neutral-800 text-neutral-200"
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
        <div className="pt-3 border-t border-neutral-200 flex justify-end">
          <button
            onClick={closeBlockDrawer}
            className="px-3 py-1.5 rounded text-xs font-semibold bg-neutral-200 hover:bg-neutral-300 text-neutral-800 cursor-pointer"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
