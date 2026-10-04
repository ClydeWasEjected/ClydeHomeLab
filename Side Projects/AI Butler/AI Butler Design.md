# AI Butler Design

Side project, not part of the core A-H roadmap. Global day-to-day AI assistant: voice
interface, Home Assistant/IoT control, project awareness via Hermes. Long-term: face
recognition, visual/hologram interface. Status: planning only, nothing built yet.

## Current State

**Status:** ⬜ Planning. No code written.

### Vision

A local-first voice assistant (TikTok-Jarvis style) that:
- Listens (STT) and talks back (TTS)
- Judges each request locally (Ollama) and routes to either local Ollama or Claude
  depending on complexity
- Controls IoT devices via Home Assistant
- Has context on Clyde's projects/phases via Hermes (the "global life butler")
- Later: face recognition for personalization, visual/hologram display

### Architecture (planned)

```
[Mic] → STT (Whisper) → Judge (Ollama) → route:
                                            ├── Ollama (simple/local-only tasks)
                                            └── Claude API (complex tasks)
                          → TTS (response) → [Speaker]

Side integrations:
  - Home Assistant (MQTT/REST) — device control
  - Hermes (claude-srv data) — project/phase/note context
```

### Build order

1. **Router/orchestrator service** — lightweight FastAPI (or similar) on claude-srv (A8).
   Takes STT text in, judge decides route, calls Claude or Ollama, returns text for TTS.
2. **Judge logic** — small Ollama model (Phi-3-mini / Llama 3.2 3B / Qwen2.5 3B,
   quantized) classifies request complexity. A small model is the right tool here —
   classification doesn't need a large model.
3. **STT (Whisper)** — `small`/`base` model, runs on the 1650's 4GB VRAM comfortably.
4. **TTS** — local text-to-speech, engine TBD.
5. **Home Assistant device control** — once 1-4 work, wire in MQTT/REST calls.
6. **Hermes context** — butler queries claude-srv's Hermes data for project/phase
   awareness.
7. **Future, no timeline:** face recognition, visual/hologram display.

### Hardware allocation

| Component | Host | Why |
|---|---|---|
| Router/orchestrator | claude-srv (A8, CT 105) | Lightweight HTTP logic, no GPU needed, A8 has 24GB RAM headroom |
| Whisper STT | proxmox-lab (GTX 1650, 4GB VRAM) | `small`/`base` Whisper models fit comfortably in 4GB |
| Ollama judge | proxmox-lab (GTX 1650) | 3B-class model, fits in 4GB alongside Whisper if not run concurrently at scale |
| TTS | TBD | likely CPU-fine, host undecided |
| Home Assistant | TBD (Vaio? svc-01?) | not yet running in the lab |

### GPU host always-on status

The 1650 lives on **proxmox-lab**, which is a dual-boot gaming PC in principle —
this vault's own rule normally keeps infra-critical services off hardware like that
([[Homelab - Project Overview]], README non-goals). As of 2026-10-03, Clyde isn't
booting it into Windows, so it's functioning as always-on in practice. Treating
proxmox-lab as the butler's GPU host on that basis.

Caveat: this is a current-state call, not a hardware guarantee. If Windows/gaming use
resumes, the butler's STT/judge capability goes down with it. Worth building the
degrade-gracefully fallback (router skips the local judge and goes Claude-only when
proxmox-lab is unreachable) regardless, as cheap insurance rather than a blocking
requirement.

### Resource sizing notes

- **A8** (AMD A8-9425, 24GB RAM, no dedicated GPU): fine for the router/orchestrator —
  it's HTTP routing, not inference. Already shares the box with pfSense (VM) and
  svc-01 (CT); 24GB has headroom for one more lightweight CT/process.
- **GTX 1650** (4GB VRAM): enough for Phase 1 scope (Whisper small/base + a 3B-class
  Ollama judge). Not enough to run a large model as the actual local responder — that's
  fine, Claude covers the complex cases via the router.

## Change Log

- 2026-10-03: Design doc created. Vision, architecture, build order, hardware
  allocation, and the proxmox-lab always-on conflict captured from planning
  conversation with Clyde. Nothing built yet; this is the plan to build from.
- 2026-10-03: Clyde confirmed proxmox-lab isn't currently used for Windows/gaming,
  so it's treated as always-on for the butler's GPU host. Noted as a current-state
  call, not a permanent guarantee; degrade-gracefully fallback still recommended.
