import { useState, useEffect } from 'react'
import { User, Loader2, ArrowLeft } from 'lucide-react'
import { useAppStore } from '../../stores/appStore'
import { api } from '../../services/api'

interface Character {
  id: string
  name: string
  source: string
}

interface CharacterSelectionProps {
  onNext: () => void
  onBack: () => void
}

export default function CharacterSelection({ onNext, onBack }: CharacterSelectionProps) {
  const { selectedCopywriting, setScriptData } = useAppStore()
  const [selectedCharacter, setSelectedCharacter] = useState('')
  const [style, setStyle] = useState('搞笑')
  const [isLoading, setIsLoading] = useState(false)
  const [characters, setCharacters] = useState<Character[]>([])

  useEffect(() => {
    // 加载角色列表
    const loadCharacters = async () => {
      try {
        const chars = await api.getCharacters()
        setCharacters(chars)
      } catch (error) {
        console.error('加载角色失败:', error)
      }
    }
    loadCharacters()
  }, [])

  const handleGenerate = async () => {
    if (!selectedCopywriting) {
      alert('请先选择文案')
      return
    }

    if (!selectedCharacter) {
      alert('请选择角色')
      return
    }

    setIsLoading(true)
    try {
      const result = await api.generateScript({
        input_type: 'copywriting',
        input_text: selectedCopywriting.content,
        character_id: selectedCharacter,
        style,
      })

      if (result.success && result.data) {
        setScriptData(result.data)
        sessionStorage.setItem('scriptData', JSON.stringify(result.data))
        onNext()
      } else {
        alert(result.message || '生成失败')
      }
    } catch (error) {
      console.error('生成失败:', error)
      alert('生成失败，请重试')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8">
        {/* Selected Copywriting Summary */}
        {selectedCopywriting && (
          <div className="mb-6 p-4 bg-purple-50 rounded-xl border border-purple-200">
            <h3 className="font-semibold text-purple-800 mb-2">{selectedCopywriting.title}</h3>
            <p className="text-sm text-purple-600 line-clamp-2">{selectedCopywriting.content.substring(0, 200)}...</p>
          </div>
        )}

        {/* Character Selection */}
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-3">
            选择角色
          </label>
          <div className="grid grid-cols-5 gap-3">
            {characters.map((char) => (
              <button
                key={char.id}
                onClick={() => setSelectedCharacter(char.id)}
                className={`p-4 rounded-xl border-2 transition-all ${
                  selectedCharacter === char.id
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <div className="flex flex-col items-center gap-1">
                  <User className="w-6 h-6 text-gray-600" />
                  <span className="text-xs font-medium text-gray-700">{char.name}</span>
                  <span className="text-xs text-gray-500">{char.source}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Style Selection */}
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-3">
            风格选择
          </label>
          <div className="flex gap-3">
            {['搞笑', '温馨', '励志', '治愈'].map((s) => (
              <button
                key={s}
                onClick={() => setStyle(s)}
                className={`px-6 py-2 rounded-full font-medium transition-all ${
                  style === s
                    ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between">
          <button
            onClick={onBack}
            className="px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-all flex items-center gap-2"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>返回</span>
          </button>
          <button
            onClick={handleGenerate}
            disabled={isLoading}
            className="px-8 py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>生成中...</span>
              </>
            ) : (
              <>
                <User className="w-5 h-5" />
                <span>生成剧本</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
