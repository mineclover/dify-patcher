/**
 * Custom AI Node - Frontend Components
 *
 * This file exports the node and panel components for the Custom AI node.
 */

import manifest from '../manifest.json'

export { CustomAINode as NodeComponent } from './node'
export { CustomAIPanel as PanelComponent } from './panel'
export { customAIDefault as defaultConfig } from './default'

export const nodeType = manifest.node_type
export { manifest }
