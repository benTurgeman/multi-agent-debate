import React, { useEffect, useState } from 'react';
import { Select, LoadingSpinner } from '../../atoms';
import { providersApi } from '../../../api';
import { AgentConfig, AgentRole, ModelProvider, ProviderInfo } from '../../../types';

export interface JudgeSelectProps {
  /**
   * Current judge configuration
   */
  value: AgentConfig | null;

  /**
   * Change handler
   */
  onChange: (judge: AgentConfig) => void;
}

export const JudgeSelect: React.FC<JudgeSelectProps> = ({ value, onChange }) => {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        setIsLoading(true);
        const response = await providersApi.list();
        setProviders(response.providers);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load providers');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProviders();
  }, []);

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = e.target.value;
    if (!selectedValue) return;

    // Parse the selected value (format: "provider:model_id")
    const [providerStr, modelId] = selectedValue.split(':');
    const provider = providers.find((p) => p.provider_id === providerStr);
    const model = provider?.models.find((m) => m.model_id === modelId);

    if (!provider || !model) return;

    // Create judge config
    const judgeConfig: AgentConfig = {
      agent_id: 'judge',
      name: 'Judge',
      role: AgentRole.JUDGE,
      stance: 'neutral',
      llm_config: {
        provider: provider.provider_id as ModelProvider,
        model_name: model.model_id,
        api_key_env_var: provider.api_key_env_var,
      },
      system_prompt: `You are an impartial judge evaluating a debate. Analyze each participant's arguments objectively and provide scores based on logic, evidence, and persuasiveness.`,
      temperature: 0.7,
      max_tokens: 3000,
    };

    onChange(judgeConfig);
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 p-4">
        <LoadingSpinner size="sm" color="slate" />
        <span className="text-sm text-slate-400">Loading judge models...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3">
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  // Build options from providers
  const options = providers.flatMap((provider) =>
    provider.models.map((model) => ({
      value: `${provider.provider_id}:${model.model_id}`,
      label: `${model.display_name} (${provider.display_name})${
        model.recommended ? ' ⭐' : ''
      }`,
    }))
  );

  return (
    <Select
      label="Judge Model"
      options={options}
      value={value ? `${value.llm_config.provider}:${value.llm_config.model_name}` : ''}
      onChange={handleSelectChange}
      placeholder="Select a judge model..."
      helperText="The judge will evaluate arguments and determine the winner"
      fullWidth
    />
  );
};
