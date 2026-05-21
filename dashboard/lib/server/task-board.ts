import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const repoRoot = resolve(process.cwd(), "..");
const scriptsDir = resolve(repoRoot, "scripts");
const venvPython = resolve(repoRoot, "venv", "bin", "python3");
const pythonBin = process.env.PYTHON_BIN || (existsSync(venvPython) ? venvPython : "python3");

async function runScript(scriptName: string) {
  const scriptPath = resolve(scriptsDir, scriptName);
  const { stdout, stderr } = await execFileAsync(pythonBin, [scriptPath], {
    cwd: repoRoot,
    maxBuffer: 1024 * 1024
  });

  const trimmed = stdout.trim();
  if (!trimmed) {
    throw new Error(stderr.trim() || `Script ${scriptName} returned no output.`);
  }

  try {
    return JSON.parse(trimmed);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown JSON parse failure";
    throw new Error(`Unable to parse ${scriptName} output: ${message}`);
  }
}

export async function getTaskBoardSnapshot() {
  return runScript("task_board_snapshot.py");
}

export async function runSalesTrigger() {
  return runScript("run_sales.py");
}

export async function runLegalTrigger() {
  return runScript("run_legal.py");
}
