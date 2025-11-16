/**
 * Default configuration for Claude Code Executor node frontend
 */

export const claudeCodeExecutorDefault = {
  config: {
    api_endpoint: 'http://localhost:3000',
    api_key: '',
    execution_mode: 'single',
    max_iterations: 5,
    loop_delay: 1.0,
    stop_on_error: true,
    timeout: 300,
    working_directory: '',
  },
  variables: {
    prompt: '',
    context: '',
    custom_instructions: '',
  },
}
