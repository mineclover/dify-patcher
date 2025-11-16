"""
Custom AI Node - Backend Implementation

This node allows integration with custom AI services that have special interfaces.
"""

from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from dify_custom_nodes import CustomNode, NodeConfig, NodeInput, NodeOutput


class CustomAIConfig(BaseModel):
    """Configuration for Custom AI node"""

    # API Endpoint Configuration
    api_endpoint: str = Field(
        default="",
        description="Custom AI API endpoint URL"
    )

    api_key: str = Field(
        default="",
        description="API key for authentication"
    )

    # Model Configuration
    model_name: str = Field(
        default="default",
        description="Model name to use"
    )

    # Special Interface Parameters
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for response generation"
    )

    max_tokens: int = Field(
        default=1000,
        ge=1,
        le=32000,
        description="Maximum tokens to generate"
    )

    # Custom Interface Settings
    use_custom_format: bool = Field(
        default=False,
        description="Enable custom request/response format"
    )

    custom_headers: dict[str, str] = Field(
        default_factory=dict,
        description="Additional custom headers"
    )

    timeout: int = Field(
        default=60,
        ge=1,
        le=300,
        description="Request timeout in seconds"
    )


class CustomAINode(CustomNode):
    """
    Custom AI Node with special interface support

    This node allows integration with custom AI services that may have
    non-standard interfaces or special requirements.
    """

    node_type: str = "custom-ai"

    class Config(NodeConfig):
        """Node configuration schema"""
        config: CustomAIConfig

        # Input variables
        prompt: str = Field(
            default="",
            description="The prompt to send to the custom AI"
        )

        system_message: str = Field(
            default="",
            description="System message for the AI"
        )

        context: str = Field(
            default="",
            description="Additional context for the AI"
        )

    async def run(self, inputs: NodeInput) -> NodeOutput:
        """
        Execute the custom AI request

        Args:
            inputs: Node input containing prompt and configuration

        Returns:
            NodeOutput containing the AI response
        """
        config: CustomAIConfig = inputs.config

        # Validate required fields
        if not config.api_endpoint:
            return NodeOutput(
                status="failed",
                error="API endpoint is required",
                outputs={}
            )

        if not config.api_key:
            return NodeOutput(
                status="failed",
                error="API key is required",
                outputs={}
            )

        # Get input values
        prompt = inputs.variables.get("prompt", "")
        system_message = inputs.variables.get("system_message", "")
        context = inputs.variables.get("context", "")

        if not prompt:
            return NodeOutput(
                status="failed",
                error="Prompt is required",
                outputs={}
            )

        try:
            # Prepare request
            if config.use_custom_format:
                # Custom format for special interfaces
                request_data = self._prepare_custom_request(
                    prompt=prompt,
                    system_message=system_message,
                    context=context,
                    config=config
                )
            else:
                # Standard format
                request_data = self._prepare_standard_request(
                    prompt=prompt,
                    system_message=system_message,
                    context=context,
                    config=config
                )

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.api_key}",
                **config.custom_headers
            }

            # Make API request
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                response = await client.post(
                    config.api_endpoint,
                    json=request_data,
                    headers=headers
                )

                response.raise_for_status()
                result = response.json()

            # Parse response
            if config.use_custom_format:
                output = self._parse_custom_response(result)
            else:
                output = self._parse_standard_response(result)

            return NodeOutput(
                status="success",
                outputs={
                    "text": output.get("text", ""),
                    "usage": output.get("usage", {}),
                    "metadata": output.get("metadata", {}),
                    "raw_response": result
                }
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
                error=f"Error calling custom AI: {str(e)}",
                outputs={}
            )

    def _prepare_standard_request(
        self,
        prompt: str,
        system_message: str,
        context: str,
        config: CustomAIConfig
    ) -> dict[str, Any]:
        """Prepare standard OpenAI-compatible request format"""
        messages = []

        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })

        user_content = prompt
        if context:
            user_content = f"{context}\n\n{prompt}"

        messages.append({
            "role": "user",
            "content": user_content
        })

        return {
            "model": config.model_name,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens
        }

    def _prepare_custom_request(
        self,
        prompt: str,
        system_message: str,
        context: str,
        config: CustomAIConfig
    ) -> dict[str, Any]:
        """Prepare custom request format for special interfaces"""
        # This can be customized based on specific AI service requirements
        return {
            "model": config.model_name,
            "prompt": prompt,
            "system": system_message,
            "context": context,
            "parameters": {
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            }
        }

    def _parse_standard_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Parse standard OpenAI-compatible response"""
        try:
            text = response["choices"][0]["message"]["content"]
            usage = response.get("usage", {})

            return {
                "text": text,
                "usage": usage,
                "metadata": {
                    "model": response.get("model", ""),
                    "finish_reason": response["choices"][0].get("finish_reason", "")
                }
            }
        except (KeyError, IndexError) as e:
            return {
                "text": str(response),
                "usage": {},
                "metadata": {"parse_error": str(e)}
            }

    def _parse_custom_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Parse custom response format"""
        # This can be customized based on specific AI service response format
        return {
            "text": response.get("output", response.get("text", str(response))),
            "usage": response.get("usage", {}),
            "metadata": response.get("metadata", {})
        }
