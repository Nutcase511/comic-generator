import { useState } from 'react'
import { Sparkles, FileText, User, Loader2 } from 'lucide-react'
import { useAppStore } from '../../stores/appStore'
import { api } from '../../services/api'

interface InputPanelProps {
  onNext: () => void
}

export default function InputPanel({ onNext }: InputPanelProps) {
  const { setScriptData } = useAppStore()
  const [inputType, setInputType] = useState<'topic' | 'paste'>('topic')
  const [inputText, setInputText] = useState('')
  const [selectedCharacter, setSelectedCharacter] = useState('')
  const [style, setStyle] = useState('搞笑')
  const [isLoading, setIsLoading] = useState(false)
  const [characters, setCharacters] = useState([
    { id: 'wukong', name: '孙悟空', source: '西游记' },
    { id: 'ironman', name: '钢铁侠', source: '漫威' },
    { id: 'luffy', name: '路飞', source: '海贼王' },
    { id: 'nobita', name: '大雄', source: '哆啦A梦' },
    { id: 'conan', name: '柯南', source: '名侦探柯南' },
    { id: 'harry', name: '哈利波特', source: '哈利波特' },
    { id: 'goku', name: '悟空', source: '龙珠' },
    { id: 'elsa', name: '艾莎', source: '冰雪奇缘' },
    { id: 'spiderman', name: '蜘蛛侠', source: '漫威' },
    { id: 'doraemon', name: '哆啦A梦', source: '哆啦A梦' },
  ])

  const handleGenerate = async () => {
    if (!inputText.trim()) {
      alert('请输入内容')
      return
    }

    if (inputType === 'topic' && !selectedCharacter) {
      alert('请选择角色')
      return
    }

    setIsLoading(true)
    try {
      const result = await api.generateScript({
        input_type: inputType,
        input_text: inputText,
        character_id: selectedCharacter || undefined,
        style,
      })

      if (result.success && result.data) {
        // Store script data in Zustand
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
        {/* Mode Toggle */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setInputType('topic')}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
              inputType === 'topic'
                ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <Sparkles className="w-5 h-5" />
              <span>主题生成</span>
            </div>
          </button>
          <button
            onClick={() => setInputType('paste')}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
              inputType === 'paste'
                ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <FileText className="w-5 h-5" />
              <span>剧本粘贴</span>
            </div>
          </button>
        </div>

        {/* Topic Mode */}
        {inputType === 'topic' && (
          <div className="space-y-6">
            <div>
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

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                输入主题
              </label>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="例如：孙悟空在现代办公室使用打印机的故事"
                className="w-full h-32 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none resize-none"
              />
            </div>
          </div>
        )}

        {/* Paste Mode */}
        {inputType === 'paste' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                粘贴四格漫画剧本
              </label>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="第一格：[场景描述]&#10;第二格：[场景描述]&#10;第三格：[场景描述]&#10;第四格：[场景描述]"
                className="w-full h-48 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none resize-none font-mono text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                选择角色（可选）
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
          </div>
        )}

        {/* Style Selection */}
        <div className="mt-6">
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

        {/* Generate Button */}
        <div className="mt-8 flex justify-end">
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
                <Sparkles className="w-5 h-5" />
                <span>生成剧本</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
