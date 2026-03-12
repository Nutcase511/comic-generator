import { Loader2 } from 'lucide-react'

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${className}`} />
  )
}

interface ImageGenerationSkeletonProps {
  currentIndex?: number
  totalImages?: number
}

export function ImageGenerationSkeleton({
  currentIndex = 0,
  totalImages = 4
}: ImageGenerationSkeletonProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      {[1, 2, 3, 4].map((i) => {
        const isGenerating = i === currentIndex + 1
        const isCompleted = i < currentIndex + 1
        const isPending = i > currentIndex + 1

        return (
          <div
            key={i}
            className={`aspect-square rounded-lg overflow-hidden relative ${
              isCompleted ? 'bg-green-50 border-2 border-green-300' :
              isGenerating ? 'bg-blue-50 border-2 border-blue-300' :
              'bg-gray-100'
            }`}
          >
            {/* 状态图标 */}
            <div className="absolute inset-0 flex items-center justify-center">
              {isCompleted && (
                <div className="text-center">
                  <div className="text-5xl mb-2">✅</div>
                  <div className="text-sm font-medium text-green-600">已完成</div>
                </div>
              )}
              {isGenerating && (
                <div className="text-center">
                  <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-2" />
                  <div className="text-sm font-medium text-blue-600">生成中...</div>
                </div>
              )}
              {isPending && (
                <div className="text-center text-gray-400">
                  <div className="text-4xl mb-2">🎨</div>
                  <div className="text-sm font-medium">等待中</div>
                </div>
              )}
            </div>

            {/* 进度条 */}
            {isGenerating && (
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-200">
                <div className="h-full bg-blue-500 animate-progress" />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

interface ScriptGenerationSkeletonProps {
  step?: 'thinking' | 'writing' | 'polishing'
}

export function ScriptGenerationSkeleton({ step = 'thinking' }: ScriptGenerationSkeletonProps) {
  const steps = [
    { key: 'thinking', label: '分析主题', icon: '🤔' },
    { key: 'writing', label: '创作剧本', icon: '✍️' },
    { key: 'polishing', label: '优化细节', icon: '✨' }
  ]

  const currentStepIndex = steps.findIndex(s => s.key === step)

  return (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <Loader2 className="w-12 h-12 text-purple-500 animate-spin mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-gray-700">AI正在创作剧本...</h3>
      </div>

      {/* 步骤进度 */}
      <div className="space-y-3">
        {steps.map((s, index) => {
          const isCompleted = index < currentStepIndex
          const isCurrent = index === currentStepIndex
          const isPending = index > currentStepIndex

          return (
            <div
              key={s.key}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                isCompleted ? 'bg-green-50' :
                isCurrent ? 'bg-blue-50 border-2 border-blue-300' :
                'bg-gray-50'
              }`}
            >
              <div className={`text-2xl ${isPending ? 'grayscale opacity-50' : ''}`}>
                {isCompleted ? '✅' : s.icon}
              </div>
              <div className="flex-1">
                <div className={`font-medium ${
                  isCompleted ? 'text-green-700' :
                  isCurrent ? 'text-blue-700' :
                  'text-gray-500'
                }`}>
                  {s.label}
                </div>
                {isCurrent && (
                  <div className="text-sm text-blue-500 mt-1">
                    {step === 'thinking' && '正在分析主题内容...'}
                    {step === 'writing' && '正在编写四格漫画剧本...'}
                    {step === 'polishing' && '正在优化对话和场景...'}
                  </div>
                )}
              </div>
              {isCurrent && (
                <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
              )}
            </div>
          )
        })}
      </div>

      {/* 总体进度条 */}
      <div className="mt-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>创作进度</span>
          <span>{Math.round(((currentStepIndex + 1) / steps.length) * 100)}%</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-500"
            style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}

interface LoadingCardProps {
  title: string
  description?: string
}

export function LoadingCard({ title, description }: LoadingCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <div className="flex items-center gap-3 mb-6">
        <Loader2 className="w-6 h-6 text-purple-500 animate-spin" />
        <h2 className="text-2xl font-bold">{title}</h2>
      </div>
      {description && (
        <p className="text-gray-600 mb-6">{description}</p>
      )}

      {/* 骨架屏内容 */}
      <div className="space-y-4">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    </div>
  )
}
