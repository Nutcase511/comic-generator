// API base URL
const API_BASE_URL = '/api'

// Types
export interface Character {
  id: string
  name: string
  source: string
  source_type: string
  description: string
  prompt_keywords: string
}

export interface ScriptPanel {
  panel_number: number
  scene_description: string
  character_action: string
  dialogue: string
  visual_prompt: string
}

export interface ScriptData {
  title: string
  panels: ScriptPanel[]
}

export interface GenerateScriptRequest {
  input_type: 'topic' | 'paste'
  input_text: string
  character_id?: string
  style?: string
}

export interface GenerateScriptResponse {
  success: boolean
  message?: string
  data?: ScriptData
}

export interface GenerateImageRequest {
  script_data: ScriptData
}

export interface GenerateImageResponse {
  success: boolean
  message?: string
  data?: {
    image_urls: string[]
  }
}

export interface PublishToWechatRequest {
  script_data: ScriptData
  image_urls: string[]
}

export interface PublishToWechatResponse {
  success: boolean
  message?: string
  media_id?: string
  draft_url?: string
}

export interface HistoryItem {
  id: number
  created_at: string
  title: string
  input_type: string
  character_name: string
  wechat_media_id: string
  published_at: string
}

export interface HistoryListResponse {
  success: boolean
  total: number
  data: HistoryItem[]
}

// API Functions
export const api = {
  // Get characters
  async getCharacters(): Promise<Character[]> {
    const response = await fetch(`${API_BASE_URL}/script/characters`)
    const data = await response.json()
    return data.data.characters
  },

  // Generate script
  async generateScript(request: GenerateScriptRequest): Promise<GenerateScriptResponse> {
    const response = await fetch(`${API_BASE_URL}/script/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    return response.json()
  },

  // Generate images
  async generateImages(request: GenerateImageRequest): Promise<GenerateImageResponse> {
    const response = await fetch(`${API_BASE_URL}/image/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    return response.json()
  },

  // Publish to WeChat
  async publishToWechat(request: PublishToWechatRequest): Promise<PublishToWechatResponse> {
    const response = await fetch(`${API_BASE_URL}/wechat/publish`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    return response.json()
  },

  // Get history list
  async getHistoryList(limit: number = 20, offset: number = 0): Promise<HistoryListResponse> {
    const response = await fetch(`${API_BASE_URL}/history/list?limit=${limit}&offset=${offset}`)
    return response.json()
  },

  // Get history detail
  async getHistoryDetail(historyId: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/history/${historyId}`)
    return response.json()
  },

  // Republish to WeChat
  async republishToWechat(historyId: number): Promise<PublishToWechatResponse> {
    const response = await fetch(`${API_BASE_URL}/history/${historyId}/republish`, {
      method: 'POST',
    })
    return response.json()
  },
}
