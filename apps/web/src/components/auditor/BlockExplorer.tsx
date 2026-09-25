"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const BlockExplorer: React.FC = () => {
  const { isTampered, openBlockDrawer } = useApp();

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
          <span className="material-symbols-outlined text-sm text-emerald-600">hub</span>
          <span>Linear SHA-256 Block Chain &amp; Merkle Trees</span>
        </h3>
        <span className="text-[10px] font-mono text-slate-500">
          Click any block to open forensic JSON inspector
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3 relative">
        {/* Block #1: Genesis */}
        <div
          onClick={() => openBlockDrawer(1)}
          className="p-4 bg-white hover:bg-slate-50/80 border border-slate-200 hover:border-emerald-300 rounded-2xl text-xs space-y-2.5 cursor-pointer transition-all duration-200 shadow-xs hover:shadow-sm group relative"
        >
          <div className="flex items-center justify-between">
            <span className="font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">
              Block #1: Genesis
            </span>
            <span className="text-[9px] font-mono text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full font-bold">
              VERIFIED
            </span>
          </div>
          <div className="text-[11px] text-slate-600">
            Protocol: <strong className="text-slate-900 font-mono">AIIA-GUD-2026</strong>
          </div>
          <div className="text-[10px] font-mono space-y-1">
            <div className="bg-slate-50 p-1.5 rounded-lg border border-slate-200 text-slate-500 truncate">
              Parent: 0x0000000000000000
            </div>
            <div className="bg-emerald-50/60 p-1.5 rounded-lg border border-emerald-200/80 text-emerald-800 truncate font-semibold">
              Hash: 0xa1b2c3d4e5f60718...
            </div>
          </div>
          <div className="text-[10px] text-emerald-700 font-semibold flex items-center gap-1.5 pt-2 border-t border-slate-100">
            <span className="material-symbols-outlined text-xs text-emerald-600">check_circle</span>
            <span>Genesis Protocol Root</span>
          </div>
        </div>

        {/* Block #2: Consent */}
        <div
          onClick={() => openBlockDrawer(2)}
          className="p-4 bg-white hover:bg-slate-50/80 border border-slate-200 hover:border-emerald-300 rounded-2xl text-xs space-y-2.5 cursor-pointer transition-all duration-200 shadow-xs hover:shadow-sm group relative"
        >
          <div className="flex items-center justify-between">
            <span className="font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">
              Block #2: Consent
            </span>
            <span className="text-[9px] font-mono text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full font-bold">
              VERIFIED
            </span>
          </div>
          <div className="text-[11px] text-slate-600">
            Subject: <strong className="text-slate-900 font-mono">AIIA-P089</strong> (DPDP §6)
          </div>
          <div className="text-[10px] font-mono space-y-1">
            <div className="bg-slate-50 p-1.5 rounded-lg border border-slate-200 text-slate-500 truncate">
              Parent: 0xa1b2c3d4...
            </div>
            <div className="bg-emerald-50/60 p-1.5 rounded-lg border border-emerald-200/80 text-emerald-800 truncate font-semibold">
              Hash: 0xb2c3d4e5f6071829...
            </div>
          </div>
          <div className="text-[10px] text-emerald-700 font-semibold flex items-center gap-1.5 pt-2 border-t border-slate-100">
            <span className="material-symbols-outlined text-xs text-emerald-600">check_circle</span>
            <span>Consent Chain Linked</span>
          </div>
        </div>

        {/* Block #3: Day 14 Labs (Dynamic Tamper Target) */}
        <div
          onClick={() => openBlockDrawer(3)}
          className={`p-4 rounded-2xl text-xs space-y-2.5 cursor-pointer transition-all duration-200 shadow-xs relative ${
            isTampered
              ? "bg-rose-50/40 border-2 border-rose-300 shadow-[0_4px_20px_rgba(244,63,94,0.12)]"
              : "bg-white hover:bg-slate-50/80 border border-slate-200 hover:border-emerald-300 hover:shadow-sm"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-bold text-slate-900">Block #3: Day 14 Labs</span>
            <span
              className={`text-[9px] font-mono px-2 py-0.5 rounded-full font-bold ${
                isTampered
                  ? "bg-rose-100 text-rose-700 border border-rose-200"
                  : "bg-emerald-50 text-emerald-800 border border-emerald-200"
              }`}
            >
              {isTampered ? "RUPTURED" : "VERIFIED"}
            </span>
          </div>
          <div className="text-[11px] text-slate-600">
            ALT:{" "}
            <strong
              className={
                isTampered ? "text-rose-700 font-mono underline" : "text-slate-900 font-mono"
              }
            >
              {isTampered ? "35 U/L (Tampered!)" : "165 U/L"}
            </strong>
          </div>
          <div className="text-[10px] font-mono space-y-1">
            <div className="bg-slate-50 p-1.5 rounded-lg border border-slate-200 text-slate-500 truncate">
              Parent: 0xb2c3d4e5...
            </div>
            <div
              className={`p-1.5 rounded-lg border truncate font-semibold ${
                isTampered
                  ? "bg-rose-100/70 border-rose-200 text-rose-700 font-bold"
                  : "bg-emerald-50/60 border-emerald-200/80 text-emerald-800"
              }`}
            >
              {isTampered
                ? "Hash: 0x7a19ff02... (CORRUPT)"
                : "Hash: 0x8c7b89f2e34a719d..."}
            </div>
          </div>
          <div
            className={`text-[10px] font-semibold flex items-center gap-1.5 pt-2 border-t ${
              isTampered
                ? "border-rose-200 text-rose-700"
                : "border-slate-100 text-emerald-700"
            }`}
          >
            <span className="material-symbols-outlined text-xs">
              {isTampered ? "cancel" : "check_circle"}
            </span>
            <span>
              {isTampered
                ? "SHA-256 Hash Broken!"
                : "Merkle Root Intact"}
            </span>
          </div>
        </div>

        {/* Block #4: SAE Escalation */}
        <div
          onClick={() => openBlockDrawer(4)}
          className={`p-4 rounded-2xl text-xs space-y-2.5 cursor-pointer transition-all duration-200 shadow-xs ${
            isTampered
              ? "bg-slate-50/60 border border-slate-200 opacity-70"
              : "bg-white hover:bg-slate-50/80 border border-slate-200 hover:border-emerald-300 hover:shadow-sm"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-bold text-slate-900">Block #4: SAE Escalation</span>
            <span
              className={`text-[9px] font-mono px-2 py-0.5 rounded-full font-bold ${
                isTampered
                  ? "bg-amber-50 text-amber-700 border border-amber-200"
                  : "bg-emerald-50 text-emerald-800 border border-emerald-200"
              }`}
            >
              {isTampered ? "ORPHANED" : "VERIFIED"}
            </span>
          </div>
          <div className="text-[11px] text-slate-600">
            Event: <strong className="text-slate-900 font-mono">Grade 3 DILI</strong>
          </div>
          <div className="text-[10px] font-mono space-y-1">
            <div
              className={`p-1.5 rounded-lg border truncate ${
                isTampered
                  ? "bg-rose-50 border-rose-200 text-rose-700 font-bold"
                  : "bg-slate-50 border-slate-200 text-slate-500"
              }`}
            >
              Parent: {isTampered ? "0x8c7b... (MISMATCH)" : "0x8c7b89f2..."}
            </div>
            <div className="bg-slate-50 p-1.5 rounded-lg border border-slate-200 text-slate-700 truncate font-semibold">
              Hash: 0xd931ab04f71a0988...
            </div>
          </div>
          <div
            className={`text-[10px] font-semibold flex items-center gap-1.5 pt-2 border-t ${
              isTampered
                ? "border-slate-200 text-slate-500"
                : "border-slate-100 text-emerald-700"
            }`}
          >
            <span className="material-symbols-outlined text-xs">
              {isTampered ? "link_off" : "check_circle"}
            </span>
            <span>
              {isTampered
                ? "Parent Pointer Severed"
                : "T-24h Timestamp Stamped"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
