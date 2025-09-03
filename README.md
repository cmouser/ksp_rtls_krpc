# KSP Booster Programming

A Kerbal Space Program project to autonomously launch boosters and land them back at the launch site. This project uses [kRPC](https://krpc.github.io/krpc/) to control KSP vessels programmatically using Python.

## Overview
The goal for this project is to be educational. I want to help people understand how code is used to control rockets at a very high level. You should be able to follow along even if you don't know how to code.

## Goals:
- Explain state machines and demonstrate their use in rockets
- Implement and use a PID controller to demonstrate its advantages/disadvantages
- Implement Model Predictive Control (MPC) and compare/contrast with PID. Emphasizing the differences between how computers and humans see control.
- Stretch Goal 1: Use Machine Learning to create MPC model
- Stretch Goal 2: Use end-to-end AI for rocket launch.

## Disclaimers

1. This is not professional grade software. It is just showing the basics. I'm hoping to do each episode in one sitting. Don't try to compare it against entire teams spending decades.

2. This is intentionally unoptimized. I want to minimize complex math to keep it simple to understand.

## Development Episodes

- **[Episode 1](docs/episodes/episode1.md)** - State Machines (Launch through Boostback)
- **[Episode 2](docs/episodes/episode2.md)** - PID Controller (Entry)
- **[Episode 3](docs/episodes/episode3.md)** - MPC Controller (Landing Burn)

# Try it yourself
If you would like to follow along and run this code yourself, the instructions below should help you get set up.

## Requirements
- Kerbal Space Program
- kRPC mod installed (I installed with [CKAN](https://github.com/KSP-CKAN/CKAN/releases/tag/v1.36.0))
- Python 3.x
- Required Python packages listed in requirements.txt

## Getting Started

1. Install KSP and kRPC mod
2. Clone this repository
3. Create a venv: `python -m venv .venv`
4. Activate your venv `.venv/Scripts/Activate.ps1` (Varies by OS)
5. Install Python dependencies: `pip install -r requirements.txt`
6. Run the main script: `python src/main.py`
