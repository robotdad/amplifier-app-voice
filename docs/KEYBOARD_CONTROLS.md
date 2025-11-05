# Keyboard Controls

Interaction controls for amplifier-app-voice.

## Press-to-Talk

**SPACE** - Record while held
- **Press**: Start recording from microphone
- **Hold**: Continue recording (up to 30 seconds max)
- **Release**: Stop recording and send to AI

**Visual feedback**:
```
🎤 Recording... (3.2s)
```

## Exit

**Ctrl+C** - Exit application
- Graceful shutdown
- Closes Amplifier session
- Releases audio devices

## During AI Response

**ESC** - Cancel current response (future)
- Stops audio playback
- Returns to ready state

**Note**: Currently responses play to completion. Interruption coming in future version.

## Status Indicators

While running, the terminal shows:

```
Press SPACE to talk...          # Ready state
🎤 Recording... (2.5s)          # Recording
⏳ Sending to AI...             # Processing
🔊 Playing response...          # Playback
```

## Keyboard Permissions

### macOS

First launch requires granting keyboard access:

1. **System Settings** → **Privacy & Security** → **Accessibility**
2. Find your terminal app (Terminal.app, iTerm2, etc.)
3. Enable checkbox

**Why**: macOS requires explicit permission for apps to detect key presses.

### Linux

No special permissions needed for keyboard detection.

### Windows

No special permissions needed for keyboard detection.

## Troubleshooting

### Spacebar not detected

**macOS**:
- Check accessibility permissions (see above)
- Restart terminal after granting permission

**All platforms**:
- Ensure terminal window has focus
- Try pressing key harder/longer
- Check terminal for error messages

### "Permission denied" on macOS

**Solution**:
- Grant accessibility permission (see macOS section above)
- Restart amplifier-voice

## See Also

- [Architecture](ARCHITECTURE.md) - How keyboard detection works
- [Configuration](CONFIGURATION.md) - Keyboard settings
