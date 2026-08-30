import { copyFile, cp, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const target = resolve(root, 'public', 'portfolio');

await mkdir(target, { recursive: true });
await Promise.all([
  copyFile(resolve(root, 'index.html'), resolve(target, 'index.html')),
  copyFile(resolve(root, 'styles.css'), resolve(target, 'styles.css')),
  copyFile(resolve(root, 'script.js'), resolve(target, 'script.js')),
  cp(resolve(root, 'assets'), resolve(target, 'assets'), {
    recursive: true,
    force: true,
  }),
]);