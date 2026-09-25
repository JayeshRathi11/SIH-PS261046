"use client";

import React, { useEffect, useState } from "react";
import { useApp } from "@/context/AppContext";
import { WS_BASE_URL } from "@/lib/api";

export const StatutoryBanner: React.FC = () => {
  const { slaCountdown, openCT16Modal } = useApp();
  const [wsTime, setWsTime] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [slaStatus, setSlaStatus] = useState<string>("T-24h Mandatory Window");

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;

    const connectWs = () => {
      try {
        ws = new WebSocket(`${WS_BASE_URL}/sla-countdown`);

        ws.onopen = () => {
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.formatted_time) {
              setWsTime(data.formatted_time);
            } else if (typeof data.remaining_seconds === "number") {
              const sec = Math.max(0, Math.floor(data.remaining_seconds));
              const h = Math.floor(sec / 3600);
              const m = Math.floor((sec % 3600) / 60);
              const s = sec % 60;
              setWsTime(
                `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(
                  s
                ).padStart(2, "0")}`
              );
            }
            if (data.sla_status) {
              setSlaStatus(data.sla_status);
            }
          } catch {
            // ignore non-json ping
          }
        };

        ws.onerror = () => {
          setWsConnected(false);
        };

        ws.onclose = () => {
          setWsConnected(false);
          reconnectTimeout = setTimeout(connectWs, 5000);
        };
      } catch {
        setWsConnected(false);
      }
    };

    connectWs();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  const displayTime = wsTime || slaCountdown;

  return (
    <div className="w-full px-4 pt-2">
      <div className="bg-white/95 backdrop-blur-md border border-rose-200/90 shadow-sm rounded-full py-1.5 px-4 mx-auto max-w-6xl flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3 flex-wrap">
          {/* Pulsing Soft Rose Dot & Alert Pill */}
          <span className="inline-flex items-center gap-2 bg-rose-50 text-rose-700 border border-rose-200 px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
            </span>
            Active SAE: Patient AIIA-P089
          </span>

          {/* Monospace Countdown */}
          <span className="font-mono text-xs text-slate-600 flex items-center gap-2">
            <span className="font-sans text-slate-500 hidden sm:inline">CDSCO Statutory Clock:</span>
            <span className="font-mono text-sm font-semibold text-rose-700 bg-rose-50/80 px-2 py-0.5 rounded-md border border-rose-200/80 tracking-wider">
              {displayTime}
            </span>
            <span className="text-slate-500 text-[11px] hidden md:inline">remaining until Form CT-16 cutoff</span>
          </span>

          {/* Statutory NDCT Rule Pill */}
          <span className="text-slate-500 text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200/80 hidden lg:inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
            Rule 34(1) NDCT Rules 2019, Sch III
          </span>
        </div>

        <div className="flex items-center gap-3 ml-auto sm:ml-0">
          <div className="hidden sm:flex items-center gap-1.5 text-[10px] font-mono text-slate-500">
            <span
              className={`inline-block w-2 h-2 rounded-full ${
                wsConnected ? "bg-emerald-500" : "bg-amber-400"
              }`}
            ></span>
            <span className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-600 font-semibold border border-slate-200">
              {wsConnected ? "STREAM ACTIVE" : "LOCAL BACKUP"}
            </span>
          </div>

          <button
            onClick={openCT16Modal}
            className="bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <span className="material-symbols-outlined text-xs">file_download</span>
            <span>Download Form CT-16</span>
          </button>
        </div>
      </div>
    </div>
  );
};

