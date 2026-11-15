// Persist interactive Pi sessions in their Herdr Core terminal for hc-agent-resume.
import { spawnSync } from "node:child_process";

let saved = "";
let signalled = false;

function resume(args: string[]) {
  try {
    return spawnSync("hc-agent-resume", args, { stdio: "ignore", timeout: 8_000 });
  } catch {
    return null;
  }
}

function record(ctx: any) {
  if (!process.env.HC_TERMINAL_ID) return;
  try {
    const session = ctx.sessionManager.getSessionId();
    const cwd = ctx.sessionManager.getCwd?.() || ctx.cwd;
    if (!session || !cwd) return;
    const key = session + "\0" + cwd;
    if (key === saved) return;
    if (resume(["record", "--agent", "pi", "--session", session, "--cwd", cwd])?.status === 0) {
      saved = key;
    }
  } catch {
    // A fresh Pi session may not exist until after its first turn.
  }
}

export default function (pi: any) {
  // Pi reports "quit" for signal shutdown too, so preserve the record then.
  // Pi's own signal handler can emit session_shutdown before extension listeners
  // run, so yield once before deciding whether this was a real /quit.
  process.on("SIGHUP", () => { signalled = true; });
  process.on("SIGTERM", () => { signalled = true; });

  pi.on("session_start", (_event: any, ctx: any) => record(ctx));
  pi.on("agent_end", (_event: any, ctx: any) => record(ctx));
  pi.on("session_shutdown", async (event: any, ctx: any) => {
    await new Promise<void>((resolve) => setImmediate(resolve));
    if (ctx.mode === "tui" && event.reason === "quit" && !signalled) resume(["forget"]);
  });
}
