---
profile:
  name: voice
  version: "1.0.0"
  description: Voice assistant configuration for OpenAI Realtime API

providers:
  - module: provider-openai-realtime
    source: git+https://github.com/robotdad/amplifier-module-provider-openai-realtime@main
    config:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o-realtime-preview-2024-12-17
      voice: alloy
      temperature: 0.7
---

Voice assistant profile for desktop application.

Uses OpenAI Realtime API for native speech-to-speech interaction.
