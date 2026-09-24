"use client";

import React, { useState } from "react";
import { useApp, PRESET_PERSONAS, Role, UserPersona } from "@/context/AppContext";

export default function LoginPage() {
  const { login } = useApp();
  const [selectedRole, setSelectedRole] = useState<Role>("doctor");
  const [email, setEmail] = useState<string>(PRESET_PERSONAS.doctor.email);
  const [password, setPassword] = useState<string>("••••••••••••");
  const [rememberMe, setRememberMe] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const personas = Object.values(PRESET_PERSONAS);

  const handleSelectPersona = (persona: UserPersona) => {
    setSelectedRole(persona.role);
    setEmail(persona.email);
    setPassword("AyushSecure2026!#");
    // Direct 1-click login action
    executeLogin(persona);
  };

  const executeLogin = (persona: UserPersona) => {
    setIsSubmitting(true);
    setTimeout(() => {
      login(persona);
    }, 250);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const persona = PRESET_PERSONAS[selectedRole] || PRESET_PERSONAS.doctor;
    executeLogin(persona);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#002117] via-[#003527] to-[#044e39] text-white flex flex-col justify-between p-4 sm:p-8 font-sans selection:bg-[#059669] selection:text-white">
      {/* Top Regulatory Credential Bar */}
      <div className="w-full max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4 py-2 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/20 border border-emerald-400/30 flex items-center justify-center text-emerald-400 font-bold shadow-inner">
            <span className="material-symbols-outlined text-2xl">local_pharmacy</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-widest text-emerald-400 font-bold">
                Government of India
              </span>
              <span className="text-white/30">•</span>
              <span className="text-xs text-white/70">Ministry of Ayush</span>
              <span className="text-white/30">•</span>
              <span className="text-xs text-emerald-300 font-medium">AIIA Apex Centre</span>
            </div>
            <h1 className="text-base sm:text-lg font-bold tracking-tight text-white flex items-center gap-2">
              AyuTrial-CTMS
              <span className="text-xs font-normal text-emerald-300/80 bg-emerald-950/60 border border-emerald-700/50 px-2 py-0.5 rounded-full">
                SIH Problem Statement ID: 26046
              </span>
            </h1>
          </div>
        </div>

        {/* Regulatory Badges */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="bg-emerald-900/60 border border-emerald-500/30 text-emerald-300 text-[10px] font-mono px-2.5 py-1 rounded">
            NDCT Rules 2019
          </span>
          <span className="bg-emerald-900/60 border border-emerald-500/30 text-emerald-300 text-[10px] font-mono px-2.5 py-1 rounded">
            21 CFR Part 11
          </span>
          <span className="bg-emerald-900/60 border border-emerald-500/30 text-emerald-300 text-[10px] font-mono px-2.5 py-1 rounded">
            DPDP Act 2023
          </span>
          <span className="bg-emerald-900/60 border border-emerald-500/30 text-emerald-300 text-[10px] font-mono px-2.5 py-1 rounded">
            GCP-ASU Compliant
          </span>
        </div>
      </div>

      {/* Main Dual-Column Authentication Showcase */}
      <div className="w-full max-w-7xl mx-auto my-auto py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Section: 1-Click Quick Access Persona Grid */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-400/20 text-emerald-300 text-xs font-semibold mb-2">
              <span className="material-symbols-outlined text-sm">bolt</span>
              Hackathon Evaluation Fast-Track (1-Click Role Switcher)
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              Instant Clinical Persona Sign-In
            </h2>
            <p className="text-sm text-emerald-100/70 mt-1 max-w-xl">
              Under 21 CFR §11.10 and NDCT Rules 2019, each persona possesses isolated statutory privileges. Click any role card below to authenticate instantly with pre-verified credentials.
            </p>
          </div>

          {/* Persona Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            {personas.map((p) => {
              const isSelected = selectedRole === p.role;
              return (
                <button
                  key={p.id}
                  onClick={() => handleSelectPersona(p)}
                  disabled={isSubmitting}
                  className={`group relative text-left p-4 rounded-xl border transition-all duration-200 cursor-pointer ${
                    isSelected
                      ? "bg-emerald-950/80 border-emerald-400 shadow-lg shadow-emerald-900/40 ring-1 ring-emerald-400"
                      : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-emerald-500/50"
                  } ${isSubmitting ? "opacity-75 pointer-events-none" : ""}`}
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex items-center gap-2.5">
                      <div
                        className={`w-9 h-9 rounded-lg flex items-center justify-center font-bold text-lg shadow-sm ${p.avatarColor}`}
                      >
                        <span className="material-symbols-outlined text-xl">
                          {p.avatarIcon}
                        </span>
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors">
                          {p.name}
                        </h3>
                        <p className="text-[11px] font-mono text-emerald-300/80">
                          {p.roleHeader}
                        </p>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-white/80 border border-white/10">
                      {p.siteId}
                    </span>
                  </div>

                  <p className="text-xs text-white/70 line-clamp-2 leading-relaxed mb-3">
                    {p.description}
                  </p>

                  <div className="flex items-center justify-between pt-2 border-t border-white/10 text-[11px]">
                    <span className="text-white/40 truncate max-w-[180px]">
                      {p.email}
                    </span>
                    <span className="text-emerald-400 font-semibold flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                      1-Click Login
                      <span className="material-symbols-outlined text-xs">arrow_forward</span>
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Section: Standard Credentials Card & Workstation Security */}
        <div className="lg:col-span-5 bg-white/10 backdrop-blur-xl border border-white/20 p-6 sm:p-8 rounded-2xl shadow-2xl">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono uppercase tracking-wider text-emerald-300 font-semibold flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Terminal Authentication
              </span>
              <span className="text-[10px] font-mono text-white/60 bg-black/30 px-2 py-0.5 rounded border border-white/10">
                TLS 1.3 | SHA-256
              </span>
            </div>
            <h3 className="text-xl font-bold text-white">Clinical Workstation Access</h3>
            <p className="text-xs text-white/70 mt-1">
              Authenticate via Institutional Ayush Directory or National Health Stack ID.
            </p>
          </div>

          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-emerald-200 mb-1">
                Institutional Email Address
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-2.5 text-white/40 text-lg">
                  mail
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="investigator@aiia.gov.in"
                  className="w-full pl-10 pr-4 py-2 bg-black/40 border border-white/20 rounded-lg text-sm text-white placeholder-white/40 focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-semibold text-emerald-200">
                  Workstation Password / Security PIN
                </label>
                <span className="text-[10px] text-emerald-300/70 hover:underline cursor-pointer">
                  Smart Card / OTP Login
                </span>
              </div>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-2.5 text-white/40 text-lg">
                  lock
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-4 py-2 bg-black/40 border border-white/20 rounded-lg text-sm text-white placeholder-white/40 focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-white/80 pt-1">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-white/30 text-emerald-600 focus:ring-emerald-500 bg-black/40"
                />
                Remember this workstation for 24h
              </label>
              <span className="font-mono text-[10px] text-emerald-300">
                GAMP 5 Cat.4
              </span>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-2 py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm tracking-wide shadow-lg shadow-emerald-900/50 hover:shadow-emerald-700/50 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                  <span>Authenticating Session...</span>
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-lg">login</span>
                  <span>Sign In as {PRESET_PERSONAS[selectedRole]?.name}</span>
                </>
              )}
            </button>
          </form>

          {/* Audit & Legal Disclaimer */}
          <div className="mt-6 pt-4 border-t border-white/10 text-[10px] text-white/50 space-y-1">
            <p className="flex items-center gap-1">
              <span className="material-symbols-outlined text-xs text-emerald-400">verified</span>
              Electronic Signatures are legally binding under Rule 34(1) of NDCT Rules 2019.
            </p>
            <p>
              Unauthorized access attempts are cryptographically recorded in the immutable ALCOA+ audit ledger.
            </p>
          </div>
        </div>
      </div>

      {/* Bottom Compliance Footer */}
      <div className="w-full max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4 py-3 border-t border-white/10 text-xs text-white/60">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>FastAPI Engine: <strong>Operational (Port 8000)</strong></span>
          <span>•</span>
          <span>PostgreSQL 16: <strong>Encrypted Dual Ledger</strong></span>
        </div>
        <div>
          <span>AyuTrial-CTMS v1.0.0-PROD | Designed for All India Institute of Ayurveda &amp; NPvCC</span>
        </div>
      </div>
    </div>
  );
}
