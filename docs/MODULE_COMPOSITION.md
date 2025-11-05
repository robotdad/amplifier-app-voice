# Module Composition

How amplifier-app-voice composes Amplifier modules to create a working voice assistant.

## Overview

This app demonstrates **Amplifier's modular architecture** by composing one new module (OpenAI Realtime provider) with existing Amplifier modules (orchestrator and context manager).

## Module Stack

```
┌─────────────────────────────────────────┐
│  amplifier-app-voice (THIS APP)         │
│  • Desktop application layer            │
│  • PyAudio for mic/speakers             │
│  • Rich for terminal UI                 │
│  • Coordinates voice interaction        │
└──────────────┬──────────────────────────┘
               │ configures via
               ▼
┌─────────────────────────────────────────┐
│  profiles/voice.md (PROFILE)            │
│  • Declares module composition          │
│  • Sets default configuration           │
└──────────────┬──────────────────────────┘
               │ compiled to mount plan
               ▼
┌──────────────────────────────────────────────────────┐
│  Amplifier Core (KERNEL)                             │
│  • Loads modules per mount plan                      │
│  • Coordinates execution                             │
│  • Zero changes for audio support!                   │
└─┬────────────┬─────────────────┬─────────────────────┘
  │            │                 │
  ▼            ▼                 ▼
┌──────────┐ ┌───────────────┐ ┌──────────────────────────┐
│ EXISTING │ │ EXISTING      │ │ NEW MODULE               │
│          │ │               │ │                          │
│ loop-    │ │ context-      │ │ provider-openai-realtime │
│ basic    │ │ simple        │ │                          │
│          │ │               │ │ • WebSocket to OpenAI    │
│ Turn-    │ │ In-memory     │ │ • Audio I/O (PCM16)      │
│ based    │ │ conversation  │ │ • Native speech-to-speech│
│ execution│ │ history       │ │ • Audio in raw field     │
└──────────┘ └───────────────┘ └──────────────────────────┘
```

## The Modules

### NEW: amplifier-module-provider-openai-realtime

**What we built**: OpenAI Realtime API provider

**Repository**: https://github.com/robotdad/amplifier-module-provider-openai-realtime

**Purpose**: Native speech-to-speech via OpenAI's Realtime API

**Capabilities**:
- WebSocket connection to OpenAI (`wss://api.openai.com/v1/realtime`)
- Accepts audio input (PCM16, 24kHz, mono)
- Returns audio output + text transcript
- Stores audio in `ProviderResponse.raw` field
- Zero kernel changes (pure edge implementation)
- Follows provider protocol (works with existing orchestrators)

**Novel contribution**: First audio-capable provider in Amplifier ecosystem

---

### EXISTING: amplifier-module-loop-basic

**Source**: https://github.com/microsoft/amplifier-module-loop-basic

**Purpose**: Basic turn-based orchestrator

**What it does**:
- Manages conversation flow
- Calls `provider.complete()` with messages
- Handles tool execution
- Returns responses to caller

**Why we use it**: Simple, proven orchestrator. Works perfectly for turn-based voice conversation.

---

### EXISTING: amplifier-module-context-simple

**Source**: https://github.com/microsoft/amplifier-module-context-simple

**Purpose**: In-memory conversation context

**What it does**:
- Stores conversation history
- Provides context to provider
- Maintains state during session

**Why we use it**: Lightweight, no persistence needed for exploratory voice app.

---

## How They Work Together

### 1. Profile Defines Composition

**File**: `profiles/voice.md`

```yaml
session:
  orchestrator:
    module: loop-basic          # Existing Microsoft module
  context:
    module: context-simple      # Existing Microsoft module

providers:
  - module: provider-openai-realtime  # NEW robotdad module
    source: git+https://github.com/robotdad/amplifier-module-provider-openai-realtime@main
```

This is **declarative module composition** - we declare what modules we want, Amplifier loads them.

### 2. App Loads Profile

**File**: `src/amplifier_app_voice/session_manager.py`

```python
# Load voice profile
profile_path = Path(__file__).parent.parent.parent / "profiles"
loader = ProfileLoader(search_paths=[profile_path])
profile = loader.load_profile("voice")

# Compile to mount plan
mount_plan = compile_profile_to_mount_plan(profile)

# Override config with app settings
mount_plan["providers"][0]["config"]["api_key"] = self.config.api_key
mount_plan["providers"][0]["config"]["voice"] = self.config.voice
# ... etc

# Create session
session = AmplifierSession(config=mount_plan)
```

