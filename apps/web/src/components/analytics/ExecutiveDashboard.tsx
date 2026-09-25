"use client";

import React from "react";
import { useApp } from "@/context/AppContext";

export const ExecutiveDashboard: React.FC = () => {
  const { showToast } = useApp();

  const protocols = [
    {
      id: "AIIA-GUD-2026",
      ctri: "CTRI/2026/04/091234",
      title: "Guduchi Ghanavati in Metabolic Dysregulation",
      pi: "Dr. V. Sharma (AIIA)",
      enrolled: "120 / 150 (80.0%)",
      status: "Active Enrolling",
      risk: "SAE Under Triage (DILI)",
      riskColor: "bg-[#ffdad6] text-[#ba1a1a]",
    },
    {
      id: "AIIA-ASH-2025",
      ctri: "CTRI/2025/08/074812",
      title: "Ashwagandha KSM-66 in Chronic Stress & Cognition",
      pi: "Dr. R. K. Saxena (NIMHANS)",
      enrolled: "184 / 200 (92.0%)",
      status: "Active Enrolling",
      risk: "Clean Safety Profile",
      riskColor: "bg-[#ecfdf5] text-[#059669]",
    },
    {
      id: "AIIA-GUG-2024",
      ctri: "CTRI/2024/11/061298",
      title: "Shuddha Guggulu in Secondary Hyperlipidemia",
      pi: "Dr. P. Manjunath (SDM Udupi)",
      enrolled: "80 / 120 (66.7%)",
      status: "Active Enrolling",
      risk: "Herb-Drug: Warfarin Interaction",
      riskColor: "bg-[#fffbeb] text-[#d97706]",
    },
    {
      id: "AIIA-CT-2024-14",
      ctri: "Pending CTRI Reg",
      title: "Brahmi Medhya Rasayana Phase IIa Comparative",
      pi: "Dr. K. S. Balachandran (AVS)",
      enrolled: "0 / 60 (0.0%)",
      status: "IEC Protocol Review",
      risk: "Pre-Clinical Safe",
      riskColor: "bg-neutral-100 text-neutral-600",
    },
  ];

  return (
    <div className="space-y-4">
      {/* Top Metric Bento Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
            Active Protocols
          </div>
          <div className="text-xl font-bold text-slate-900 font-mono mt-1">4 Studies</div>
          <div className="text-[10px] text-emerald-700 font-medium mt-1.5 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
            Across 3 National Sites
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
            Total Recruitment
          </div>
          <div className="text-xl font-bold text-slate-900 font-mono mt-1">
            384 / 600 <span className="text-xs text-slate-500 font-normal">(64.0%)</span>
          </div>
          <div className="text-[10px] text-emerald-700 font-medium mt-1.5 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
            Target Quota On-Track
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
            Safety Compliance
          </div>
          <div className="text-xl font-bold text-emerald-700 font-mono mt-1">97.8%</div>
          <div className="text-[10px] text-slate-500 mt-1.5">
            Statutory Threshold: &gt;= 95.0%
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
            Open SAE Investigations
          </div>
          <div className="text-xl font-bold text-rose-700 font-mono mt-1">1 Critical</div>
          <div className="text-[10px] text-rose-600 font-medium mt-1.5 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span>
            Patient AIIA-P089 (T-24h)
          </div>
        </div>
      </div>

      {/* Multi-Center Recruitment & DSMB Hepatic Safety Gauges */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recruitment Velocity by Site */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-sm text-emerald-600">
                domain
              </span>
              <h3 className="text-xs font-bold text-slate-900 tracking-tight">
                Multi-Center Enrollment Velocity Matrix
              </h3>
            </div>
            <span className="text-[10px] font-mono text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              Live Gateway Sync
            </span>
          </div>

          <div className="space-y-3.5">
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="font-semibold text-slate-800">
                  SITE-01: All India Institute of Ayurveda, New Delhi
                </span>
                <span className="font-mono font-bold text-emerald-700">176 / 200 (88.0%)</span>
              </div>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden p-0.5 border border-slate-200/60">
                <div
                  className="bg-gradient-to-r from-emerald-600 to-teal-500 h-full rounded-full"
                  style={{ width: "88%" }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="font-semibold text-slate-800">
                  SITE-02: IPGT&amp;RA, Gujarat Ayurved University, Jamnagar
                </span>
                <span className="font-mono font-bold text-emerald-700">148 / 200 (74.0%)</span>
              </div>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden p-0.5 border border-slate-200/60">
                <div
                  className="bg-gradient-to-r from-emerald-600 to-teal-500 h-full rounded-full"
                  style={{ width: "74%" }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="font-semibold text-slate-700">
                  SITE-03: Faculty of Ayurveda, BHU Varanasi
                </span>
                <span className="font-mono font-bold text-amber-700">60 / 200 (30.0%)</span>
              </div>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden p-0.5 border border-slate-200/60">
                <div
                  className="bg-gradient-to-r from-amber-500 to-amber-400 h-full rounded-full"
                  style={{ width: "30%" }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* DSMB Hepatic Safety Gauge & SPC Shewhart Anomaly Card */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-sm text-rose-600">
                monitor_heart
              </span>
              <h3 className="text-xs font-bold text-slate-900 tracking-tight">
                DSMB Hepatic Safety Gauge &amp; Shewhart SPC
              </h3>
            </div>
            <span className="text-[10px] font-mono text-rose-700 bg-rose-50 border border-rose-200 px-2.5 py-0.5 rounded-full font-bold">
              1 Active Outlier
            </span>
          </div>

          <div className="space-y-3 text-xs">
            {/* Outlier Incident Capsule */}
            <div className="flex items-center justify-between p-3 rounded-xl bg-rose-50/70 border border-rose-200 shadow-2xs">
              <div>
                <div className="font-bold text-rose-900 flex items-center gap-2">
                  <span>Subject AIIA-P089 (AIIA-GUD-2026)</span>
                  <span className="bg-rose-100 text-rose-800 text-[9px] font-mono px-2 py-0.5 rounded-full font-bold border border-rose-200">
                    Z-Score: +3.6σ
                  </span>
                </div>
                <div className="text-[11px] text-rose-700 mt-0.5">
                  ALT 165 U/L (3.6x ULN) • Guduchi + Aspirin bleeding risk
                </div>
              </div>
              <button
                onClick={() =>
                  showToast(
                    "Navigating to Patient AIIA-P089 Bedside Review Workspace",
                    "info"
                  )
                }
                className="px-3 py-1 bg-white hover:bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-[11px] font-bold cursor-pointer transition-colors shadow-2xs"
              >
                Inspect
              </button>
            </div>

            {/* Statistical Process Control Shewhart Anomaly Card */}
            <div className="p-3 bg-slate-50/80 rounded-xl border border-slate-200 text-[11px] text-slate-700 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800 font-mono uppercase tracking-wider text-[10px]">
                  Statistical Process Control (SPC) Shewhart Telemetry:
                </span>
                <span className="bg-emerald-50 text-emerald-800 font-mono text-[10px] px-2 py-0.5 rounded-full border border-emerald-200">
                  UCL = 3σ | LCL = -3σ
                </span>
              </div>
              <p className="leading-relaxed text-slate-600">
                Portfolio-wide transaminase distribution across 384 subjects remains within standard Shewhart limits (Mean ALT: 28.4 U/L, σ = 8.2). Subject AIIA-P089 is an isolated botanical-pharmaceutical CYP interaction event, ruling out systemic manufacturing contamination.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Master Protocol Registry Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 bg-slate-50/60 border-b border-slate-200/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-sm text-emerald-600">
              assignment
            </span>
            <h3 className="text-xs font-bold text-slate-900 tracking-tight">
              Master Institutional Protocol Registry
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-500">
            Displaying 4 Registered Clinical Protocols
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 border-b border-slate-200 text-[10px] uppercase font-mono tracking-wider">
                <th className="p-3">Protocol &amp; CTRI</th>
                <th className="p-3">Study Title</th>
                <th className="p-3">Principal Investigator</th>
                <th className="p-3">Enrolled</th>
                <th className="p-3">Safety Profile</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {protocols.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-3 font-mono">
                    <div className="font-bold text-slate-900">{p.id}</div>
                    <div className="text-[10px] text-slate-500">{p.ctri}</div>
                  </td>
                  <td className="p-3 font-medium text-slate-800">{p.title}</td>
                  <td className="p-3 text-slate-600">{p.pi}</td>
                  <td className="p-3 font-mono font-semibold text-slate-900">
                    {p.enrolled}
                  </td>
                  <td className="p-3">
                    <span
                      className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full font-semibold border ${
                        p.risk.includes("SAE")
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : p.risk.includes("Clean")
                          ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                          : "bg-amber-50 text-amber-800 border border-amber-200"
                      }`}
                    >
                      {p.risk}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className="bg-emerald-50 text-emerald-800 text-[10px] font-semibold px-2.5 py-0.5 rounded-full border border-emerald-200">
                      {p.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
