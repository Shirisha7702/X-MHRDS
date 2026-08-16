import React, { createContext, useState } from 'react';

export const AppContext = createContext();

export function AppProvider({ children }) {
  const [activeTab, setActiveTab] = useState('sandbox');
  const [modelChoice, setModelChoice] = useState('Logistic Regression');
  const [isCmdOpen, setIsCmdOpen] = useState(false);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [anonymizeActive, setAnonymizeActive] = useState(true);
  const [explanationMethod, setExplanationMethod] = useState('fast');

  const value = {
    activeTab,
    setActiveTab,
    modelChoice,
    setModelChoice,
    isCmdOpen,
    setIsCmdOpen,
    isCopilotOpen,
    setIsCopilotOpen,
    anonymizeActive,
    setAnonymizeActive,
    explanationMethod,
    setExplanationMethod,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
