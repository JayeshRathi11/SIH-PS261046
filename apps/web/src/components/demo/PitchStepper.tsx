"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const PitchStepper: React.FC = () => {
  const { currentStep, runDemoStep, nextDemoStep, resetDemo } = useApp();

  const steps = [
    {
      num: 1,
      title: "1. Protocol Clearance",
      desc: "CTRI Regex & Ethics Gate",
    },
    {
      num: 2,
      title: "2. eCRF Incident",
      desc: "P-089 ALT 165 + AyuScribe",
    },
    {
      num: 3,
      title: "3. MedDRA & SLA",
      desc: "BioBERT & T-24h Ticker",
    },
    {
      num: 4,
      title: "4. Form CT-16",
      desc: "CDSCO Expedited Dossier",
    },
    {
      num: 5,
      title: "5. Merkle Tamper",
      desc: "Simulate DBA Attack",
    },
    {
      num: 6,
      title: "6. Interop Export",
      desc: "CDISC SDTM & FHIR R4",
    },
  ];

  return (
    <div className="bg-[#003527] text-white px-4 sm:px-6 py-2.5 border-b border-[#064e3b] shadow-inner flex flex-wrap items-center justify-between gap-3">
      {/* Title & Badge */}
      <div className="flex items-center gap-2">
        <span className="material-symbols-outlined text-[#85f8c4] text-lg">
          play_circle
        </span>
        <div>
          <div className="text-xs font-bold text-white flex items-center gap-1.5">
            <span>HACKATHON JUDGE PITCH SHOWCASE</span>
            <span className="bg-[#85f8c4] text-[#002114] text-[9px] font-mono px-1.5 py-0.2 rounded font-bold">
              6-STEP E2E STORYLINE
            </span>
          </div>
          <div className="text-[10px] text-[#80bea6]">
            Click any step or use "Next Step" to advance the live regulatory demo
          </div>
        </div>
      </div>

      {/* Stepper Buttons Strip */}
      <div className="flex items-center gap-1.5 overflow-x-auto py-1 max-w-full">
        {steps.map((s) => {
          const isActive = currentStep === s.num;
          return (
            <button
              key={s.num}
              onClick={() => runDemoStep(s.num)}
              className={`px-2.5 py-1 rounded text-left transition-all shrink-0 cursor-pointer ${
                isActive
                  ? "bg-[#064e3b] border-2 border-[#85f8c4] shadow-md"
                  : "bg-white/10 hover:bg-white/20 border border-white/20"
              }`}
            >
              <div
                className={`text-[11px] font-bold ${
                  isActive ? "text-[#85f8c4]" : "text-white"
                }`}
              >
                {s.title}
              </div>
              <div className="text-[9px] text-[#80bea6] truncate max-w-[130px]">
                {s.desc}
              </div>
            </button>
          );
        })}
      </div>

      {/* Stepper Actions */}
      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={nextDemoStep}
          className="bg-[#006c4a] hover:bg-[#005137] text-white px-3 py-1 rounded text-xs font-semibold flex items-center gap-1 shadow-sm transition-transform active:scale-95 cursor-pointer"
        >
          <span>Next Step</span>
          <span className="material-symbols-outlined text-sm">arrow_forward</span>
        </button>
        <button
          onClick={resetDemo}
          className="bg-white/10 hover:bg-white/20 text-white/90 px-2 py-1 rounded text-xs transition-colors cursor-pointer"
          title="Reset to Step 1"
        >
          <span className="material-symbols-outlined text-sm">restart_alt</span>
        </button>
      </div>
    </div>
  );
};
