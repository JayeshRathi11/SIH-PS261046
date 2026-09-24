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
      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="bg-white p-3.5 rounded border border-[#bfc9c3]/60 shadow-xs">
          <div className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider">
            Active Protocols
          </div>
          <div className="text-xl font-bold text-[#003527] font-mono mt-0.5">4 Studies</div>
          <div className="text-[10px] text-[#006c4a] font-medium mt-1">
            Across 3 National Sites
          </div>
        </div>

        <div className="bg-white p-3.5 rounded border border-[#bfc9c3]/60 shadow-xs">
          <div className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider">
            Total Recruitment
          </div>
          <div className="text-xl font-bold text-[#003527] font-mono mt-0.5">
            384 / 600 <span className="text-xs text-neutral-500">(64.0%)</span>
          </div>
          <div className="text-[10px] text-[#006c4a] font-medium mt-1">
            Target Quota On-Track
          </div>
        </div>

        <div className="bg-white p-3.5 rounded border border-[#bfc9c3]/60 shadow-xs">
          <div className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider">
            Safety Compliance
          </div>
          <div className="text-xl font-bold text-[#006c4a] font-mono mt-0.5">97.8%</div>
          <div className="text-[10px] text-neutral-500 mt-1">
            Threshold: &gt;= 95.0%
          </div>
        </div>

        <div className="bg-white p-3.5 rounded border border-[#bfc9c3]/60 shadow-xs">
          <div className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider">
            Open SAE Investigations
          </div>
          <div className="text-xl font-bold text-[#ba1a1a] font-mono mt-0.5">1 Critical</div>
          <div className="text-[10px] text-[#ba1a1a] font-medium mt-1 animate-pulse">
            Patient AIIA-P089 (T-24h)
          </div>
        </div>
      </div>

      {/* Multi-Center Recruitment & DILI Incidence Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recruitment Progress by Site */}
        <div className="bg-white p-4 rounded border border-[#bfc9c3]/60 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-[#bfc9c3]/30 pb-2">
            <h3 className="text-xs font-bold text-[#003527] flex items-center gap-1.5">
              <span className="material-symbols-outlined text-sm text-[#006c4a]">
                domain
              </span>
              <span>Multi-Center Site Recruitment Matrix</span>
            </h3>
            <span className="text-[10px] font-mono text-neutral-500">Live Sync</span>
          </div>

          <div className="space-y-2.5">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-semibold text-[#003527]">
                  SITE-01: All India Institute of Ayurveda, New Delhi
                </span>
                <span className="font-mono font-bold text-neutral-800">176 / 200 (88.0%)</span>
              </div>
              <div className="w-full bg-neutral-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#006c4a] h-full rounded-full" style={{ width: "88%" }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-semibold text-[#003527]">
                  SITE-02: IPGT&amp;RA, Gujarat Ayurved University, Jamnagar
                </span>
                <span className="font-mono font-bold text-neutral-800">148 / 200 (74.0%)</span>
              </div>
              <div className="w-full bg-neutral-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#006c4a] h-full rounded-full" style={{ width: "74%" }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-semibold text-neutral-700">
                  SITE-03: Faculty of Ayurveda, BHU Varanasi
                </span>
                <span className="font-mono font-bold text-neutral-800">60 / 200 (30.0%)</span>
              </div>
              <div className="w-full bg-neutral-200 h-2 rounded-full overflow-hidden">
                <div className="bg-[#d97706] h-full rounded-full" style={{ width: "30%" }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* DSMB Hepatic Enzyme Safety Radar */}
        <div className="bg-white p-4 rounded border border-[#bfc9c3]/60 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-[#bfc9c3]/30 pb-2">
            <h3 className="text-xs font-bold text-[#003527] flex items-center gap-1.5">
              <span className="material-symbols-outlined text-sm text-[#ba1a1a]">
                monitor_heart
              </span>
              <span>DSMB Safety Telemetry &amp; DILI Outlier Monitoring</span>
            </h3>
            <span className="text-[10px] font-mono text-[#ba1a1a] bg-[#ffdad6] px-1.5 py-0.5 rounded font-bold">
              1 Active Deviation
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between p-2 rounded bg-[#ffdad6]/30 border border-[#ffdad6]">
              <div>
                <div className="font-bold text-[#ba1a1a]">
                  Subject AIIA-P089 (AIIA-GUD-2026)
                </div>
                <div className="text-[10px] text-[#93000a]">
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
                className="px-2 py-1 bg-white border border-[#ba1a1a] text-[#ba1a1a] rounded text-[11px] font-semibold cursor-pointer"
              >
                Inspect
              </button>
            </div>

            <div className="p-2.5 bg-[#faf8ff] rounded border border-[#dae2fd] text-[11px] text-[#404944] leading-relaxed">
              <strong>Statistical Process Control (SPC) Alert:</strong> Portfolio-wide
              ALT/AST mean across all 384 subjects remains within normal baseline range
              (Mean ALT: 28.4 U/L, σ = 8.2). Subject AIIA-P089 represents an isolated
              botanical-pharmaceutical drug interaction incident, not broad batch impurity.
            </div>
          </div>
        </div>
      </div>

      {/* Master Protocol Registry Table */}
      <div className="bg-white rounded border border-[#bfc9c3]/60 shadow-xs overflow-hidden">
        <div className="p-3 bg-[#faf8ff] border-b border-[#bfc9c3]/40 flex items-center justify-between">
          <h3 className="text-xs font-bold text-[#003527] flex items-center gap-1.5">
            <span className="material-symbols-outlined text-sm text-[#006c4a]">
              assignment
            </span>
            <span>Master Institutional Protocol Registry</span>
          </h3>
          <span className="text-[10px] font-mono text-neutral-500">
            Displaying 4 Registered Clinical Protocols
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#f2f3ff] text-[#404944] border-b border-[#bfc9c3]/40 text-[11px] font-bold">
                <th className="p-2.5">Protocol &amp; CTRI</th>
                <th className="p-2.5">Study Title</th>
                <th className="p-2.5">Principal Investigator</th>
                <th className="p-2.5">Enrolled</th>
                <th className="p-2.5">Safety Profile</th>
                <th className="p-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {protocols.map((p) => (
                <tr key={p.id} className="hover:bg-[#faf8ff] transition-colors">
                  <td className="p-2.5 font-mono">
                    <div className="font-bold text-[#003527]">{p.id}</div>
                    <div className="text-[10px] text-neutral-500">{p.ctri}</div>
                  </td>
                  <td className="p-2.5 font-medium text-neutral-800">{p.title}</td>
                  <td className="p-2.5 text-neutral-600">{p.pi}</td>
                  <td className="p-2.5 font-mono font-semibold text-neutral-800">
                    {p.enrolled}
                  </td>
                  <td className="p-2.5">
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${p.riskColor}`}
                    >
                      {p.risk}
                    </span>
                  </td>
                  <td className="p-2.5">
                    <span className="bg-[#ecfdf5] text-[#059669] text-[10px] font-semibold px-2 py-0.5 rounded border border-[#a7f3d0]">
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
