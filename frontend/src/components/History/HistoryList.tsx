import { useState, useEffect } from 'react'
import { History, Trash2, Eye, Send, Calendar, User, Image as ImageIcon } from 'lucide-react'
import { api, HistoryItem } from '../../services/api'

interface HistoryListProps {
  onRepublish?: (historyId: number) => void
  onView?: (historyId: number) => void
}

export default function HistoryList({ onRepublish, onView }: HistoryListProps) {
  const [histories, setHistories] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(0)
  const [filterType, setFilterType] = useState<'all' | 'topic' | 'paste'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const pageSize = 20

  const loadHistories = async () => {
    setLoading(true)
    try {
      const result = await api.getHistoryList(pageSize, currentPage * pageSize)
      if (result.success) {
        setHistories(result.data || [])
        setTotal(result.total || 0)
      }
    } catch (error) {
      console.error('加载历史记录失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistories()
  }, [currentPage])

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这条历史记录吗？')) return

    try {
      // TODO: 添加删除API
      alert('删除功能待实现')
      loadHistories()
    } catch (error) {
      console.error('删除失败:', error)
      alert('删除失败')
    }
  }

  const handleRepublish = async (id: number) => {
    if (!confirm('确定要重新发布到微信公众号吗？')) return

    try {
      const result = await api.republishToWechat(id)
      if (result.success) {
        alert(`重新发布成功！\n\n媒体ID: ${result.media_id}\n\n请到微信公众号后台查看草稿箱`)
        loadHistories()
        onRepublish?.(id)
      } else {
        alert(result.message || '重新发布失败')
      }
    } catch (error) {
      console.error('重新发布失败:', error)
      alert('重新发布失败，请重试')
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

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8">
        {/* 标题和统计 */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <History className="w-6 h-6 text-purple-500" />
            <h2 className="text-2xl font-bold">历史记录</h2>
            <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
              共 {total} 条
            </span>
          </div>
        </div>

        {/* 筛选和搜索 */}
        <div className="flex gap-4 mb-6">
          <div className="flex gap-2">
            {(['all', 'topic', 'paste'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  filterType === type
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {type === 'all' ? '全部' : type === 'topic' ? '主题生成' : '剧本粘贴'}
              </button>
            ))}
          </div>
          <div className="flex-1">
            <input
              type="text"
              placeholder="搜索标题或内容..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:outline-none"
            />
          </div>
        </div>

        {/* 加载状态 */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            <span className="ml-3 text-gray-600">加载中...</span>
          </div>
        ) : histories.length === 0 ? (
          /* 空状态 */
          <div className="text-center py-12">
            <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">暂无历史记录</p>
          </div>
        ) : (
          /* 历史记录列表 */
          <div className="space-y-4">
            {histories.map((item) => (
              <div
                key={item.id}
                className="border-2 border-gray-200 rounded-xl p-5 hover:border-purple-300 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* 标题 */}
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">{item.title}</h3>

                    {/* 元信息 */}
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(item.created_at)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <User className="w-4 h-4" />
                        <span>{item.character_name || '未知角色'}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <ImageIcon className="w-4 h-4" />
                        <span>{item.input_type === 'topic' ? '主题生成' : '剧本粘贴'}</span>
                      </div>
                      {item.published_at && (
                        <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                          已发布
                        </span>
                      )}
                    </div>

                    {/* 微信媒体ID */}
                    {item.wechat_media_id && (
                      <div className="text-xs text-gray-500">
                        媒体ID: {item.wechat_media_id}
                      </div>
                    )}
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => onView?.(item.id)}
                      className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                      title="查看详情"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleRepublish(item.id)}
                      className="p-2 text-green-500 hover:bg-green-50 rounded-lg transition-colors"
                      title="重新发布"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      title="删除"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 分页 */}
        {total > pageSize && (
          <div className="flex justify-center items-center gap-2 mt-6">
            <button
              onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
              disabled={currentPage === 0}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一页
            </button>
            <span className="text-gray-600">
              第 {currentPage + 1} 页，共 {Math.ceil(total / pageSize)} 页
            </span>
            <button
              onClick={() => setCurrentPage(Math.min(Math.ceil(total / pageSize) - 1, currentPage + 1))}
              disabled={currentPage >= Math.ceil(total / pageSize) - 1}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一页
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
