# Keep the graph updated with Hermes Agent

Once your graph is loaded (steps 1 and 2 in [`README.md`](README.md)), you
can hand the weekly maintenance to [Hermes Agent](https://hermes-agent.nousresearch.com),
a free, open source AI agent that runs on your own computer. Every Monday it
reads the week's chip news for the companies in your graph, proposes new
relationships, sends you the diff on Telegram, and writes to your Neo4j only
after you reply to approve. It never deletes or edits anything that is
already in the graph.

Nothing here is shared with anyone. Your Neo4j credentials stay on your
machine in `~/.hermes/.env`, your bot is yours, and the skill runs locally.

Six steps, one command each. Do them in this order; step 3 has to come
before step 5, because a Telegram chat cannot ask you for a password.

## 0. Install Hermes and uv (once)

- Hermes: follow the install page at hermes-agent.nousresearch.com, then run
  `hermes setup` and pick a model provider (see [`provider.md`](provider.md)
  for what that costs).
- uv: a small Python tool runner. The skill's scripts use it so you never
  have to install Python packages yourself.
  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  (On Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`.)

## 1. Install the skill

```
hermes skills install https://raw.githubusercontent.com/pakornpootranon/chip-kg/main/skills/kg-update/SKILL.md --category research -y
```

That downloads the skill and its three scripts into
`~/.hermes/skills/research/kg-update/`. Check with `hermes skills list`; you
should see `kg-update` under `research`.

## 2. Give it your Neo4j credentials, once

Open the Hermes desktop app (or run `hermes chat`) and type:

```
Load the kg-update skill and tell me whether it is ready to run.
```

Hermes notices the skill needs three values and asks you for them, one at a
time: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`. Copy them from the
credentials file you downloaded from Aura in step 1 of the README. They are
saved to `~/.hermes/.env` and reused from then on.

If you would rather not be prompted, add those three lines to
`~/.hermes/.env` yourself. Same result.

## 3. Test it before scheduling anything

Still in the app or `hermes chat`:

```
Use the kg-update skill to list the companies in my graph and run screen 05.
```

You should get a company list and a stale-edges table (probably empty on a
fresh graph). If you get a certificate error instead, see Troubleshooting.

## 4. Connect Telegram

Follow [`telegram.md`](telegram.md). About five minutes, mostly scanning a QR
code. Come back here when `hermes gateway status` says Telegram is connected.

## 5. Schedule the weekly run

```
hermes cron create "every monday 07:00" --skill kg-update --deliver telegram "Run the kg-update skill: scan news for the current chip-kg company list from the past 7 days, propose edges, send me the diff, wait for my approval, apply, then re-run screen 05 and report."
```

Two things to know:

- Hermes has no timezone setting for schedules. "07:00" means 7 in the
  morning on the clock of the computer running Hermes. If that computer is
  not on Bangkok time, change the hour to match.
- The computer has to be awake at that time. A laptop that is closed at 7am
  will run the job when it wakes up (Hermes catches up missed runs by
  default).

## 6. The first Monday

You will get a Telegram message with the proposed edges in plain English and
the name of the pending file. Reply to approve, and Hermes applies it and
sends back the stale-edges screen. If you say nothing, nothing is written;
the proposal waits.

To try it without waiting for Monday, send your bot a message like:

```
Use the kg-update skill on this article: https://...
```

## Troubleshooting

**"CERTIFICATE_VERIFY_FAILED" or "certificate verify failed"**
Something on your network (often company security software) inspects TLS.
Edit `~/.hermes/.env` and change `neo4j+s://` at the start of `NEO4J_URI` to
`neo4j+ssc://`. Still encrypted; it just stops checking the certificate
chain. Change it back if you move to a normal network.

**"The neo4j package is missing"**
uv is not installed or not on your PATH. Redo step 0, then open a new
terminal.

**Hermes says the skill needs setup, but never asks for the values**
You are talking to it through Telegram. Telegram cannot collect secrets. Do
step 2 from the desktop app or `hermes chat`, or edit `~/.hermes/.env`.

**The proposal has a company that is not in my graph**
The scripts refuse that on purpose: this skill adds relationships between
companies you already have, never new companies. Add the company to your
graph first (or tell Hermes to skip it).

## What the skill can and cannot do to your graph

- Can: add a new relationship between two nodes that already exist, stamped
  with today's date, the article's URL, and a confidence level.
- Cannot: delete anything, change anything, add a company. The apply script
  refuses any file that tries.
- Where things live: proposals in `~/.chip-kg/pending/`, applied ones in
  `~/.chip-kg/pending/applied/`.
