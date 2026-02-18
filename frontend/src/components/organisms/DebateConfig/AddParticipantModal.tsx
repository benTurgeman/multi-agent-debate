import React, { useState, useEffect } from 'react';
import { Dialog } from '@headlessui/react';
import { X } from 'lucide-react';
import { Button, Input, Select, LoadingSpinner } from '../../atoms';
import { providersApi } from '../../../api';
import { AgentConfig, AgentRole, ModelProvider, ProviderInfo } from '../../../types';
import { PersonaSelector } from './PersonaSelector';
import { PersonaTemplate } from '../../../types/persona';

export interface AddParticipantModalProps {
  /**
   * Whether modal is open
   */
  isOpen: boolean;

  /**
   * Close handler
   */
  onClose: () => void;

  /**
   * Submit handler
   */
  onSubmit: (agent: AgentConfig) => void;
}

export const AddParticipantModal: React.FC<AddParticipantModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [selectedPersona, setSelectedPersona] = useState<PersonaTemplate | null>(null);
  const [agentName, setAgentName] = useState('');
  const [stance, setStance] = useState('Pro');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [temperature, setTemperature] = useState(1.0);
  const [maxTokens, setMaxTokens] = useState(1024);

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        setIsLoading(true);
        const response = await providersApi.list();
        setProviders(response.providers);

        // Auto-select first provider and model
        if (response.providers.length > 0) {
          const firstProvider = response.providers[0];
          setSelectedProvider(firstProvider.provider_id);
          if (firstProvider.models.length > 0) {
            setSelectedModel(firstProvider.models[0].model_id);
          }
        }
      } catch (err) {
        console.error('Failed to load providers:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (isOpen) {
      fetchProviders();
    }
  }, [isOpen]);

  const handlePersonaChange = (persona: PersonaTemplate | null) => {
    setSelectedPersona(persona);

    if (persona) {
      // Auto-populate form fields from persona template
      setAgentName(persona.name);
      setSystemPrompt(persona.system_prompt_template.replace('{stance}', stance));
      setTemperature(persona.suggested_temperature);
      setMaxTokens(persona.suggested_max_tokens);
    } else {
      // Reset to default when persona is cleared
      // Don't clear agentName or stance as user may have customized them
    }
  };

  // Update system prompt when stance changes and persona is selected
  useEffect(() => {
    if (selectedPersona && systemPrompt.includes('{stance}')) {
      setSystemPrompt(selectedPersona.system_prompt_template.replace('{stance}', stance));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stance, selectedPersona]);

  const handleSubmit = () => {
    if (!agentName.trim() || !selectedProvider || !selectedModel) {
      return;
    }

    const provider = providers.find((p) => p.provider_id === selectedProvider);
    if (!provider) return;

    const agentConfig: AgentConfig = {
      agent_id: `agent_${Date.now()}`,
      name: agentName.trim(),
      role: AgentRole.DEBATER,
      stance,
      llm_config: {
        provider: selectedProvider as ModelProvider,
        model_name: selectedModel,
        api_key_env_var: provider.api_key_env_var,
      },
      system_prompt:
        systemPrompt.trim() ||
        `You are a skilled debater arguing ${stance} for the given topic. Present clear, logical arguments with evidence to support your position.`,
      temperature,
      max_tokens: maxTokens,
    };

    onSubmit(agentConfig);

    // Reset form
    setSelectedPersona(null);
    setAgentName('');
    setStance('Pro');
    setSystemPrompt('');
    setTemperature(1.0);
    setMaxTokens(1024);
    onClose();
  };

  const currentProvider = providers.find((p) => p.provider_id === selectedProvider);
  const modelOptions =
    currentProvider?.models.map((model) => ({
      value: model.model_id,
      label: `${model.display_name}${model.recommended ? ' ⭐' : ''}`,
    })) || [];

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50" aria-hidden="true" />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="w-full max-w-2xl rounded-lg bg-slate-800 border border-slate-700 shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-700 px-6 py-4">
            <Dialog.Title className="text-lg font-semibold text-slate-100">
              Add Participant
            </Dialog.Title>
            <button
              onClick={onClose}
              className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <LoadingSpinner size="lg" color="slate" />
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                {/* Persona Selector */}
                <PersonaSelector
                  value={selectedPersona?.persona_id || null}
                  onChange={handlePersonaChange}
                />

                {/* Agent Name */}
                <Input
                  label="Agent Name"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  placeholder="e.g., Agent Smith"
                  fullWidth
                  required
                />

                {/* Stance */}
                <Select
                  label="Stance"
                  value={stance}
                  onChange={(e) => setStance(e.target.value)}
                  options={[
                    { value: 'Pro', label: 'Pro (For)' },
                    { value: 'Con', label: 'Con (Against)' },
                  ]}
                  fullWidth
                />

                {/* Provider */}
                <Select
                  label="Provider"
                  value={selectedProvider}
                  onChange={(e) => {
                    setSelectedProvider(e.target.value);
                    const provider = providers.find((p) => p.provider_id === e.target.value);
                    if (provider && provider.models.length > 0) {
                      setSelectedModel(provider.models[0].model_id);
                    }
                  }}
                  options={providers.map((p) => ({
                    value: p.provider_id,
                    label: p.display_name,
                  }))}
                  fullWidth
                />

                {/* Model */}
                <Select
                  label="Model"
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  options={modelOptions}
                  fullWidth
                />

                {/* System Prompt (Optional) */}
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-slate-200">
                    System Prompt (Optional)
                  </label>
                  <textarea
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                    placeholder="Leave empty to use default prompt..."
                    rows={3}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900 text-slate-200 px-3 py-2 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Advanced Settings */}
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Temperature"
                    type="number"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    min={0}
                    max={2}
                    step={0.1}
                    fullWidth
                  />

                  <Input
                    label="Max Tokens"
                    type="number"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value, 10))}
                    min={256}
                    max={4096}
                    step={256}
                    fullWidth
                  />
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 border-t border-slate-700 px-6 py-4">
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSubmit}
              disabled={!agentName.trim() || !selectedProvider || !selectedModel}
            >
              Add Agent
            </Button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};
