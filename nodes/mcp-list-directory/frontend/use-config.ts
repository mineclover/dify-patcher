/**
 * Configuration hook for List Directory Node
 *
 * Auto-generated from MCP tool schema.
 */

import { useCallback, useState } from 'react'
import { produce } from 'immer'
import type { MCPListDirectoryNodeData } from './types'
import type { UseConfigReturn } from '../../../sdk/typescript/src/types'

export const useConfig = (
  id: string,
  payload: MCPListDirectoryNodeData
): UseConfigReturn<MCPListDirectoryNodeData> => {
  const [inputs, setInputs] = useState<MCPListDirectoryNodeData>(payload)

  const handleFieldChange = useCallback(
    (field: keyof MCPListDirectoryNodeData) => {
      return (value: any) => {
        const newInputs = produce(inputs, (draft) => {
          ;(draft as any)[field] = value
        })
        setInputs(newInputs)
      }
    },
    [inputs, id]
  )

  const handleBulkChange = useCallback(
    (changes: Partial<MCPListDirectoryNodeData>) => {
      const newInputs = produce(inputs, (draft) => {
        Object.assign(draft, changes)
      })
      setInputs(newInputs)
    },
    [inputs, id]
  )

  return {
    inputs,
    readOnly: false,
    handleFieldChange,
    handleBulkChange,
  }
}
