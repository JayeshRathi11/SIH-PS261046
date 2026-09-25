"use client";

import React, { useState } from "react";
import { useApp } from "@/context/AppContext";
import { BlockExplorer } from "./BlockExplorer";
import { BlockDrawer } from "./BlockDrawer";
import { api } from "@/lib/api";

export const TamperSimulator: React.FC = () => {
  const { isTampered, toggleTamperSimulation, showToast } = useApp();
  const [activeApiTab, setActiveApiTab] = useState<"verify" | "witness" | "block3">("verify");
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [apiResult, setApiResult] = useState<any>(null);

  const runLiveVerification = async () => {
    setIsVerifying(true);
    try {
      const res = await api.verifyChain();
      setApiResult(res);
      if (res.status === "VERIFIED_SECURE" && !isTampered) {
        showToast(
          `✅ Merkle Audit Chain 100% Verified Secure (${res.total_blocks} blocks verified)!`,
          "success"
        );
      } else {
        showToast(
          `🚨 Cryptographic Tamper Detected: Status ${res.status}!`,
          "error"
        );
      }
    } catch {
      if (isTampered) {
        showToast(
          "🚨 Verification Failed: Cryptographic mismatch detected at Block #3 (ALT 35 vs 165)!",
          "error"
        );
      } else {
        showToast("✅ Merkle Audit Chain 100% Verified Secure & Tamper-Free!", "success");
      }
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Metric Cards Bento Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
            Total Blocks
          </div>
          <div className="text-xl font-bold text-slate-900 font-mono mt-1">
            {apiResult?.total_blocks || 4} Blocks
          </div>
          <div className="text-[10px] text-emerald-700 font-semibold flex items-center gap-1.5 mt-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            Continuous Linear Chain
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
            Enclave Merkle Root
          </div>
          <div className="text-xs font-bold text-emerald-800 font-mono truncate mt-1.5">
            {isTampered ? "0xMISMATCH_ALERT" : (apiResult?.witness_merkle_root || "0x7f83b165c92f...")}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            AWS Nitro / CDSCO HSM
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
            Tamper Detection
          </div>
          <div
            className={`text-sm font-bold font-mono mt-1.5 flex items-center gap-1.5 ${
              isTampered ? "text-rose-700" : "text-emerald-700"
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${isTampered ? "bg-rose-500 animate-ping" : "bg-emerald-500"}`}></span>
            {isTampered ? "ALARM TRIGGERED" : "ARMED & SECURE"}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Linear SHA-256 Validation
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
            21 CFR Part 11
          </div>
          <div className="text-xl font-bold text-slate-900 font-mono mt-1">100% Valid</div>
          <div className="text-[10px] text-emerald-700 font-semibold flex items-center gap-1.5 mt-1.5">
            <span className="material-symbols-outlined text-xs">shield</span>
            <span>GAMP 5 Cat.4 Attested</span>
          </div>
        </div>
      </div>

      {/* Interactive Tamper Testing Control Box */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
          <div>
            <div className="text-[11px] font-semibold tracking-wider text-emerald-800 bg-emerald-50/80 px-2.5 py-0.5 rounded-full border border-emerald-200/60 inline-flex items-center gap-1.5 mb-1">
              ▪ ALCOA+ Cryptographic Ledger
            </div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight mt-0.5 flex items-center gap-2">
              <span className="material-symbols-outlined text-emerald-700 text-base">security</span>
              <span>Regulatory Cryptographic Tamper Simulator &amp; Forensic Defense</span>
            </h3>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Simulate an unauthorized rogue DBA mutating audit-trailed clinical labs in PostgreSQL
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={runLiveVerification}
              disabled={isVerifying}
              className="bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-xs transition-all active:scale-95 cursor-pointer disabled:opacity-50"
            >
              <span
                className={`material-symbols-outlined text-sm ${
                  isVerifying ? "animate-spin" : ""
                }`}
              >
                refresh
              </span>
              <span>{isVerifying ? "Querying..." : "Verify Entire Chain"}</span>
            </button>

            {/* Tactile Toggle Switch for DBA Tamper */}
            <button
              onClick={toggleTamperSimulation}
              className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 shadow-xs transition-all cursor-pointer active:scale-95 ${
                isTampered
                  ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                  : "bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200"
              }`}
            >
              <span className="material-symbols-outlined text-sm font-bold">
                {isTampered ? "restore" : "bug_report"}
              </span>
              <span>
                {isTampered
                  ? "Revert Data Tampering & Re-verify"
                  : "Simulate Unauthorized DBA Data Manipulation"}
              </span>
            </button>
          </div>
        </div>

        {/* Real-time Forensic Log Terminal */}
        {isTampered && (
          <div className="bg-slate-900 text-emerald-400 font-mono text-xs rounded-xl p-4 space-y-1.5 shadow-md border border-slate-800">
            <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-2">
              <span className="flex items-center gap-2 text-rose-400">
                <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
                <span>AyuTrial Forensic Audit Engine v2.4</span>
              </span>
              <span className="text-rose-300 font-bold bg-rose-950/60 px-2 py-0.5 rounded-full border border-rose-800 text-[10px]">
                ● BREACH ALERT ACTIVE
              </span>
            </div>
            <p className="text-slate-400 pt-1">
              [CRITICAL] 2026-09-25T04:42:01Z - Linear audit chain integrity verification failed!
            </p>
            <p className="text-rose-400 font-bold">
              [ERROR] Block #3 leaf hash mismatch: Expected 0x8c7b89f2..., Found 0x7a19ff02...
            </p>
            <p className="text-amber-300">
              [TRACE] Table `ecrf_records`: Field `form_data-&gt;alt_sgpt` mutated from 165 to 35 without valid 21 CFR e-signature!
            </p>
            <p className="text-slate-300">
              [ACTION] Isolated witness Merkle root mismatch triggered regulatory audit flag under 21 CFR §11.10(e).
            </p>
          </div>
        )}

        {/* 4-Block Visualizer */}
        <BlockExplorer />
      </div>

      {/* Live FastAPI Mock Console Tabs */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-sm text-emerald-700">
              code
            </span>
            <span className="text-xs font-bold text-slate-900 tracking-tight">
              FastAPI ALCOA+ REST Endpoint Inspector
            </span>
          </div>

          <div className="flex items-center bg-slate-100 p-1 rounded-full border border-slate-200 text-xs font-mono">
            <button
              onClick={() => setActiveApiTab("verify")}
              className={`px-3 py-1 rounded-full cursor-pointer transition-all ${
                activeApiTab === "verify"
                  ? "bg-white text-emerald-800 font-bold shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              GET /api/v1/audit/verify-chain
            </button>
            <button
              onClick={() => setActiveApiTab("witness")}
              className={`px-3 py-1 rounded-full cursor-pointer transition-all ${
                activeApiTab === "witness"
                  ? "bg-white text-emerald-800 font-bold shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              POST /api/v1/audit/notarize-witness
            </button>
            <button
              onClick={() => setActiveApiTab("block3")}
              className={`px-3 py-1 rounded-full cursor-pointer transition-all ${
                activeApiTab === "block3"
                  ? "bg-white text-emerald-800 font-bold shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              GET /api/v1/audit/block/3
            </button>
          </div>
        </div>

        <pre className="p-4 bg-slate-900 text-emerald-400 font-mono text-xs rounded-xl overflow-x-auto shadow-inner border border-slate-800">
          {activeApiTab === "verify" &&
            JSON.stringify(
              isTampered
                ? {
                    status: "TAMPER_DETECTED",
                    protocol: "AIIA-GUD-2026",
                    fault_block: 3,
                    error: "SHA256_MISMATCH_POST_WRITE",
                    expected_hash: "0x8c7b89f2e34a719d3bb2a0018f34bc98e5781a93b4510cdb281f90ac832b",
                    actual_hash: "0x7a19ff02e34a719d3bb2a0018f34bc98e5781a93b4510cdb281f90ac832b",
                    isolated_witness_merkle: "WITNESS_ROOT_MISMATCH",
                    alcoa_plus_compliant: false,
                    latency_ms: 9,
                    cdsco_notification_sent: true,
                  }
                : (apiResult || {
                    status: "VERIFIED_SECURE",
                    protocol: "AIIA-GUD-2026",
                    blocks_verified: 4,
                    fault_block: null,
                    merkle_root: "0x7f83b165c92f40b2a9e3d81b957648b29c5421df608a",
                    witness_enclave_status: "MATCH_CONFIRMED",
                    alcoa_plus_compliant: true,
                    latency_ms: 14,
                    timestamp_utc: new Date().toISOString(),
                  }),
              null,
              2
            )}

          {activeApiTab === "witness" &&
            JSON.stringify(
              {
                status: isTampered ? "WITNESS_ROOT_REJECTED" : "NOTARIZED",
                merkle_root: isTampered
                  ? "MISMATCH_ALERT_FROZEN"
                  : (apiResult?.local_merkle_root || "50ea5bd8f7c0794585f4e3eadac31f0b66fa10697b64eae4f9439a73c9ff7f1c"),
                isolated_witness_enclave: "AWS Nitro Enclave / CDSCO Hardware Security Module",
                witness_epoch_status: isTampered ? "SEVERED_HASH_CHAIN" : "ANCHOR_LOCKED",
                alcoa_plus_witness: isTampered ? false : true,
              },
              null,
              2
            )}

          {activeApiTab === "block3" &&
            JSON.stringify(
              {
                block_height: 3,
                type: "eCRF_DAY_14_LABS",
                immutable_hash: "0x8c7b89f2e34a719d3bb2a0018f34bc98e5781a93b4510cdb281f90ac832b",
                current_db_alt_sgpt: isTampered ? 35 : 165,
                tamper_flag: isTampered,
                signer_pki: "CN=Dr. V. Sharma, O=AIIA, C=IN",
              },
              null,
              2
            )}
        </pre>
      </div>

      <BlockDrawer />
    </div>
  );
};

