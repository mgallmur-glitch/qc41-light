import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** Absolute path to the qc41-light package root. */
export const ROOT = path.resolve(__dirname, '..');

export function resolveFromRoot(...parts) {
  return path.join(ROOT, ...parts);
}
