/**
 * List Directory Node - Configuration Panel
 *
 * Auto-generated from MCP tool schema.
 */

import React from 'react'
import type { FC } from 'react'
import { useConfig } from './use-config'
import type { NodePanelProps } from '../../../sdk/typescript/src/types'
import type { MCPListDirectoryNodeData } from './types'

interface FieldProps {
  title: string
  required?: boolean
  children: React.ReactNode
}

const Field: FC<FieldProps> = ({ title, required, children }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
      {title}{required && <span className="text-red-500 ml-1">*</span>}
    </label>
    {children}
  </div>
)

interface InputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  type?: string
}

const Input: FC<InputProps> = ({ value, onChange, placeholder, type = 'text' }) => (
  <input
    type={type}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder}
    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
  />
)

interface SelectProps {
  value: string
  onChange: (value: string) => void
  options: Array<{ value: string; label: string }>
}

const Select: FC<SelectProps> = ({ value, onChange, options }) => (
  <select
    value={value}
    onChange={(e) => onChange(e.target.value)}
    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
  >
    {options.map((option) => (
      <option key={option.value} value={option.value}>
        {option.label}
      </option>
    ))}
  </select>
)

interface SwitchProps {
  checked: boolean
  onChange: (checked: boolean) => void
}

const Switch: FC<SwitchProps> = ({ checked, onChange }) => (
  <button
    type="button"
    role="switch"
    aria-checked={checked}
    onClick={() => onChange(!checked)}
    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${checked ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}`}
  >
    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${checked ? 'translate-x-6' : 'translate-x-1'}`} />
  </button>
)

export const MCPListDirectoryPanel: FC<NodePanelProps<MCPListDirectoryNodeData>> = ({ id, data }) => {
  const { inputs, handleFieldChange, readOnly } = useConfig(id, data)

  return (
    <div className="mt-2">
      <div className="space-y-4 px-4 pb-4">

        <Field title="MCP Server URL" required>
          <Input
            value={inputs.mcp_server_url || ''}
            onChange={handleFieldChange('mcp_server_url')}
            placeholder="MCP server endpoint URL"
          />
          <div className="mt-1 text-xs text-gray-500">SSE or HTTP endpoint for MCP server</div>
        </Field>

        <Field title="Path" required>
          <Input
            
            value={inputs.path || ''}
            onChange={handleFieldChange('path')}
            placeholder="Enter path"
          />
          <div className="mt-1 text-xs text-gray-500">The directory path to list</div>
        </Field>

        <div className="rounded-md bg-blue-50 dark:bg-blue-900/20 p-3">
          <div className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
            📋 Output Variables
          </div>
          <div className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
            <div>• <code>text</code> - Text content from result</div>
            <div>• <code>result</code> - Full result object</div>
            <div>• <code>is_error</code> - Whether tool returned error</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default React.memo(MCPListDirectoryPanel)
