import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const repoRoot = resolve(process.cwd(), "..");
const scriptsDir = resolve(repoRoot, "scripts");
const venvPython = resolve(repoRoot, "venv", "bin", "python3");
const pythonBin = process.env.PYTHON_BIN || (existsSync(venvPython) ? venvPython : "python3");

async function runLeadScript(scriptName: string, args: string[] = []) {
  const scriptPath = resolve(scriptsDir, scriptName);
  let stdout = "";
  let stderr = "";

  try {
    const result = await execFileAsync(pythonBin, [scriptPath, ...args], {
      cwd: repoRoot,
      maxBuffer: 1024 * 1024
    });
    stdout = result.stdout;
    stderr = result.stderr;
  } catch (error) {
    const message =
      error && typeof error === "object" && "stderr" in error && typeof error.stderr === "string"
        ? error.stderr.trim().split("\n").pop()
        : error instanceof Error
          ? error.message
          : `Unable to execute ${scriptName}.`;
    throw new Error(message || `Unable to execute ${scriptName}.`);
  }

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

export async function getLeadInboxSnapshot() {
  return runLeadScript("lead_inbox_snapshot.py");
}

export async function approveLead(leadId: string) {
  return runLeadScript("lead_inbox_action.py", ["approve", leadId]);
}

export async function rejectLead(leadId: string) {
  return runLeadScript("lead_inbox_action.py", ["reject", leadId]);
}
