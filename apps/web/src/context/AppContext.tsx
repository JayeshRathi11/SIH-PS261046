"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export type Role = "doctor" | "coordinator" | "npvcc" | "auditor" | "admin";
export type Site = "SITE-01" | "SITE-02";
export type Tab =
  | "state_machine"
  | "ecrf_desk"
  | "npvcc_desk"
  | "alcoa_ledger"
  | "herb_drug"
  | "regulatory_export"
  | "analytics";

export interface ToastItem {
  id: string;
  message: string;
  type: "info" | "success" | "error";
}

export interface UserPersona {
  id: string;
  name: string;
  title: string;
  email: string;
  role: Role;
  roleHeader: string;
  siteId: Site;
  siteLabel: string;
  description: string;
  token: string;
  avatarColor: string;
  avatarIcon: string;
}

export const PRESET_PERSONAS: Record<Role, UserPersona> = {
  doctor: {
    id: "USER-PI-01",
    name: "Dr. Jayesh Rathi",
    title: "Principal Investigator (PI / Doctor)",
    email: "dr.jayesh.rathi@aiia.gov.in",
    role: "doctor",
    roleHeader: "DOCTOR",
    siteId: "SITE-01",
    siteLabel: "SITE-01 (AIIA New Delhi Apex Centre)",
    description: "Bedside eCRF, AyuScribe Voice AI, Herb-Drug Adverse Reporting",
    token: "mock-jwt-bearer-dr-jayesh-rathi-2026",
    avatarColor: "bg-[#064e3b] text-[#85f8c4]",
    avatarIcon: "stethoscope",
  },
  coordinator: {
    id: "USER-CRC-01",
    name: "Priya Sharma, MSc",
    title: "Clinical Research Coordinator (CRC)",
    email: "priya.sharma@aiia.gov.in",
    role: "coordinator",
    roleHeader: "CLINICAL_RESEARCH_COORDINATOR",
    siteId: "SITE-01",
    siteLabel: "SITE-01 (AIIA New Delhi Apex Centre)",
    description: "CTRI Linking, Subject Screening, Offline Batch Sync",
    token: "mock-jwt-bearer-priya-sharma-2026",
    avatarColor: "bg-[#004d61] text-[#97f0ff]",
    avatarIcon: "clinical_notes",
  },
  npvcc: {
    id: "USER-NPVCC-01",
    name: "Dr. K. Vaidya",
    title: "NPvCC Medical Safety Officer (National Reviewer)",
    email: "k.vaidya@npvcc.nic.in",
    role: "npvcc",
    roleHeader: "NPVCC_OFFICER",
    siteId: "SITE-01",
    siteLabel: "Global Oversight (National Pharmacovigilance)",
    description: "24h SAE Countdown Triage, MedDRA Coding, Form CT-16 Dispatch",
    token: "mock-jwt-bearer-dr-k-vaidya-2026",
    avatarColor: "bg-[#7c2d12] text-[#ffedd5]",
    avatarIcon: "emergency",
  },
  auditor: {
    id: "USER-AUD-01",
    name: "Inspector R. K. Verma",
    title: "CDSCO Regulatory Auditor (Central Inspection Team)",
    email: "rk.verma@cdsco.gov.in",
    role: "auditor",
    roleHeader: "REGULATORY_AUDITOR",
    siteId: "SITE-01",
    siteLabel: "Pan-India Regulatory Audit",
    description: "ALCOA+ Cryptographic Ledger, Merkle Witness Proof, Live Tamper Test",
    token: "mock-jwt-bearer-inspector-rk-verma-2026",
    avatarColor: "bg-[#4a154b] text-[#fbcfe8]",
    avatarIcon: "verified_user",
  },
  admin: {
    id: "USER-DSMB-01",
    name: "Prof. Anand Joshi",
    title: "DSMB Chairman / Executive Admin",
    email: "anand.joshi@dsmb-ayush.org",
    role: "admin",
    roleHeader: "SUPER_ADMIN",
    siteId: "SITE-01",
    siteLabel: "Global Portfolio Governance",
    description: "Multi-Center Portfolio KPIs, SPC Anomaly Alerts, Export Hub",
    token: "mock-jwt-bearer-prof-anand-joshi-2026",
    avatarColor: "bg-[#1e1b4b] text-[#c7d2fe]",
    avatarIcon: "monitoring",
  },
};

interface AppContextType {
  currentUser: UserPersona;
  isAuthenticated: boolean;
  isMounted: boolean;
  currentRole: Role;
  currentSite: Site;
  activeTab: Tab;
  activeTrialId: string | null;
  activePatientId: string | null;
  activeAeId: string | null;
  setActiveTrialId: (id: string | null) => void;
  setActivePatientId: (id: string | null) => void;
  setActiveAeId: (id: string | null) => void;
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
  login: (persona: UserPersona) => void;
  logout: () => void;
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
  const router = useRouter();
  const [isMounted, setIsMounted] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<UserPersona>(PRESET_PERSONAS.doctor);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
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
  const [activeBlockDrawer, setActiveBlockDrawer] = useState<number | null>(null);
  const [activeTrialId, setActiveTrialId] = useState<string | null>(
    "35113a2b-9fda-4e2c-89a8-ac2f0f25e1af"
  );
  const [activePatientId, setActivePatientId] = useState<string | null>(
    "8331d3f7-9578-44d8-abb2-898d995386f4"
  );
  const [activeAeId, setActiveAeId] = useState<string | null>(
    "deebbc58-adc7-4d64-a685-6935f2b8e959"
  );