**This is the same pattern as blog-creator** - load profile, compile to mount plan, override settings, create session.

### 3. Execution Flow

```
1. User presses SPACE
   ↓
2. App records audio (PyAudio)
   ↓
3. App calls provider.complete([audio_message])
   ↓
4. Provider sends audio to OpenAI via WebSocket
   ↓
5. OpenAI processes audio → responds with audio
   ↓
6. Provider returns ProviderResponse:
   - content: text transcript
   - raw.audio_data: PCM16 audio bytes
   ↓
7. App plays audio through speakers (PyAudio)
   ↓
8. App displays transcript (Rich)
```

**Note**: We bypass the orchestrator for audio because `session.execute()` doesn't support audio yet. We call `provider.complete()` directly with audio messages.

## Why This Architecture Works

### Zero Kernel Changes ✅

The new audio provider works with **existing** Amplifier infrastructure:
- ✅ loop-basic orchestrator (no changes)
- ✅ context-simple manager (no changes)
- ✅ amplifier-core kernel (no changes)
- ✅ Provider protocol (no changes)

**The only new code**: The provider module itself

### Modular Composition ✅

Mix and match modules:
- Want different orchestrator? Change profile to `loop-streaming`
- Want persistent context? Change profile to `context-persistent`
- Want different provider? Swap in `provider-anthropic`
- **Modules are interchangeable**

### Profile-Based Configuration ✅

Just like blog-creator:
- Profile declares modules
- App loads profile
- Runtime overrides config
- Clean separation: what modules (profile) vs how to configure them (app)

## Edge-First Audio Strategy

### Why Audio in `raw` Field?

**Current approach**: Audio stored in `ProviderResponse.raw`, not as new `AudioBlock` content type

**Rationale** (per Amplifier kernel philosophy):
1. **Two-implementation rule**: Wait for second audio provider before promoting to kernel
2. **Prototype at edges**: Prove pattern works before kernel changes
3. **No breaking changes**: Works with existing Amplifier infrastructure
4. **Reversible**: Can promote to `AudioBlock` later if validated

### Evolution Path

```
Phase 1 (now): Audio in raw field
    ↓ validates that audio providers are useful
Phase 2: Second audio provider emerges (Azure Speech? ElevenLabs?)
    ↓ convergence on audio pattern
Phase 3: Propose AudioBlock to amplifier-core
    ↓ with evidence from 2+ implementations
Phase 4: Kernel accepts, promote to ContentBlockUnion
```

**This is exactly how Amplifier is designed to evolve** - edges prove patterns, then kernel adopts.

## What Makes This Special

### First Audio Support in Amplifier

- **Before**: Text-only providers (Anthropic, OpenAI, Azure, Ollama)
- **Now**: Audio-capable provider (OpenAI Realtime)
- **Impact**: Opens voice interaction use cases

### Composability Validated

This app proves you can:
- ✅ Build new providers (audio)
- ✅ Compose with existing modules (orchestrator, context)
- ✅ Use profile system (voice.md)
- ✅ No kernel changes needed
- ✅ Everything works together

### True Audio-to-Audio

Not STT→LLM→TTS (3-step pipeline). This is **native audio I/O**:
- Microphone → OpenAI Realtime API → Speakers
- Single model, single API call
- Ultra-low latency (~1-2 seconds)

## Comparison to Blog Creator

| Aspect | Blog Creator | Voice App |
|--------|-------------|-----------|
| **New modules** | style-extraction, image-generation, markdown-utils | provider-openai-realtime |
| **Existing modules** | loop-basic, context-simple, provider-anthropic, tool-filesystem, tool-bash | loop-basic, context-simple |
| **Profile location** | `.amplifier/profiles/blog-creator.md` | `profiles/voice.md` |
| **Config pattern** | Extends base, adds tools | Standalone, adds audio provider |
| **Novel capability** | Style-aware writing + illustration | Native speech-to-speech |

**Both follow the same Amplifier pattern**: Compose modules via profiles.

## See Also

- [Architecture](ARCHITECTURE.md) - App design and components
- [Configuration](CONFIGURATION.md) - Settings and overrides
- [Provider README](https://github.com/robotdad/amplifier-module-provider-openai-realtime) - Provider documentation
