# FreeModel Radar

**FreeModel Radar checks OpenRouter's free model lineup every 30 minutes and tracks every listing and delisting — so you hear about free models going live (or disappearing) the same half hour it happens, not days later.**

**Status:** 🟢 [19 free models live right now](https://freemodel-radar.brodydung.workers.dev) · checks run every 30 minutes · data below as of 2026-10-30 02:45 UTC

## Live status

The always-updated status page is here: **[freemodel-radar.brodydung.workers.dev](https://freemodel-radar.brodydung.workers.dev)**

It shows the current free lineup and the most recent listing/delisting changes. The machine-readable snapshot behind it is [`data.json`](data.json) in this repository.

## FreeModel Radar Pro — $19/year

The public status page is free. **Pro** adds speed and history:

- **Instant Telegram alerts** the moment a free model is listed or delisted (within one 30-minute check cycle)
- **Full change history archive** — every listing/delisting event since launch

👉 **[Get FreeModel Radar Pro — $19/year](https://original2011.gumroad.com/l/ifxmg)**

## Honest note — what this radar does and does not do

FreeModel Radar tracks **listing status and free/paid status only**. It does **not** run, benchmark, or test individual models, and it makes no claim about any model's quality, speed, or reliability. Every model in the list is explicitly marked **"Not tested"** — if you pick one, you are evaluating it yourself.

A model counts as free when its OpenRouter API pricing is fully $0 (prompt and completion pricing present and zero, and no non-zero charge on any other pricing component).

## Current free models

Data as of 2026-10-30 02:45 UTC — 19 models. Source: [`data.json`](data.json) (snapshot of the radar's live status file).

| # | Model | Free status | Tested status |
|---|-------|-------------|---------------|
| 1 | `cohere/north-mini-code:free` | Listed · Free | Not tested |
| 2 | `dots-studio/dots-3-note-preview:free` | Listed · Free | Not tested |
| 3 | `google/gemma-4-26b-a4b-it:free` | Listed · Free | Not tested |
| 4 | `google/gemma-4-31b-it:free` | Listed · Free | Not tested |
| 5 | `google/lyria-3-clip-preview` | Listed · Free | Not tested |
| 6 | `google/lyria-3-pro-preview` | Listed · Free | Not tested |
| 7 | `liquid/lfm-2.5-2.6b:free` | Listed · Free | Not tested |
| 8 | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | Listed · Free | Not tested |
| 9 | `nvidia/nemotron-3-ultra-550b-a55b:free` | Listed · Free | Not tested |
| 10 | `nvidia/nemotron-3.5-content-safety:free` | Listed · Free | Not tested |
| 11 | `nvidia/nemotron-3.5-lightning:free` | Listed · Free | Not tested |
| 12 | `nvidia/nemotron-3.5-super-vl:free` | Listed · Free | Not tested |
| 13 | `openrouter/free` | Listed · Free | Not tested |
| 14 | `poolside/laguna-s-2.1:free` | Listed · Free | Not tested |
| 15 | `poolside/laguna-xs-2.1:free` | Listed · Free | Not tested |
| 16 | `recursive/flint-v1.0:free` | Listed · Free | Not tested |
| 17 | `thinkingmachines/inkling-small:free` | Listed · Free | Not tested |
| 18 | `thinkingmachines/inkling:free` | Listed · Free | Not tested |
| 19 | `xingchen-agi/xing4.0-29b-a4b:free` | Listed · Free | Not tested |

## How it works

A poller queries OpenRouter's public `/models` endpoint every 30 minutes, diffs the free set against the previous snapshot, and records listing/delisting events. An empty or sharply shrunken response is refused rather than recorded, so a glitch upstream never wipes the baseline.

## License

MIT — see [`LICENSE`](LICENSE). The model list data in `data.json` is a factual snapshot of OpenRouter's public pricing pages.
