"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const AyuScribeVoice: React.FC = () => {
  const {
    dictationActive,
    currentLang,
    clinicalNotes,
    toggleVoiceDictation,
    setDictationLang,
    setClinicalNotes,
    appendClinicalNotes,
  } = useApp();

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
      {/* Header & Dialect Controls */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-center justify-center shadow-xs">
            <span className="material-symbols-outlined text-base">mic</span>
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-900 flex items-center gap-2">
              <span>AyuScribe Clinical Voice Dictation</span>
              <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 text-[9px] font-mono px-2 py-0.5 rounded-full font-bold">
                BILINGUAL AI
              </span>
            </h3>
            <p className="text-[10px] text-slate-500">
              Speech-to-text with Sanskrit/Hinglish clinical term recognition
            </p>
          </div>
        </div>

        {/* Dialect Switcher Segmented Capsule */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-full border border-slate-200 shadow-xs">
          <button
            onClick={() => setDictationLang("hi-IN")}
            className={`px-3 py-1 rounded-full text-[11px] font-semibold transition-all cursor-pointer ${
              currentLang === "hi-IN"
                ? "bg-white text-emerald-800 shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            हिंदी (hi-IN)
          </button>
          <button
            onClick={() => setDictationLang("en-IN")}
            className={`px-3 py-1 rounded-full text-[11px] font-semibold transition-all cursor-pointer ${
              currentLang === "en-IN"
                ? "bg-white text-emerald-800 shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            English (en-IN)
          </button>
        </div>
      </div>

      {/* Mic Trigger & Waveform */}
      <div className="flex items-center gap-3.5 bg-slate-50 p-3 rounded-xl border border-slate-200">
        <button
          onClick={toggleVoiceDictation}
          className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all cursor-pointer shadow-sm active:scale-95 ${
            dictationActive
              ? "bg-rose-600 text-white animate-pulse"
              : "bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs"
          }`}
        >
          <span className="material-symbols-outlined text-sm font-bold">
            {dictationActive ? "mic_off" : "mic"}
          </span>
          <span>{dictationActive ? "Stop Dictation" : "Record Voice Note"}</span>
        </button>

        {dictationActive ? (
          <div className="flex items-center gap-2 flex-1">
            <span className="text-xs text-emerald-800 font-semibold font-mono animate-pulse">
              Listening in {currentLang === "hi-IN" ? "Hindi/Sanskrit" : "English"}...
            </span>
            <div className="flex items-center gap-1.5 h-6 ml-2">
              <span className="w-1 bg-emerald-500 rounded-full animate-wave-1"></span>
              <span className="w-1 bg-emerald-500 rounded-full animate-wave-2"></span>
              <span className="w-1 bg-emerald-500 rounded-full animate-wave-3"></span>
              <span className="w-1 bg-emerald-500 rounded-full animate-wave-4"></span>
              <span className="w-1 bg-emerald-500 rounded-full animate-wave-5"></span>
            </div>
          </div>
        ) : (
          <div className="text-[11px] text-slate-500 italic">
            Click mic to dictate clinical notes in Hindi or English (auto-codes to MedDRA)
          </div>
        )}
      </div>

      {/* Clinical Notes Textarea */}
      <div>
        <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
          Transcribed Clinical Examination &amp; Notes
        </label>
        <textarea
          rows={3}
          value={clinicalNotes}
          onChange={(e) => setClinicalNotes(e.target.value)}
          className="w-full text-xs font-mono p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white"
          placeholder="Dictate or type clinical notes here..."
        />
      </div>

      {/* Quick Phrase Appenders & MedDRA Auto-Mapping Chips */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100 text-[10px]">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-semibold text-slate-500 uppercase tracking-wider">Quick Clinical Clues:</span>
          <button
            onClick={() =>
              appendClinicalNotes(
                " रोगी को नेत्र-पीतता और तीव्र अम्लपित्त (amlapitta) की शिकायत है।"
              )
            }
            className="px-2.5 py-1 bg-white hover:bg-slate-50 text-slate-700 rounded-full border border-slate-200 cursor-pointer transition-colors shadow-2xs font-medium"
          >
            + नेत्र-पीतता (Jaundice)
          </button>
          <button
            onClick={() =>
              appendClinicalNotes(
                " Acute right upper quadrant tenderness with elevated transaminases."
              )
            }
            className="px-2.5 py-1 bg-white hover:bg-slate-50 text-slate-700 rounded-full border border-slate-200 cursor-pointer transition-colors shadow-2xs font-medium"
          >
            + Hepatic Tenderness
          </button>
        </div>

        {/* MedDRA Preferred Term Frosted White Chip with Emerald Border */}
        <div className="flex items-center gap-1.5 text-emerald-800 font-mono font-semibold bg-white px-3 py-1 rounded-full border border-emerald-300 shadow-xs">
          <span className="material-symbols-outlined text-xs text-emerald-600 font-bold">check_circle</span>
          <span>MedDRA: Jaundice ocular (10023126)</span>
        </div>
      </div>
    </div>
  );
};

