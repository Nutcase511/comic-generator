import { useState, useEffect } from 'react'
import { User, ChevronDown, ChevronUp } from 'lucide-react'

interface Character {
  id: string
  name: string
  series: string
  series_order: number
  description: string
  prompt_keywords: string
}

interface CharacterGroup {
  series: string
  characters: Character[]
}

interface CharacterGridProps {
  selectedCharacter: string
  onCharacterSelect: (characterId: string) => void
  label?: string
}

export default function CharacterGrid({
  selectedCharacter,
  onCharacterSelect,
  label = '选择角色'
}: CharacterGridProps) {
  const [groups, setGroups] = useState<CharacterGroup[]>([])
  const [collapsedSeries, setCollapsedSeries] = useState<Set<string>>(new Set())
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadCharacters()
  }, [])

  const loadCharacters = async () => {
    try {
      const response = await fetch('/api/data/characters')
      const data = await response.json()
      if (data.characters) {
        // 按系列分组
        const grouped = data.characters.reduce((acc: { [key: string]: Character[] }, char: Character) => {
          if (!acc[char.series]) {
            acc[char.series] = []
          }
          acc[char.series].push(char)
          return acc
        }, {})

        // 转换为数组并排序
        const groupArray = Object.entries(grouped)
          .map(([series, chars]: [string, unknown]) => ({
            series,
            characters: (chars as Character[]).sort((a, b) => a.series_order - b.series_order)
          }))
          .sort((a, b) => a.series.localeCompare(b.series, 'zh-CN'))

        setGroups(groupArray)

        // 默认展开所有系列
        setCollapsedSeries(new Set())
      }
    } catch (error) {
      console.error('加载角色失败:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleSeries = (series: string) => {
    setCollapsedSeries(prev => {
      const newSet = new Set(prev)
      if (newSet.has(series)) {
        newSet.delete(series)
      } else {
        newSet.add(series)
      }
      return newSet
    })
  }

  if (isLoading) {
    return (
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          {label}
        </label>
        <div className="animate-pulse">
          <div className="h-32 bg-gray-200 rounded-xl"></div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-3">
        {label}
      </label>
      <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
        {groups.map((group) => {
          const isCollapsed = collapsedSeries.has(group.series)
          return (
            <div key={group.series} className="border-2 border-gray-200 rounded-xl overflow-hidden">
              {/* 系列标题 */}
              <button
                onClick={() => toggleSeries(group.series)}
                className="w-full px-4 py-2 bg-gradient-to-r from-purple-50 to-blue-50 hover:from-purple-100 hover:to-blue-100 transition-colors flex items-center justify-between"
              >
                <span className="font-semibold text-gray-800 text-sm">
                  {group.series}
                </span>
                {isCollapsed ? (
                  <ChevronDown className="w-4 h-4 text-gray-600" />
                ) : (
                  <ChevronUp className="w-4 h-4 text-gray-600" />
                )}
              </button>

              {/* 角色列表 */}
              {!isCollapsed && (
                <div className="p-3 bg-white grid grid-cols-4 gap-2">
                  {group.characters.map((char) => (
                    <button
                      key={char.id}
                      onClick={() => onCharacterSelect(char.id)}
                      className={`p-2 rounded-lg border-2 transition-all ${
                        selectedCharacter === char.id
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-purple-300 hover:bg-purple-50'
                      }`}
                      title={char.description}
                    >
                      <div className="flex flex-col items-center gap-1">
                        <User className="w-5 h-5 text-gray-600" />
                        <span className="text-xs font-medium text-gray-700 text-center">
                          {char.name}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
