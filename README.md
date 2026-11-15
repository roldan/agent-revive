# hc-agent-resume

Automatically restore coding-agent sessions after herdr-core or the machine
restarts.

Herdr restores panes and terminal shells. hc-agent-resume remembers which
agent session belonged to each terminal, then resumes it when Herdr Core
reports that the terminal has recovered.

## How it works

1. An agent integration records its session id and working directory in an
   `hc-agent-resume.record` label on its Herdr Core terminal.
2. `hc-agent-resumed.service` subscribes to Herdr Core's `events.subscribe`
   API.
3. On a core reconnect it receives an atomic terminal snapshot; on changes it
   receives ordered `restarted`, `foreground`, and `labels` events.
4. When a labelled terminal has recovered to an idle shell, the supervisor
   sends its safe resume command to that shell. The agent remains Bash's direct
   foreground child, so Herdr receives and displays its agent status.

There is no shell startup hook, polling race, or per-terminal background
process. The supervisor reconnects after a core restart and reconciles the new
snapshot.

## Requirements

- Herdr and herdr-core (`hc`)
- Python 3.9 or newer
- systemd user services (Linux)
- A supported agent (currently Pi)

## Install

```sh
git clone https://github.com/roldan/hc-agent-resume.git
cd hc-agent-resume
./install.sh
```

The installer copies the command to `~/.local/bin`, installs the supported
agent integration, and installs/enables `hc-agent-resumed.service`.

For Pi, reload it with `/reload`, or start a new Pi session, then send at least
one message. Pi creates durable session data only after its first turn.

## Commands

```sh
hc-agent-resume status
systemctl --user status hc-agent-resumed.service
journalctl --user -u hc-agent-resumed.service -f
```

## Adding an agent

Resume commands are explicit adapters in `bin/hc-agent-resume`:

```python
ADAPTERS = {
    "pi":     ("pi", "--session"),
    "claude": ("claude", "--resume"),
    "codex":  ("codex", "resume"),
}
```

To enable an adapter, add the agent's thin session-start/session-end
integration. It calls `hc-agent-resume record --agent NAME --session ID --cwd
PATH` when a session becomes resumable, and `hc-agent-resume forget` only when
the person explicitly ends it. The supervisor needs no changes.

## Safety

The terminal label stores structured data, not shell code. The supervisor only
uses known adapters; it validates the session id and existing working directory
before constructing a fixed resume argv.

## Current scope

Pi has the included integration. Claude and Codex have explicit resume adapters
but still need their respective hooks before they are enabled.
