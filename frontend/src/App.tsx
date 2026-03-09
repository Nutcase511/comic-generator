import { useEffect } from 'react'
import InputPanel from './components/InputPanel/InputPanel'
import { useAppStore } from './stores/appStore'
import './App.css'

function App() {
  const { currentStep, scriptData, imageUrls, setCurrentStep, setScriptData, setImageUrls } = useAppStore()

  // Load data from sessionStorage on mount
  useEffect(() => {
    const savedScriptData = sessionStorage.getItem('scriptData')
    const savedImageUrls = sessionStorage.getItem('imageUrls')
    const savedCurrentStep = sessionStorage.getItem('currentStep')

    if (savedScriptData) {
      setScriptData(JSON.parse(savedScriptData))
    }
    if (savedImageUrls) {
      setImageUrls(JSON.parse(savedImageUrls))
    }
    if (savedCurrentStep) {
      setCurrentStep(savedCurrentStep as any)
    }
  }, [setScriptData, setImageUrls, setCurrentStep])

  const handleNext = (step?: 'input' | 'script' | 'images' | 'preview') => {
    const nextStep = step || currentStep
    setCurrentStep(nextStep)
    sessionStorage.setItem('currentStep', nextStep)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            AI漫画生成器
          </h1>
          <p className="text-gray-600 mt-2">自动生成四格漫画并发布到微信公众号</p>
        </header>

        <main>
          {currentStep === 'input' && (
            <InputPanel onNext={() => handleNext('script')} />
          )}

          {currentStep === 'script' && scriptData && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold mb-4">剧本预览</h2>
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-gray-800">{scriptData.title}</h3>
                </div>
                {scriptData.panels.map((panel, index) => (
                  <div key={panel.panel_number} className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-semibold text-gray-700 mb-2">第{index + 1}格</h4>
                    <p className="text-sm text-gray-600 mb-1"><strong>场景：</strong>{panel.scene_description}</p>
                    <p className="text-sm text-gray-600 mb-1"><strong>动作：</strong>{panel.character_action}</p>
                    <p className="text-sm text-gray-600"><strong>对话：</strong>{panel.dialogue}</p>
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
                <h2 className="text-2xl font-bold mb-4">图片生成中...</h2>
                <div className="grid grid-cols-2 gap-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center">
                      <div className="text-center text-gray-400">
                        <div className="animate-pulse">第{i}格</div>
                        <div className="text-sm mt-2">生成中...</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentStep === 'preview' && imageUrls && imageUrls.length === 4 && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold mb-4">漫画预览</h2>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  {imageUrls.map((url, index) => (
                    <div key={index} className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                      <img src={url} alt={`第${index + 1}格`} className="w-full h-full object-cover" />
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
                    onClick={() => alert('发布功能开发中...')}
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
