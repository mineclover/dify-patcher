"""
List Directory Node

Auto-generated from MCP tool schema.
List files and directories in a specified path. Returns file names, sizes, and modification times.
"""

from typing import Any

from core.dify_custom_nodes import BaseCustomNode, register_node
from core.workflow.enums import WorkflowNodeExecutionStatus
from core.workflow.node_events import NodeRunResult


@register_node('mcp-list-directory', version='1', author='MCP Node Generator')
class MCPListDirectoryNode(BaseCustomNode):
    """
    MCP Tool: list_directory

    List files and directories in a specified path. Returns file names, sizes, and modification times.
    """

    # MCP Tool name (server URL is provided via node input)
    MCP_TOOL_NAME = 'list_directory'

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
                inputs={},
                outputs={},
                error="MCP Server URL is required"
            )

        # Extract inputs
        path = self.get_input('path', '''')

        if not path:
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                inputs={'path': path},
                outputs={},
                error="Path is required"
            )

        # Build tool parameters
        tool_params = {'path': path}

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
                    outputs={'text': text_content, 'result': result, 'is_error': True},
                    error=text_content or "Tool returned an error"
                )

            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                inputs=tool_params,
                outputs={
                    'text': text_content,
                    'result': result,
                    'is_error': False,
                }
            )

        except Exception as e:
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                inputs=tool_params,
                outputs={},
                error=f"MCP tool invocation failed: {str(e)}"
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
                json={
                    'jsonrpc': '2.0',
                    'id': 1,
                    'method': 'tools/call',
                    'params': {
                        'name': self.MCP_TOOL_NAME,
                        'arguments': params,
                    },
                },
                headers={'Content-Type': 'application/json'},
            )
            response.raise_for_status()
            result = response.json()
            return result.get('result', {})

    def _convert_result(self, result: Any) -> dict[str, Any]:
        """Convert MCPClient result to dictionary."""
        if hasattr(result, 'content'):
            return {
                'content': [
                    {'type': c.type, 'text': getattr(c, 'text', None)}
                    for c in result.content
                ] if result.content else [],
                'structuredContent': result.structuredContent,
                'isError': result.isError,
            }
        return result if isinstance(result, dict) else {'raw': result}

    def _extract_text(self, result: dict[str, Any]) -> str:
        """Extract text content from tool result."""
        content = result.get('content', [])
        text_parts = []

        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                text_parts.append(item.get('text', ''))
            elif hasattr(item, 'type') and item.type == 'text':
                text_parts.append(getattr(item, 'text', ''))

        return '\n'.join(text_parts)
