"""
Claude Code Executor Node - Backend Implementation

This node allows executing Claude Code CLI via API server with loop support.
"""

from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from dify_custom_nodes import CustomNode, NodeConfig, NodeInput, NodeOutput


class ClaudeCodeExecutorConfig(BaseModel):
    """Configuration for Claude Code Executor node"""

    # API Server Configuration
    api_endpoint: str = Field(
        default="http://localhost:3000",
        description="Claude Code API server endpoint"
    )

    api_key: str = Field(
        default="",
        description="API key for authentication (if required)"
    )

    # Execution Mode
    execution_mode: Literal["single", "loop"] = Field(
        default="single",
        description="Execute once or in a loop"
    )

    # Loop Configuration
    max_iterations: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum number of iterations for loop mode"
    )

    loop_delay: float = Field(
        default=1.0,
        ge=0.0,
        le=60.0,
        description="Delay between loop iterations (seconds)"
    )

    stop_on_error: bool = Field(
        default=True,
        description="Stop loop execution on error"
    )

    # Request Configuration
    timeout: int = Field(
        default=300,
        ge=10,
        le=3600,
        description="Request timeout in seconds"
    )

    working_directory: str = Field(
        default="",
        description="Working directory for Claude Code execution"
    )


class ClaudeCodeExecutorNode(CustomNode):
    """
    Claude Code Executor Node

    Executes Claude Code CLI via API server with support for:
    - Single execution
    - Loop execution with configurable iterations
    - Custom prompts and working directories
    """

    node_type: str = "claude-code-executor"

    class Config(NodeConfig):
        """Node configuration schema"""
        config: ClaudeCodeExecutorConfig

        # Input variables
        prompt: str = Field(
            default="",
            description="The prompt to execute with Claude Code"
        )

        context: str = Field(
            default="",
            description="Additional context or files to include"
        )

        custom_instructions: str = Field(
            default="",
            description="Custom instructions for Claude Code"
        )

    async def run(self, inputs: NodeInput) -> NodeOutput:
        """
        Execute Claude Code via API server

        Args:
            inputs: Node input containing prompt and configuration

        Returns:
            NodeOutput containing execution results
        """
        config: ClaudeCodeExecutorConfig = inputs.config

        # Validate required fields
        if not config.api_endpoint:
            return NodeOutput(
                status="failed",
                error="API endpoint is required",
                outputs={}
            )

        # Get input values
        prompt = inputs.variables.get("prompt", "")
        context = inputs.variables.get("context", "")
        custom_instructions = inputs.variables.get("custom_instructions", "")

        if not prompt:
            return NodeOutput(
                status="failed",
                error="Prompt is required",
                outputs={}
            )

        try:
            if config.execution_mode == "single":
                result = await self._execute_single(
                    prompt=prompt,
                    context=context,
                    custom_instructions=custom_instructions,
                    config=config
                )
            else:  # loop mode
                result = await self._execute_loop(
                    prompt=prompt,
                    context=context,
                    custom_instructions=custom_instructions,
                    config=config
                )

            return NodeOutput(
                status="success",
                outputs=result
            )

        except httpx.HTTPStatusError as e:
            return NodeOutput(
                status="failed",
                error=f"HTTP error: {e.response.status_code} - {e.response.text}",
                outputs={}
            )
        except httpx.TimeoutException:
            return NodeOutput(
                status="failed",
                error=f"Request timeout after {config.timeout} seconds",
                outputs={}
            )
        except Exception as e:
            return NodeOutput(
                status="failed",
                error=f"Error executing Claude Code: {str(e)}",
                outputs={}
            )

    async def _execute_single(
        self,
        prompt: str,
        context: str,
        custom_instructions: str,
        config: ClaudeCodeExecutorConfig
    ) -> dict[str, Any]:
        """Execute Claude Code once"""
        request_data = {
            "prompt": prompt,
            "context": context,
            "custom_instructions": custom_instructions,
            "working_directory": config.working_directory,
            "timeout": config.timeout
        }

        headers = self._prepare_headers(config)

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            response = await client.post(
                f"{config.api_endpoint}/api/execute",
                json=request_data,
                headers=headers
            )

            response.raise_for_status()
            result = response.json()

        return {
            "execution_mode": "single",
            "result": result.get("result", ""),
            "output": result.get("output", ""),
            "error": result.get("error", ""),
            "metadata": result.get("metadata", {}),
            "success": result.get("success", True)
        }

    async def _execute_loop(
        self,
        prompt: str,
        context: str,
        custom_instructions: str,
        config: ClaudeCodeExecutorConfig
    ) -> dict[str, Any]:
        """Execute Claude Code in a loop"""
        import asyncio

        iterations = []
        errors = []
        total_iterations = 0

        for i in range(config.max_iterations):
            total_iterations = i + 1

            try:
                # Prepare iteration-specific prompt
                iteration_prompt = f"[Iteration {i + 1}/{config.max_iterations}]\n{prompt}"

                request_data = {
                    "prompt": iteration_prompt,
                    "context": context,
                    "custom_instructions": custom_instructions,
                    "working_directory": config.working_directory,
                    "timeout": config.timeout,
                    "iteration": i + 1,
                    "max_iterations": config.max_iterations
                }

                headers = self._prepare_headers(config)

                async with httpx.AsyncClient(timeout=config.timeout) as client:
                    response = await client.post(
                        f"{config.api_endpoint}/api/execute",
                        json=request_data,
                        headers=headers
                    )

                    response.raise_for_status()
                    result = response.json()

                iterations.append({
                    "iteration": i + 1,
                    "result": result.get("result", ""),
                    "output": result.get("output", ""),
                    "success": result.get("success", True),
                    "metadata": result.get("metadata", {})
                })

                # Check if execution failed
                if not result.get("success", True):
                    error_msg = result.get("error", "Unknown error")
                    errors.append({
                        "iteration": i + 1,
                        "error": error_msg
                    })

                    if config.stop_on_error:
                        break

                # Delay before next iteration
                if i < config.max_iterations - 1 and config.loop_delay > 0:
                    await asyncio.sleep(config.loop_delay)

            except Exception as e:
                error_msg = str(e)
                errors.append({
                    "iteration": i + 1,
                    "error": error_msg
                })

                if config.stop_on_error:
                    break

                # Delay before retry
                if i < config.max_iterations - 1 and config.loop_delay > 0:
                    await asyncio.sleep(config.loop_delay)

        return {
            "execution_mode": "loop",
            "total_iterations": total_iterations,
            "max_iterations": config.max_iterations,
            "iterations": iterations,
            "errors": errors,
            "success": len(errors) == 0,
            "completed": total_iterations == config.max_iterations,
            "stopped_early": total_iterations < config.max_iterations and config.stop_on_error
        }

    def _prepare_headers(self, config: ClaudeCodeExecutorConfig) -> dict[str, str]:
        """Prepare HTTP headers"""
        headers = {
            "Content-Type": "application/json"
        }

        if config.api_key:
            headers["Authorization"] = f"Bearer {config.api_key}"

        return headers
