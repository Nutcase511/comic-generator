import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Calendar, User, Send, Image as ImageIcon } from 'lucide-react'
import { api } from '../../services/api'

interface HistoryDetail {
  id: number
  created_at: string
  title: string
  input_type: string
  input_text?: string
  character_id?: string
  character_name?: string
  script_data: {
    title: string
    panels: Array<{
      panel_number: number
      scene_description: string
      character_action: string
      dialogue: string
    }>
  }
  images: string[]
  wechat_media_id?: string
  published_at?: string
}

export default function HistoryDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [history, setHistory] = useState<HistoryDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [republishing, setRepublishing] = useState(false)

  useEffect(() => {
    const loadDetail = async () => {
      if (!id) return

      setLoading(true)
      try {
        const result = await api.getHistoryDetail(parseInt(id))
        if (result.success && result.data) {
          setHistory(result.data)
        }
      } catch (error) {
        console.error('加载历史记录详情失败:', error)
      } finally {
        setLoading(false)
      }
    }

    loadDetail()
  }, [id])

  const handleRepublish = async () => {
    if (!id) return

    setRepublishing(true)
    try {
      const result = await api.republishToWechat(parseInt(id))
      if (result.success) {
        alert(`重新发布成功！\n\n媒体ID: ${result.media_id}\n\n请到微信公众号后台查看草稿箱`)
        // 重新加载详情
        const detailResult = await api.getHistoryDetail(parseInt(id))
        if (detailResult.success && detailResult.data) {
          setHistory(detailResult.data)
        }
      } else {
        alert(result.message || '重新发布失败')
      }
    } catch (error) {
      console.error('重新发布失败:', error)
      alert('重新发布失败，请重试')
    } finally {
      setRepublishing(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
        <span className="ml-3 text-gray-600">加载中...</span>
      </div>
    )
  }

  if (!history) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">历史记录不存在</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>返回</span>
          </button>

          <button
            onClick={handleRepublish}
            disabled={republishing}
            className="px-6 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-5 h-5" />
            <span>{republishing ? '发布中...' : '重新发布'}</span>
          </button>
        </div>

        {/* 标题 */}
        <h1 className="text-3xl font-bold mb-4">{history.title}</h1>

        {/* 元信息 */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-6 pb-6 border-b">
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            <span>{formatDate(history.created_at)}</span>
          </div>
          <div className="flex items-center gap-1">
            <User className="w-4 h-4" />
            <span>{history.character_name || '未知角色'}</span>
          </div>
          <div className="flex items-center gap-1">
            <ImageIcon className="w-4 h-4" />
            <span>{history.input_type === 'topic' ? '主题生成' : '剧本粘贴'}</span>
          </div>
          {history.published_at && (
            <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
              已发布: {formatDate(history.published_at)}
            </span>
          )}
          {history.wechat_media_id && (
            <span className="text-xs text-gray-500">
              媒体ID: {history.wechat_media_id}
            </span>
          )}
        </div>

        {/* 输入文本 */}
        {history.input_text && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">输入内容</h2>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-gray-700">{history.input_text}</p>
            </div>
          </div>
        )}

        {/* 剧本内容 */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-3">剧本内容</h2>
          <div className="grid grid-cols-2 gap-4">
            {history.script_data.panels.map((panel) => (
              <div key={panel.panel_number} className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-2">第{panel.panel_number}格</h4>
                <p className="text-sm text-gray-600 mb-1"><strong>场景：</strong>{panel.scene_description}</p>
                <p className="text-sm text-gray-600 mb-1"><strong>动作：</strong>{panel.character_action}</p>
                <p className="text-sm text-gray-600"><strong>对话：</strong>{panel.dialogue}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 图片预览 */}
        <div>
          <h2 className="text-lg font-semibold mb-3">漫画图片</h2>
          {history.images && history.images.length > 0 ? (
            <div className="grid grid-cols-2 gap-4">
              {history.images.map((imageUrl, index) => (
                <div key={index} className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={imageUrl}
                    alt={`第${index + 1}格`}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              暂无图片
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
