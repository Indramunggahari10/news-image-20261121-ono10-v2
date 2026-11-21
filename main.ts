import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const OUT = process.env.MAKEFUN_OUTPUT_DIR || join(process.cwd(), "output");
const SRC = join(process.cwd(), "entry.png");

function fail(msg: string): never {
  console.error("main.ts: " + msg);
  process.exit(1);
}

if (!existsSync(SRC)) fail("entry.png not found in repo root");
const buf = readFileSync(SRC);
if (
  buf.length < 8 ||
  buf[0] !== 0x89 ||
  buf[1] !== 0x50 ||
  buf[2] !== 0x4e ||
  buf[3] !== 0x47
) {
  fail("entry.png is not a PNG");
}
const w = buf.readUInt32BE(16);
const h = buf.readUInt32BE(20);
if (w !== 1024 || h !== 1024) {
  fail(`entry.png must be 1024x1024, got ${w}x${h}`);
}
if (buf.length > 1024 * 1024) {
  fail(`entry.png exceeds 1 MiB (${buf.length} bytes)`);
}
mkdirSync(OUT, { recursive: true });
const dest = join(OUT, "entry.png");
copyFileSync(SRC, dest);
const out = readFileSync(dest);
if (!out.equals(buf)) fail("copied entry.png differs from source");
console.log(`main.ts: wrote ${dest} (${buf.length} bytes, 1024x1024)`);
