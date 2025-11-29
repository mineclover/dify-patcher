/**
 * Default configuration for List Directory Node
 *
 * Auto-generated from MCP tool schema.
 */

import type { NodeDefault, ValidationResult } from '../../../sdk/typescript/src/types'
import { VarType } from '../../../sdk/typescript/src/types'
import type { MCPListDirectoryNodeData } from './types'

export const mcplistdirectoryDefault: NodeDefault<MCPListDirectoryNodeData> = {
  defaultValue: {
    title: 'List Directory',
    desc: 'List files and directories in a specified path. Returns file names, sizes, and modification times.',
    type: 'mcp-list-directory',
    mcp_server_url: '',
    path: '',
  },

  checkValid(payload: MCPListDirectoryNodeData, t: any): ValidationResult {
    if (!payload.mcp_server_url || payload.mcp_server_url.trim() === '') {
      return {
        isValid: false,
        errorMessage: t?.('workflow.nodes.mcp.serverUrlRequired') || 'MCP Server URL is required',
      }
    }
    if (!payload.path || (typeof payload.path === 'string' && payload.path.trim() === '')) {
      return {
        isValid: false,
        errorMessage: t?.('workflow.nodes.mcp-list-directory.pathRequired') || 'Path is required',
      }
    }

    return {
      isValid: true,
    }
  },

  getOutputVars(payload: MCPListDirectoryNodeData) {
    return [
      {
        variable: 'text',
        type: VarType.String,
        description: 'Text content from tool result',
      },
      {
        variable: 'result',
        type: VarType.Object,
        description: 'Full tool result object',
      },
      {
        variable: 'is_error',
        type: VarType.Boolean,
        description: 'Whether the tool returned an error',
      },
    ]
  },
}
