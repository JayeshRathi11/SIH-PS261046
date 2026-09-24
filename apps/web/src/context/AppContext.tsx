"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export type Role = "doctor" | "coordinator" | "npvcc" | "auditor";
export type Site = "SITE-01" | "SITE-02";
export type Tab =
  | "state_machine"
  | "ecrf_desk"
  | "npvcc_desk"
  | "alcoa_ledger"
  | "herb_drug"
  | "regulatory_export";

export interface ToastItem {
  id: string;
  message: string;
  type: "info" | "success" | "error";
}

interface AppContextType {
  currentRole: Role;
  currentSite: Site;
  activeTab: Tab;
  currentStep: number;
  isTampered: boolean;
  dictationActive: boolean;
  currentLang: "hi-IN" | "en-IN";
  clinicalNotes: string;
  ct16ModalOpen: boolean;
  sugamDispatched: boolean;
  sugamAckTime: string | null;
  slaCountdown: string;
  toasts: ToastItem[];
  activeBlockDrawer: number | null;
  changePersona: (role: Role) => void;
  switchSite: (site: Site) => void;
  switchTab: (tab: Tab) => void;
  runDemoStep: (step: number) => void;
  nextDemoStep: () => void;
  resetDemo: () => void;
  toggleTamperSimulation: () => void;
  toggleVoiceDictation: () => void;
  setDictationLang: (lang: "hi-IN" | "en-IN") => void;
  setClinicalNotes: React.Dispatch<React.SetStateAction<string>>;
  appendClinicalNotes: (phrase: string) => void;
  openCT16Modal: () => void;
  closeCT16Modal: () => void;
  dispatchToSugam: () => void;
  showToast: (message: string, type?: "info" | "success" | "error") => void;
  openBlockDrawer: (blockId: number) => void;
  closeBlockDrawer: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [currentRole, setCurrentRole] = useState<Role>("doctor");
  const [currentSite, setCurrentSite] = useState<Site>("SITE-01");
  const [activeTab, setActiveTab] = useState<Tab>("ecrf_desk");
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [isTampered, setIsTampered] = useState<boolean>(false);
  const [dictationActive, setDictationActive] = useState<boolean>(false);
  const [currentLang, setCurrentLang] = useState<"hi-IN" | "en-IN">("hi-IN");
  const [clinicalNotes, setClinicalNotes] = useState<string>(
    "Subject presented on Day 14 with scleral icterus (netra-peetata) and severe amlapitta after taking Guduchi 500mg BD concomitantly with Aspirin 75mg OD."
  );
  const [ct16ModalOpen, setCt16ModalOpen] = useState<boolean>(false);
  const [sugamDispatched, setSugamDispatched] = useState<boolean>(false);
  const [sugamAckTime, setSugamAckTime] = useState<string | null>(null);
  const [slaCountdown, setSlaCountdown] = useState<string>("23:58:41");
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [activeBlockDrawer, setActiveBlockDrawer] = useState<number | null>(
    null
  );

