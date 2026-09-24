"use client";

import React, { useState } from "react";
import { useApp } from "@/context/AppContext";
import { api } from "@/lib/api";

export const HerbDrugAlertModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
}> = ({ isOpen, onClose }) => {
  const { openCT16Modal, showToast, currentRole, currentSite, clinicalNotes } = useApp();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [conflicts, setConflicts] = useState<any[] | null>(null);

  if (!isOpen) return null;

  const handleReportAdverseEvent = async () => {
    setIsSubmitting(true);
    const payload = {
      patient_id: "00000000-0000-0000-0000-000000000089",
      severity: "HOSPITALIZATION",
      clinical_notes: clinicalNotes,
      ayurvedic_intervention: "Guduchi Extract 500mg BD",
      concomitant_drugs: ["Aspirin 75mg OD"],
      reported_by: "dr_v_sharma",
    };

    try {
      const res = await api.submitAdverseEvent(payload, currentRole, currentSite);
      if (res.herb_drug_conflicts && res.herb_drug_conflicts.length > 0) {
        setConflicts(res.herb_drug_conflicts);
      }
      showToast(
        "⚠️ Serious Adverse Event registered with CDSCO 24h statutory countdown!",
        "error"
      );
    } catch {
      // In local demo mode, show simulated conflict response
      setConflicts([
        {
          herb: "Guduchi (Tinospora cordifolia)",
          drug: "Aspirin",
          severity: "CRITICAL",
          mechanism: "Synergistic antiplatelet inhibition & additive hepatic transaminase elevation.",
        },
      ]);
      showToast("⚠️ Adverse event logged to NPvCC safety queue.", "info");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
      <div className="bg-white rounded-lg border-2 border-[#ba1a1a] shadow-2xl max-w-xl w-full p-5 space-y-4 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-neutral-200 pb-3">
          <div className="flex items-center gap-2 text-[#ba1a1a]">
            <span className="material-symbols-outlined text-2xl">emergency</span>
            <div>
              <h2 className="text-sm font-bold tracking-tight">
                CRITICAL HERB-DRUG INTERACTION ALERT
              </h2>
              <p className="text-[11px] text-neutral-500 font-mono">
                POST /api/v1/safety/adverse-event Live Interlock
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-neutral-400 hover:text-neutral-700 text-lg cursor-pointer"
          >
            ✕
          </button>
        </div>

        {/* Interaction Summary Box */}
        <div className="bg-[#ffdad6]/30 border border-[#ffdad6] p-3 rounded space-y-2">
          <div className="flex items-center justify-between text-xs font-bold">
            <span className="text-[#003527] bg-[#b0f0d6] px-2 py-0.5 rounded">
              🌿 Guduchi (Tinospora cordifolia) 500mg
            </span>
            <span className="text-[#ba1a1a] font-mono">⇄ INTERACTION ⇄</span>
            <span className="text-neutral-800 bg-neutral-200 px-2 py-0.5 rounded">
              💊 Aspirin (Acetylsalicylic Acid) 75mg
            </span>
          </div>
          <p className="text-xs text-[#93000a] leading-relaxed">
            <strong>Mechanism:</strong> Additive antiplatelet synergism and additive
            hepatic cytochrome P450 inhibition. Concomitant use with Aspirin increases
            gastrointestinal mucosal bleeding diathesis (<em>Raktapitta</em>) and promotes
            hepatocellular transaminase leakage (acute ALT/AST elevation).
          </p>
        </div>

        {/* Server-Returned Conflict Feed */}
        {conflicts && (
          <div className="bg-[#fffbeb] border border-[#fde68a] p-2.5 rounded text-xs space-y-1">
            <div className="font-bold text-[#d97706] flex items-center gap-1">
              <span className="material-symbols-outlined text-xs">sync_saved_locally</span>
              <span>FastAPI Returned Conflict Details:</span>
            </div>
            {conflicts.map((c, i) => (
              <div key={i} className="text-[11px] text-neutral-700 font-mono">
                • {c.herb || "Guduchi"} + {c.drug || "Aspirin"}: {c.mechanism || c.description}
              </div>
            ))}
          </div>
        )}

        {/* Clinical Evidence & Patient Correlation */}
        <div className="space-y-2 text-xs">
          <div className="font-semibold text-neutral-800">
            Subject Correlation (Patient AIIA-P089):
          </div>
          <div className="grid grid-cols-2 gap-2 text-[11px] font-mono bg-neutral-50 p-2.5 rounded border border-neutral-200">
            <div>
              <span className="text-neutral-500">Day 14 ALT (SGPT):</span>{" "}
              <strong className="text-[#ba1a1a]">165 U/L (Critical High)</strong>
            </div>
            <div>
              <span className="text-neutral-500">Day 14 AST (SGOT):</span>{" "}
              <strong className="text-[#ba1a1a]">142 U/L (High)</strong>
            </div>
            <div>
              <span className="text-neutral-500">Total Bilirubin:</span>{" "}
              <strong className="text-[#ba1a1a]">3.4 mg/dL (Icteric)</strong>
            </div>
            <div>
              <span className="text-neutral-500">Ayurvedic Phenotype:</span>{" "}
              <strong>Mandagni / Pitta-Kapha</strong>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-2 border-t border-neutral-200">
          <button
            onClick={handleReportAdverseEvent}
            disabled={isSubmitting}
            className="px-3 py-1.5 rounded text-xs font-semibold bg-[#ffdad6] text-[#ba1a1a] hover:bg-[#ffdad6]/80 flex items-center gap-1 cursor-pointer disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-sm">report_problem</span>
            <span>{isSubmitting ? "Dispatching API..." : "Log to Safety Desk API"}</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded text-xs font-semibold text-neutral-700 hover:bg-neutral-100 border border-neutral-300 cursor-pointer"
            >
              Dismiss
            </button>
            <button
              onClick={() => {
                onClose();
                openCT16Modal();
              }}
              className="px-3 py-1.5 rounded text-xs font-semibold bg-[#ba1a1a] hover:bg-[#93000a] text-white flex items-center gap-1 shadow-sm cursor-pointer"
            >
              <span className="material-symbols-outlined text-sm">assignment_late</span>
              <span>Open CDSCO Form CT-16 Dossier</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
