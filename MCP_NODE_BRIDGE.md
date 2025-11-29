# MCP→Node Bridge

> **Transform MCP Tools into Deterministic Workflow Nodes**

This document describes the MCP→Node Bridge feature that allows individual MCP (Model Context Protocol) tools to be used as standalone workflow nodes without AI orchestration.

## Overview

The MCP→Node Bridge converts each MCP tool registered in Dify into a dedicated workflow node. Unlike the standard MCP integration (which uses AI to select and invoke tools), this approach:

- **Deterministic execution** - Tools run exactly when placed in the workflow
- **No AI overhead** - Direct tool invocation without LLM orchestration
- **Full workflow integration** - Connect inputs/outputs like any other node
- **Visual composition** - Build complex flows by chaining MCP tool nodes

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    Dify Workflow Editor                            │
│                                                                    │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │  Start   │───▶│ MCP Tool Node │───▶│ MCP Tool Node │───▶ ...    │
│  │  Node    │    │ (list_files)  │    │ (read_file)   │             │
│  └──────────┘    └──────────────┘    └──────────────┘             │
│                         │                    │                     │
└─────────────────────────┼────────────────────┼─────────────────────┘
                          │                    │
                          ▼                    ▼
              ┌───────────────────────────────────────────┐
              │         MCP Tool Node Registry            │
              │  mcp-{provider_id}-{tool_name} → Node     │
              └───────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────────────────────────┐
              │         MCP Server (SSE/HTTP)             │
              │  e.g., filesystem server, API server      │
              └───────────────────────────────────────────┘
```

## Key Components

### 1. MCPToolNode (`api/core/workflow/nodes/mcp_tool/node.py`)

The base node class that wraps MCP tool invocation:

```python
class MCPToolNode(Node[MCPToolNodeData]):
    """
    Workflow node that directly invokes an MCP tool.

    Unlike the standard Tool Node which relies on AI to select tools,
    this node directly calls a specific MCP tool with configured parameters.
    """

    def _run(self) -> NodeRunResult:
        # 1. Resolve parameters from variable pool
        parameters = self._resolve_parameters()

        # 2. Get MCP server connection info
        server_url, headers, timeout = self._get_connection_info()

        # 3. Invoke the tool directly
        with MCPClient(server_url=server_url, ...) as client:
            result = client.invoke_tool(tool_name, parameters)

        # 4. Return structured outputs
        return NodeRunResult(
            status=WorkflowNodeExecutionStatus.SUCCEEDED,
            outputs=self._process_result(result)
        )
```

### 2. MCP Node Registry (`api/core/workflow/nodes/mcp_tool/registry.py`)

Dynamic registration of MCP tools as workflow nodes:

```python
# Registry structure
_MCP_NODE_REGISTRY: dict[str, dict[str, type[MCPToolNode]]] = {
    "mcp-abc123-list_files": {"latest": MCPToolNode_list_files, "1": ...},
    "mcp-abc123-read_file": {"latest": MCPToolNode_read_file, "1": ...},
    # ...
}

# Key functions
load_mcp_nodes(tenant_id)          # Load from database
register_mcp_tool_node(...)        # Manual registration
get_mcp_node_class(node_type)      # Retrieve node class
refresh_mcp_nodes()                # Reload registry
```

### 3. Node Type Naming

MCP tool nodes use a deterministic naming scheme:

```
mcp-{provider_id_prefix}-{sanitized_tool_name}

Examples:
- mcp-abc12345-list_files
- mcp-abc12345-read_file
- mcp-xyz98765-search_documents
```

### 4. Integration with Node Mapping (`api/core/workflow/nodes/node_mapping.py`)

```python
# Combined mapping supports both NodeType enum and string keys
COMBINED_NODE_MAPPING: dict[NodeTypeKey, ...] = dict(NODE_TYPE_CLASSES_MAPPING)

def get_node_class(node_type: NodeTypeKey, version: str = "latest"):
    # Check built-in and custom nodes
    if node_type in COMBINED_NODE_MAPPING:
        return COMBINED_NODE_MAPPING[node_type].get(version)

    # Check MCP nodes dynamically
    if isinstance(node_type, str) and node_type.startswith("mcp-"):
        from core.workflow.nodes.mcp_tool.registry import get_mcp_node_class
        return get_mcp_node_class(node_type, version)

    return None
```

## Data Structures

### MCPToolNodeData

```python
class MCPToolNodeData(BaseNodeData):
    """Node configuration stored in workflow JSON."""
    provider_id: str                      # MCP provider UUID
    tool_name: str                        # Tool name from MCP server
    tool_parameters: dict[str, Any] = {}  # Parameter values or variable references
    timeout: float | None = None          # Optional override
    sse_read_timeout: float | None = None
```

### MCPToolInfo

```python
class MCPToolInfo(BaseModel):
    """Metadata about an MCP tool."""
    provider_id: str
    provider_name: str
    server_url: str
    tool_name: str
    tool_description: str | None
    input_schema: dict[str, Any]   # JSON Schema for parameters
    output_schema: dict[str, Any] | None

    @property
    def node_type(self) -> str:
        """Generate deterministic node type string."""
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', self.tool_name)
        return f"mcp-{self.provider_id[:8]}-{safe_name}"
