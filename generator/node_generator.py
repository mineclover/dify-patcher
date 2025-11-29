"""
Custom Node Generator

Generates dify-patcher custom node code from MCP tool schemas.
"""

import json
import os
from pathlib import Path
from typing import Any

from .schema_extractor import MCPToolSchema


class CustomNodeGenerator:
    """
    Generates complete custom node packages from MCP tool schemas.

    Each generated node includes:
    - manifest.json - Node metadata
    - backend/
      - __init__.py
      - node.py - Python implementation
    - frontend/
      - index.ts - Exports
      - types.ts - TypeScript types
      - node.tsx - Canvas component
      - panel.tsx - Configuration panel
      - use-config.ts - Config hook
      - default.ts - Default values
    """

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)

    def generate(self, schema: MCPToolSchema, server_url: str = '') -> Path:
        """
        Generate a complete custom node from an MCP tool schema.

        Args:
            schema: MCP tool schema
            server_url: MCP server URL for the node to connect to

        Returns:
            Path to the generated node directory
        """
        node_dir = self.output_dir / schema.node_type
        node_dir.mkdir(parents=True, exist_ok=True)

        # Generate all files
        self._generate_manifest(node_dir, schema)
        self._generate_backend(node_dir, schema, server_url)
        self._generate_frontend(node_dir, schema)

        return node_dir

    def generate_all(
        self,
        schemas: list[MCPToolSchema],
        server_url: str = '',
    ) -> list[Path]:
        """
        Generate nodes for all schemas.

        Args:
            schemas: List of MCP tool schemas
            server_url: MCP server URL

        Returns:
            List of paths to generated node directories
        """
        return [self.generate(schema, server_url) for schema in schemas]

    def _generate_manifest(self, node_dir: Path, schema: MCPToolSchema) -> None:
        """Generate manifest.json."""
        manifest = {
            'node_type': schema.node_type,
            'version': '1',
            'name': self._format_name(schema.name),
            'description': schema.description or f'MCP tool: {schema.name}',
            'author': 'MCP Node Generator',
            'icon': self._get_icon(schema),
            'category': 'mcp-tools',
            'backend': {
                'entry': 'node.py',
                'dependencies': ['httpx>=0.27.0'],
            },
            'frontend': {
                'entry': 'index.ts',
            },
            'inputs': self._generate_input_schema(schema),
            'outputs': self._generate_output_schema(schema),
        }

        with open(node_dir / 'manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)

    def _generate_backend(
        self,
        node_dir: Path,
        schema: MCPToolSchema,
        server_url: str,
    ) -> None:
        """Generate backend Python files."""
        backend_dir = node_dir / 'backend'
        backend_dir.mkdir(exist_ok=True)

        # __init__.py
        with open(backend_dir / '__init__.py', 'w') as f:
            f.write('')

        # node.py
        node_code = self._generate_node_py(schema, server_url)
        with open(backend_dir / 'node.py', 'w') as f:
            f.write(node_code)

    def _generate_frontend(self, node_dir: Path, schema: MCPToolSchema) -> None:
        """Generate frontend TypeScript/React files."""
        frontend_dir = node_dir / 'frontend'
        frontend_dir.mkdir(exist_ok=True)

        # Generate all frontend files
        files = {
            'index.ts': self._generate_index_ts(schema),
            'types.ts': self._generate_types_ts(schema),
            'node.tsx': self._generate_node_tsx(schema),
            'panel.tsx': self._generate_panel_tsx(schema),
            'use-config.ts': self._generate_use_config_ts(schema),
            'default.ts': self._generate_default_ts(schema),
        }

        for filename, content in files.items():
            with open(frontend_dir / filename, 'w') as f:
                f.write(content)

    def _format_name(self, name: str) -> str:
        """Format tool name for display."""
        # Convert snake_case or kebab-case to Title Case
        words = name.replace('_', ' ').replace('-', ' ').split()
        return ' '.join(word.capitalize() for word in words)

    def _get_icon(self, schema: MCPToolSchema) -> str:
        """Get an appropriate icon for the tool."""
        name = schema.name.lower()

        # Map common tool types to icons
        icon_map = {
            'file': '📁',
            'read': '📖',
            'write': '📝',
            'search': '🔍',
            'list': '📋',
            'delete': '🗑️',
            'create': '➕',
            'edit': '✏️',
            'get': '📥',
            'send': '📤',
            'api': '🔌',
            'http': '🌐',
            'database': '🗃️',
            'query': '❓',
            'execute': '▶️',
            'run': '🏃',
        }

        for keyword, icon in icon_map.items():
            if keyword in name:
                return icon

        return '🔧'  # Default icon

    def _generate_input_schema(self, schema: MCPToolSchema) -> dict[str, Any]:
        """Generate input schema for manifest."""
        inputs = {
            'mcp_server_url': {
                'type': 'string',
                'title': 'MCP Server URL',
                'description': 'MCP server endpoint (SSE or HTTP)',
                'required': True,
            }
        }
        properties = schema.properties
        required = schema.required_fields

        for prop_name, prop_schema in properties.items():
            input_def: dict[str, Any] = {
                'type': prop_schema.get('type', 'string'),
                'title': self._format_name(prop_name),
            }

            if 'description' in prop_schema:
                input_def['description'] = prop_schema['description']

            if prop_name in required:
                input_def['required'] = True

            if 'default' in prop_schema:
                input_def['default'] = prop_schema['default']

            if 'enum' in prop_schema:
                input_def['enum'] = prop_schema['enum']

            inputs[prop_name] = input_def

        return inputs

    def _generate_output_schema(self, schema: MCPToolSchema) -> dict[str, Any]:
        """Generate output schema for manifest."""
        return {
            'text': {
                'type': 'string',
                'description': 'Text content from tool result',
            },
            'result': {
                'type': 'object',
                'description': 'Full tool result object',
            },
            'is_error': {
                'type': 'boolean',
                'description': 'Whether the tool returned an error',
            },
        }

    def _generate_node_py(self, schema: MCPToolSchema, server_url: str) -> str:
        """Generate node.py content."""
        properties = schema.properties
        required = schema.required_fields

        # Build input extraction code
        input_lines = []
        validation_lines = []

        for prop_name, prop_schema in properties.items():
            default = prop_schema.get('default', "''")
            if isinstance(default, str):
                default = f"'{default}'"
            elif default is None:
                default = 'None'

            input_lines.append(
                f"        {prop_name} = self.get_input('{prop_name}', {default})"
            )

            if prop_name in required:
                validation_lines.append(f"""
        if not {prop_name}:
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                inputs={{{', '.join(f"'{p}': {p}" for p in properties.keys())}}},
                outputs={{}},
                error="{self._format_name(prop_name)} is required"
            )""")

        inputs_str = '\n'.join(input_lines)
        validations_str = ''.join(validation_lines)
        params_dict = ', '.join(f"'{p}': {p}" for p in properties.keys())

        return f'''"""
{self._format_name(schema.name)} Node

Auto-generated from MCP tool schema.
{schema.description or ''}
"""

from typing import Any

from core.dify_custom_nodes import BaseCustomNode, register_node
from core.workflow.enums import WorkflowNodeExecutionStatus
from core.workflow.node_events import NodeRunResult


@register_node('{schema.node_type}', version='1', author='MCP Node Generator')
class {schema.class_name}(BaseCustomNode):
    """
    MCP Tool: {schema.name}

    {schema.description or 'No description available.'}
    """

    # MCP Tool name (server URL is provided via node input)
    MCP_TOOL_NAME = '{schema.name}'

    @classmethod
    def version(cls) -> str:
        return "1"

    def _run(self) -> NodeRunResult:
        """Execute MCP tool invocation."""
        # Get MCP server URL from node input
        mcp_server_url = self.get_input('mcp_server_url', '')
        if not mcp_server_url:
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                inputs={{}},
                outputs={{}},
                error="MCP Server URL is required"
            )

        # Extract inputs
{inputs_str}
{validations_str}

        # Build tool parameters
        tool_params = {{{params_dict}}}

        try:
            # Invoke MCP tool
            result = self._invoke_mcp_tool(mcp_server_url, tool_params)

            # Process result
            text_content = self._extract_text(result)
            is_error = result.get('isError', False)

            if is_error:
                return NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    inputs=tool_params,
                    outputs={{'text': text_content, 'result': result, 'is_error': True}},
                    error=text_content or "Tool returned an error"
                )

            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                inputs=tool_params,
                outputs={{
                    'text': text_content,
                    'result': result,
                    'is_error': False,
                }}
            )

        except Exception as e:
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                inputs=tool_params,
                outputs={{}},
                error=f"MCP tool invocation failed: {{str(e)}}"
            )

    def _invoke_mcp_tool(self, server_url: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Invoke the MCP tool via HTTP/SSE.

        Override this method to customize the invocation logic.
        """
        try:
            from core.mcp import MCPClient

            with MCPClient(server_url=server_url, timeout=30.0) as client:
                result = client.invoke_tool(self.MCP_TOOL_NAME, params)
                return self._convert_result(result)

        except ImportError:
            # Fallback to standalone HTTP invocation
            return self._invoke_via_http(server_url, params)

    def _invoke_via_http(self, server_url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Fallback HTTP invocation without Dify's MCPClient."""
        import httpx

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                server_url,
                json={{
                    'jsonrpc': '2.0',
                    'id': 1,
                    'method': 'tools/call',
                    'params': {{
                        'name': self.MCP_TOOL_NAME,
                        'arguments': params,
                    }},
                }},
                headers={{'Content-Type': 'application/json'}},
            )
            response.raise_for_status()
            result = response.json()
            return result.get('result', {{}})

    def _convert_result(self, result: Any) -> dict[str, Any]:
        """Convert MCPClient result to dictionary."""
        if hasattr(result, 'content'):
            return {{
                'content': [
                    {{'type': c.type, 'text': getattr(c, 'text', None)}}
                    for c in result.content
                ] if result.content else [],
                'structuredContent': result.structuredContent,
                'isError': result.isError,
            }}
        return result if isinstance(result, dict) else {{'raw': result}}

    def _extract_text(self, result: dict[str, Any]) -> str:
        """Extract text content from tool result."""
        content = result.get('content', [])
        text_parts = []

        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                text_parts.append(item.get('text', ''))
            elif hasattr(item, 'type') and item.type == 'text':
                text_parts.append(getattr(item, 'text', ''))

        return '\\n'.join(text_parts)
'''

    def _generate_index_ts(self, schema: MCPToolSchema) -> str:
        """Generate index.ts content."""
        component_name = schema.class_name.replace('Node', '')
        return f'''/**
 * {self._format_name(schema.name)} - Frontend Components
 *
 * Auto-generated from MCP tool schema.
 */

import manifest from '../manifest.json'

export {{ {component_name}Node as NodeComponent }} from './node'
export {{ {component_name}Panel as PanelComponent }} from './panel'
export {{ {schema.node_type.replace('-', '')}Default as defaultConfig }} from './default'

export const nodeType = manifest.node_type
export {{ manifest }}
'''

    def _generate_types_ts(self, schema: MCPToolSchema) -> str:
        """Generate types.ts content."""
        properties = schema.properties

        # Build interface fields (mcp_server_url first)
        fields = ['  mcp_server_url: string']
        for prop_name, prop_schema in properties.items():
            ts_type = schema.get_typescript_type(prop_schema)
            optional = '?' if prop_name not in schema.required_fields else ''
            fields.append(f'  {prop_name}{optional}: {ts_type}')

        fields_str = '\n'.join(fields)
        interface_name = f'{schema.class_name.replace("Node", "")}NodeData'

        return f'''/**
 * Type definitions for {self._format_name(schema.name)} Node
 *
 * Auto-generated from MCP tool schema.
 */

import type {{ CustomNodeData }} from '../../../sdk/typescript/src/types'

export interface {interface_name} extends CustomNodeData {{
  type: '{schema.node_type}'
{fields_str}
}}
'''

    def _generate_node_tsx(self, schema: MCPToolSchema) -> str:
        """Generate node.tsx content."""
        component_name = schema.class_name.replace('Node', '')
        interface_name = f'{component_name}NodeData'

        # Get first property for display
        first_prop = next(iter(schema.properties.keys()), None)
        display_content = f"data.{first_prop}" if first_prop else "'MCP Tool'"

        return f'''/**
 * {self._format_name(schema.name)} Node - Canvas Component
 *
 * Auto-generated from MCP tool schema.
 */

import React from 'react'
import type {{ FC }} from 'react'
import type {{ NodeProps }} from '../../../sdk/typescript/src/types'
import type {{ {interface_name} }} from './types'

export const {component_name}Node: FC<NodeProps<{interface_name}>> = ({{ data }}) => {{
  return (
    <div className="mb-1 px-3 py-1">
      <div className="flex items-center gap-2 rounded-md bg-gray-50 dark:bg-gray-800/50 p-2">
        <div className="text-2xl">{self._get_icon(schema)}</div>
        <div className="flex-1">
          <div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
            {{{display_content} || '{self._format_name(schema.name)}'}}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            MCP Tool
          </div>
        </div>
      </div>
    </div>
  )
}}

export default React.memo({component_name}Node)
'''

    def _generate_panel_tsx(self, schema: MCPToolSchema) -> str:
        """Generate panel.tsx content."""
        component_name = schema.class_name.replace('Node', '')
        interface_name = f'{component_name}NodeData'
        properties = schema.properties
        required = schema.required_fields

        # Build form fields - MCP Server URL first
        field_components = ['''
        <Field title="MCP Server URL" required>
          <Input
            value={inputs.mcp_server_url || ''}
            onChange={handleFieldChange('mcp_server_url')}
            placeholder="MCP server endpoint URL"
          />
          <div className="mt-1 text-xs text-gray-500">SSE or HTTP endpoint for MCP server</div>
        </Field>''']

        for prop_name, prop_schema in properties.items():
            title = self._format_name(prop_name)
            description = prop_schema.get('description', '')
            is_required = prop_name in required
            prop_type = prop_schema.get('type', 'string')

            if 'enum' in prop_schema:
                # Select field
                options = ', '.join(
                    f"{{ value: '{v}', label: '{self._format_name(str(v))}' }}"
                    for v in prop_schema['enum']
                )
                field_components.append(f'''
        <Field title="{title}"{' required' if is_required else ''}>
          <Select
            value={{inputs.{prop_name} || '{prop_schema.get("default", prop_schema["enum"][0])}'}}
            onChange={{handleFieldChange('{prop_name}')}}
            options={{[{options}]}}
          />
          {f'<div className="mt-1 text-xs text-gray-500">{description}</div>' if description else ''}
        </Field>''')

            elif prop_type == 'boolean':
                # Switch field
                field_components.append(f'''
        <Field title="{title}">
          <Switch
            checked={{!!inputs.{prop_name}}}
            onChange={{(checked) => handleFieldChange('{prop_name}')(checked)}}
          />
          {f'<div className="mt-1 text-xs text-gray-500">{description}</div>' if description else ''}
        </Field>''')

            elif prop_type in ('number', 'integer'):
                # Number input
                field_components.append(f'''
        <Field title="{title}"{' required' if is_required else ''}>
          <Input
            type="number"
            value={{String(inputs.{prop_name} ?? '')}}
            onChange={{(v) => handleFieldChange('{prop_name}')(v ? Number(v) : undefined)}}
            placeholder="Enter {title.lower()}"
          />
          {f'<div className="mt-1 text-xs text-gray-500">{description}</div>' if description else ''}
        </Field>''')

            else:
                # Text input
                is_password = 'password' in prop_name.lower() or 'key' in prop_name.lower() or 'secret' in prop_name.lower()
                field_components.append(f'''
        <Field title="{title}"{' required' if is_required else ''}>
          <Input
            {'type="password"' if is_password else ''}
            value={{inputs.{prop_name} || ''}}
            onChange={{handleFieldChange('{prop_name}')}}
            placeholder="Enter {title.lower()}"
          />
          {f'<div className="mt-1 text-xs text-gray-500">{description}</div>' if description else ''}
        </Field>''')

        fields_str = '\n'.join(field_components)

        return f'''/**
 * {self._format_name(schema.name)} Node - Configuration Panel
 *
 * Auto-generated from MCP tool schema.
 */

import React from 'react'
import type {{ FC }} from 'react'
import {{ useConfig }} from './use-config'
import type {{ NodePanelProps }} from '../../../sdk/typescript/src/types'
import type {{ {interface_name} }} from './types'

interface FieldProps {{
  title: string
  required?: boolean
  children: React.ReactNode
}}

const Field: FC<FieldProps> = ({{ title, required, children }}) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
      {{title}}{{required && <span className="text-red-500 ml-1">*</span>}}
    </label>
    {{children}}
  </div>
)

interface InputProps {{
  value: string
  onChange: (value: string) => void
  placeholder?: string
  type?: string
}}

const Input: FC<InputProps> = ({{ value, onChange, placeholder, type = 'text' }}) => (
  <input
    type={{type}}
    value={{value}}
    onChange={{(e) => onChange(e.target.value)}}
    placeholder={{placeholder}}
    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
  />
)

interface SelectProps {{
  value: string
  onChange: (value: string) => void
  options: Array<{{ value: string; label: string }}>
}}

const Select: FC<SelectProps> = ({{ value, onChange, options }}) => (
  <select
    value={{value}}
    onChange={{(e) => onChange(e.target.value)}}
    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
  >
    {{options.map((option) => (
      <option key={{option.value}} value={{option.value}}>
        {{option.label}}
      </option>
    ))}}
  </select>
)

interface SwitchProps {{
  checked: boolean
  onChange: (checked: boolean) => void
}}

const Switch: FC<SwitchProps> = ({{ checked, onChange }}) => (
  <button
    type="button"
    role="switch"
    aria-checked={{checked}}
    onClick={{() => onChange(!checked)}}
    className={{`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${{checked ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}}`}}
  >
    <span className={{`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${{checked ? 'translate-x-6' : 'translate-x-1'}}`}} />
  </button>
)

export const {component_name}Panel: FC<NodePanelProps<{interface_name}>> = ({{ id, data }}) => {{
  const {{ inputs, handleFieldChange, readOnly }} = useConfig(id, data)

  return (
    <div className="mt-2">
      <div className="space-y-4 px-4 pb-4">
{fields_str}

        <div className="rounded-md bg-blue-50 dark:bg-blue-900/20 p-3">
          <div className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
            {self._get_icon(schema)} Output Variables
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
}}

export default React.memo({component_name}Panel)
'''

    def _generate_use_config_ts(self, schema: MCPToolSchema) -> str:
        """Generate use-config.ts content."""
        interface_name = f'{schema.class_name.replace("Node", "")}NodeData'

        return f'''/**
 * Configuration hook for {self._format_name(schema.name)} Node
 *
 * Auto-generated from MCP tool schema.
 */

import {{ useCallback, useState }} from 'react'
import {{ produce }} from 'immer'
import type {{ {interface_name} }} from './types'
import type {{ UseConfigReturn }} from '../../../sdk/typescript/src/types'

export const useConfig = (
  id: string,
  payload: {interface_name}
): UseConfigReturn<{interface_name}> => {{
  const [inputs, setInputs] = useState<{interface_name}>(payload)

  const handleFieldChange = useCallback(
    (field: keyof {interface_name}) => {{
      return (value: any) => {{
        const newInputs = produce(inputs, (draft) => {{
          ;(draft as any)[field] = value
        }})
        setInputs(newInputs)
      }}
    }},
    [inputs, id]
  )

  const handleBulkChange = useCallback(
    (changes: Partial<{interface_name}>) => {{
      const newInputs = produce(inputs, (draft) => {{
        Object.assign(draft, changes)
      }})
      setInputs(newInputs)
    }},
    [inputs, id]
  )

  return {{
    inputs,
    readOnly: false,
    handleFieldChange,
    handleBulkChange,
  }}
}}
'''

    def _generate_default_ts(self, schema: MCPToolSchema) -> str:
        """Generate default.ts content."""
        interface_name = f'{schema.class_name.replace("Node", "")}NodeData'
        var_name = schema.node_type.replace('-', '') + 'Default'
        properties = schema.properties
        required = schema.required_fields

        # Build default values - mcp_server_url first
        defaults = [
            f"    title: '{self._format_name(schema.name)}',",
            f"    desc: '{schema.description or 'MCP Tool'}',",
            f"    type: '{schema.node_type}',",
            "    mcp_server_url: '',",
        ]

        for prop_name, prop_schema in properties.items():
            default = prop_schema.get('default')
            if default is not None:
                if isinstance(default, str):
                    defaults.append(f"    {prop_name}: '{default}',")
                elif isinstance(default, bool):
                    defaults.append(f"    {prop_name}: {str(default).lower()},")
                else:
                    defaults.append(f"    {prop_name}: {default},")
            elif prop_schema.get('type') == 'boolean':
                defaults.append(f"    {prop_name}: false,")
            else:
                defaults.append(f"    {prop_name}: '',")

        defaults_str = '\n'.join(defaults)

        # Build validation checks - mcp_server_url first
        validations = ['''
    if (!payload.mcp_server_url || payload.mcp_server_url.trim() === '') {
      return {
        isValid: false,
        errorMessage: t?.('workflow.nodes.mcp.serverUrlRequired') || 'MCP Server URL is required',
      }
    }''']
        for prop_name in required:
            validations.append(f'''
    if (!payload.{prop_name} || (typeof payload.{prop_name} === 'string' && payload.{prop_name}.trim() === '')) {{
      return {{
        isValid: false,
        errorMessage: t?.('workflow.nodes.{schema.node_type}.{prop_name}Required') || '{self._format_name(prop_name)} is required',
      }}
    }}''')

        validations_str = ''.join(validations)

        return f'''/**
 * Default configuration for {self._format_name(schema.name)} Node
 *
 * Auto-generated from MCP tool schema.
 */

import type {{ NodeDefault, ValidationResult }} from '../../../sdk/typescript/src/types'
import {{ VarType }} from '../../../sdk/typescript/src/types'
import type {{ {interface_name} }} from './types'

export const {var_name}: NodeDefault<{interface_name}> = {{
  defaultValue: {{
{defaults_str}
  }},

  checkValid(payload: {interface_name}, t: any): ValidationResult {{{validations_str}

    return {{
      isValid: true,
    }}
  }},

  getOutputVars(payload: {interface_name}) {{
    return [
      {{
        variable: 'text',
        type: VarType.String,
        description: 'Text content from tool result',
      }},
      {{
        variable: 'result',
        type: VarType.Object,
        description: 'Full tool result object',
      }},
      {{
        variable: 'is_error',
        type: VarType.Boolean,
        description: 'Whether the tool returned an error',
      }},
    ]
  }},
}}
'''
