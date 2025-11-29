"""
MCP Schema Extractor

Connects to an MCP server and extracts tool schemas for code generation.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse


@dataclass
class MCPToolSchema:
    """Represents an MCP tool's schema for code generation."""

    name: str
    description: str | None
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None
    annotations: dict[str, Any] | None = None

    # Derived fields
    node_type: str = field(default='', init=False)
    class_name: str = field(default='', init=False)

    def __post_init__(self):
        self.node_type = self._generate_node_type()
        self.class_name = self._generate_class_name()

    def _generate_node_type(self) -> str:
        """Generate a valid node type from tool name."""
        # Replace non-alphanumeric chars with hyphens
        safe_name = re.sub(r'[^a-zA-Z0-9]', '-', self.name.lower())
        # Remove consecutive hyphens
        safe_name = re.sub(r'-+', '-', safe_name)
        # Remove leading/trailing hyphens
        safe_name = safe_name.strip('-')
        return f"mcp-{safe_name}"

    def _generate_class_name(self) -> str:
        """Generate a valid Python class name from tool name."""
        # Convert to PascalCase
        words = re.split(r'[_\-\s]+', self.name)
        class_name = ''.join(word.capitalize() for word in words if word)
        return f"MCP{class_name}Node"

    @property
    def properties(self) -> dict[str, Any]:
        """Get input properties from schema."""
        return self.input_schema.get('properties', {})

    @property
    def required_fields(self) -> list[str]:
        """Get required field names."""
        return self.input_schema.get('required', [])

    def get_typescript_type(self, prop_schema: dict[str, Any]) -> str:
        """Convert JSON Schema type to TypeScript type."""
        json_type = prop_schema.get('type', 'any')

        if json_type == 'string':
            if 'enum' in prop_schema:
                return ' | '.join(f"'{v}'" for v in prop_schema['enum'])
            return 'string'
        elif json_type == 'number' or json_type == 'integer':
            return 'number'
        elif json_type == 'boolean':
            return 'boolean'
        elif json_type == 'array':
            items = prop_schema.get('items', {})
            item_type = self.get_typescript_type(items)
            return f'{item_type}[]'
        elif json_type == 'object':
            return 'Record<string, any>'
        else:
            return 'any'

    def get_python_type(self, prop_schema: dict[str, Any]) -> str:
        """Convert JSON Schema type to Python type hint."""
        json_type = prop_schema.get('type', 'Any')

        if json_type == 'string':
            return 'str'
        elif json_type == 'number':
            return 'float'
        elif json_type == 'integer':
            return 'int'
        elif json_type == 'boolean':
            return 'bool'
        elif json_type == 'array':
            items = prop_schema.get('items', {})
            item_type = self.get_python_type(items)
            return f'list[{item_type}]'
        elif json_type == 'object':
            return 'dict[str, Any]'
        else:
            return 'Any'

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'input_schema': self.input_schema,
            'output_schema': self.output_schema,
            'annotations': self.annotations,
            'node_type': self.node_type,
            'class_name': self.class_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'MCPToolSchema':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            description=data.get('description'),
            input_schema=data.get('input_schema', {}),
            output_schema=data.get('output_schema'),
            annotations=data.get('annotations'),
        )


