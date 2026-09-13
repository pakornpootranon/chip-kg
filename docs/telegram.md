# Connect Hermes to Telegram

Hermes talks to you through a Telegram bot that only you can use. There are
two ways to get one. Path A is the easy one and needs nothing from Telegram's
side. Path B is for people who already have a bot or want full control.

Both paths end with the same three commands, so read to the end either way.

## Path A: let Hermes create the bot for you (recommended)

1. In the Hermes desktop app open Messaging, choose Telegram, and click the
   Create button. On the command line the same thing is
   `hermes gateway setup`, then choose Telegram and the managed bot option.
2. A QR code appears. Scan it with your phone, or tap the link it shows if
   you are already on your phone. Telegram opens a new bot chat that Hermes
   created for you (the name will look like "Hermes Agent").
3. Press Start in that chat. Hermes finishes the pairing on its own and
   stores the bot token locally in `~/.hermes/.env`.

(Screenshot of the Create button goes here.)

## Path B: bring your own bot

1. In Telegram, open @BotFather and send `/newbot`. Answer the two questions
   (a display name, then a username ending in `bot`). BotFather replies with
   a token that looks like `123456789:AA...`. That token is a password.
2. Open @userinfobot and press Start. It replies with your numeric user ID.
3. Run `hermes gateway setup`, choose Telegram, choose the own-bot option, and
   paste the token and your user ID when asked.

## Then, for both paths

1. Start the gateway as a background service so it keeps listening after you
   close the terminal:
   ```
   hermes gateway install
   ```
   (`hermes gateway run` runs it in the foreground instead, handy for a first
   test.)
2. Send any message to your bot from Telegram. The first message from a new
   account is held until you approve it:
   ```
   hermes pairing list
   hermes pairing approve <code>
   ```
3. Check it is connected:
   ```
   hermes gateway status
   ```

## Keep the token secret

The bot token lives in `~/.hermes/.env`. Never paste it into a chat, a
screenshot, or a git repo. Anyone with the token can send and read messages
as your bot. If it ever leaks, open @BotFather, send `/revoke`, pick the bot,
and run `hermes gateway setup` again with the new token.

## One thing to know before scheduling anything

A Telegram chat cannot ask you for a password. If a skill needs a credential
that is not set yet (for example the three Neo4j values the kg-update skill
uses), Hermes can only prompt for it in the desktop app or in `hermes chat`
on your computer, not in Telegram. Enter those once from the app before you
create a cron job, or add them to `~/.hermes/.env` yourself. See
[`hermes.md`](hermes.md) for the order that avoids this problem.
