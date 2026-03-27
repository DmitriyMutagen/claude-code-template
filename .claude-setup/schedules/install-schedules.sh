#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$AGENTS_DIR"

CLAUDE_BIN="$(which claude 2>/dev/null || echo "/usr/local/bin/claude")"

echo "Using claude binary: $CLAUDE_BIN"

# --- daily-review at 23:00 ---
cat > "$AGENTS_DIR/com.aragant.claude-daily-review.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aragant.claude-daily-review</string>
    <key>ProgramArguments</key>
    <array>
        <string>$CLAUDE_BIN</string>
        <string>-p</string>
        <string>run /daily-review and send results to Telegram</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>23</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/claude-daily-review.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/claude-daily-review.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>$HOME</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin</string>
    </dict>
</dict>
</plist>
EOF

# --- good-morning at 09:00 ---
cat > "$AGENTS_DIR/com.aragant.claude-good-morning.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aragant.claude-good-morning</string>
    <key>ProgramArguments</key>
    <array>
        <string>$CLAUDE_BIN</string>
        <string>-p</string>
        <string>run /good-morning and send results to Telegram</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/claude-good-morning.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/claude-good-morning.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>$HOME</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin</string>
    </dict>
</dict>
</plist>
EOF

# --- improver weekly Sunday at 20:00 ---
cat > "$AGENTS_DIR/com.aragant.claude-improver.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aragant.claude-improver</string>
    <key>ProgramArguments</key>
    <array>
        <string>$CLAUDE_BIN</string>
        <string>-p</string>
        <string>run /improver</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>20</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/claude-improver.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/claude-improver.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>$HOME</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin</string>
    </dict>
</dict>
</plist>
EOF

echo "Plists created. Loading..."

# Unload old versions if present
launchctl unload "$AGENTS_DIR/com.aragant.claude-daily-review.plist" 2>/dev/null || true
launchctl unload "$AGENTS_DIR/com.aragant.claude-good-morning.plist" 2>/dev/null || true
launchctl unload "$AGENTS_DIR/com.aragant.claude-improver.plist" 2>/dev/null || true

# Load new
launchctl load "$AGENTS_DIR/com.aragant.claude-daily-review.plist"
launchctl load "$AGENTS_DIR/com.aragant.claude-good-morning.plist"
launchctl load "$AGENTS_DIR/com.aragant.claude-improver.plist"

echo ""
echo "Installed schedules:"
echo "  daily-review  -> every day at 23:00"
echo "  good-morning  -> every day at 09:00"
echo "  improver      -> every Sunday at 20:00"
echo ""
echo "Check: launchctl list | grep aragant"
echo "Logs:  /tmp/claude-*.log"
