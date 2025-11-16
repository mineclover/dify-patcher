/**
 * Default configuration for Custom AI node frontend
 */

export const customAIDefault = {
  config: {
    api_endpoint: '',
    api_key: '',
    model_name: 'default',
    temperature: 0.7,
    max_tokens: 1000,
    use_custom_format: false,
    custom_headers: {},
    timeout: 60,
  },
  variables: {
    prompt: '',
    system_message: '',
    context: '',
  },
}
