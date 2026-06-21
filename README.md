🤖 Agent Intelligence Hub

A high-performance AI orchestration layer for low-latency agentic workflows.
🎯 The "At-a-Glance" Summary

This project provides a robust framework for deploying AI agents that require sub-second inference and persistent memory. By offloading heavy compute to Groq's LPU (Language Processing Unit) and state management to Supabase, this hub solves the bottleneck of slow, "forgetful" AI interactions.
🏗️ How it Works

    Orchestration: The core logic manages agent prompts and task routing.


    Inference (Groq): Handles high-speed LLM processing to minimize user wait times.

    Persistence (Supabase): Stores conversation history, user profiles, and vector embeddings for long-term agent memory.

    Interface: Provides an API/CLI entry point for triggering agent tasks.

📂 Quick Directory Guide

    /src: Core logic and agent definitions.

    /supabase: Migrations and database schema.

    .env.example: Template for required API keys (Groq & Supabase).

    .gitignore: Configured to protect sensitive keys from being exposed.

🛠️ Core Capabilities

    Context Injection: Automatically pulls relevant user data from Supabase to provide "smart" agent responses.

    Stream Processing: Supports real-time token streaming from Groq for a better UX.

    Security-First: Built-in protection for secret keys and authenticated database access.

👨‍💻 Developed By

Amogh Hosamani

Computer Science & Engineering Student | CHRIST (Deemed to be University)
