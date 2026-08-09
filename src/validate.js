/**
 * Lightweight structural validation mirroring scripts/validate_report.py.
 * Enough to catch broken model output before writing a report.
 */

const STAGES = new Set([
  'opening', 'agenda', 'discovery', 'problem', 'impact', 'solution', 'proof',
  'price', 'objection', 'decision', 'next_step', 'unknown',
]);
const OBJECTIONS = new Set([
  'timing', 'priority', 'trust', 'fit', 'price', 'authority', 'risk',
  'implementation', 'unknown',
]);
const MISTAKES = new Set([
  'weak_agenda', 'premature_pitch', 'shallow_discovery', 'missed_follow_up',
  'unsupported_claim', 'overtalking', 'weak_transition', 'objection_not_clarified',
  'pressure', 'vague_next_step', 'poor_fit_not_addressed', 'other',
]);
const TOP = new Set([
  'version', 'language', 'transcript_quality', 'call_summary', 'call_outcome',
  'stage_analysis', 'strengths', 'breakpoint', 'objections', 'mistakes',
  'corrections', 'recovery_line', 'replay_plan', 'next_call_focus',
  'next_call_checklist', 'confidence', 'limitations',
]);

function fail(msg) {
  throw new Error(msg);
}

function nonempty(value, path, minimum = 1) {
  if (typeof value !== 'string' || value.trim().length < minimum) {
    fail(`${path}: expected non-empty string (min ${minimum})`);
  }
  return value;
}

function evidence(obj, path) {
  if (!obj || typeof obj !== 'object') fail(`${path}: expected object`);
  const keys = Object.keys(obj).sort().join(',');
  if (keys !== 'quote,speaker,timestamp') fail(`${path}: fields must be quote,speaker,timestamp`);
  nonempty(obj.quote, `${path}.quote`, 2);
  for (const key of ['speaker', 'timestamp']) {
    if (obj[key] !== null && typeof obj[key] !== 'string') {
      fail(`${path}.${key}: expected string or null`);
    }
  }
}

function score(value, path) {
  if (typeof value !== 'number' || Number.isNaN(value) || value < 0 || value > 1) {
    fail(`${path}: expected number between 0 and 1`);
  }
}

