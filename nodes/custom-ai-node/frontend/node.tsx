/**
 * Custom AI Node - Visual Component
 */

import React from 'react'
import type { NodeProps } from 'reactflow'

interface CustomAINodeData {
  title: string
  desc?: string
  selected?: boolean
  _runningStatus?: string
}

export const CustomAINode: React.FC<NodeProps<CustomAINodeData>> = ({
  data,
  selected,
}) => {
  const isRunning = data._runningStatus === 'running'
  const isFailed = data._runningStatus === 'failed'
  const isSuccess = data._runningStatus === 'success'

  return (
    <div
      className={`
        relative rounded-lg border-2 bg-white shadow-sm transition-all
        ${selected ? 'border-primary-600 shadow-lg' : 'border-gray-200'}
        ${isRunning ? 'border-blue-500' : ''}
        ${isFailed ? 'border-red-500' : ''}
        ${isSuccess ? 'border-green-500' : ''}
        min-w-[240px] max-w-[320px]
      `}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2 border-b border-gray-200">
        <div className="text-2xl">🤖</div>
        <div className="flex-1">
          <div className="text-sm font-semibold text-gray-900">
            {data.title || 'Custom AI'}
          </div>
          {data.desc && (
            <div className="text-xs text-gray-500 truncate">
              {data.desc}
            </div>
          )}
        </div>
        {isRunning && (
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
        )}
      </div>

      {/* Body */}
      <div className="px-3 py-2 space-y-2">
        <div className="text-xs text-gray-600">
          Custom AI with special interface
        </div>
      </div>

      {/* Status indicator */}
      {(isRunning || isFailed || isSuccess) && (
        <div className="px-3 py-1 border-t border-gray-200">
          <div
            className={`
              text-xs font-medium
              ${isRunning ? 'text-blue-600' : ''}
              ${isFailed ? 'text-red-600' : ''}
              ${isSuccess ? 'text-green-600' : ''}
            `}
          >
            {isRunning && 'Running...'}
            {isFailed && 'Failed'}
            {isSuccess && 'Success'}
          </div>
        </div>
      )}
    </div>
  )
}
