import { create } from 'zustand'
import { ScriptData } from '../services/api'

interface CopywritingOption {
  id: string
  title: string
  content: string
  tags: string[]
}

interface AppState {
  // Current step
  currentStep: 'input' | 'copywriting' | 'character' | 'script' | 'images' | 'preview'

  // Data
  scriptData: ScriptData | null
  imageUrls: string[] | null

  // Copywriting data
  copywritingOptions: CopywritingOption[]
  selectedCopywriting: CopywritingOption | null
  copywritingTopic: string

  // Actions
  setCurrentStep: (step: 'input' | 'copywriting' | 'character' | 'script' | 'images' | 'preview') => void
  setScriptData: (data: ScriptData) => void
  setImageUrls: (urls: string[]) => void
  setCopywritingOptions: (options: CopywritingOption[]) => void
  setSelectedCopywriting: (option: CopywritingOption | null) => void
  setCopywritingTopic: (topic: string) => void
  reset: () => void
}

export const useAppStore = create<AppState>((set) => ({
  currentStep: 'input',
  scriptData: null,
  imageUrls: null,
  copywritingOptions: [],
  selectedCopywriting: null,
  copywritingTopic: '',

  setCurrentStep: (step) => set({ currentStep: step }),
  setScriptData: (data) => set({ scriptData: data }),
  setImageUrls: (urls) => set({ imageUrls: urls }),
  setCopywritingOptions: (options) => set({ copywritingOptions: options }),
  setSelectedCopywriting: (option) => set({ selectedCopywriting: option }),
  setCopywritingTopic: (topic) => set({ copywritingTopic: topic }),

  reset: () => set({
    currentStep: 'input',
    scriptData: null,
    imageUrls: null,
    copywritingOptions: [],
    selectedCopywriting: null,
    copywritingTopic: '',
  }),
}))