class MCPSchemaExtractor:
    """
    Extracts tool schemas from an MCP server.

    Supports both:
    - SSE endpoints (Server-Sent Events)
    - HTTP endpoints (direct JSON-RPC)
    """

    def __init__(
        self,
        server_url: str,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ):
        self.server_url = server_url
        self.headers = headers or {}
        self.timeout = timeout
        self._tools: list[MCPToolSchema] = []

    def extract_tools(self) -> list[MCPToolSchema]:
        """
        Connect to MCP server and extract all tool schemas.

        Returns:
            List of MCPToolSchema objects
        """
        # Always use standalone mode for dify-patcher independence
        return self._extract_tools_standalone()

    def _extract_tools_with_client(self) -> list[MCPToolSchema]:
        """Extract tools using Dify's MCPClient."""
        from core.mcp import MCPClient

        with MCPClient(
            server_url=self.server_url,
            headers=self.headers,
            timeout=self.timeout,
        ) as client:
            tools = client.list_tools()

            self._tools = [
                MCPToolSchema(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.inputSchema or {},
                    output_schema=tool.outputSchema,
                    annotations=tool.annotations,
                )
                for tool in tools
            ]

        return self._tools

    def _extract_tools_standalone(self) -> list[MCPToolSchema]:
        """
        Extract tools without Dify dependencies.
        Uses httpx for HTTP requests and sse-starlette for SSE parsing.
        """
        import httpx

        parsed = urlparse(self.server_url)

        # Try SSE endpoint first (common pattern)
        if '/sse' in self.server_url or parsed.path.endswith('/sse'):
            return self._extract_via_sse()

        # Try direct HTTP
        return self._extract_via_http()

    def _extract_via_http(self) -> list[MCPToolSchema]:
        """Extract tools via HTTP JSON-RPC."""
        import httpx

        with httpx.Client(timeout=self.timeout) as client:
            # Send tools/list request
            response = client.post(
                self.server_url,
                headers={**self.headers, 'Content-Type': 'application/json'},
                json={
                    'jsonrpc': '2.0',
                    'id': 1,
                    'method': 'tools/list',
                    'params': {},
                }
            )
            response.raise_for_status()

            result = response.json()
            tools_data = result.get('result', {}).get('tools', [])

            self._tools = [
                MCPToolSchema(
                    name=tool['name'],
                    description=tool.get('description'),
                    input_schema=tool.get('inputSchema', {}),
                    output_schema=tool.get('outputSchema'),
                    annotations=tool.get('annotations'),
                )
                for tool in tools_data
            ]

        return self._tools

    def _extract_via_sse(self) -> list[MCPToolSchema]:
        """Extract tools via SSE (Server-Sent Events)."""
        import httpx

        with httpx.Client(timeout=self.timeout) as client:
            # Connect to SSE endpoint
            with client.stream(
                'GET',
                self.server_url,
                headers={**self.headers, 'Accept': 'text/event-stream'},
            ) as response:
                response.raise_for_status()

                # Read SSE events
                endpoint_url = None
                for line in response.iter_lines():
                    if line.startswith('data: '):
                        data = json.loads(line[6:])
                        if 'endpoint' in data:
                            endpoint_url = data['endpoint']
                            break

                if not endpoint_url:
                    raise ValueError("No endpoint URL received from SSE")

        # Now call the endpoint for tools/list
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                endpoint_url,
                headers={**self.headers, 'Content-Type': 'application/json'},
                json={
                    'jsonrpc': '2.0',
                    'id': 1,
                    'method': 'tools/list',
                    'params': {},
                }
            )
            response.raise_for_status()

            result = response.json()
            tools_data = result.get('result', {}).get('tools', [])

            self._tools = [
                MCPToolSchema(
                    name=tool['name'],
                    description=tool.get('description'),
                    input_schema=tool.get('inputSchema', {}),
                    output_schema=tool.get('outputSchema'),
                    annotations=tool.get('annotations'),
                )
                for tool in tools_data
            ]

        return self._tools

    @classmethod
    def from_json_file(cls, file_path: str) -> list[MCPToolSchema]:
        """
        Load tool schemas from a JSON file.

        Useful for offline code generation without connecting to a server.

        Args:
            file_path: Path to JSON file containing tool schemas

        Returns:
            List of MCPToolSchema objects
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        if isinstance(data, list):
            tools_data = data
        else:
            tools_data = data.get('tools', [])

        return [MCPToolSchema.from_dict(tool) for tool in tools_data]

    def save_schemas(self, file_path: str) -> None:
        """
        Save extracted schemas to a JSON file.

        Args:
            file_path: Path to save the JSON file
        """
        with open(file_path, 'w') as f:
            json.dump(
                [tool.to_dict() for tool in self._tools],
                f,
                indent=2,
            )