  // Dynamic Trial and Patient ID resolution from live API
  useEffect(() => {
    let isSubscribed = true;
    const fetchDynamicEntities = async () => {
      try {
        const trials = await api.getTrials();
        if (isSubscribed && Array.isArray(trials) && trials.length > 0) {
          const match = trials.find((t: any) => t.protocol_id === "AIIA-GUD-2026") || trials[0];
          if (match?.id) setActiveTrialId(match.id);
        }
      } catch {
        // Fallback to pre-seeded ID
      }

      try {
        const patients = await api.getPatients();
        if (isSubscribed && Array.isArray(patients) && patients.length > 0) {
          const match = patients.find((p: any) => p.usubjid === "AIIA-P089") || patients[0];
          if (match?.id) setActivePatientId(match.id);
        }
      } catch {
        // Fallback to pre-seeded ID
      }
    };

    fetchDynamicEntities();
    return () => {
      isSubscribed = false;
    };
  }, []);

  // SSR-Safe Session Rehydration from localStorage
  useEffect(() => {
    setIsMounted(true);
    try {
      const stored = localStorage.getItem("ayutrial_session");
      if (stored) {
        const session: UserPersona = JSON.parse(stored);
        if (session && session.role) {
          setCurrentUser(session);
          setCurrentRole(session.role);
          setCurrentSite(session.siteId || "SITE-01");
          setIsAuthenticated(true);
          const roleToTab: Record<Role, Tab> = {
            doctor: "ecrf_desk",
            coordinator: "state_machine",
            npvcc: "npvcc_desk",
            auditor: "alcoa_ledger",
            admin: "analytics",
          };
          setActiveTab(roleToTab[session.role] || "ecrf_desk");
        } else {
          setIsAuthenticated(false);
        }
      } else {
        setIsAuthenticated(false);
      }
    } catch {
      setIsAuthenticated(false);
    }
  }, []);

  // Live statutory countdown ticker
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

  const login = (persona: UserPersona) => {
    setCurrentUser(persona);
    setCurrentRole(persona.role);
    setCurrentSite(persona.siteId);
    setIsAuthenticated(true);
    try {
      localStorage.setItem("ayutrial_session", JSON.stringify(persona));
    } catch {
      // ignore
    }

    const roleToTab: Record<Role, Tab> = {
      doctor: "ecrf_desk",
      coordinator: "state_machine",
      npvcc: "npvcc_desk",
      auditor: "alcoa_ledger",
      admin: "analytics",
    };
    setActiveTab(roleToTab[persona.role] || "ecrf_desk");

    showToast(`Session authenticated under 21 CFR §11.10: Welcome, ${persona.name}`, "success");
    setTimeout(() => {
      router.push("/");
    }, 300);
  };

  const logout = () => {
    try {
      localStorage.removeItem("ayutrial_session");
    } catch {
      // ignore
    }
    setIsAuthenticated(false);
    showToast("Session terminated under 21 CFR §11.10 security policies", "info");
    router.push("/login");
  };

  const changePersona = (role: Role) => {
    const persona = PRESET_PERSONAS[role] || PRESET_PERSONAS.doctor;
    setCurrentUser(persona);
    setCurrentRole(role);
    setCurrentSite(persona.siteId);
    try {
      localStorage.setItem("ayutrial_session", JSON.stringify(persona));
    } catch {
      // ignore
    }

    const roleToTab: Record<Role, Tab> = {
      doctor: "ecrf_desk",
      coordinator: "state_machine",
      npvcc: "npvcc_desk",
      auditor: "alcoa_ledger",
      admin: "analytics",
    };
    setActiveTab(roleToTab[role]);
    showToast(`Switched active persona: ${persona.name} (${persona.title})`);
  };

  const switchSite = (site: Site) => {
    setCurrentSite(site);
    const updatedUser = { ...currentUser, siteId: site };
    setCurrentUser(updatedUser);
    try {
      localStorage.setItem("ayutrial_session", JSON.stringify(updatedUser));
    } catch {
      // ignore
    }
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
      regulatory_export: "admin",
      analytics: "admin",
    };
    const newRole = tabToRole[tab];
    if (newRole && newRole !== currentRole) {
      changePersona(newRole);
    }
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
      const istTime =
        now.toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata" }) + " IST";
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
        currentUser,
        isAuthenticated,
        isMounted,
        currentRole,
        currentSite,
        activeTab,
        activeTrialId,
        activePatientId,
        activeAeId,
        setActiveTrialId,
        setActivePatientId,
        setActiveAeId,
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
        login,
        logout,
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