```

## Parameter Resolution

Tool parameters support three input modes:

### 1. Constant Values
```json
{
  "tool_parameters": {
    "path": "/home/user/documents"
  }
}
```

### 2. Variable References
```json
{
  "tool_parameters": {
    "path": {
      "type": "variable",
      "value": ["start", "user_path"]
    }
  }
}
```

### 3. Mixed Templates
```json
{
  "tool_parameters": {
    "query": {
      "type": "mixed",
      "value": "Search for {{#start.keyword#}} in {{#start.folder#}}"
    }
  }
}
```

## Output Structure

MCP tool results are processed into structured outputs:

```python
{
    "text": "Combined text content from all TextContent items",
    "images": [{"data": "base64...", "mime_type": "image/png"}],
    "audio": [{"data": "base64...", "mime_type": "audio/wav"}],
    "structured": {...},  # If structuredContent available
    # Plus any keys from structuredContent spread as individual outputs
}
```

## Usage Flow

### 1. Register MCP Provider

First, add an MCP server in Dify's MCP Tools settings:
- Server URL (SSE endpoint)
- Authentication headers
- Connection timeouts

### 2. Tools Become Nodes

When an MCP provider is registered, each of its tools automatically becomes available as a workflow node with type `mcp-{provider_id}-{tool_name}`.

### 3. Use in Workflow

In the workflow editor:
1. Find MCP tool nodes in the node palette (custom category)
2. Drag onto canvas
3. Configure parameters (constants or variable references)
4. Connect inputs/outputs to other nodes

### 4. Execution

When the workflow runs:
1. Node resolves parameters from variable pool
2. Connects to MCP server using stored credentials
3. Invokes the specific tool
4. Returns outputs to variable pool for downstream nodes

## Comparison: MCP Node vs Standard Tool Node

| Feature | MCP Tool Node | Standard Tool Node |
|---------|--------------|-------------------|
| Tool Selection | Fixed at design time | AI selects at runtime |
| Execution | Deterministic | AI-dependent |
| Parameters | Workflow variables | AI generates from context |
| Use Case | Predictable pipelines | Flexible agent behavior |
| Overhead | Direct invocation | LLM inference required |

## Frontend Integration (TODO)

The frontend components for MCP nodes are not yet implemented.

### API Endpoint (Implemented)

The backend API is ready:

```
GET /console/api/apps/{app_id}/workflows/mcp-tool-nodes

Response:
[
  {
    "node_type": "mcp-abc12345-list_files",
    "provider_id": "abc12345-...",
    "provider_name": "Filesystem",
    "provider_icon": "...",
    "provider_icon_type": "emoji",
    "provider_icon_background": "#...",
    "tool_name": "list_files",
    "tool_description": "List files in a directory",
    "input_schema": {
      "type": "object",
      "properties": {
        "path": {"type": "string", "description": "Directory path"}
      },
      "required": ["path"]
    },
    "output_schema": null
  }
]
```

### Required Frontend Work

#### 1. Node Component
- Display tool name and icon
- Show parameter summary
- Indicate MCP provider connection status

#### 2. Panel Component
- Dynamic form from JSON Schema (`input_schema`)
- Variable reference picker for each parameter
- Connection test button

#### 3. Node Discovery & Palette
- Fetch available MCP tool nodes from API
- Add to node palette under "MCP Tools" category
- Support drag-and-drop creation

#### 4. Implementation Approach

Since MCP tool nodes are dynamically generated (not static like custom nodes),
the recommended approach is:

**Option A: Extend Tool Node (Recommended)**
- Add a new tab or mode in the existing Tool node for "MCP Direct" execution
- Reuse existing Tool node infrastructure
- Less invasive to codebase

**Option B: New Node Type**
- Create a dedicated "mcp-tool" BlockEnum type
- Register as built-in node in components.ts
- Dynamic rendering based on node_type prefix

**Option C: Dynamic Custom Nodes**
- Generate custom node entries at runtime
- More complex but keeps separation from Dify core

## Files Reference

| File | Purpose |
|------|---------|
| `api/core/workflow/nodes/mcp_tool/__init__.py` | Module exports |
| `api/core/workflow/nodes/mcp_tool/entities.py` | Data models |
| `api/core/workflow/nodes/mcp_tool/node.py` | Node implementation |
| `api/core/workflow/nodes/mcp_tool/registry.py` | Dynamic registration |
| `api/core/workflow/nodes/node_mapping.py` | Integration point |
| `api/core/workflow/nodes/node_factory.py` | Node instantiation |

## Example: File System Workflow

Using an MCP filesystem server:

```
[Start]
  │ folder_path: "/documents/inbox"
  ▼
[MCP: list_files]
  │ path: {{#start.folder_path#}}
  │ outputs: files (array)
  ▼
[Iteration]
  │ items: {{#mcp-xxx-list_files.files#}}
  ▼
  [MCP: read_file]
    │ path: {{#iteration.item#}}
    │ outputs: content
    ▼
  [LLM: Analyze]
    │ input: {{#mcp-xxx-read_file.content#}}
    │ outputs: summary
    ▼
  [MCP: write_file]
    │ path: "/documents/processed/{{#iteration.item#}}.summary"
    │ content: {{#llm.summary#}}
```

This creates a deterministic pipeline that:
1. Lists files in inbox folder
2. Iterates through each file
3. Reads content
4. Analyzes with LLM
5. Writes summary to processed folder

## Limitations

1. **No streaming** - Results returned after tool completes
2. **Single tool per node** - Each node wraps exactly one MCP tool
3. **Frontend pending** - Node/panel components not yet implemented
4. **Schema-based only** - Requires `inputSchema` from MCP tool definition

## Future Enhancements

- [ ] Frontend node/panel components
- [ ] Streaming support for long-running tools
- [ ] Tool output caching
- [ ] Batch invocation mode
- [ ] Error retry policies
- [ ] Tool versioning support
