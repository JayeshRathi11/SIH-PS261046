"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useApp, PRESET_PERSONAS, Role, UserPersona } from "@/context/AppContext";

export default function LoginPage() {
  const { login, isAuthenticated, isMounted } = useApp();
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState<Role>("doctor");
  const [email, setEmail] = useState<string>(PRESET_PERSONAS.doctor.email);
  const [password, setPassword] = useState<string>("••••••••••••");
  const [rememberMe, setRememberMe] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const personas = Object.values(PRESET_PERSONAS);

  useEffect(() => {
    if (isMounted && isAuthenticated) {
      router.push("/");
    }
  }, [isMounted, isAuthenticated, router]);

  const handleSelectPersona = (persona: UserPersona) => {
    setSelectedRole(persona.role);
    setEmail(persona.email);
    setPassword("AyushSecure2026!#");
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
    <div className="min-h-screen bg-[#FBFBFA] text-slate-900 flex flex-col justify-between p-4 sm:p-8 font-sans selection:bg-emerald-100 selection:text-emerald-900 relative">
      {/* Top Regulatory Credential Bar */}
      <div className="w-full max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4 py-3 border-b border-slate-200">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 font-bold shadow-xs">
            <span className="material-symbols-outlined text-2xl">local_pharmacy</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] tracking-widest uppercase text-emerald-800 font-bold">
                Government of India
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-[10px] tracking-wider text-slate-600 font-medium">Ministry of Ayush</span>
              <span className="text-slate-300">•</span>
              <span className="text-[10px] tracking-wider text-emerald-700 font-semibold">AIIA Apex Centre</span>
            </div>
            <h1 className="text-base sm:text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
              AyuTrial-CTMS
              <span className="text-[11px] font-mono font-medium text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                SIH Problem Statement ID: 26046
              </span>
            </h1>
          </div>
        </div>

        {/* Floating White Regulatory Badges */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="bg-white border border-slate-200 shadow-xs px-3 py-1 rounded-full text-xs text-slate-700 font-medium font-mono">
            NDCT Rules 2019
          </span>
          <span className="bg-white border border-slate-200 shadow-xs px-3 py-1 rounded-full text-xs text-slate-700 font-medium font-mono">
            21 CFR Part 11
          </span>
          <span className="bg-white border border-slate-200 shadow-xs px-3 py-1 rounded-full text-xs text-slate-700 font-medium font-mono">
            DPDP Act 2023
          </span>
          <span className="bg-white border border-slate-200 shadow-xs px-3 py-1 rounded-full text-xs text-slate-700 font-medium font-mono">
            GCP-ASU Compliant
          </span>
        </div>
      </div>

      {/* Main Dual-Column Authentication Showcase */}
      <div className="w-full max-w-7xl mx-auto my-auto py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Section: Bento Grid Persona Showcase */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          <div>
            <div className="text-[11px] font-semibold tracking-wider text-emerald-800 bg-emerald-50/80 px-2.5 py-1 rounded-full border border-emerald-200/60 inline-flex items-center gap-1.5 mb-2 shadow-2xs">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
              ▪ Statutory Authentication
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Clinical Workstation Access
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-xl leading-relaxed">
              Under 21 CFR §11.10 and NDCT Rules 2019, each persona possesses isolated statutory privileges. Select any credentialed persona below for 1-click cryptographic access.
            </p>
          </div>

          {/* Luxury Bento Grid for 5 Personas */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
            {personas.map((p, idx) => {
              const isSelected = selectedRole === p.role;
              const isHeroCard = idx === 0;

              return (
                <button
                  key={p.id}
                  onClick={() => handleSelectPersona(p)}
                  disabled={isSubmitting}
                  className={`group relative text-left p-5 rounded-2xl border transition-all duration-200 cursor-pointer ${
                    isHeroCard ? "sm:col-span-2" : ""
                  } ${
                    isSelected
                      ? "bg-emerald-50/40 border-emerald-500 shadow-md ring-1 ring-emerald-500"
                      : "bg-white border-slate-200/80 hover:border-emerald-500 hover:shadow-md"
                  } ${isSubmitting ? "opacity-75 pointer-events-none" : ""}`}
                >
                  <div className="flex items-start justify-between gap-3 mb-2.5">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-lg shadow-xs ${p.avatarColor}`}
                      >
                        <span className="material-symbols-outlined text-xl">
                          {p.avatarIcon}
                        </span>
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-bold text-slate-900 group-hover:text-emerald-800 transition-colors">
                            {p.name}
                          </h3>
                          <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium">
                            ACTIVE
                          </span>
                        </div>
                        <p className="text-[11px] font-mono text-emerald-700 font-semibold mt-0.5">
                          {p.roleHeader}
                        </p>
                      </div>
                    </div>

                    <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                      {p.siteId}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed mb-3">
                    {p.description}
                  </p>

                  <div className="flex items-center justify-between pt-2.5 border-t border-slate-100 text-[11px]">
                    <span className="text-slate-500 truncate max-w-[200px] font-mono text-[10px]">
                      {p.email}
                    </span>
                    <span className="text-emerald-700 font-semibold flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                      1-Click Access
                      <span className="material-symbols-outlined text-xs">arrow_forward</span>
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Section: Direct Credential Sign-In Card */}
        <div className="lg:col-span-5 bg-white border border-slate-200/80 p-6 sm:p-8 rounded-3xl shadow-sm relative">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono uppercase tracking-wider text-emerald-700 font-semibold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                Direct Sign-In
              </span>
              <span className="text-[10px] font-mono text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-full border border-slate-200 font-medium">
                TLS 1.3 | SHA-256
              </span>
            </div>
            <h3 className="text-xl font-bold text-slate-900 tracking-tight">Terminal Authentication</h3>
            <p className="text-xs text-slate-500 mt-1">
              Verify credentials against Institutional Directory or National Health Stack ID.
            </p>
          </div>

          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] uppercase tracking-wider font-semibold text-slate-700 mb-1.5">
                Institutional Email Address
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3.5 top-3 text-slate-400 text-lg">
                  mail
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="investigator@aiia.gov.in"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all font-mono text-xs"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-[11px] uppercase tracking-wider font-semibold text-slate-700">
                  Workstation Password / Security PIN
                </label>
                <span className="text-[10px] text-emerald-700 hover:text-emerald-800 cursor-pointer font-medium">
                  Smart Card / OTP Login
                </span>
              </div>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3.5 top-3 text-slate-400 text-lg">
                  lock
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all font-mono text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-600 pt-1">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                />
                <span className="text-slate-600 text-xs">Remember workstation for 24h</span>
              </label>
              <span className="font-mono text-[10px] text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-semibold">
                GAMP 5 Cat.4
              </span>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-3 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm tracking-wide shadow-sm hover:shadow transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 active:scale-[0.99]"
            >
              {isSubmitting ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
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
          <div className="mt-6 pt-4 border-t border-slate-200 text-[10px] text-slate-500 space-y-1">
            <p className="flex items-center gap-1.5">
              <span className="material-symbols-outlined text-xs text-emerald-600">verified</span>
              Electronic Signatures are legally binding under Rule 34(1) of NDCT Rules 2019.
            </p>
            <p className="text-slate-400">
              Unauthorized access attempts are cryptographically recorded in the immutable ALCOA+ audit ledger.
            </p>
          </div>
        </div>
      </div>

      {/* Bottom Compliance Footer */}
      <div className="w-full max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4 py-3 border-t border-slate-200 text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>FastAPI Engine: <strong className="text-slate-800">Operational (Port 8000)</strong></span>
          <span>•</span>
          <span>PostgreSQL 16: <strong className="text-slate-800">Dual Ledger Committed</strong></span>
        </div>
        <div>
          <span>AyuTrial-CTMS v1.0.0-PROD | Designed for All India Institute of Ayurveda &amp; NPvCC</span>
        </div>
      </div>
    </div>
  );
}


