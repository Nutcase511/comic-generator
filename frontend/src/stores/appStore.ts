import { create } from 'zustand'
import { ScriptData } from '../services/api'

interface AppState {
  // Current step
  currentStep: 'input' | 'script' | 'images' | 'preview'

  // Data
  scriptData: ScriptData | null
  imageUrls: string[] | null

  // Actions
  setCurrentStep: (step: 'input' | 'script' | 'images' | 'preview') => void
  setScriptData: (data: ScriptData) => void
  setImageUrls: (urls: string[]) => void
  reset: () => void
}

export const useAppStore = create<AppState>((set) => ({
  currentStep: 'input',
  scriptData: null,
  imageUrls: null,

  setCurrentStep: (step) => set({ currentStep: step }),
  setScriptData: (data) => set({ scriptData: data }),
  setImageUrls: (urls) => set({ imageUrls: urls }),

  reset: () => set({
    currentStep: 'input',
    scriptData: null,
    imageUrls: null,
  }),
}))
