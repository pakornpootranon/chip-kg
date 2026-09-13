# Which AI model Hermes uses, and what it costs

Hermes Agent is the program that runs on your computer. The thinking is done
by a model from a provider you choose. You need exactly one provider set up
before any skill or cron job will run.

## Pick a provider

Run the setup wizard:

```
hermes setup
```

It walks you through choosing a provider and signing in or pasting a key.
You can change it later with `hermes model`. Providers Hermes supports
out of the box include:

- Nous Portal (sign in with `hermes login`; includes free models, which is
  the cheapest way to start)
- OpenRouter (one key, routes to almost any model; key name `OPENROUTER_API_KEY`)
- OpenAI Codex (sign in through `hermes auth`)
- Z.AI, Kimi, MiniMax, AWS Bedrock, and any OpenAI-compatible endpoint

## Where the key goes

Keys are stored in `~/.hermes/.env`, the same file that holds your Neo4j
credentials and your Telegram bot token. Never paste that file or any key
into a chat, a screenshot, or a git repo.

## What one daily brief costs

Rough numbers, so you can decide whether a free model is enough:

- One run of the kg-morning-brief skill reads a company list, does a handful
  of web searches, and writes five to eight lines. Expect something in the
  region of 20,000 to 60,000 tokens per run, mostly input.
- At 30 runs a month that is roughly 1 m to 2 m tokens.
- On a free model through Nous Portal: $0.
- On a mid-priced model through OpenRouter (say $1 to $3 per million input
  tokens): roughly $2 to $6 a month.
- On a top-tier model ($10 to $15 per million input tokens): roughly $15 to
  $30 a month.

The weekly kg-update run is smaller (four or five runs a month) and adds a
fraction of that.

These are estimates from typical token counts, not a promise. Every provider
shows usage on its own dashboard; check it after the first week and adjust.

## Which model is good enough

The brief and the update loop are reading and summarising tasks with a few
tool calls. A mid-tier model handles them well. If the proposals in the
weekly diff start looking sloppy (wrong company names, made-up
relationships), that is the signal to move up a tier, not a reason to skip
the human approval step.