export function validateReport(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) fail('root: expected object');
  const keys = new Set(Object.keys(data));
  if (keys.size !== TOP.size || [...TOP].some((k) => !keys.has(k))) {
    const missing = [...TOP].filter((k) => !keys.has(k));
    const extra = [...keys].filter((k) => !TOP.has(k));
    fail(`root fields mismatch; missing=${missing.sort()}, extra=${extra.sort()}`);
  }
  if (data.version !== 'qc41-light-0.2') fail('version: expected qc41-light-0.2');
  nonempty(data.language, 'language', 2);
  const lang = data.language;
  if (!(lang === 'en' || lang.startsWith('en-') || lang === 'es' || lang.startsWith('es-'))) {
    fail('language: expected en, es, or a regional variant');
  }

  const tq = data.transcript_quality;
  if (!tq || typeof tq !== 'object') fail('transcript_quality: invalid');
  if (!['complete', 'partial', 'fragment'].includes(tq.completeness)) {
    fail('transcript_quality.completeness: invalid');
  }
  if (typeof tq.speaker_labels !== 'boolean' || typeof tq.timestamps !== 'boolean') {
    fail('transcript_quality labels/timestamps: expected boolean');
  }
  if (!Array.isArray(tq.notes)) fail('transcript_quality.notes: expected array');
  tq.notes.forEach((n, i) => nonempty(n, `transcript_quality.notes[${i}]`, 3));

  nonempty(data.call_summary, 'call_summary', 20);
  const outcome = data.call_outcome;
  if (!outcome || typeof outcome !== 'object') fail('call_outcome: invalid');
  if (!['won', 'lost', 'follow_up', 'no_decision', 'disqualified', 'unknown'].includes(outcome.status)) {
    fail('call_outcome.status: invalid');
  }
  evidence(outcome.evidence, 'call_outcome.evidence');

  if (!Array.isArray(data.stage_analysis) || data.stage_analysis.length < 3 || data.stage_analysis.length > 12) {
    fail('stage_analysis: expected 3-12 items');
  }
  data.stage_analysis.forEach((s, i) => {
    const p = `stage_analysis[${i}]`;
    if (!STAGES.has(s.stage)) fail(`${p}.stage: invalid`);
    if (!['strong', 'partial', 'weak', 'not_observed'].includes(s.status)) fail(`${p}.status: invalid`);
    if (!Array.isArray(s.evidence) || s.evidence.length > 3) fail(`${p}.evidence: expected max 3`);
    s.evidence.forEach((e, j) => evidence(e, `${p}.evidence[${j}]`));
    nonempty(s.finding, `${p}.finding`, 10);
  });

  if (!Array.isArray(data.strengths) || data.strengths.length !== 2) fail('strengths: expected exactly 2');
  data.strengths.forEach((s, i) => {
    nonempty(s.finding, `strengths[${i}].finding`, 10);
    evidence(s.evidence, `strengths[${i}].evidence`);
    nonempty(s.why_keep, `strengths[${i}].why_keep`, 10);
  });

  const bp = data.breakpoint;
  if (!STAGES.has(bp.stage)) fail('breakpoint.stage: invalid');
  evidence(bp.evidence, 'breakpoint.evidence');
  nonempty(bp.why_it_mattered, 'breakpoint.why_it_mattered', 10);

  if (!Array.isArray(data.objections) || data.objections.length > 5) fail('objections: expected 0-5');
  data.objections.forEach((o, i) => {
    if (!OBJECTIONS.has(o.label)) fail(`objections[${i}].label: invalid`);
    evidence(o.evidence, `objections[${i}].evidence`);
    nonempty(o.interpretation, `objections[${i}].interpretation`, 10);
    score(o.confidence, `objections[${i}].confidence`);
  });

  if (!Array.isArray(data.mistakes) || data.mistakes.length !== 3) fail('mistakes: expected exactly 3');
  data.mistakes.forEach((m, i) => {
    if (!/^M[1-3]$/.test(m.id)) fail(`mistakes[${i}].id: invalid`);
    if (!MISTAKES.has(m.category)) fail(`mistakes[${i}].category: invalid`);
    nonempty(m.finding, `mistakes[${i}].finding`, 10);
    evidence(m.evidence, `mistakes[${i}].evidence`);
    nonempty(m.consequence, `mistakes[${i}].consequence`, 10);
  });

  if (!Array.isArray(data.corrections) || data.corrections.length !== 3) fail('corrections: expected exactly 3');
  data.corrections.forEach((c, i) => {
    if (!['M1', 'M2', 'M3'].includes(c.mistake_id)) fail(`corrections[${i}].mistake_id: invalid`);
    nonempty(c.action, `corrections[${i}].action`, 10);
    nonempty(c.why, `corrections[${i}].why`, 10);
    nonempty(c.example_line, `corrections[${i}].example_line`, 5);
  });

  nonempty(data.recovery_line.text, 'recovery_line.text', 10);
  nonempty(data.recovery_line.why, 'recovery_line.why', 10);

  const rp = data.replay_plan;
  for (const k of ['opening_question', 'diagnostic_follow_up', 'objection_clarifier', 'next_step_line']) {
    nonempty(rp[k], `replay_plan.${k}`, 10);
  }

  if (!Array.isArray(data.next_call_focus) || data.next_call_focus.length < 1 || data.next_call_focus.length > 3) {
    fail('next_call_focus: expected 1-3');
  }
  data.next_call_focus.forEach((x, i) => nonempty(x, `next_call_focus[${i}]`, 5));

  if (!Array.isArray(data.next_call_checklist) || data.next_call_checklist.length !== 5) {
    fail('next_call_checklist: expected exactly 5');
  }
  data.next_call_checklist.forEach((x, i) => nonempty(x, `next_call_checklist[${i}]`, 5));

  score(data.confidence.score, 'confidence.score');
  nonempty(data.confidence.reason, 'confidence.reason', 10);
  if (!Array.isArray(data.confidence.missing_context)) fail('confidence.missing_context: expected array');
  data.confidence.missing_context.forEach((x, i) => nonempty(x, `confidence.missing_context[${i}]`, 3));

  if (!Array.isArray(data.limitations) || data.limitations.length < 1) fail('limitations: expected non-empty array');
  data.limitations.forEach((x, i) => nonempty(x, `limitations[${i}]`, 5));

  return data;
}

/** Extract JSON object from model text (raw or fenced). */
export function extractJson(text) {
  const trimmed = String(text || '').trim();
  if (!trimmed) fail('empty model response');
  try {
    return JSON.parse(trimmed);
  } catch {
    /* continue */
  }
  const fence = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) {
    return JSON.parse(fence[1].trim());
  }
  const start = trimmed.indexOf('{');
  const end = trimmed.lastIndexOf('}');
  if (start >= 0 && end > start) {
    return JSON.parse(trimmed.slice(start, end + 1));
  }
  fail('could not parse JSON from model response');
}
