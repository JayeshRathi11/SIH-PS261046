"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const BlockExplorer: React.FC = () => {
  const { isTampered, openBlockDrawer } = useApp();

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-[#003527] flex items-center gap-1.5">
          <span className="material-symbols-outlined text-sm">hub</span>
          <span>Linear SHA-256 Block Chain &amp; Merkle Trees</span>
        </h3>
        <span className="text-[10px] font-mono text-neutral-500">
          Click any block to open forensic JSON inspector
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
        {/* Block #1 */}
        <div
          onClick={() => openBlockDrawer(1)}
          className="p-3 bg-[#f2f3ff] hover:bg-[#eaedff] border border-[#dae2fd] rounded text-xs space-y-2 cursor-pointer transition-all shadow-xs"
        >
          <div className="flex items-center justify-between">
            <span className="font-bold text-[#003527]">Block #1: Genesis</span>
            <span className="text-[9px] font-mono text-[#006c4a] bg-white px-1.5 py-0.5 rounded font-bold">
              VERIFIED
            </span>
          </div>
          <div className="text-[11px] text-neutral-600">
            Protocol: <strong>AIIA-GUD-2026</strong>
          </div>
          <div className="text-[10px] font-mono text-neutral-500 space-y-0.5">
            <div>Parent: 0x0000000000000000</div>
            <div className="text-[#006c4a] truncate font-semibold">
              Hash: 0xa1b2c3d4e5f60718...
            </div>
          </div>
          <div className="text-[10px] text-[#006c4a] font-semibold flex items-center gap-1 pt-1 border-t border-[#dae2fd]">
            <span className="material-symbols-outlined text-xs">check_circle</span>
            Genesis Protocol Root
          </div>
        </div>

        {/* Block #2 */}
        <div
          onClick={() => openBlockDrawer(2)}
          className="p-3 bg-[#f2f3ff] hover:bg-[#eaedff] border border-[#dae2fd] rounded text-xs space-y-2 cursor-pointer transition-all shadow-xs"
        >
          <div className="flex items-center justify-between">
            <span className="font-bold text-[#003527]">Block #2: Consent</span>
            <span className="text-[9px] font-mono text-[#006c4a] bg-white px-1.5 py-0.5 rounded font-bold">
              VERIFIED
            </span>
          </div>
          <div className="text-[11px] text-neutral-600">
            Subject: <strong>AIIA-P089</strong> (DPDP §6)
          </div>
          <div className="text-[10px] font-mono text-neutral-500 space-y-0.5">
            <div className="truncate">Parent: 0xa1b2c3d4...</div>
            <div className="text-[#006c4a] truncate font-semibold">
              Hash: 0xb2c3d4e5f6071829...
            </div>
          </div>
          <div className="text-[10px] text-[#006c4a] font-semibold flex items-center gap-1 pt-1 border-t border-[#dae2fd]">
            <span className="material-symbols-outlined text-xs">check_circle</span>
            Consent Chain Linked
          </div>
        </div>

        {/* Block #3 (Dynamic Tamper Target) */}
        <div
          onClick={() => openBlockDrawer(3)}
          className={`p-3 rounded text-xs space-y-2 cursor-pointer transition-all shadow-xs ${
            isTampered
              ? "bg-[#ffdad6]/40 border-2 border-[#ba1a1a] animate-pulse"
              : "bg-[#f2f3ff] hover:bg-[#eaedff] border border-[#dae2fd]"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-bold text-[#003527]">Block #3: Day 14 Labs</span>
            <span
              className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-bold ${
                isTampered
                  ? "bg-[#ba1a1a] text-white"
                  : "bg-white text-[#006c4a]"
              }`}
            >
              {isTampered ? "RUPTURED" : "VERIFIED"}
            </span>
          </div>
          <div className="text-[11px]">
            ALT:{" "}
            <strong
              className={
                isTampered ? "text-[#ba1a1a] underline" : "text-neutral-800"
              }
            >
              {isTampered ? "35 U/L (Tampered!)" : "165 U/L"}
            </strong>
          </div>
          <div className="text-[10px] font-mono text-neutral-500 space-y-0.5">
            <div className="truncate">Parent: 0xb2c3d4e5...</div>
            <div
              className={`truncate font-semibold ${
                isTampered ? "text-[#ba1a1a]" : "text-[#006c4a]"
              }`}
            >
              {isTampered
                ? "Hash: 0x7a19ff02... (CORRUPT)"
                : "Hash: 0x8c7b89f2e34a719d..."}
            </div>
          </div>
          <div
            className={`text-[10px] font-semibold flex items-center gap-1 pt-1 border-t ${
              isTampered
                ? "border-[#ba1a1a]/40 text-[#ba1a1a]"
                : "border-[#dae2fd] text-[#006c4a]"
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

        {/* Block #4 */}
        <div
          onClick={() => openBlockDrawer(4)}
          className={`p-3 rounded text-xs space-y-2 cursor-pointer transition-all shadow-xs ${
            isTampered
              ? "bg-neutral-50 border border-neutral-300 opacity-90"
              : "bg-[#f2f3ff] hover:bg-[#eaedff] border border-[#dae2fd]"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-bold text-[#003527]">Block #4: SAE Escalation</span>
            <span
              className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-bold ${
                isTampered
                  ? "bg-neutral-200 text-neutral-600"
                  : "bg-white text-[#006c4a]"
              }`}
            >
              {isTampered ? "ORPHANED" : "VERIFIED"}
            </span>
          </div>
          <div className="text-[11px] text-neutral-600">
            Event: <strong>Grade 3 DILI</strong>
          </div>
          <div className="text-[10px] font-mono text-neutral-500 space-y-0.5">
            <div
              className={`truncate ${
                isTampered ? "text-[#ba1a1a] font-bold" : ""
              }`}
            >
              Parent: {isTampered ? "0x8c7b... (MISMATCH)" : "0x8c7b89f2..."}
            </div>
            <div className="text-neutral-700 truncate font-semibold">
              Hash: 0xd931ab04f71a0988...
            </div>
          </div>
          <div
            className={`text-[10px] font-semibold flex items-center gap-1 pt-1 border-t ${
              isTampered
                ? "border-neutral-300 text-neutral-600"
                : "border-[#dae2fd] text-[#006c4a]"
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
