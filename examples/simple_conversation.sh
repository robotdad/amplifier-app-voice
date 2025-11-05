#!/bin/bash
# Quick start script for amplifier-app-voice

set -e

echo "🎤 Amplifier Voice Assistant - Quick Start"
echo ""

# Check OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set"
    echo ""
    echo "Set your API key:"
    echo "  export OPENAI_API_KEY=\"sk-...\""
    echo ""
    exit 1
fi

echo "✅ API key found"

# Check PortAudio (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! brew list portaudio &>/dev/null; then
        echo "⚠️  PortAudio not installed"
        echo ""
        echo "Installing PortAudio..."
        brew install portaudio
    else
        echo "✅ PortAudio installed"
    fi
fi

# Check if amplifier-voice is installed
if ! command -v amplifier-voice &>/dev/null; then
    echo "⚠️  amplifier-voice not installed"
    echo ""
    echo "Install with:"
    echo "  uv pip install git+https://github.com/robotdad/amplifier-app-voice@main"
    echo ""
    exit 1
fi

echo "✅ amplifier-voice installed"
echo ""
echo "🚀 Launching voice assistant..."
echo ""
echo "Controls:"
echo "  SPACE - Hold to record, release to send"
echo "  Ctrl+C - Exit"
echo ""
echo "────────────────────────────────────────"
echo ""

# Launch the app
amplifier-voice
