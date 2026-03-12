import { useState, useEffect } from 'react'
import { Sparkles, FileText, Loader2, Lightbulb, TrendingUp } from 'lucide-react'
import { useAppStore } from '../../stores/appStore'
import { api } from '../../services/api'
import { ScriptGenerationSkeleton } from '../Skeleton'
import CharacterGrid from './CharacterGrid'

interface InputPanelProps {
  onNext: () => void
}

interface CopywritingTopic {
  id: string
  name: string
  description: string
}

interface HotTopic {
  id: string
  title: string
  description: string
}

export default function InputPanel({ onNext }: InputPanelProps) {
  const { setScriptData, setCopywritingOptions, setCopywritingTopic, setCurrentStep } = useAppStore()
  const [inputType, setInputType] = useState<'topic' | 'paste' | 'copywriting'>('topic')
  const [inputText, setInputText] = useState('')
  const [selectedCharacter, setSelectedCharacter] = useState('')
  const [style, setStyle] = useState('搞笑')
  const [isLoading, setIsLoading] = useState(false)
  const [scriptGenStep, setScriptGenStep] = useState<'thinking' | 'writing' | 'polishing'>('thinking')

  // Copywriting mode state
  const [copywritingTopics, setCopywritingTopics] = useState<CopywritingTopic[]>([])
  const [selectedTopic, setSelectedTopic] = useState('')
  const [customTopic, setCustomTopic] = useState('')
  const [hotTopics, setHotTopics] = useState<HotTopic[]>([])
  const [isLoadingHotTopics, setIsLoadingHotTopics] = useState(false)

  useEffect(() => {
    // Load copywriting topics when copywriting mode is selected
    if (inputType === 'copywriting') {
      loadCopywritingTopics()
      loadHotTopics()
    }
  }, [inputType])

  const loadHotTopics = async () => {
    setIsLoadingHotTopics(true)
    try {
      const result = await api.getHotTopics()
      if (result.success && result.data) {
        setHotTopics(result.data)
      }
    } catch (error) {
      console.error('加载热门话题失败:', error)
    } finally {
      setIsLoadingHotTopics(false)
    }
  }

  const loadCopywritingTopics = async () => {
    try {
      const result = await api.getCopywritingTopics()
      if (result.success && result.data) {
        setCopywritingTopics(result.data)
      }
    } catch (error) {
      console.error('加载文案主题失败:', error)
    }
  }

  const handleGenerateScript = async () => {
    if (!inputText.trim()) {
      alert('请输入内容')
      return
    }

    if (inputType === 'topic' && !selectedCharacter) {
      alert('请选择角色')
      return
    }

    setIsLoading(true)
    setScriptGenStep('thinking')

    // 模拟步骤切换以展示骨架屏动画
    const stepTimer = setTimeout(() => setScriptGenStep('writing'), 2000)
    const stepTimer2 = setTimeout(() => setScriptGenStep('polishing'), 5000)

    try {
      const result = await api.generateScript({
        input_type: inputType,
        input_text: inputText,
        character_id: selectedCharacter || undefined,
        style,
      })

      clearTimeout(stepTimer)
      clearTimeout(stepTimer2)

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
      clearTimeout(stepTimer)
      clearTimeout(stepTimer2)
    }
  }

  const handleGenerateCopywriting = async () => {
    let topic = ''

    // 优先级：预设主题 > 自定义主题 > 热门话题
    if (selectedTopic) {
      topic = copywritingTopics.find(t => t.id === selectedTopic)?.name || ''
    } else if (customTopic) {
      topic = customTopic
    }

    if (!topic.trim()) {
      alert('请选择或输入主题')
      return
    }

    setIsLoading(true)
    try {
      const result = await api.generateCopywriting({ topic })

      if (result.success && result.data) {
        setCopywritingOptions(result.data)
        setCopywritingTopic(topic)
        sessionStorage.setItem('copywritingOptions', JSON.stringify(result.data))
        sessionStorage.setItem('copywritingTopic', topic)
        setCurrentStep('copywriting')
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

  const handleSelectHotTopic = (hotTopic: HotTopic) => {
    setCustomTopic(hotTopic.title)
    setSelectedTopic('')
    // 清空预设主题选择
  }

  return (
    <div className="max-w-4xl mx-auto">
      {isLoading ? (
        /* 剧本生成骨架屏 */
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <ScriptGenerationSkeleton step={scriptGenStep} />
        </div>
      ) : (
        /* 正常输入面板 */
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
          <button
            onClick={() => setInputType('copywriting')}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
              inputType === 'copywriting'
                ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <Lightbulb className="w-5 h-5" />
              <span>文案生成</span>
            </div>
          </button>
        </div>

        {/* Topic Mode */}
        {inputType === 'topic' && (
          <div className="space-y-6">
            <CharacterGrid
              selectedCharacter={selectedCharacter}
              onCharacterSelect={setSelectedCharacter}
              label="选择角色"
            />

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

            <CharacterGrid
              selectedCharacter={selectedCharacter}
              onCharacterSelect={setSelectedCharacter}
              label="选择角色（可选）"
            />
          </div>
        )}

        {/* Copywriting Mode */}
        {inputType === 'copywriting' && (
          <div className="space-y-6">
            {/* Hot Topics Section */}
            {hotTopics.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-red-500" />
                  <label className="block text-sm font-semibold text-gray-700">
                    今日热门话题
                  </label>
                  {isLoadingHotTopics && <Loader2 className="w-4 h-4 animate-spin text-gray-400" />}
                </div>
                <div className="grid grid-cols-5 gap-2 mb-4">
                  {hotTopics.slice(0, 5).map((hotTopic) => (
                    <button
                      key={hotTopic.id}
                      onClick={() => handleSelectHotTopic(hotTopic)}
                      className={`p-3 rounded-lg border transition-all text-left ${
                        customTopic === hotTopic.title
                          ? 'border-red-400 bg-red-50'
                          : 'border-gray-200 hover:border-red-300 hover:bg-red-50'
                      }`}
                      title={hotTopic.description}
                    >
                      <div className="flex items-center gap-1">
                        <TrendingUp className="w-3 h-3 text-red-500 flex-shrink-0" />
                        <p className="text-xs font-medium text-gray-700 line-clamp-2">{hotTopic.title}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                选择预设主题
              </label>
              <div className="grid grid-cols-3 gap-3 mb-4">
                {copywritingTopics.map((topic) => (
                  <button
                    key={topic.id}
                    onClick={() => {
                      setSelectedTopic(topic.id)
                      setCustomTopic('')
                    }}
                    className={`p-4 rounded-xl border-2 transition-all text-left ${
                      selectedTopic === topic.id
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <h4 className="font-semibold text-gray-800 mb-1">{topic.name}</h4>
                    <p className="text-xs text-gray-600">{topic.description}</p>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                或输入自定义主题
              </label>
              <input
                type="text"
                value={customTopic}
                onChange={(e) => {
                  setCustomTopic(e.target.value)
                  setSelectedTopic('')
                }}
                placeholder="例如：算法推荐、社交媒体、远程办公等"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
              />
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
            onClick={inputType === 'copywriting' ? handleGenerateCopywriting : handleGenerateScript}
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
                {inputType === 'copywriting' ? (
                  <>
                    <Lightbulb className="w-5 h-5" />
                    <span>生成文案</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>生成剧本</span>
                  </>
                )}
              </>
            )}
          </button>
        </div>
      </div>
      )}
    </div>
  )
}
