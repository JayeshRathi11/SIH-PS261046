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
    <div className="w-full bg-[#ba1a1a] text-white px-4 sm:px-6 py-1.5 flex flex-wrap items-center justify-between border-b border-white/20 z-50 text-xs shadow-sm">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="inline-flex items-center gap-1 bg-white text-[#ba1a1a] px-2 py-0.5 rounded text-[11px] tracking-wider uppercase font-bold animate-sae-pulse">
          <span className="material-symbols-outlined text-sm">emergency</span>
          Active SAE: Patient AIIA-P089
        </span>
        <span className="font-mono text-xs font-medium tracking-tight">
          CDSCO Statutory Clock:{" "}
          <strong className="font-bold underline tracking-wide">
            {displayTime}
          </strong>{" "}
          remaining until Form CT-16 cutoff
        </span>
        <span className="bg-white/20 text-white text-[10px] font-mono px-2 py-0.5 rounded border border-white/30 hidden md:inline-block">
          {slaStatus} (NDCT Rules 2019, Sch III)
        </span>
      </div>

      <div className="flex items-center gap-3 mt-1 sm:mt-0">
        <div className="flex items-center gap-1.5 text-[10px] font-mono opacity-90">
          <span
            className={`inline-block w-2 h-2 rounded-full ${
              wsConnected ? "bg-[#85f8c4] animate-ping" : "bg-yellow-400"
            }`}
          ></span>
          <span>
            {WS_BASE_URL}/sla-countdown [{wsConnected ? "ONLINE STREAM" : "LOCAL BACKUP"}]
          </span>
        </div>
        <button
          onClick={openCT16Modal}
          className="bg-white text-[#ba1a1a] hover:bg-neutral-100 px-2 py-0.5 rounded text-[11px] font-semibold transition-transform active:scale-95 flex items-center gap-1 shadow-sm cursor-pointer"
        >
          <span className="material-symbols-outlined text-sm">file_download</span>
          Download CDSCO Form CT-16
        </button>
      </div>
    </div>
  );
};
