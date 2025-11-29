/**
 * Type definitions for List Directory Node
 *
 * Auto-generated from MCP tool schema.
 */

import type { CustomNodeData } from '../../../sdk/typescript/src/types'

export interface MCPListDirectoryNodeData extends CustomNodeData {
  type: 'mcp-list-directory'
  mcp_server_url: string
  path: string
}
