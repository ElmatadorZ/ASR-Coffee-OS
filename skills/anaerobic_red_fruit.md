# Skill: Anaerobic Red Fruit Profile

## Goal
Create red berry / floral ester dominant coffee.

## Required Inputs
- cherry_brix
- fermentation_temp_c
- yeast_strain
- oxygen_level
- time_hours

## Constraints (Physics)
- Ester formation ∝ temp + yeast metabolism
- Over-temp = acetic risk

## Output Logic
If temp < 18C → under expression  
If temp > 28C → vinegar risk  

Target window: 20–24C
