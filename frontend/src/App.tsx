import { useEffect, useState, useRef } from 'react'
import InputPanel from './components/InputPanel/InputPanel'
import CopywritingOptions from './components/InputPanel/CopywritingOptions'
import CharacterSelection from './components/InputPanel/CharacterSelection'
import { ImageGenerationSkeleton, ScriptGenerationSkeleton } from './components/Skeleton'
import { useAppStore } from './stores/appStore'
import { api } from './services/api'
import { wsService, ProgressData } from './services/websocket'
import './App.css'

function App() {
  const {
    currentStep,
    scriptData,
    imageUrls,
    copywritingOptions,
    setCopywritingOptions,
    selectedCopywriting,
    setSelectedCopywriting,
    copywritingTopic,
    setCopywritingTopic,
    setCurrentStep,
    setScriptData,
    setImageUrls
  } = useAppStore()

  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState({ current: 0, total: 4 })
  const [scriptGenerationStep, setScriptGenerationStep] = useState<'thinking' | 'writing' | 'polishing'>('thinking')
  const [isResetting, setIsResetting] = useState(false)
  const abortControllerRef = useRef<AbortController | null>(null)

  // 重置函数
  const handleReset = () => {
    const confirmed = window.confirm('确定要重置吗？当前进度将会丢失。')
    if (!confirmed) return

    // 取消正在进行的请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }

    setIsResetting(true)
    setIsGenerating(false)

    // 清空所有状态
    setScriptData(null)
    setImageUrls(null)
    setCopywritingOptions([])
    setSelectedCopywriting(null)
    setCopywritingTopic('')
    setCurrentStep('input')
    setGenerationProgress({ current: 0, total: 4 })

    // 清空 sessionStorage
    sessionStorage.removeItem('scriptData')
    sessionStorage.removeItem('imageUrls')
    sessionStorage.removeItem('currentStep')
    sessionStorage.removeItem('copywritingOptions')
    sessionStorage.removeItem('selectedCopywriting')
    sessionStorage.removeItem('copywritingTopic')

    setTimeout(() => {
      setIsResetting(false)
    }, 100)
  }

  // Load data from sessionStorage on mount
  useEffect(() => {
    const savedScriptData = sessionStorage.getItem('scriptData')
    const savedImageUrls = sessionStorage.getItem('imageUrls')
    const savedCurrentStep = sessionStorage.getItem('currentStep')
    const savedCopywritingOptions = sessionStorage.getItem('copywritingOptions')
    const savedSelectedCopywriting = sessionStorage.getItem('selectedCopywriting')
    const savedCopywritingTopic = sessionStorage.getItem('copywritingTopic')

    if (savedScriptData) {
      setScriptData(JSON.parse(savedScriptData))
    }
    if (savedImageUrls) {
      setImageUrls(JSON.parse(savedImageUrls))
    }
    if (savedCurrentStep) {
      setCurrentStep(savedCurrentStep as any)
    }
    if (savedCopywritingOptions) {
      setCopywritingOptions(JSON.parse(savedCopywritingOptions))
    }
    if (savedSelectedCopywriting) {
      setSelectedCopywriting(JSON.parse(savedSelectedCopywriting))
    }
    if (savedCopywritingTopic) {
      setCopywritingTopic(savedCopywritingTopic)
    }

    // 连接WebSocket
    wsService.connect()

    return () => {
      wsService.disconnect()
    }
  }, [setScriptData, setImageUrls, setCurrentStep, setCopywritingOptions, setSelectedCopywriting, setCopywritingTopic])

  // 监听WebSocket进度更新
  useEffect(() => {
    const handleProgress = (data: ProgressData) => {
      console.log('收到进度更新:', data)

      switch (data.type) {
        case 'generation_start':
          setGenerationProgress({ current: 0, total: data.total || 4 })
          break

        case 'panel_start':
          setGenerationProgress({
            current: data.panel_number || 1,
            total: data.total || 4
          })
          break

        case 'panel_complete':
          // 图片生成完成，更新UI
          if (data.image_url) {
            setImageUrls((prev) => {
              const urls = prev || []
              urls[(data.panel_number || 1) - 1] = data.image_url!
              return [...urls]
            })
          }
          break

        case 'generation_complete':
          // 所有图片生成完成
          if (data.image_urls) {
            setImageUrls(data.image_urls)
            sessionStorage.setItem('imageUrls', JSON.stringify(data.image_urls))

            setTimeout(() => {
              setCurrentStep('preview')
              sessionStorage.setItem('currentStep', 'preview')
            }, 500)
          }
          setIsGenerating(false)
          break

        case 'panel_error':
        case 'generation_error':
          console.error('生成错误:', data.error)
          alert(data.message || '生成失败')
          setIsGenerating(false)
          setCurrentStep('script')
          break
      }
    }

    wsService.onProgress(handleProgress)

    return () => {
      wsService.offProgress(handleProgress)
    }
  }, [setCurrentStep, setImageUrls])

  // 当进入 images 步骤时，自动开始生成图片
  useEffect(() => {
    if (currentStep === 'images' && scriptData && !imageUrls && !isGenerating && !isResetting) {
      const generate = async () => {
        if (!scriptData) return

        abortControllerRef.current = new AbortController()
        setIsGenerating(true)

        try {
          console.log('开始生成图片...', scriptData)

          const result = await api.generateImages({ script_data: scriptData })

          if (isResetting) return

          console.log('图片生成结果:', result)

          if (result.success && result.data && Array.isArray(result.data)) {
            const urls = result.data
            setImageUrls(urls)
            sessionStorage.setItem('imageUrls', JSON.stringify(urls))

            setTimeout(() => {
              if (!isResetting) {
                setCurrentStep('preview')
                sessionStorage.setItem('currentStep', 'preview')
              }
            }, 500)
          } else {
            alert(result.message || '图片生成失败')
            setCurrentStep('script')
          }
        } catch (error) {
          if (isResetting) return
          console.error('生成图片失败:', error)
          alert('生成图片失败，请重试')
          setCurrentStep('script')
        } finally {
          if (!isResetting) {
            setIsGenerating(false)
          }
          abortControllerRef.current = null
        }
      }

      generate()
    }
  }, [currentStep, scriptData, imageUrls, isGenerating, isResetting, setScriptData, setImageUrls, setCurrentStep])

  const handlePublishToWechat = async () => {
    if (!scriptData || !imageUrls || imageUrls.length !== 4) {
      alert('请先生成完整的四格漫画')
      return
    }

    const confirmed = window.confirm('确认发布到微信公众号草稿箱？')
    if (!confirmed) return

    try {
      console.log('开始发布到微信公众号...')

      const result = await api.publishToWechat({
        script_data: scriptData,
        image_urls: imageUrls
      })

      console.log('发布结果:', result)

      if (result.success) {
        alert(`发布成功！\n\n媒体ID: ${result.media_id}\n\n请到微信公众号后台查看草稿箱`)

        // 重置所有状态
        setScriptData(null)
        setImageUrls(null)
        setCopywritingOptions([])
        setSelectedCopywriting(null)
        setCopywritingTopic('')
        setCurrentStep('input')

        // 清空 sessionStorage
        sessionStorage.removeItem('scriptData')
        sessionStorage.removeItem('imageUrls')
        sessionStorage.removeItem('currentStep')
        sessionStorage.removeItem('copywritingOptions')
        sessionStorage.removeItem('selectedCopywriting')
        sessionStorage.removeItem('copywritingTopic')
      } else {
        alert(result.message || '发布失败')
      }
    } catch (error) {
      console.error('发布失败:', error)
      alert('发布失败，请检查网络连接和微信公众号配置')
    }
  }

  const handleNext = (step?: 'input' | 'copywriting' | 'character' | 'script' | 'images' | 'preview') => {
    const nextStep = step || currentStep
    setCurrentStep(nextStep)
    sessionStorage.setItem('currentStep', nextStep)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      <div className="container mx-auto px-4 py-8">
        <header className="flex justify-between items-center mb-8">
          <div className="text-center flex-1">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              AI漫画生成器
            </h1>
            <p className="text-gray-600 mt-2">自动生成四格漫画并发布到微信公众号</p>
          </div>
          <button
            onClick={handleReset}
            disabled={isResetting}
            className="ml-4 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            重置
          </button>
        </header>

        <main>
          {currentStep === 'input' && (
            <InputPanel onNext={() => handleNext('script')} />
          )}

          {currentStep === 'copywriting' && (
            <CopywritingOptions onNext={() => handleNext('character')} />
          )}

          {currentStep === 'character' && (
            <CharacterSelection
              onNext={() => handleNext('script')}
              onBack={() => handleNext('copywriting')}
            />
          )}

          {currentStep === 'script' && scriptData && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold mb-4">剧本预览</h2>
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-gray-800">{scriptData.title}</h3>
                </div>

                {/* 调试信息区域 */}
                <div className="mb-6 p-4 bg-blue-50 border-2 border-blue-300 rounded-lg">
                  <h4 className="font-semibold text-blue-800 mb-2">📝 调试信息（角色检查）</h4>
                  <div className="text-sm">
                    <p className="mb-1"><strong>角色列表：</strong>
                      {scriptData.characters && scriptData.characters.length > 0
                        ? scriptData.characters.map((c: any) => c.name).join('、')
                        : '（无）'
                      }
                    </p>
                    <p className="text-gray-600 text-xs">如果这里显示的不是您选择的角色（如蜘蛛侠），说明剧本生成时角色替换失败。</p>
                  </div>
                </div>

                {scriptData.panels.map((panel, index) => (
                  <div key={panel.panel_number} className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-semibold text-gray-700 mb-2">第{index + 1}格</h4>
                    <p className="text-sm text-gray-600 mb-1"><strong>场景：</strong>{panel.scene_description}</p>
                    <p className="text-sm text-gray-600 mb-1"><strong>动作：</strong>{panel.character_action || panel.character_actions || '-'}</p>
                    <p className="text-sm text-gray-600 mb-1"><strong>对话：</strong>{panel.dialogue}</p>

                    {/* 显示visual_prompt（这是生成图片的关键！） */}
                    <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded">
                      <p className="text-xs"><strong>🎨 画面提示词：</strong></p>
                      <p className="text-xs text-gray-700 break-words">{panel.visual_prompt || '（无）'}</p>
                    </div>
                  </div>
                ))}
                <div className="mt-6 flex justify-between">
                  <button
                    onClick={() => handleNext('input')}
                    className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    返回
                  </button>
                  <button
                    onClick={() => handleNext('images')}
                    className="px-6 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg hover:shadow-lg"
                  >
                    生成图片
                  </button>
                </div>
              </div>
            </div>
          )}

          {currentStep === 'images' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <div className="text-center mb-6">
                  <h2 className="text-2xl font-bold mb-2">
                    {isGenerating ? '图片生成中...' : '准备生成图片'}
                  </h2>
                  <p className="text-gray-600">
                    {isGenerating
                      ? `AI正在绘制漫画，已完成 ${generationProgress.current}/${generationProgress.total} 张...`
                      : '即将开始生成漫画图片，预计需要40-80秒'
                    }
                  </p>
                </div>

                {/* 使用新的骨架屏组件 */}
                <ImageGenerationSkeleton
                  currentIndex={isGenerating ? generationProgress.current - 1 : -1}
                  totalImages={4}
                />

                {/* 额外的加载提示 */}
                {isGenerating && (
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center justify-center gap-3">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                      <p className="text-sm text-blue-700">
                        正在调用即梦AI生成第{generationProgress.current}张图片...
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {currentStep === 'preview' && imageUrls && imageUrls.length === 4 && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold mb-4">漫画预览</h2>
                {/* 使用响应式网格，移动端单列，平板及以上双列 */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                  {imageUrls.map((url, index) => (
                    <div key={index} className="relative w-full pb-[100%] bg-gray-100 rounded-lg overflow-hidden">
                      <img
                        src={url}
                        alt={`第${index + 1}格`}
                        className="absolute top-0 left-0 w-full h-full object-contain"
                        style={{ aspectRatio: '1/1' }}
                      />
                    </div>
                  ))}
                </div>
                <div className="flex justify-between">
                  <button
                    onClick={() => handleNext('images')}
                    className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    重新生成
                  </button>
                  <button
                    onClick={handlePublishToWechat}
                    className="px-6 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:shadow-lg"
                  >
                    发布到公众号
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
