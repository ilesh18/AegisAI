"""
Re-exports and thin wrappers making the Guard pipeline importable
as a standalone package without the FastAPI server.
Copyright (C) 2024 Sarthak Doshi (github.com/SdSarthak)
SPDX-License-Identifier: AGPL-3.0-only

TODO (help wanted):
  - Copy the following files from backend/app/modules/guard/ into
    guard-sdk/src/aegisai_guard/ (preserve directory structure):
      * regex_rules.py
      * intent_classifier.py
      * decision_engine.py
      * sanitizer.py
      * llm_guard.py
  - Remove any imports of `app.core.config` or `app.core.security` —
    replace config values with constructor arguments or env vars.
  - Expose LLMGuard, SanitizationLevel, and a typed GuardResult TypedDict.
  - Write at least 3 unit tests in guard-sdk/tests/test_guard.py covering
    allow / sanitize / block decisions.
  - Acceptance criteria: `pip install -e guard-sdk/` then
    `from aegisai_guard import LLMGuard; LLMGuard().guard("hello")` works.
"""

# TODO (help wanted): implement re-exports after copying module files
# from aegisai_guard.llm_guard import LLMGuard
# from aegisai_guard.sanitizer import SanitizationLevel
