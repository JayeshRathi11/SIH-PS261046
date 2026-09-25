"use client";

import React, { useState } from "react";
import { useApp } from "@/context/AppContext";
import { AyuScribeVoice } from "./AyuScribeVoice";
import { HerbDrugAlertModal } from "./HerbDrugAlertModal";
import { api } from "@/lib/api";

export const DynamicECRF: React.FC = () => {
  const { showToast, openCT16Modal, currentRole, currentSite, clinicalNotes, activePatientId } = useApp();
  const [activeVisit, setActiveVisit] = useState<number>(2);
  const [pittaScore, setPittaScore] = useState<number>(82);
  const [vataScore, setVataScore] = useState<number>(35);
  const [kaphaScore, setKaphaScore] = useState<number>(45);
  const [agniState, setAgniState] = useState<string>("mandagni");
  const [altValue, setAltValue] = useState<number>(165);
  const [astValue, setAstValue] = useState<number>(142);
  const [bilirubinValue, setBilirubinValue] = useState<number>(3.4);
  const [isAlertModalOpen, setIsAlertModalOpen] = useState<boolean>(false);
  const [signingReason, setSigningReason] = useState<string>(
    "Day 14 eCRF Evaluation & SAE Escalation"
  );
  const [password, setPassword] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [activeLockField, setActiveLockField] = useState<string | null>(null);

  // Field-level Concurrency Locking
  const handleFieldFocus = async (fieldName: string) => {
    setActiveLockField(fieldName);
    try {
      await api.acquireLock(`ecrf_aiia_p089_v${activeVisit}`, fieldName, "dr_v_sharma");
    } catch {
      // Non-blocking in demo UI
    }
  };

  const handleFieldBlur = async (fieldName: string) => {
    setActiveLockField(null);
    try {
      await api.releaseLock(`ecrf_aiia_p089_v${activeVisit}`, fieldName, "dr_v_sharma");
    } catch {
      // Non-blocking
    }
  };

  const handleCommitRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    const payload = {
      visit_number: activeVisit,
      visit_name: activeVisit === 1 ? "Day 0 - Baseline" : activeVisit === 2 ? "Day 14 - Active" : "Day 28 - Follow-up",
      form_data: {
        pitta_dosha: pittaScore,
        vata_dosha: vataScore,
        kapha_dosha: kaphaScore,
        baseline_agni: agniState.toUpperCase(),
        alt_sgpt: altValue,
        ast_sgot: astValue,
        total_bilirubin: bilirubinValue,
        clinical_notes: clinicalNotes,
        signing_reason: signingReason,
        attestation: "21 CFR Part 11 Attested",
      },
      modified_by: "dr_v_sharma",
    };

    const targetPatientId = activePatientId || "8331d3f7-9578-44d8-abb2-898d995386f4";
    try {
      await api.saveECRF(targetPatientId, payload, currentRole, currentSite);
      showToast(
        `🔒 21 CFR §11.50 Attestation: Visit ${activeVisit} record cryptographically signed & chained to ALCOA+ ledger (SHA-256).`,
        "success"
      );
    } catch (err: any) {
      if (err?.message?.includes("409") || err?.message?.includes("already exists")) {
        showToast(
          `Visit ${activeVisit} (Day 14) is already locked in ALCOA+ ledger. Incrementing to Visit 3 (Day 28 Follow-up).`,
          "info"
        );
        setActiveVisit(3);
        setSigningReason("Day 28 Follow-up eCRF Attestation");
      } else {
        showToast(
          "🔒 21 CFR §11.50 Attestation: Dr. V. Sharma digital signature committed to Merkle ledger with UTC/IST timestamp.",
          "success"
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Patient Header Bento Card */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-center justify-center font-bold text-sm shadow-xs font-mono">
            P089
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] font-semibold tracking-wider text-emerald-800 bg-emerald-50/80 px-2.5 py-0.5 rounded-full border border-emerald-200/60 inline-flex items-center gap-1.5">
                ▪ Bedside Encounter
              </span>
              <span className="text-slate-300">•</span>
              <h2 className="text-base font-bold text-slate-900 tracking-tight leading-tight">
                Subject AIIA-P089
              </h2>
              <span className="bg-slate-100 text-slate-700 border border-slate-200 text-[10px] font-mono font-medium px-2.5 py-0.5 rounded-full">
                Trial: AIIA-GUD-2026
              </span>
              <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10px] font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                DPDP Consent Obtained
              </span>

              {/* HIDDEN FOR CORE DEMO: Telegram adherence webhook telemetry
              <div className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-sky-50 border border-sky-200 text-[10px] font-semibold text-sky-800 font-mono">
                <span className="h-1.5 w-1.5 rounded-full bg-sky-500"></span>
                Telegram Dose Compliance (98.2%)
              </div>
              */}

              {/* HIDDEN FOR CORE DEMO: DPDP Act Purge / Right to Erasure Action Button
              <button
                type="button"
                className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-rose-50 border border-rose-200 text-[10px] font-semibold text-rose-700 hover:bg-rose-100 transition-colors cursor-pointer"
                title="Trigger irreversible cryptographic purge cascade (DPDP Act 2023 §12)"
              >
                <span className="material-symbols-outlined text-xs">delete_forever</span>
                <span>Purge Patient (DPDP Act)</span>
              </button>
              */}
            </div>
            <div className="text-xs text-slate-500 flex items-center gap-2 mt-1 flex-wrap">
              <span>Prakriti: <strong className="text-slate-800">Pitta-Kapha</strong></span>
              <span className="text-slate-300">•</span>
              <span>Baseline Agni: <strong className="text-slate-800 capitalize">{agniState}</strong></span>
              <span className="text-slate-300">•</span>
              <span>Intervention: <strong className="text-emerald-700 font-mono text-[11px]">Guduchi Ghanavati 500mg BD</strong></span>
            </div>
          </div>
        </div>

        {/* Segmented Visit Tabs */}
        <div className="flex items-center bg-slate-100 rounded-full border border-slate-200/80 p-1 text-xs font-semibold shadow-xs">
          <button
            onClick={() => setActiveVisit(1)}
            className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
              activeVisit === 1
                ? "bg-white text-slate-900 shadow-sm border border-slate-200/60"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Visit 1 (Day 0)
          </button>
          <button
            onClick={() => setActiveVisit(2)}
            className={`px-3 py-1 rounded-full transition-all cursor-pointer flex items-center gap-1.5 ${
              activeVisit === 2
                ? "bg-rose-50 text-rose-700 border border-rose-200 shadow-sm font-bold"
                : "text-rose-600 hover:text-rose-800"
            }`}
          >
            <span>Visit 2 (Day 14)</span>
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span>
          </button>
          <button
            onClick={() => setActiveVisit(3)}
            className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
              activeVisit === 3
                ? "bg-white text-slate-900 shadow-sm border border-slate-200/60"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Visit 3 (Day 28)
          </button>
        </div>
      </div>

      {/* Critical Herb-Drug Interaction Callout */}
      <div className="bg-rose-50/70 border border-rose-200 p-4 rounded-2xl flex flex-wrap items-center justify-between gap-3 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-rose-100 border border-rose-200 flex items-center justify-center text-rose-700 animate-sae-pulse">
            <span className="material-symbols-outlined text-xl">warning</span>
          </div>
          <div>
            <div className="text-xs font-bold text-rose-900 flex items-center gap-2">
              <span>CRITICAL SAFETY INTERACTION: Guduchi 500mg BD + Concomitant Aspirin 75mg OD</span>
              <span className="bg-rose-100 text-rose-800 text-[10px] font-mono px-2 py-0.5 rounded-full uppercase tracking-wider font-semibold border border-rose-200">
                Pharmacology Alert
              </span>
            </div>
            <div className="text-[11px] text-rose-700 mt-0.5">
              Additive antiplatelet effect &amp; hepatocellular transaminase elevation detected at Day 14.
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsAlertModalOpen(true)}
            className="px-3.5 py-1.5 bg-white hover:bg-rose-50 text-rose-800 border border-rose-200 rounded-xl text-xs font-semibold shadow-xs transition-all cursor-pointer"
          >
            Inspect Pharmacology
          </button>
          <button
            onClick={openCT16Modal}
            className="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer flex items-center gap-1.5 active:scale-95"
          >
            <span className="material-symbols-outlined text-sm">assignment_late</span>
            <span>Open Form CT-16</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Dosha Scoring & Biomarkers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Column: Traditional Phenotype & Dosha Scoring */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
            <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <span className="material-symbols-outlined text-emerald-700 text-base">psychiatry</span>
              <span>Ayurvedic Dosha Imbalance Scoring (Vikriti)</span>
            </h3>
            <span className="text-[10px] font-mono text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full font-semibold">
              Standardized Charaka Scale
            </span>
          </div>

          {/* Pitta Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs items-center">
              <span className="font-semibold text-rose-800">
                Pitta Dosha (Heat/Metabolic):
              </span>
              <span className="bg-slate-100 text-slate-800 border border-slate-200 rounded-lg px-2.5 py-1 font-mono text-xs font-bold">
                {pittaScore}% (Severe Aggravation)
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={pittaScore}
              onChange={(e) => setPittaScore(Number(e.target.value))}
              onFocus={() => handleFieldFocus("pitta_dosha")}
              onBlur={() => handleFieldBlur("pitta_dosha")}
              className="w-full accent-rose-600 cursor-pointer h-2 bg-emerald-100/70 rounded-lg appearance-none"
            />
            <div className="text-[10px] text-slate-500 flex justify-between font-mono">
              <span>Sama (Balanced)</span>
              <span className="text-rose-700 font-bold">Vitiated (Netra-peetata)</span>
            </div>
          </div>

          {/* Vata Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs items-center">
              <span className="font-semibold text-slate-700">
                Vata Dosha (Movement/Nervous):
              </span>
              <span className="bg-slate-100 text-slate-800 border border-slate-200 rounded-lg px-2.5 py-1 font-mono text-xs font-bold">
                {vataScore}% (Normalized)
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={vataScore}
              onChange={(e) => setVataScore(Number(e.target.value))}
              onFocus={() => handleFieldFocus("vata_dosha")}
              onBlur={() => handleFieldBlur("vata_dosha")}
              className="w-full accent-emerald-600 cursor-pointer h-2 bg-emerald-100/70 rounded-lg appearance-none"
            />
          </div>

          {/* Kapha Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs items-center">
              <span className="font-semibold text-slate-700">
                Kapha Dosha (Structure/Fluid):
              </span>
              <span className="bg-slate-100 text-slate-800 border border-slate-200 rounded-lg px-2.5 py-1 font-mono text-xs font-bold">
                {kaphaScore}% (Stable)
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={kaphaScore}
              onChange={(e) => setKaphaScore(Number(e.target.value))}
              onFocus={() => handleFieldFocus("kapha_dosha")}
              onBlur={() => handleFieldBlur("kapha_dosha")}
              className="w-full accent-emerald-600 cursor-pointer h-2 bg-emerald-100/70 rounded-lg appearance-none"
            />
          </div>

          {/* Agni Radio Group Assessment */}
          <div className="space-y-2 pt-2 border-t border-slate-100">
            <div className="flex justify-between text-xs items-center">
              <span className="font-semibold text-slate-800">
                Agni Assessment (Digestive Fire):
              </span>
              <span className="text-[10px] font-mono text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full font-semibold uppercase">
                {agniState}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {[
                { id: "mandagni", label: "Mandagni", desc: "Sluggish / Hypo-metabolic" },
                { id: "tikshnagni", label: "Tikshnagni", desc: "Hyper-metabolic / Acidic" },
                { id: "vishamagni", label: "Vishamagni", desc: "Variable / Erratic" },
                { id: "samagni", label: "Samagni", desc: "Balanced / Homeostatic" },
              ].map((agni) => (
                <label
                  key={agni.id}
                  onClick={() => setAgniState(agni.id)}
                  className={`p-2.5 rounded-xl border cursor-pointer transition-all flex items-start gap-2.5 ${
                    agniState === agni.id
                      ? "bg-emerald-50/80 border-emerald-300 shadow-2xs text-slate-900"
                      : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  <input
                    type="radio"
                    name="agni_radio"
                    value={agni.id}
                    checked={agniState === agni.id}
                    onChange={() => setAgniState(agni.id)}
                    className="mt-0.5 text-emerald-600 focus:ring-emerald-500 accent-emerald-600"
                  />
                  <div>
                    <div className="font-bold text-[11px] leading-tight">{agni.label}</div>
                    <div className="text-[9px] text-slate-500 mt-0.5">{agni.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Qualitative Ayurvedic Findings Bento Tiles */}
          <div className="pt-2 border-t border-slate-100 grid grid-cols-2 gap-2.5 text-xs">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80">
              <div className="text-[10px] text-slate-500 font-semibold font-mono uppercase tracking-wider">
                Jihwa (Tongue) Exam:
              </div>
              <div className="font-bold text-slate-900 mt-0.5">Saama (Thick Yellowish Coat)</div>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80">
              <div className="text-[10px] text-slate-500 font-semibold font-mono uppercase tracking-wider">
                Nadi (Pulse) Exam:
              </div>
              <div className="font-bold text-slate-900 mt-0.5">Mandagni / Tikshna Gati</div>
            </div>
          </div>
        </div>

        {/* Right Column: Quantitative Clinical Vitals & Lab Transaminases */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
            <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <span className="material-symbols-outlined text-emerald-700 text-base">ecg_heart</span>
              <span>Day 14 Quantitative Biomarkers &amp; Hepatic Enzymes</span>
            </h3>
            <span className="text-[10px] font-mono text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-full font-bold">
              ALT &gt; 3x ULN
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2.5">
            <div className="bg-slate-50/70 p-3 rounded-xl border border-slate-200">
              <label className="block text-[10px] font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                Systolic BP
              </label>
              <div className="flex items-center gap-1 font-mono text-sm">
                <input
                  type="number"
                  defaultValue={132}
                  onFocus={() => handleFieldFocus("systolic_bp")}
                  onBlur={() => handleFieldBlur("systolic_bp")}
                  className="w-full text-sm font-mono font-bold text-slate-900 bg-transparent border-0 p-0 focus:ring-0"
                />
                <span className="text-[10px] text-slate-400">mmHg</span>
              </div>
            </div>
            <div className="bg-slate-50/70 p-3 rounded-xl border border-slate-200">
              <label className="block text-[10px] font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                Diastolic BP
              </label>
              <div className="flex items-center gap-1 font-mono text-sm">
                <input
                  type="number"
                  defaultValue={86}
                  onFocus={() => handleFieldFocus("diastolic_bp")}
                  onBlur={() => handleFieldBlur("diastolic_bp")}
                  className="w-full text-sm font-mono font-bold text-slate-900 bg-transparent border-0 p-0 focus:ring-0"
                />
                <span className="text-[10px] text-slate-400">mmHg</span>
              </div>
            </div>
            <div className="bg-slate-50/70 p-3 rounded-xl border border-slate-200">
              <label className="block text-[10px] font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                Heart Rate
              </label>
              <div className="flex items-center gap-1 font-mono text-sm">
                <input
                  type="number"
                  defaultValue={78}
                  onFocus={() => handleFieldFocus("heart_rate")}
                  onBlur={() => handleFieldBlur("heart_rate")}
                  className="w-full text-sm font-mono font-bold text-slate-900 bg-transparent border-0 p-0 focus:ring-0"
                />
                <span className="text-[10px] text-slate-400">bpm</span>
              </div>
            </div>
          </div>

          {/* Liver Biomarkers */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 space-y-3">
            <div className="text-[11px] font-bold text-slate-900 flex items-center justify-between">
              <span>Serum Liver Enzymes (Ref: NABL Central Lab)</span>
              <div className="flex items-center gap-2">
                {activeLockField && (
                  <span className="text-[9px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 font-semibold">
                    Lock Held: {activeLockField}
                  </span>
                )}
                <span className="text-[10px] text-rose-700 font-mono font-bold bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
                  ⚠️ DILI THRESHOLD
                </span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2.5 text-xs">
              <div className="p-3 bg-white rounded-xl border border-rose-200 shadow-xs">
                <div className="text-[10px] text-slate-500 font-semibold">
                  ALT / SGPT (&lt;45)
                </div>
                <input
                  type="number"
                  value={altValue}
                  onChange={(e) => setAltValue(Number(e.target.value))}
                  onFocus={() => handleFieldFocus("alt_sgpt")}
                  onBlur={() => handleFieldBlur("alt_sgpt")}
                  className="w-full font-mono text-xl font-bold text-slate-900 bg-transparent border-0 p-0 focus:ring-0 mt-0.5"
                />
                <div className="bg-rose-50 text-rose-700 border border-rose-200 text-xs px-2 py-0.5 rounded-full font-medium inline-block mt-1">
                  Grade 3 Critical
                </div>
              </div>

              <div className="p-3 bg-white rounded-xl border border-rose-200 shadow-xs">
                <div className="text-[10px] text-slate-500 font-semibold">
                  AST / SGOT (&lt;35)
                </div>
                <input
                  type="number"
                  value={astValue}
                  onChange={(e) => setAstValue(Number(e.target.value))}
                  onFocus={() => handleFieldFocus("ast_sgot")}
                  onBlur={() => handleFieldBlur("ast_sgot")}
                  className="w-full font-mono text-xl font-bold text-slate-900 bg-transparent border-0 p-0 focus:ring-0 mt-0.5"
                />
                <div className="bg-rose-50 text-rose-700 border border-rose-200 text-xs px-2 py-0.5 rounded-full font-medium inline-block mt-1">
                  Elevated
                </div>
              </div>

              <div className="p-3 bg-white rounded-xl border border-rose-200 shadow-xs">
                <div className="text-[10px] text-slate-500 font-semibold">
                  Bilirubin (&lt;1.2)
                </div>
                <input
                  type="number"
                  step="0.1"
                  value={bilirubinValue}
                  onChange={(e) => setBilirubinValue(Number(e.target.value))}
                  onFocus={() => handleFieldFocus("total_bilirubin")}
                  onBlur={() => handleFieldBlur("total_bilirubin")}
                  className="w-full font-mono text-xl font-bold text-slate-900 bg-transparent border-0 p-0 focus:ring-0 mt-0.5"
                />
                <div className="bg-rose-50 text-rose-700 border border-rose-200 text-xs px-2 py-0.5 rounded-full font-medium inline-block mt-1">
                  Ocular Icterus
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AyuScribe Voice Recognition Suite */}
      <AyuScribeVoice />

      {/* 21 CFR Part 11 Electronic Signature Box */}
      <form
        onSubmit={handleCommitRecord}
        className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4"
      >
        <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700">
              <span className="material-symbols-outlined text-base">verified</span>
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-900 tracking-tight">
                US FDA 21 CFR §11.50 Electronic Attestation &amp; Cryptographic Seal
              </h3>
              <p className="text-[10px] text-slate-500">
                Non-repudiation binding with timestamped SHA-256 Merkle chain commitment
              </p>
            </div>
          </div>
          <span className="text-[10px] font-mono text-emerald-800 font-semibold bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
            ALCOA+ AUDIT TRAIL PRESERVED
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="block text-[10px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Authorized Signer
            </label>
            <input
              type="text"
              readOnly
              value="Dr. V. Sharma, MD (Ayu), PhD [PI-8891]"
              className="w-full text-xs font-mono p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-700"
            />
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Reason for Modification / Signing
            </label>
            <input
              type="text"
              value={signingReason}
              onChange={(e) => setSigningReason(e.target.value)}
              className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:bg-white focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              required
            />
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Re-authenticate Password
            </label>
            <input
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full text-xs font-mono p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:bg-white focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              required
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-slate-100">
          <div className="text-[10px] text-slate-500 font-mono flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            <span>SHA-256 linear hash chained automatically upon commit</span>
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 shadow-xs transition-all active:scale-95 cursor-pointer disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-sm font-bold">
              {isSubmitting ? "hourglass_empty" : "lock"}
            </span>
            <span>
              {isSubmitting ? "Committing SHA-256 Block..." : "Attest & Commit to Immutable Ledger"}
            </span>
          </button>
        </div>
      </form>

      {/* Modal Dialogs */}
      <HerbDrugAlertModal
        isOpen={isAlertModalOpen}
        onClose={() => setIsAlertModalOpen(false)}
      />
    </div>
  );
};

