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
    <div className="w-full px-4 sm:px-6">
      <div className="bg-white border border-slate-200 shadow-sm rounded-2xl p-3 my-3 flex flex-wrap items-center justify-between gap-3 text-slate-800">
        {/* Title & Badge */}
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 shadow-xs">
            <span className="material-symbols-outlined text-base">play_circle</span>
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <span className="tracking-tight uppercase">
                Judge Evaluation Dock
              </span>
              <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">
                6-STEP E2E
              </span>
            </div>
            <div className="text-[11px] text-slate-500">
              Statutory regulatory sequence step-by-step
            </div>
          </div>
        </div>

        {/* Stepper Buttons Strip - Floating Dock */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-1 max-w-full">
          {steps.map((s, idx) => {
            const isActive = currentStep === s.num;
            const isCompleted = currentStep > s.num;
            const padNum = String(s.num).padStart(2, "0");

            return (
              <React.Fragment key={s.num}>
                <button
                  onClick={() => runDemoStep(s.num)}
                  className={`flex items-center gap-2.5 px-3 py-1.5 rounded-xl text-left transition-all duration-150 shrink-0 cursor-pointer ${
                    isActive
                      ? "bg-emerald-50/80 border border-emerald-300 text-emerald-900 shadow-xs"
                      : isCompleted
                      ? "bg-slate-50 hover:bg-slate-100 border border-slate-200/80 text-slate-800"
                      : "bg-slate-50/50 hover:bg-slate-100 border border-slate-200/60 text-slate-600"
                  }`}
                >
                  {/* Circular Numbered Capsule */}
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono font-bold transition-all ${
                      isActive
                        ? "bg-emerald-600 text-white shadow-sm"
                        : isCompleted
                        ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                        : "bg-slate-100 text-slate-600 border border-slate-200"
                    }`}
                  >
                    {isCompleted ? (
                      <span className="material-symbols-outlined text-xs">check</span>
                    ) : (
                      padNum
                    )}
                  </div>

                  <div>
                    <div
                      className={`text-xs font-semibold leading-tight ${
                        isActive ? "text-emerald-900" : "text-slate-800"
                      }`}
                    >
                      {s.title.substring(3)}
                    </div>
                    <div className="text-[10px] text-slate-500 truncate max-w-[120px] font-mono">
                      {s.desc}
                    </div>
                  </div>
                </button>

                {/* Subtle hairline divider */}
                {idx < steps.length - 1 && (
                  <div className="hidden 2xl:block w-[1px] h-6 bg-slate-200" />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Stepper Actions */}
        <div className="flex items-center gap-2 shrink-0 ml-auto sm:ml-0">
          <button
            onClick={nextDemoStep}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-3.5 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-all active:scale-95 cursor-pointer"
          >
            <span>Next Step</span>
            <span className="material-symbols-outlined text-sm font-bold">arrow_forward</span>
          </button>
          <button
            onClick={resetDemo}
            className="bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 px-2.5 py-1.5 rounded-xl text-xs transition-colors cursor-pointer border border-slate-200"
            title="Reset to Step 1"
          >
            <span className="material-symbols-outlined text-sm">restart_alt</span>
          </button>
        </div>
      </div>
    </div>
  );
};

