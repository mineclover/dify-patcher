/**
 * Claude Code Executor Node - Visual Component
 */

import React from 'react'
import type { NodeProps } from 'reactflow'

interface ClaudeCodeExecutorNodeData {
  title: string
  desc?: string
  selected?: boolean
  _runningStatus?: string
  config?: {
    execution_mode?: string
    max_iterations?: number
  }
}

export const ClaudeCodeExecutorNode: React.FC<
  NodeProps<ClaudeCodeExecutorNodeData>
> = ({ data, selected }) => {
  const isRunning = data._runningStatus === 'running'
  const isFailed = data._runningStatus === 'failed'
  const isSuccess = data._runningStatus === 'success'
  const isLoop = data.config?.execution_mode === 'loop'

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
            {data.title || 'Claude Code Executor'}
          </div>
          {data.desc && (
            <div className="text-xs text-gray-500 truncate">{data.desc}</div>
          )}
        </div>
        {isRunning && (
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
        )}
      </div>

      {/* Body */}
      <div className="px-3 py-2 space-y-1">
        <div className="flex items-center gap-2 text-xs">
          <span className="text-gray-600">Mode:</span>
          <span
            className={`font-medium ${
              isLoop ? 'text-purple-600' : 'text-blue-600'
            }`}
          >
            {isLoop ? 'Loop' : 'Single'}
          </span>
          {isLoop && data.config?.max_iterations && (
            <span className="text-gray-500">
              (max {data.config.max_iterations})
            </span>
          )}
        </div>
        <div className="text-xs text-gray-600">
          Execute Claude Code via API
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
            {isRunning && 'Executing...'}
            {isFailed && 'Failed'}
            {isSuccess && 'Success'}
          </div>
        </div>
      )}
    </div>
  )
}
