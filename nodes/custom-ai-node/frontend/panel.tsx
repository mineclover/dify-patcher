/**
 * Custom AI Node - Configuration Panel
 */

import React from 'react'
import type { FC } from 'react'

interface CustomAIConfig {
  api_endpoint: string
  api_key: string
  model_name: string
  temperature: number
  max_tokens: number
  use_custom_format: boolean
  custom_headers: Record<string, string>
  timeout: number
}

interface CustomAIPanelProps {
  config: CustomAIConfig
  onChange: (config: CustomAIConfig) => void
}

export const CustomAIPanel: FC<CustomAIPanelProps> = ({
  config,
  onChange,
}) => {
  const handleChange = (field: keyof CustomAIConfig, value: any) => {
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
            placeholder="https://api.example.com/v1/chat/completions"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <p className="mt-1 text-xs text-gray-500">
            The endpoint URL for your custom AI service
          </p>
        </div>

        {/* API Key */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            API Key <span className="text-red-500">*</span>
          </label>
          <input
            type="password"
            value={config.api_key}
            onChange={(e) => handleChange('api_key', e.target.value)}
            placeholder="sk-..."
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <p className="mt-1 text-xs text-gray-500">
            Authentication key for the API
          </p>
        </div>

        {/* Model Name */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Model Name
          </label>
          <input
            type="text"
            value={config.model_name}
            onChange={(e) => handleChange('model_name', e.target.value)}
            placeholder="gpt-4"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Model Parameters Section */}
      <div className="space-y-3 pt-4 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900">
          Model Parameters
        </h3>

        {/* Temperature */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Temperature: {config.temperature}
          </label>
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={config.temperature}
            onChange={(e) =>
              handleChange('temperature', parseFloat(e.target.value))
            }
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Precise</span>
            <span>Creative</span>
          </div>
        </div>

        {/* Max Tokens */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Max Tokens
          </label>
          <input
            type="number"
            min="1"
            max="32000"
            value={config.max_tokens}
            onChange={(e) =>
              handleChange('max_tokens', parseInt(e.target.value))
            }
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <p className="mt-1 text-xs text-gray-500">
            Maximum number of tokens to generate
          </p>
        </div>

        {/* Timeout */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Timeout (seconds)
          </label>
          <input
            type="number"
            min="1"
            max="300"
            value={config.timeout}
            onChange={(e) => handleChange('timeout', parseInt(e.target.value))}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Special Interface Section */}
      <div className="space-y-3 pt-4 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900">
          Special Interface Options
        </h3>

        {/* Use Custom Format */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="use_custom_format"
            checked={config.use_custom_format}
            onChange={(e) =>
              handleChange('use_custom_format', e.target.checked)
            }
            className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
          />
          <label
            htmlFor="use_custom_format"
            className="text-xs font-medium text-gray-700"
          >
            Use Custom Request/Response Format
          </label>
        </div>
        <p className="text-xs text-gray-500 ml-6">
          Enable this if your AI service uses a non-standard format
        </p>

        {/* Custom Headers */}
        {config.use_custom_format && (
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Custom Headers (JSON)
            </label>
            <textarea
              value={JSON.stringify(config.custom_headers, null, 2)}
              onChange={(e) => {
                try {
                  const headers = JSON.parse(e.target.value)
                  handleChange('custom_headers', headers)
                }
                catch {
                  // Invalid JSON, ignore
                }
              }}
              placeholder='{"X-Custom-Header": "value"}'
              rows={4}
              className="w-full px-3 py-2 text-sm font-mono border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-900">
          <strong>Note:</strong> This node supports custom AI services with
          special interfaces. Configure the API endpoint and authentication,
          then adjust the parameters based on your service&apos;s requirements.
        </p>
      </div>
    </div>
  )
}
