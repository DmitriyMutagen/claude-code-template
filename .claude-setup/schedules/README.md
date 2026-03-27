# Scheduled Tasks

## Option A: Claude Code /schedule (interactive)

Run these commands in Claude Code:

```
/schedule → "Run /daily-review every day at 23:00"
/schedule → "Run /good-morning every day at 09:00"
/schedule → "Run /improver every Sunday at 20:00"
```

## Option B: macOS launchd (standalone, works without Claude open)

Install:

```bash
bash ~/.claude/schedules/install-schedules.sh
```

Uninstall:

```bash
launchctl unload ~/Library/LaunchAgents/com.aragant.claude-daily-review.plist
launchctl unload ~/Library/LaunchAgents/com.aragant.claude-good-morning.plist
launchctl unload ~/Library/LaunchAgents/com.aragant.claude-improver.plist
rm ~/Library/LaunchAgents/com.aragant.claude-*.plist
```

Check status:

```bash
launchctl list | grep aragant
```

Logs:

```bash
tail -f /tmp/claude-daily-review.log
tail -f /tmp/claude-good-morning.log
tail -f /tmp/claude-improver.log
```
