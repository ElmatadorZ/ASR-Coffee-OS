# ASR Coffee OS (Prototype)
Physics-first Coffee AI OS for Alternative Slowbar:Roaster.

## Why this exists
Most "AI coffee advice" fails because it guesses.
ASR Coffee OS refuses to guess: it only outputs claims backed by proofs (equations, measurements, axioms).

## Core Ideas
- Brewing = energy + mass transfer
- Output must be proof-gated
- Missing inputs -> request measurements, not hallucinate

## Install (editable)
pip install -e .

## CLI usage
asr-coffee --method pourover --dose 18 --water 300 --kettle 98 --room 26 --preheat true --time 210

Optional:
asr-coffee --tds 1.35 --beverage 285 --json

## Roadmap
- Add roast physics module (ROR/dev ratio/thermal momentum)
- Add CVA/Cupping descriptor mapping as *input data*, not authority
- Add sensor integration hooks (Artisan logs, BLE probes)
- Add skill packs (Markdown folders) for specialized workflows
