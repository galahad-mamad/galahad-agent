# Galahad Agent — Private Tutor Skill
# 3-4 hour intensive learning sessions for any skill

name: galahad-tutor
version: "1.0.0"
description: "Private tutor mode — 3-4 hour structured learning sessions with adaptive pacing, hands-on exercises, and progress tracking"
category: education
tags: [tutor, learning, education, skill-acquisition, adaptive]

author: "Galahad Agent Team"
license: MIT

# Configuration
config:
  session_duration_hours: 3.5  # 3-4 hours
  break_interval_minutes: 45
  min_exercise_per_module: 2
  max_modules_per_session: 5
  progress_checkpoint_interval: 30  # minutes
  language: "fa"  # default Persian

# Session structure template
session_template:
  - phase: "assessment"
    duration_minutes: 20
    description: "Initial skill assessment and goal setting"
    activities:
      - "Pre-session questionnaire"
      - "Current level evaluation"
      - "Learning objectives definition"
      - "Personalized curriculum outline"

  - phase: "foundation"
    duration_minutes: 50
    description: "Core concepts and mental models"
    activities:
      - "Concept mapping"
      - "Interactive explanation with analogies"
      - "Quick comprehension checks"
      - "Note-taking framework setup"

  - phase: "guided_practice"
    duration_minutes: 70
    description: "Hands-on exercises with real-time feedback"
    activities:
      - "Progressive difficulty exercises"
      - "Live coding/doing alongside tutor"
      - "Error diagnosis and correction"
      - "Pattern recognition drills"

  - phase: "independent_practice"
    duration_minutes: 45
    description: "Solo work with tutor observation"
    activities:
      - "Project-based challenge"
      - "Tutor intervenes only on blockers"
      - "Self-debugging practice"
      - "Solution review and optimization"

  - phase: "synthesis"
    duration_minutes: 35
    description: "Consolidation and next steps"
    activities:
      - "Knowledge synthesis exercise"
      - "Cheat sheet creation"
      - "Spaced repetition schedule"
      - "Next session roadmap"
      - "Resource curation"

# Adaptive pacing rules
adaptive_rules:
  - condition: "learner_struggling"
    triggers: ["multiple_failed_exercises", "long_pause", "explicit_confusion"]
    actions:
      - "reduce_difficulty"
      - "add_scaffolding"
      - "increase_examples"
      - "extend_phase_duration"

  - condition: "learner_advancing_fast"
    triggers: ["perfect_exercises", "quick_completion", "anticipating_concepts"]
    actions:
      - "increase_difficulty"
      - "skip_redundant_examples"
      - "add_extension_challenges"
      - "compress_phase_duration"

  - condition: "engagement_drop"
    triggers: ["short_responses", "distraction_signals", "declining_quality"]
    actions:
      - "change_modality"
      - "add_gamification"
      - "break_early"
      - "reconnect_to_goals"

# Supported domains (extensible)
domains:
  programming:
    languages: ["python", "javascript", "typescript", "rust", "go", "c++", "java", "kotlin", "swift"]
    frameworks: ["react", "vue", "django", "fastapi", "nextjs", "flutter", "spring"]
    topics: ["algorithms", "data-structures", "system-design", "testing", "debugging", "git"]

  mobile_repair:
    topics: ["android-basics", "adb-fastboot", "partition-management", "custom-roms", "root-magisk", "bootloader", "edl-mode", "jtag", "microsoldering"]
    tools: ["adb", "fastboot", "odin", "edl-tools", "sp-flash-tool", "mi-flash", "qfil"]

  electronics:
    topics: ["circuit-analysis", "soldering", "multimeter-use", "oscilloscope", "component-testing", "pcb-repair", "bms-repair"]
    equipment: ["multimeter", "oscilloscope", "soldering-station", "hot-air", "microscope"]

  languages:
    languages: ["english", "spanish", "french", "german", "chinese", "japanese", "korean", "arabic", "russian"]
    skills: ["conversation", "grammar", "vocabulary", "reading", "writing", "listening", "pronunciation"]

  math_science:
    topics: ["algebra", "calculus", "linear-algebra", "statistics", "physics", "chemistry", "biology"]
    levels: ["high-school", "undergraduate", "graduate"]

  creative:
    topics: ["drawing", "digital-art", "video-editing", "music-production", "3d-modeling", "animation", "writing"]
    tools: ["blender", "photoshop", "illustrator", "premiere", "davinci", "ableton", "fl-studio"]

# Exercise templates by type
exercise_templates:
  code:
    - "fix-the-bug"
    - "complete-the-function"
    - "refactor-this"
    - "write-from-scratch"
    - "explain-the-output"
    - "optimize-this"

  conceptual:
    - "concept-map"
    - "analogy-creation"
    - "teach-back"
    - "compare-contrast"
    - "edge-case-thinking"

  hands_on:
    - "guided-project"
    - "debug-session"
    - "feature-implementation"
    - "tool-workflow"
    - "configuration-task"

# Progress tracking
progress_metrics:
  - "concept_understanding"  # 0-100
  - "practical_application"  # 0-100
  - "problem_solving_speed"  # relative
  - "retention_score"        # from spaced repetition
  - "confidence_level"       # self-reported 1-10
  - "autonomy_index"         # % tasks completed without help

# Output artifacts per session
artifacts:
  - "session_notes.md"
  - "personal_cheatsheet.md"
  - "exercise_solutions/"
  - "spaced_repetition_schedule.json"
  - "next_session_plan.md"
  - "resource_list.md"
  - "progress_report.json"

# Integration hooks
hooks:
  pre_session:
    - "load_learner_profile"
    - "prepare_environment"
    - "fetch_prerequisites"

  post_session:
    - "save_progress"
    - "update_learner_model"
    - "generate_artifacts"
    - "schedule_review"

  between_sessions:
    - "daily_micro_practice"
    - "spaced_repetition_prompts"
    - "progress_check_in"