# Run the daily news task

The graph stays useful only if news keeps flowing into it. One prompt, [`prompts/daily-news.md`](../prompts/daily-news.md), does the whole job: it searches the last 24 hours, adds each relevant item as a NewsItem linked to the companies and chokepoints it touches, and writes a short ranked brief. It never deletes or edits anything that was already in the graph.

The same prompt runs in two places. Followers use Cowork, which runs in the cloud with your computer off. The author runs it as a local Claude Code task on his own machine, which also saves the brief into the repo.

## Before either path: allow writes

The task adds nodes, so the chip-kg connector must have its read-write tool enabled. In the connector's settings in Claude, open the tools list and switch on the read-write tool alongside schema and read. Leave it off in chats where you only ask questions.

## Path A: Cowork scheduled task (followers)

Needs a paid Claude plan. Runs remotely on Anthropic's infrastructure, so it fires whether or not your laptop is open.

1. Open Claude Desktop and switch to **Cowork**.
2. Click **Scheduled**, then **New task**.
3. Name it `chip-kg daily news`. Set the schedule to **Daily** at a morning time in your time zone.
4. In the connectors list for the task, enable **chip-kg** (the MCP for Aura connector from [`mcp.md`](mcp.md)) and make sure web search is on.
5. Paste the full text of `prompts/daily-news.md` as the task prompt. Save.
6. Click **Run now** once to test. The brief appears as the task's result, along with a count of nodes created.

Screenshot placeholder: `docs/img/schedule-01-cowork-new-task.png`.
Screenshot placeholder: `docs/img/schedule-02-cowork-connectors.png`.

Each later run appears in the Scheduled list with its brief. Scheduled runs can fire later than the set time; the prompt handles that by searching backwards from whenever it actually runs.

If the task cannot see the chip-kg connector, the connector is probably not enabled for scheduled tasks on your plan. Fall back to Path B, or run the prompt by hand in a normal chat each morning.

## Path B: Claude Code Desktop local task (author)

Runs on your own machine inside the repo, so the brief lands in `briefs/YYYY-MM-DD.md`. It only fires while the Claude Desktop app is open and the computer is awake.

1. Open Claude Desktop, go to the **Code** tab and open the chip-kg folder.
2. Click **Scheduled tasks**, then **New task**. Choose **Local**, this repo folder, **Daily** at 07:00. Leave worktree off so the brief is written into the real folder.
3. Paste the full text of `prompts/daily-news.md` as the prompt. Save.
4. Open the task and click **Run now**. On every permission prompt that appears choose **Always allow**, otherwise the next unattended run will stall waiting for you.
5. In Claude Desktop settings, under **Desktop app**, turn on **Keep computer awake**.

Screenshot placeholder: `docs/img/schedule-03-code-new-task.png`.

How missed runs behave: if the machine is asleep at 07:00 the run is skipped. When the app is next open it does one catch-up run for the most recent missed time within the last seven days, not one per missed day.

## Check that the task only added news

Before the first scheduled run, save a baseline of the graph:

```
python scripts/counts.py > briefs/baseline.json
```

After any run:

```
python scripts/counts.py --diff briefs/baseline.json
```

It prints how many NewsItem nodes were added and fails if the Company count or any non-news edge type changed. That should never happen; if it does, stop the task and check `briefs/` and the graph before running again.

## Reading the brief

Each line is one news item, ranked by graph impact: chokepoint hits first, then Tier 1, Tier 2, Tier 3 companies. If the last line says "candidate edge", the news suggests a supply relationship has changed. That is a prompt for the author to edit `data/edges.csv`, not something the task does itself. Screen 06 in [`analysis.md`](analysis.md) shows the same data over any window you choose.
