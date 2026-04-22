import fs from "node:fs";
import path from "node:path";
import type { Kural } from "../types";

const CONTENT_DIR = path.resolve(process.cwd(), "..", "content", "kurals");

function readKuralFile(file: string): Kural {
  const raw = fs.readFileSync(path.join(CONTENT_DIR, file), "utf-8");
  return JSON.parse(raw) as Kural;
}

export function getAllKurals(): Kural[] {
  if (!fs.existsSync(CONTENT_DIR)) return [];
  return fs
    .readdirSync(CONTENT_DIR)
    .filter((f) => f.endsWith(".json"))
    .map(readKuralFile)
    .sort((a, b) => a.id - b.id);
}

export function getKural(id: string): Kural | null {
  const filePath = path.join(CONTENT_DIR, `${id}.json`);
  if (!fs.existsSync(filePath)) return null;
  return readKuralFile(`${id}.json`);
}

export function getAllKuralIds(): string[] {
  return getAllKurals().map((k) => String(k.id));
}
