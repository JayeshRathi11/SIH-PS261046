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
    <div className="bg-white p-4 rounded border border-[#bfc9c3]/60 shadow-xs space-y-3">
      {/* Header & Dialect Controls */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-[#064e3b] text-[#85f8c4] flex items-center justify-center">
            <span className="material-symbols-outlined text-sm">mic</span>
          </div>
          <div>
            <h3 className="text-xs font-bold text-[#003527] flex items-center gap-1.5">
              <span>AyuScribe Clinical Voice Dictation</span>
              <span className="bg-[#82f5c1] text-[#00714e] text-[9px] font-mono px-1.5 py-0.2 rounded font-bold">
                BILINGUAL AI
              </span>
            </h3>
            <p className="text-[10px] text-[#404944]">
              Speech-to-text with Sanskrit/Hinglish clinical term recognition
            </p>
          </div>
        </div>

        {/* Dialect Switcher */}
        <div className="flex items-center gap-1 bg-[#f2f3ff] p-0.5 rounded border border-[#bfc9c3]/40">
          <button
            onClick={() => setDictationLang("hi-IN")}
            className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
              currentLang === "hi-IN"
                ? "bg-white text-[#003527] shadow-xs"
                : "text-[#404944] hover:text-[#003527]"
            }`}
          >
            हिंदी (hi-IN)
          </button>
          <button
            onClick={() => setDictationLang("en-IN")}
            className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors cursor-pointer ${
              currentLang === "en-IN"
                ? "bg-white text-[#003527] shadow-xs"
                : "text-[#404944] hover:text-[#003527]"
            }`}
          >
            English (en-IN)
          </button>
        </div>
      </div>

      {/* Mic Trigger & Waveform */}
      <div className="flex items-center gap-3 bg-[#faf8ff] p-2.5 rounded border border-[#dae2fd]">
        <button
          onClick={toggleVoiceDictation}
          className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-1.5 text-white transition-all cursor-pointer shadow-sm ${
            dictationActive
              ? "bg-[#ba1a1a] animate-pulse"
              : "bg-[#006c4a] hover:bg-[#005137]"
          }`}
        >
          <span className="material-symbols-outlined text-sm">
            {dictationActive ? "mic_off" : "mic"}
          </span>
          <span>{dictationActive ? "Stop Dictation" : "Record Voice Note"}</span>
        </button>

        {dictationActive ? (
          <div className="flex items-center gap-1.5 flex-1">
            <span className="text-xs text-[#ba1a1a] font-medium font-mono animate-pulse">
              Listening in {currentLang === "hi-IN" ? "Hindi/Sanskrit" : "English"}...
            </span>
            <div className="flex items-center gap-1 h-5 ml-2">
              <span className="w-1 bg-[#ba1a1a] rounded-full animate-wave-1"></span>
              <span className="w-1 bg-[#ba1a1a] rounded-full animate-wave-2"></span>
              <span className="w-1 bg-[#ba1a1a] rounded-full animate-wave-3"></span>
              <span className="w-1 bg-[#ba1a1a] rounded-full animate-wave-4"></span>
              <span className="w-1 bg-[#ba1a1a] rounded-full animate-wave-5"></span>
            </div>
          </div>
        ) : (
          <div className="text-[11px] text-[#404944] italic">
            Click mic to dictate clinical notes in Hindi or English (auto-codes to MedDRA)
          </div>
        )}
      </div>

      {/* Clinical Notes Textarea */}
      <div>
        <label className="block text-[11px] font-semibold text-[#003527] mb-1">
          Transcribed Clinical Examination & Notes
        </label>
        <textarea
          rows={3}
          value={clinicalNotes}
          onChange={(e) => setClinicalNotes(e.target.value)}
          className="w-full text-xs font-mono p-2.5 bg-white border border-[#bfc9c3] rounded focus:ring-1 focus:ring-[#006c4a] focus:border-[#006c4a] text-[#131b2e]"
          placeholder="Dictate or type clinical notes here..."
        />
      </div>

      {/* Quick Phrase Appenders & MedDRA Auto-Mapping */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-[#bfc9c3]/30 text-[10px]">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="font-semibold text-[#404944]">Quick Clinical Clues:</span>
          <button
            onClick={() =>
              appendClinicalNotes(
                " रोगी को नेत्र-पीतता और तीव्र अम्लपित्त (amlapitta) की शिकायत है।"
              )
            }
            className="px-2 py-0.5 bg-[#f2f3ff] hover:bg-[#eaedff] text-[#003527] rounded border border-[#bfc9c3]/50 cursor-pointer"
          >
            + नेत्र-पीतता (Jaundice)
          </button>
          <button
            onClick={() =>
              appendClinicalNotes(
                " Acute right upper quadrant tenderness with elevated transaminases."
              )
            }
            className="px-2 py-0.5 bg-[#f2f3ff] hover:bg-[#eaedff] text-[#003527] rounded border border-[#bfc9c3]/50 cursor-pointer"
          >
            + Hepatic Tenderness
          </button>
        </div>

        <div className="flex items-center gap-1 text-[#006c4a] font-mono font-semibold bg-[#82f5c1]/30 px-2 py-0.5 rounded border border-[#82f5c1]">
          <span className="material-symbols-outlined text-xs">auto_awesome</span>
          <span>MedDRA: Jaundice ocular (10023126)</span>
        </div>
      </div>
    </div>
  );
};
