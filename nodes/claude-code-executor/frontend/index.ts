/**
 * Claude Code Executor Node - Frontend Components
 *
 * This file exports the node and panel components for the Claude Code Executor node.
 */

import manifest from '../manifest.json'

export { ClaudeCodeExecutorNode as NodeComponent } from './node'
export { ClaudeCodeExecutorPanel as PanelComponent } from './panel'
export { claudeCodeExecutorDefault as defaultConfig } from './default'

export const nodeType = manifest.node_type
export { manifest }
