/**
 * List Directory Node - Canvas Component
 *
 * Auto-generated from MCP tool schema.
 */

import React from 'react'
import type { FC } from 'react'
import type { NodeProps } from '../../../sdk/typescript/src/types'
import type { MCPListDirectoryNodeData } from './types'

export const MCPListDirectoryNode: FC<NodeProps<MCPListDirectoryNodeData>> = ({ data }) => {
  return (
    <div className="mb-1 px-3 py-1">
      <div className="flex items-center gap-2 rounded-md bg-gray-50 dark:bg-gray-800/50 p-2">
        <div className="text-2xl">📋</div>
        <div className="flex-1">
          <div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
            {data.path || 'List Directory'}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            MCP Tool
          </div>
        </div>
      </div>
    </div>
  )
}

export default React.memo(MCPListDirectoryNode)
