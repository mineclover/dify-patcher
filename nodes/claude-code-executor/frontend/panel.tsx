/**
 * Claude Code Executor Node - Configuration Panel
 */

import React from 'react'
import type { FC } from 'react'

interface ClaudeCodeExecutorConfig {
  api_endpoint: string
  api_key: string
  execution_mode: 'single' | 'loop'
  max_iterations: number
  loop_delay: number
  stop_on_error: boolean
  timeout: number
  working_directory: string
}

interface ClaudeCodeExecutorPanelProps {
  config: ClaudeCodeExecutorConfig
  onChange: (config: ClaudeCodeExecutorConfig) => void
}

export const ClaudeCodeExecutorPanel: FC<ClaudeCodeExecutorPanelProps> = ({
  config,
  onChange,
}) => {
  const handleChange = (
    field: keyof ClaudeCodeExecutorConfig,
    value: any,
  ) => {
    onChange({
      ...config,
      [field]: value,
    })
  }

  return (
    <div className="space-y-4">
      {/* API Configuration Section */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-gray-900">
          API Configuration
        </h3>

        {/* API Endpoint */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            API Endpoint <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={config.api_endpoint}
            onChange={(e) => handleChange('api_endpoint', e.target.value)}
            placeholder="http://localhost:3000"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <p className="mt-1 text-xs text-gray-500">
            Claude Code API server endpoint
          </p>
        </div>

        {/* API Key */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            API Key (Optional)
          </label>
          <input
            type="password"
            value={config.api_key}
            onChange={(e) => handleChange('api_key', e.target.value)}
            placeholder="Enter API key if required"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Working Directory */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Working Directory
          </label>
          <input
            type="text"
            value={config.working_directory}
            onChange={(e) =>
              handleChange('working_directory', e.target.value)
            }
            placeholder="/path/to/project"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <p className="mt-1 text-xs text-gray-500">
            Working directory for Claude Code execution
          </p>
        </div>

        {/* Timeout */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Timeout (seconds)
          </label>
          <input
            type="number"
            min="10"
            max="3600"
            value={config.timeout}
            onChange={(e) => handleChange('timeout', parseInt(e.target.value))}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Execution Mode Section */}
      <div className="space-y-3 pt-4 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900">
          Execution Mode
        </h3>

        {/* Mode Selection */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-2">
            Mode
          </label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => handleChange('execution_mode', 'single')}
              className={`
                flex-1 px-4 py-2 text-sm font-medium rounded-lg border transition-colors
                ${
                  config.execution_mode === 'single'
                    ? 'bg-primary-50 border-primary-500 text-primary-700'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }
              `}
            >
              Single
            </button>
            <button
              type="button"
              onClick={() => handleChange('execution_mode', 'loop')}
              className={`
                flex-1 px-4 py-2 text-sm font-medium rounded-lg border transition-colors
                ${
                  config.execution_mode === 'loop'
                    ? 'bg-purple-50 border-purple-500 text-purple-700'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }
              `}
            >
              Loop
            </button>
          </div>
        </div>

        {/* Loop Configuration (only show when loop mode is selected) */}
        {config.execution_mode === 'loop' && (
          <div className="space-y-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
            <h4 className="text-xs font-semibold text-purple-900">
              Loop Configuration
            </h4>

            {/* Max Iterations */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Max Iterations
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={config.max_iterations}
                onChange={(e) =>
                  handleChange('max_iterations', parseInt(e.target.value))
                }
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                Maximum number of loop iterations (1-100)
              </p>
            </div>

            {/* Loop Delay */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Loop Delay (seconds)
              </label>
              <input
                type="number"
                min="0"
                max="60"
                step="0.1"
                value={config.loop_delay}
                onChange={(e) =>
                  handleChange('loop_delay', parseFloat(e.target.value))
                }
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                Delay between iterations
              </p>
            </div>

            {/* Stop on Error */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="stop_on_error"
                checked={config.stop_on_error}
                onChange={(e) =>
                  handleChange('stop_on_error', e.target.checked)
                }
                className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
              />
              <label
                htmlFor="stop_on_error"
                className="text-xs font-medium text-gray-700"
              >
                Stop on Error
              </label>
            </div>
            <p className="text-xs text-gray-500 ml-6">
              Stop loop execution when an error occurs
            </p>
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-900">
          <strong>Note:</strong> This node executes Claude Code CLI via API
          server. Make sure your API server is running at the specified
          endpoint.
          {config.execution_mode === 'loop' && (
            <>
              {' '}
              In loop mode, the prompt will be executed{' '}
              <strong>{config.max_iterations}</strong> times with{' '}
              <strong>{config.loop_delay}s</strong> delay between iterations.
            </>
          )}
        </p>
      </div>
    </div>
  )
}
