import { buildCompiledPrompt } from './prompt.js';
import { extractJson, validateReport } from './validate.js';

/**
 * Resolve provider + API key from options / env.
 * Never logs the key.
 */
export function resolveCredentials({ provider, key } = {}) {
  const explicitKey = key && key !== 'env' ? key : null;
  const anthropic = explicitKey && provider === 'anthropic'
    ? explicitKey
    : process.env.ANTHROPIC_API_KEY || '';
  const openai = explicitKey && provider === 'openai'
    ? explicitKey
    : process.env.OPENAI_API_KEY || '';

  if (provider === 'anthropic') {
    if (!anthropic && !explicitKey) return { provider: null, key: null };
    return { provider: 'anthropic', key: explicitKey || anthropic };
  }
  if (provider === 'openai') {
    if (!openai && !explicitKey) return { provider: null, key: null };
    return { provider: 'openai', key: explicitKey || openai };
  }

  // Auto-detect
  if (explicitKey) {
    // Heuristic: Anthropic keys often start with sk-ant-
    if (String(explicitKey).startsWith('sk-ant-')) {
      return { provider: 'anthropic', key: explicitKey };
    }
    return { provider: provider || 'openai', key: explicitKey };
  }
  if (anthropic) return { provider: 'anthropic', key: anthropic };
  if (openai) return { provider: 'openai', key: openai };
  return { provider: null, key: null };
}

export function offlineSkillHint() {
  return [
    'No API key found. QC 4.1 Light works offline as a skill:',
    '',
    '  1. Give your AI harness SKILL.md + prompts/analyze-call.md',
    '  2. Paste the transcript',
    '  3. Ask: Analyze this call with QC 4.1 Light.',
    '  4. Validate: python3 scripts/validate_report.py report.json',
    '',
    'For live API analysis, set ANTHROPIC_API_KEY or OPENAI_API_KEY,',
    'or pass --provider anthropic|openai --key <key> (prefer env).',
    '',
    'Demo without a key: qc41-light demo',
  ].join('\n');
}

async function callAnthropic(key, compiledPrompt) {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': key,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: process.env.QC41_ANTHROPIC_MODEL || 'claude-sonnet-4-20250514',
      max_tokens: 8192,
      temperature: 0.2,
      messages: [{ role: 'user', content: compiledPrompt }],
    }),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`Anthropic API ${res.status}: ${body.slice(0, 400)}`);
  }
  const data = await res.json();
  const text = (data.content || [])
    .filter((b) => b.type === 'text')
    .map((b) => b.text)
    .join('\n');
  return text;
}

async function callOpenAI(key, compiledPrompt) {
  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: process.env.QC41_OPENAI_MODEL || 'gpt-4o',
      temperature: 0.2,
      response_format: { type: 'json_object' },
      messages: [
        {
          role: 'system',
          content: 'You are QC 4.1 Light. Return only valid JSON matching the schema.',
        },
        { role: 'user', content: compiledPrompt },
      ],
    }),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`OpenAI API ${res.status}: ${body.slice(0, 400)}`);
  }
  const data = await res.json();
  return data.choices?.[0]?.message?.content || '';
}

/**
 * Analyze a transcript with BYOK provider.
 * @returns {Promise<object>} validated report
 */
export async function analyzeTranscript(transcript, options = {}) {
  const { provider, key } = resolveCredentials(options);
  if (!provider || !key) {
    const err = new Error(offlineSkillHint());
    err.code = 'NO_API_KEY';
    err.exitCode = 2;
    throw err;
  }

  const compiled = buildCompiledPrompt(transcript, {
    context: options.context || '',
    language: options.language || '',
  });

  const raw =
    provider === 'anthropic'
      ? await callAnthropic(key, compiled)
      : await callOpenAI(key, compiled);

  const parsed = extractJson(raw);
  return validateReport(parsed);
}
