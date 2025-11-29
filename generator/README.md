# MCP Node Generator

Generate Dify custom nodes from MCP (Model Context Protocol) tool schemas.

## Overview

This generator automates the creation of dify-patcher custom nodes from MCP tools:

1. **Extract** - Connect to an MCP server and retrieve tool schemas
2. **Generate** - Create complete node packages (backend + frontend) from schemas

## Installation

```bash
cd dify-patcher

# Install dependencies
pip install -r generator/requirements.txt

# Or with uv
uv pip install -r generator/requirements.txt
```

## Usage

### List Available Tools

```bash
# List tools from an MCP server
python -m generator list --url http://localhost:3000/mcp/sse

# With custom headers (e.g., for authentication)
python -m generator list --url http://localhost:3000/mcp/sse \
  --headers "Authorization:Bearer token123"
```

### Extract Schemas

Save tool schemas to a JSON file for offline use:

```bash
python -m generator extract \
  --url http://localhost:3000/mcp/sse \
  --output ./my-tools.json
```

### Generate Nodes

Generate custom nodes from an MCP server:

```bash
python -m generator generate \
  --url http://localhost:3000/mcp/sse \
  --output ./nodes
```

Generate from a saved schema file:

```bash
python -m generator generate \
  --schema ./my-tools.json \
  --output ./nodes
```

Generate specific tools only:

```bash
python -m generator generate \
  --url http://localhost:3000/mcp/sse \
  --output ./nodes \
  --tools list_files read_file write_file
```

## Generated Structure

For each MCP tool, the generator creates:

```
nodes/{mcp-tool-name}/
├── manifest.json          # Node metadata
├── backend/
│   ├── __init__.py
│   └── node.py           # Python implementation
└── frontend/
    ├── index.ts          # Exports
    ├── types.ts          # TypeScript types
    ├── node.tsx          # Canvas component
    ├── panel.tsx         # Configuration panel
    ├── use-config.ts     # React hook
    └── default.ts        # Default values
```

## Customization

After generation, you may want to:

1. **Update MCP_SERVER_URL** in `backend/node.py` if the server URL changes
2. **Customize the icon** in `manifest.json`
3. **Add validation** in `default.ts`
4. **Enhance the panel UI** in `frontend/panel.tsx`
5. **Add output processing** in `backend/node.py`

## Example: Filesystem MCP Server

```bash
# 1. Start your MCP filesystem server
npx -y @anthropic-ai/mcp-server-filesystem ./allowed-path

# 2. List available tools (replace with your MCP server URL)
python -m generator list --url <your-mcp-server-url>

# Output:
#   list_files
#     List files in a directory
#   read_file
#     Read contents of a file
#   write_file
#     Write contents to a file

# 3. Generate nodes
python -m generator generate \
  --url <your-mcp-server-url> \
  --output ./nodes

# 4. Re-install dify-patcher to load new nodes
cd installer/cli && npm start -- install --target ../../dify --mode dev
```

## Programmatic Usage

```python
from generator import MCPSchemaExtractor, CustomNodeGenerator

# Extract schemas
extractor = MCPSchemaExtractor(server_url='<your-mcp-server-url>')
tools = extractor.extract_tools()

# Generate nodes (server_url is optional, used for defaults)
generator = CustomNodeGenerator(output_dir='./nodes')
for tool in tools:
    node_path = generator.generate(tool)
    print(f"Generated: {node_path}")

# Or generate all at once
paths = generator.generate_all(tools)
```

## Schema Format

Tool schemas follow the MCP specification:

```json
{
  "name": "list_files",
  "description": "List files in a directory",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Directory path to list"
      },
      "recursive": {
        "type": "boolean",
        "default": false
      }
    },
    "required": ["path"]
  }
}
```

This gets converted to:

- **manifest.json** inputs/outputs
- **backend/node.py** parameter extraction and validation
- **frontend/types.ts** TypeScript interface
- **frontend/panel.tsx** form fields

## Limitations

- **No streaming** - Tool results are returned after completion
- **Basic UI** - Generated panels use simple form fields
- **Manual refinement** - Complex tools may need custom UI work

## Troubleshooting

### Connection Errors

```bash
# Check if MCP server is running
curl http://localhost:3000/health

# Try with verbose output
python -m generator list --url http://localhost:3000/mcp/sse 2>&1
```

### Import Errors

```bash
# Ensure you're in the dify-patcher directory
cd dify-patcher

# Install dependencies
pip install httpx
```

### Generated Code Issues

1. Check `manifest.json` for correct node_type
2. Verify `MCP_SERVER_URL` in `backend/node.py`
3. Ensure all required fields are in `types.ts`
