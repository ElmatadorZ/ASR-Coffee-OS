# Fix Under-Development Roast

## Preconditions (must measure)
- dev_time_s
- total_time_s
- ROR curve (Artisan)

## Logic
If development_ratio < 0.18
AND ROR collapses after FC
→ root cause is thermal momentum loss

## Actions (one at a time)
- Increase environmental temp BEFORE FC
- Reduce airflow step at FC
- Do NOT extend time blindly

## Proof hooks
- roast_physics.thermal_momentum
- roast_physics.development_ratio
