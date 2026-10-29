# FreeModel Radar

Daily leaderboard of **free models on OpenRouter**, generated programmatically
from an automated daily scan of the public OpenRouter catalogue.
No hand-edited lists; models whose parameter size could not be verified are
labelled **unverified**.

<!-- RADAR:START -->
**Last scan:** 2026-10-28T23:58:54.894071+00:00 · **Free models:** 19 · **Verified eligible:** 0 · **Unverified:** 19

| Model ID | Context length (tokens) | Parameter verification status |
|---|---|---|
| `cohere/north-mini-code:free` | 256,000 | unverified — parameter size not verified |
| `dots-studio/dots-3-note-preview:free` | 512,000 | unverified — parameter size not verified |
| `google/gemma-4-26b-a4b-it:free` | 262,144 | unverified — parameter size not verified |
| `google/gemma-4-31b-it:free` | 262,144 | unverified — parameter size not verified |
| `google/lyria-3-clip-preview` | unknown | unverified — parameter status unknown (listed free, no verification data) |
| `google/lyria-3-pro-preview` | unknown | unverified — parameter status unknown (listed free, no verification data) |
| `liquid/lfm-2.5-2.6b:free` | 65,536 | unverified — parameter size not verified |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 256,000 | unverified — parameter size not verified |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1,000,000 | unverified — parameter size not verified |
| `nvidia/nemotron-3.5-content-safety:free` | unknown | unverified — parameter status unknown (listed free, no verification data) |
| `nvidia/nemotron-3.5-lightning:free` | 1,000,000 | unverified — parameter size not verified |
| `nvidia/nemotron-3.5-super-vl:free` | 1,000,000 | unverified — parameter size not verified |
| `openrouter/free` | 200,000 | unverified — parameter size not verified |
| `poolside/laguna-s-2.1:free` | 262,144 | unverified — parameter size not verified |
| `poolside/laguna-xs-2.1:free` | 262,144 | unverified — parameter size not verified |
| `recursive/flint-v1.0:free` | 262,144 | unverified — parameter size not verified |
| `thinkingmachines/inkling-small:free` | 1,048,576 | unverified — parameter size not verified |
| `thinkingmachines/inkling:free` | 1,048,576 | unverified — parameter size not verified |
| `xingchen-agi/xing4.0-29b-a4b:free` | 262,144 | unverified — parameter size not verified |

**Changes vs. 2026-10-16T23:58:48.637330+00:00:** 1 added, 1 removed.
- Added: `recursive/flint-v1.0:free`
- Removed: `nvidia/nemotron-3-super-120b-a12b:free`
<!-- RADAR:END -->

## Regenerate

```bash
python3 gen_site.py --report /path/to/freetoken-bots.json
```

`gen_site.py` rewrites `index.html`, `data.json` and the leaderboard
section of this README (between the `RADAR:START` / `RADAR:END` markers),
and prints the README segment on its own with `--emit-readme-segment`.

## Pro alerts ($3/month)

Instant add/remove alerts + the full change-history archive:
see the `#pro` section of the generated site. (Gumroad checkout link is a
placeholder until the product is connected.)
