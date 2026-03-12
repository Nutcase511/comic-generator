import { useState, useEffect } from 'react'
import { FileText, Loader2, RefreshCw } from 'lucide-react'
import { CopywritingOption } from '../../services/api'
import { useAppStore } from '../../stores/appStore'
import { api } from '../../services/api'

interface CopywritingOptionsProps {
  onNext: () => void
}

export default function CopywritingOptions({ onNext }: CopywritingOptionsProps) {
  const {
    copywritingOptions,
    setCopywritingOptions,
    selectedCopywriting,
    setSelectedCopywriting,
    copywritingTopic
  } = useAppStore()

  const [isLoading, setIsLoading] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)

  // 如果没有选项，显示加载状态
  useEffect(() => {
    if (copywritingOptions.length === 0 && !isLoading) {
      setIsLoading(true)
    }
  }, [copywritingOptions, isLoading])

  const handleSelectCopywriting = (option: CopywritingOption) => {
    setSelectedCopywriting(option)
    // 存储到 sessionStorage
    sessionStorage.setItem('selectedCopywriting', JSON.stringify(option))
    onNext()
  }

  const handleRegenerate = async () => {
    if (!copywritingTopic) return

    setIsRegenerating(true)
    try {
      const result = await api.generateCopywriting({ topic: copywritingTopic })

      if (result.success && result.data) {
        setCopywritingOptions(result.data)
        setSelectedCopywriting(null)
        sessionStorage.setItem('copywritingOptions', JSON.stringify(result.data))
      } else {
        alert(result.message || '重新生成失败')
      }
    } catch (error) {
      console.error('重新生成失败:', error)
      alert('重新生成失败，请重试')
    } finally {
      setIsRegenerating(false)
    }
  }

  // 解析文案内容
  const parseContent = (content: string) => {
    const lines = content.split('\n')
    const panels: string[] = []
    let narration = ''

    for (const line of lines) {
      if (line.startsWith('文案旁白：')) {
        narration = line.replace('文案旁白：', '').trim()
      } else if (line.match(/第[一二三四]格[：:]/)) {
        panels.push(line.replace(/第[一二三四]格[：:]\s*/, ''))
      } else if (line.match(/第\d+格[：:]/)) {
        panels.push(line.replace(/第\d+格[：:]\s*/, ''))
      }
    }

    return { panels, narration }
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-12 h-12 text-purple-500 animate-spin mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">AI正在创作文案...</h2>
            <p className="text-gray-600">预计需要10-20秒，请稍候</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">选择文案</h2>
            <p className="text-gray-600 mt-1">点击选择一个心仪的文案</p>
          </div>
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isRegenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>生成中...</span>
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4" />
                <span>重新生成</span>
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {copywritingOptions.map((option) => {
            const { panels, narration } = parseContent(option.content)
            return (
              <button
                key={option.id}
                onClick={() => handleSelectCopywriting(option)}
                className={`p-6 rounded-xl border-2 transition-all text-left hover:shadow-lg ${
                  selectedCopywriting?.id === option.id
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300 bg-white'
                }`}
              >
                <div className="flex items-start gap-3 mb-3">
                  <FileText className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-gray-800 mb-1 truncate">{option.title}</h3>
                    {option.tags && option.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {option.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="space-y-2 mb-3">
                  {panels.slice(0, 2).map((panel, index) => (
                    <p key={index} className="text-sm text-gray-600 line-clamp-1">
                      {panel}
                    </p>
                  ))}
                  {panels.length > 2 && (
                    <p className="text-sm text-gray-400">...</p>
                  )}
                </div>

                {narration && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-500 italic line-clamp-2">"{narration}"</p>
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
