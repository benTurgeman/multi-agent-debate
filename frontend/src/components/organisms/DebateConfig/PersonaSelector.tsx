import React, { useState, useEffect } from 'react';
import { Select, LoadingSpinner, Badge } from '../../atoms';
import { personasApi } from '../../../api/personas';
import { PersonaTemplate, PersonaStyle } from '../../../types/persona';

export interface PersonaSelectorProps {
  /**
   * Selected persona ID (null for custom)
   */
  value: string | null;

  /**
   * Change handler - receives full persona object or null for custom
   */
  onChange: (persona: PersonaTemplate | null) => void;
}

/**
 * Map persona style to badge variant
 */
const getStyleBadgeColor = (style: PersonaStyle): 'pro' | 'con' | 'judge' | 'neutral' => {
  switch (style) {
    case PersonaStyle.AGGRESSIVE:
      return 'con'; // Red
    case PersonaStyle.DIPLOMATIC:
      return 'judge'; // Purple
    case PersonaStyle.ANALYTICAL:
      return 'pro'; // Green
    case PersonaStyle.SOCRATIC:
      return 'neutral'; // Slate
    default:
      return 'neutral';
  }
};

export const PersonaSelector: React.FC<PersonaSelectorProps> = ({
  value,
  onChange,
}) => {
  const [personas, setPersonas] = useState<PersonaTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await personasApi.list();
        setPersonas(response.personas);
      } catch (err) {
        console.error('Failed to fetch personas:', err);
        setError('Failed to load personas. Using custom mode.');
      } finally {
        setLoading(false);
      }
    };

    fetchPersonas();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = e.target.value;

    if (!selectedId || selectedId === 'custom') {
      onChange(null);
      return;
    }

    const selectedPersona = personas.find((p) => p.persona_id === selectedId);
    if (selectedPersona) {
      onChange(selectedPersona);
    }
  };

  const selectedPersona = value ? personas.find((p) => p.persona_id === value) : null;

  if (loading) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-slate-200">Persona Template</label>
        <div className="flex items-center justify-center py-4 rounded-lg border border-slate-700 bg-slate-900">
          <LoadingSpinner size="sm" color="slate" />
          <span className="ml-2 text-sm text-slate-400">Loading personas...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-slate-200">Persona Template</label>
        <div className="rounded-lg border border-yellow-500/20 bg-yellow-500/10 px-3 py-2">
          <p className="text-sm text-yellow-500">{error}</p>
        </div>
      </div>
    );
  }

  const options = [
    { value: 'custom', label: 'None (Custom)' },
    ...personas.map((persona) => ({
      value: persona.persona_id,
      label: persona.name,
    })),
  ];

  return (
    <div className="flex flex-col gap-3">
      <Select
        label="Persona Template (Optional)"
        value={value || 'custom'}
        onChange={handleChange}
        options={options}
        helperText="Select a preconfigured persona or create a custom agent"
        fullWidth
      />

      {/* Show persona details if one is selected */}
      {selectedPersona && (
        <div className="rounded-lg border border-slate-700 bg-slate-900/50 p-4">
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-slate-100">
                {selectedPersona.name}
              </h4>
              <p className="text-xs text-slate-400 mt-0.5">
                {selectedPersona.expertise}
              </p>
            </div>
            <Badge
              variant={getStyleBadgeColor(selectedPersona.debate_style)}
              size="sm"
            >
              {selectedPersona.debate_style}
            </Badge>
          </div>

          <p className="text-sm text-slate-300 mb-3">
            {selectedPersona.description}
          </p>

          {/* Show tags if available */}
          {selectedPersona.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {selectedPersona.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 text-xs rounded bg-slate-800 text-slate-400 border border-slate-700"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Info message */}
          <div className="mt-3 pt-3 border-t border-slate-700">
            <p className="text-xs text-slate-400">
              ℹ️ All fields below can be customized after selecting a persona
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