  // Live timer tick
  useEffect(() => {
    let secondsRemaining = 23 * 3600 + 58 * 60 + 41;
    const interval = setInterval(() => {
      if (secondsRemaining > 0) {
        secondsRemaining -= 1;
        const h = Math.floor(secondsRemaining / 3600);
        const m = Math.floor((secondsRemaining % 3600) / 60);
        const s = secondsRemaining % 60;
        setSlaCountdown(
          `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(
            s
          ).padStart(2, "0")}`
        );
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const showToast = (
    message: string,
    type: "info" | "success" | "error" = "info"
  ) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3800);
  };

  const changePersona = (role: Role) => {
    setCurrentRole(role);
    const roleToTab: Record<Role, Tab> = {
      doctor: "ecrf_desk",
      coordinator: "state_machine",
      npvcc: "npvcc_desk",
      auditor: "alcoa_ledger",
    };
    setActiveTab(roleToTab[role]);
    const labels: Record<Role, string> = {
      doctor: "Principal Investigator (PI)",
      coordinator: "Clinical Research Coordinator",
      npvcc: "NPvCC Medical Officer",
      auditor: "CDSCO Regulatory Auditor",
    };
    showToast(`Switched active persona: ${labels[role]}`);
  };

  const switchSite = (site: Site) => {
    setCurrentSite(site);
    const label =
      site === "SITE-01" ? "SITE-01: AIIA New Delhi" : "SITE-02: IPGT&RA Jamnagar";
    showToast(`Multi-center scope switched to: ${label}`);
  };

  const switchTab = (tab: Tab) => {
    setActiveTab(tab);
    const tabToRole: Record<Tab, Role> = {
      state_machine: "coordinator",
      ecrf_desk: "doctor",
      npvcc_desk: "npvcc",
      alcoa_ledger: "auditor",
      herb_drug: "doctor",
      regulatory_export: "auditor",
    };
    setCurrentRole(tabToRole[tab]);
  };

  const runDemoStep = (stepNum: number) => {
    setCurrentStep(stepNum);
    switch (stepNum) {
      case 1:
        changePersona("coordinator");
        showToast(
          "Step 1: Protocol CTRI/2026/04/091234 Cleared. Cohort Screen Active."
        );
        break;
      case 2:
        changePersona("doctor");
        showToast(
          "Step 2: Subject AIIA-P089 Incident flagged! Mandagni + ALT 165 U/L."
        );
        break;
      case 3:
        changePersona("npvcc");
        showToast(
          "Step 3: BioBERT MedDRA Classifier active! T-24h Statutory Clock running."
        );
        break;
      case 4:
        setCt16ModalOpen(true);
        showToast("Step 4: Statutory Form CT-16 compiled under NDCT Rules 2019.");
        break;
      case 5:
        changePersona("auditor");
        if (!isTampered) {
          setIsTampered(true);
        }
        showToast(
          "Step 5: ALCOA+ Cryptographic Merkle Tamper Test Engaged! Block #3 Ruptured."
        );
        break;
      case 6:
        setActiveTab("regulatory_export");
        showToast(
          "Step 6: CDISC SDTM v3.4 and ABDM FHIR R4 ready for global export."
        );
        break;
      default:
        break;
    }
  };

  const nextDemoStep = () => {
    const next = currentStep >= 6 ? 1 : currentStep + 1;
    runDemoStep(next);
  };

  const resetDemo = () => {
    setIsTampered(false);
    setSugamDispatched(false);
    setSugamAckTime(null);
    runDemoStep(1);
    showToast("Demo Showcase reset to Step 1.");
  };

  const toggleTamperSimulation = () => {
    const nextState = !isTampered;
    setIsTampered(nextState);
    if (nextState) {
      showToast(
        "⚠️ UNAUTHORIZED DATABASE UPDATE DETECTED! Merkle Chain Severed.",
        "error"
      );
    } else {
      showToast(
        "✅ Merkle chain restored. SHA-256 integrity re-verified.",
        "success"
      );
    }
  };

  const phrases = {
    "hi-IN": [
      " रोगी को नेत्र-पीतता और तीव्र वमन (vomiting) की शिकायत है। अग्निमांद्य और उदर शूल विद्यमान।",
      " रोगी के यकृत प्रदेश (Right Hypochondrium) में हल्का स्पर्श-असह्यत्व। जिह्वा पर साम लक्षण।",
      " Day 14 पर पित्त वृद्धि और दौर्बल्य स्पष्ट। तिक्त रस आहार दिया जा रहा है।",
    ],
    "en-IN": [
      " Subject reports scleral icterus, acute post-prandial nausea, and mild epigastric discomfort over past 48 hours.",
      " Physical palpation reveals mild right upper quadrant tenderness. Clear signs of Pitta vitiation with coated tongue.",
      " Liver transaminases monitored closely due to additive Guduchi and antiplatelet interaction.",
    ],
  };

  const toggleVoiceDictation = () => {
    if (!dictationActive) {
      setDictationActive(true);
      showToast(
        `🎙️ AyuScribe AI: Listening to Doctor's clinical observation in ${currentLang}...`
      );

      // Check W3C SpeechRecognition support
      if (typeof window !== "undefined") {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const win = window as any;
        const SpeechRec = win.SpeechRecognition || win.webkitSpeechRecognition;

        if (SpeechRec) {
          try {
            const recognition = new SpeechRec();
            recognition.lang = currentLang;
            recognition.continuous = false;
            recognition.interimResults = false;
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            recognition.onresult = (event: any) => {
              const transcript = event.results[0][0].transcript;
              appendClinicalNotes(" " + transcript);
              setDictationActive(false);
              showToast(
                "✓ Voice note transcribed via browser Web Speech API & mapped to MedDRA PT: Jaundice (10023126)"
              );
            };
            recognition.onerror = () => {
              fallbackSimulatedDictation();
            };
            recognition.start();
            return;
          } catch {
            fallbackSimulatedDictation();
            return;
          }
        }
      }
      fallbackSimulatedDictation();
    } else {
      setDictationActive(false);
      showToast("AyuScribe voice dictation stopped.");
    }
  };

  const fallbackSimulatedDictation = () => {
    setTimeout(() => {
      const list = phrases[currentLang];
      const randomPhrase = list[Math.floor(Math.random() * list.length)];
      appendClinicalNotes(randomPhrase);
      setDictationActive(false);
      showToast(
        `✓ Clinical audio transcribed in ${currentLang} & mapped to MedDRA PT: Jaundice ocular (10023126)`
      );
    }, 2200);
  };

  const appendClinicalNotes = (phrase: string) => {
    setClinicalNotes((prev) => prev + phrase);
  };

  const openCT16Modal = () => setCt16ModalOpen(true);
  const closeCT16Modal = () => setCt16ModalOpen(false);

  const dispatchToSugam = () => {
    setTimeout(() => {
      const now = new Date();
      const istTime = now.toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata" }) + " IST";
      setSugamDispatched(true);
      setSugamAckTime(istTime);
      showToast(
        "🚀 Form CT-16 successfully submitted to CDSCO SUGAM Gateway! Ack No: SUGAM-SAE-2026-9042.",
        "success"
      );
    }, 1500);
  };

  const openBlockDrawer = (blockId: number) => setActiveBlockDrawer(blockId);
  const closeBlockDrawer = () => setActiveBlockDrawer(null);

  return (
    <AppContext.Provider
      value={{
        currentRole,
        currentSite,
        activeTab,
        currentStep,
        isTampered,
        dictationActive,
        currentLang,
        clinicalNotes,
        ct16ModalOpen,
        sugamDispatched,
        sugamAckTime,
        slaCountdown,
        toasts,
        activeBlockDrawer,
        changePersona,
        switchSite,
        switchTab,
        runDemoStep,
        nextDemoStep,
        resetDemo,
        toggleTamperSimulation,
        toggleVoiceDictation,
        setDictationLang: setCurrentLang,
        setClinicalNotes,
        appendClinicalNotes,
        openCT16Modal,
        closeCT16Modal,
        dispatchToSugam,
        showToast,
        openBlockDrawer,
        closeBlockDrawer,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
};
