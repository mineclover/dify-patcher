#!/usr/bin/env python3
"""
MCP Node Generator CLI

Command-line interface for generating custom nodes from MCP tool schemas.

Usage:
    # Generate nodes from MCP server
    python -m generator.cli generate --url http://localhost:3000/mcp/sse --output ./nodes

    # Generate nodes from JSON schema file
    python -m generator.cli generate --schema ./tools.json --output ./nodes

    # List tools from MCP server
    python -m generator.cli list --url http://localhost:3000/mcp/sse

    # Save schemas to file for later use
    python -m generator.cli extract --url http://localhost:3000/mcp/sse --output ./tools.json
"""

import argparse
import json
import sys
from pathlib import Path

from .schema_extractor import MCPSchemaExtractor, MCPToolSchema
from .node_generator import CustomNodeGenerator


def cmd_list(args: argparse.Namespace) -> int:
    """List tools from MCP server."""
    print(f"Connecting to MCP server: {args.url}")

    try:
        extractor = MCPSchemaExtractor(
            server_url=args.url,
            headers=_parse_headers(args.headers) if args.headers else None,
            timeout=args.timeout,
        )
        tools = extractor.extract_tools()

        print(f"\nFound {len(tools)} tools:\n")
        for tool in tools:
            print(f"  {tool.name}")
            if tool.description:
                print(f"    {tool.description[:80]}{'...' if len(tool.description) > 80 else ''}")
            print(f"    Node type: {tool.node_type}")
            print(f"    Parameters: {', '.join(tool.properties.keys()) or 'none'}")
            print()

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_extract(args: argparse.Namespace) -> int:
    """Extract and save schemas to file."""
    print(f"Connecting to MCP server: {args.url}")

    try:
        extractor = MCPSchemaExtractor(
            server_url=args.url,
            headers=_parse_headers(args.headers) if args.headers else None,
            timeout=args.timeout,
        )
        tools = extractor.extract_tools()

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        extractor.save_schemas(str(output_path))
        print(f"\nSaved {len(tools)} tool schemas to {output_path}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate custom nodes from schemas."""
    tools: list[MCPToolSchema] = []
    server_url = ''

    # Load schemas
    if args.url:
        print(f"Connecting to MCP server: {args.url}")
        server_url = args.url

        try:
            extractor = MCPSchemaExtractor(
                server_url=args.url,
                headers=_parse_headers(args.headers) if args.headers else None,
                timeout=args.timeout,
            )
            tools = extractor.extract_tools()
        except Exception as e:
            print(f"Error connecting to MCP server: {e}", file=sys.stderr)
            return 1

    elif args.schema:
        print(f"Loading schemas from: {args.schema}")
        try:
            tools = MCPSchemaExtractor.from_json_file(args.schema)
        except Exception as e:
            print(f"Error loading schema file: {e}", file=sys.stderr)
            return 1

        # Try to get server URL from schema file
        with open(args.schema) as f:
            data = json.load(f)
            if isinstance(data, dict):
                server_url = data.get('server_url', '')

    else:
        print("Error: Either --url or --schema is required", file=sys.stderr)
        return 1

    if not tools:
        print("No tools found to generate.")
        return 0

    # Filter tools if specified
    if args.tools:
        tool_names = set(args.tools)
        tools = [t for t in tools if t.name in tool_names]
        if not tools:
            print(f"No matching tools found for: {', '.join(tool_names)}")
            return 1

    # Generate nodes
    output_dir = Path(args.output)
    generator = CustomNodeGenerator(output_dir)

    print(f"\nGenerating {len(tools)} nodes to {output_dir}:\n")

    for tool in tools:
        try:
            node_path = generator.generate(tool, server_url)
            print(f"  ✓ {tool.name} -> {node_path.name}/")
        except Exception as e:
            print(f"  ✗ {tool.name}: {e}", file=sys.stderr)

    print(f"\nDone! Generated nodes are in {output_dir}")
    print("\nNext steps:")
    print("  1. Review and customize the generated code")
    print("  2. Update MCP_SERVER_URL in backend/node.py if needed")
    print("  3. Re-run dify-patcher installer to load new nodes")

    return 0


def _parse_headers(headers_str: str) -> dict[str, str]:
    """Parse header string like 'Key1:Value1,Key2:Value2' into dict."""
    headers = {}
    for pair in headers_str.split(','):
        if ':' in pair:
            key, value = pair.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog='mcp-node-gen',
        description='Generate Dify custom nodes from MCP tool schemas',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # list command
    list_parser = subparsers.add_parser('list', help='List tools from MCP server')
    list_parser.add_argument('--url', '-u', required=True, help='MCP server URL (SSE or HTTP)')
    list_parser.add_argument('--headers', '-H', help='Headers (Key:Value,Key2:Value2)')
    list_parser.add_argument('--timeout', '-t', type=float, default=30.0, help='Timeout in seconds')
    list_parser.set_defaults(func=cmd_list)

    # extract command
    extract_parser = subparsers.add_parser('extract', help='Extract and save schemas to file')
    extract_parser.add_argument('--url', '-u', required=True, help='MCP server URL')
    extract_parser.add_argument('--output', '-o', required=True, help='Output JSON file path')
    extract_parser.add_argument('--headers', '-H', help='Headers (Key:Value,Key2:Value2)')
    extract_parser.add_argument('--timeout', '-t', type=float, default=30.0, help='Timeout in seconds')
    extract_parser.set_defaults(func=cmd_extract)

    # generate command
    gen_parser = subparsers.add_parser('generate', help='Generate custom nodes')
    gen_parser.add_argument('--url', '-u', help='MCP server URL')
    gen_parser.add_argument('--schema', '-s', help='JSON schema file path')
    gen_parser.add_argument('--output', '-o', required=True, help='Output directory for nodes')
    gen_parser.add_argument('--tools', nargs='+', help='Specific tool names to generate')
    gen_parser.add_argument('--headers', '-H', help='Headers (Key:Value,Key2:Value2)')
    gen_parser.add_argument('--timeout', '-t', type=float, default=30.0, help='Timeout in seconds')
    gen_parser.set_defaults(func=cmd_generate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
