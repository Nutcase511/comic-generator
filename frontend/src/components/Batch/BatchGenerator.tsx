import { useState } from 'react'
import { Sparkles, Plus, X, Play, Pause, CheckCircle, XCircle, Clock } from 'lucide-react'
import { api, ScriptData } from '../../services/api'

interface BatchItem {
  id: string
  topic: string
  characterId: string
  status: 'pending' | 'generating' | 'completed' | 'error'
  progress?: number
  scriptData?: ScriptData
  imageUrls?: string[]
  error?: string
}

export default function BatchGenerator() {
  const [items, setItems] = useState<BatchItem[]>([
    { id: '1', topic: '', characterId: '', status: 'pending' }
  ])
  const [isRunning, setIsRunning] = useState(false)
  const [currentItemIndex, setCurrentItemIndex] = useState(-1)
  const [characters] = useState([
    { id: 'wukong', name: '孙悟空' },
    { id: 'ironman', name: '钢铁侠' },
    { id: 'luffy', name: '路飞' },
    { id: 'nobita', name: '大雄' },
    { id: 'conan', name: '柯南' },
  ])

  const addItem = () => {
    const newItem: BatchItem = {
      id: Date.now().toString(),
      topic: '',
      characterId: '',
      status: 'pending'
    }
    setItems([...items, newItem])
  }

  const removeItem = (id: string) => {
    setItems(items.filter(item => item.id !== id))
  }

  const updateItem = (id: string, updates: Partial<BatchItem>) => {
    setItems(items.map(item =>
      item.id === id ? { ...item, ...updates } : item
    ))
  }

  const startBatch = async () => {
    const validItems = items.filter(item => item.topic.trim() && item.characterId)

    if (validItems.length === 0) {
      alert('请至少添加一个有效的生成任务')
      return
    }

    setIsRunning(true)
    setCurrentItemIndex(0)

    // 依次处理每个任务
    for (let i = 0; i < validItems.length; i++) {
      if (!isRunning) break // 允许暂停

      setCurrentItemIndex(i)
      const item = validItems[i]

      // 更新状态为生成中
      updateItem(item.id, { status: 'generating', progress: 10 })

      try {
        // 1. 生成剧本
        updateItem(item.id, { progress: 20 })
        const scriptResult = await api.generateScript({
          input_type: 'topic',
          input_text: item.topic,
          character_id: item.characterId,
          style: '搞笑'
        })

        if (!scriptResult.success || !scriptResult.data) {
          throw new Error(scriptResult.message || '剧本生成失败')
        }

        updateItem(item.id, { scriptData: scriptResult.data, progress: 50 })

        // 2. 生成图片
        updateItem(item.id, { progress: 60 })
        const imageResult = await api.generateImages({
          script_data: scriptResult.data
        })

        if (!imageResult.success || !imageResult.data) {
          throw new Error(imageResult.message || '图片生成失败')
        }

        // 3. 完成并自动发布
        updateItem(item.id, { progress: 90 })
        const publishResult = await api.publishToWechat({
          script_data: scriptResult.data,
          image_urls: imageResult.data
        })

        if (!publishResult.success) {
          throw new Error(publishResult.message || '发布失败')
        }

        // 完成
        updateItem(item.id, {
          status: 'completed',
          progress: 100,
          imageUrls: imageResult.data
        })

      } catch (error) {
        console.error(`生成失败 [${item.topic}]:`, error)
        updateItem(item.id, {
          status: 'error',
          error: error instanceof Error ? error.message : '生成失败'
        })
      }
    }

    setIsRunning(false)
    setCurrentItemIndex(-1)
  }

  const pauseBatch = () => {
    setIsRunning(false)
  }

  const resetBatch = () => {
    if (!confirm('确定要重置所有任务吗？')) return
    setItems(items.map(item => ({
      ...item,
      status: 'pending' as const,
      progress: undefined,
      scriptData: undefined,
      imageUrls: undefined,
      error: undefined
    })))
    setCurrentItemIndex(-1)
  }

  const getStatusIcon = (status: BatchItem['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />
      case 'generating':
        return <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
    }
  }

  const completedCount = items.filter(item => item.status === 'completed').length
  const errorCount = items.filter(item => item.status === 'error').length

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8">
        {/* 标题和控制按钮 */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-purple-500" />
            <h2 className="text-2xl font-bold">批量生成</h2>
          </div>
          <div className="flex gap-2">
            {!isRunning ? (
              <>
                <button
                  onClick={addItem}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
                >
                  <Plus className="w-5 h-5" />
                  <span>添加任务</span>
                </button>
                <button
                  onClick={startBatch}
                  className="px-6 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg hover:shadow-lg transition-all flex items-center gap-2"
                >
                  <Play className="w-5 h-5" />
                  <span>开始生成</span>
                </button>
              </>
            ) : (
              <button
                onClick={pauseBatch}
                className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2"
              >
                <Pause className="w-5 h-5" />
                <span>暂停</span>
              </button>
            )}
            <button
              onClick={resetBatch}
              disabled={isRunning}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              重置
            </button>
          </div>
        </div>

        {/* 统计信息 */}
        <div className="flex gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">总计:</span>
            <span className="font-semibold">{items.length}</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span className="text-sm text-gray-600">完成:</span>
            <span className="font-semibold text-green-600">{completedCount}</span>
          </div>
          <div className="flex items-center gap-2">
            <XCircle className="w-4 h-4 text-red-500" />
            <span className="text-sm text-gray-600">失败:</span>
            <span className="font-semibold text-red-600">{errorCount}</span>
          </div>
          {isRunning && currentItemIndex >= 0 && (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm text-gray-600">正在处理: {currentItemIndex + 1}/{items.length}</span>
            </div>
          )}
        </div>

        {/* 任务列表 */}
        <div className="space-y-4">
          {items.map((item, index) => (
            <div
              key={item.id}
              className={`border-2 rounded-xl p-4 transition-all ${
                item.status === 'completed' ? 'border-green-300 bg-green-50' :
                item.status === 'error' ? 'border-red-300 bg-red-50' :
                item.status === 'generating' ? 'border-blue-300 bg-blue-50' :
                'border-gray-200'
              }`}
            >
              <div className="flex items-start gap-4">
                {/* 序号和状态 */}
                <div className="flex items-center gap-3 w-32">
                  <span className="text-lg font-bold text-gray-500">#{index + 1}</span>
                  {getStatusIcon(item.status)}
                </div>

                {/* 输入区域 */}
                <div className="flex-1 grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">主题</label>
                    <input
                      type="text"
                      value={item.topic}
                      onChange={(e) => updateItem(item.id, { topic: e.target.value })}
                      disabled={isRunning}
                      placeholder="例如：孙悟空在现代办公室使用打印机"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">角色</label>
                    <select
                      value={item.characterId}
                      onChange={(e) => updateItem(item.id, { characterId: e.target.value })}
                      disabled={isRunning}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <option value="">选择角色</option>
                      {characters.map(char => (
                        <option key={char.id} value={char.id}>{char.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* 删除按钮 */}
                <button
                  onClick={() => removeItem(item.id)}
                  disabled={isRunning}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* 进度和结果 */}
              {item.status !== 'pending' && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  {item.status === 'generating' && item.progress && (
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 transition-all duration-300"
                          style={{ width: `${item.progress}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">{item.progress}%</span>
                    </div>
                  )}

                  {item.status === 'completed' && item.scriptData && (
                    <div className="text-sm text-green-700">
                      ✓ 成功生成"{item.scriptData.title}"并已发布到微信公众号
                    </div>
                  )}

                  {item.status === 'error' && item.error && (
                    <div className="text-sm text-red-700">
                      ✗ {item.error}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {items.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p>暂无任务，点击上方"添加任务"按钮开始</p>
          </div>
        )}
      </div>
    </div>
  )
}
