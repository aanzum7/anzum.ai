# ──────────────────────────────────────────────────────────────────────────────
# file: services/rate_limiter.py
# ──────────────────────────────────────────────────────────────────────────────
"""
Device & session rate limiting for anzum.ai to prevent spam, API exhaustion,
and denial of service attacks, paired with witty/funky fallback responses.
"""
from __future__ import annotations

import random
import time
import threading
from typing import Dict, List, Optional, Tuple

from config.settings import (
    MIN_REQUEST_INTERVAL_SECONDS,
    MAX_REQUESTS_PER_MINUTE,
    MAX_SESSION_REQUESTS,
)

# Pool of funky, witty responses for rate limits
FUNKY_SPEED_RESPONSES: List[str] = [
    "🏎️ **Whoa there, speed racer!** You're typing faster than light through fiber optic cables. Take a 2-second sip of water and let's go again! ☕",
    "⚡ **Hold your quantum horses!** My neural circuits need a 2-second breather to digest that last thought. Ask again in just a moment! 🧘",
    "🚀 **Hyperdrive Warning!** You're moving at warp speed. Give Tanvir's AI Twin a tiny 2-second pitstop before your next question! ⏱️",
    "☕ **Hold that thought!** I can process 100 thoughts a second, but conversational manners need 2 seconds to catch up. Try again in 3, 2, 1... ✨",
]

FUNKY_RPM_RESPONSES: List[str] = [
    "⏳ **Brain Cooling Down!** You've asked 6 brilliant questions in under a minute! Give my synapses 30 seconds to recharge with Hamburg coffee. ☕✨",
    "🔥 **Synapse Overload!** My reasoning engine is smoking hot from all that curiosity! Let's take a 30-second breather before round two. 🧊",
    "🏃‍♂️ **Pacing the Marathon!** Even Usain Bolt takes a breather. My AI engine needs 30 seconds to catch up with your turbo curiosity! ⚡",
    "🔋 **Quick Recharge!** Whoosh, that's a flurry of questions! Let's pause for 30 seconds so my neural buffers can clear out. 🧠✨",
]

FUNKY_SESSION_CAP_RESPONSES: List[str] = [
    "🎉 **Chat Marathon Champion!** We've exchanged over 35 questions today! To protect my free-tier battery for everyone, take a peek at the **FAQ** tab or connect directly with Tanvir via the links in the sidebar! 📬✨",
    "🔋 **Battery at 1%!** Wow, you really put my AI Twin through its paces today! Check out the verified cards in the **FAQ** tab or send Tanvir an email directly. 🤝",
    "🌟 **What a Deep Dive!** You've explored so much of Tanvir's journey today. To continue the conversation, grab Tanvir's email or LinkedIn from the sidebar! 🚀",
]

FUNKY_GLITCH_RESPONSES: List[str] = [
    "🧠 **Brain Overclocked!** My neural synapses are currently taking a quick espresso break in Hamburg. Give me 10 seconds and ask me again! ☕✨",
    "🐹 **Hamster Wheel Slip!** The AI hamsters running my reasoning engine briefly slipped off their wheel. They're back on track—try asking once more! 🏃‍♂️",
    "🛸 **Cosmic Ray Alert!** A stray photon briefly scrambled my thought stream. I'm shaking it off—hit me with that question again! ✨",
    "🔌 **Tripped on the Ethernet Cable!** Tanvir's AI Twin just did a quick backflip to recover. Give it one more try, ready when you are! 🤸‍♂️",
    "🧩 **Matrix Glitch!** My thought matrix had a hiccup for a microsecond. Ask me that one more time—I'm all ears! 🕶️",
]

def get_funky_glitch_response() -> str:
    """Return a random funky response for unexpected glitches or quota pauses."""
    return random.choice(FUNKY_GLITCH_RESPONSES)


class RateLimiter:
    """
    Thread-safe rate limiter tracking per-device and per-session activity.
    Enforces:
      1. Minimum debounce interval between consecutive queries (e.g. 2.0s)
      2. Sliding window requests per minute (e.g. 6 RPM)
      3. Maximum total queries per session (e.g. 35 queries)
    """

    def __init__(
        self,
        min_interval_seconds: float = MIN_REQUEST_INTERVAL_SECONDS,
        max_requests_per_minute: int = MAX_REQUESTS_PER_MINUTE,
        max_session_requests: int = MAX_SESSION_REQUESTS,
    ):
        self.min_interval = min_interval_seconds
        self.max_rpm = max_requests_per_minute
        self.max_session = max_session_requests

        self._lock = threading.Lock()
        # client_id -> list of float timestamps
        self._request_history: Dict[str, List[float]] = {}
        # client_id -> total query count
        self._session_totals: Dict[str, int] = {}

    def check_rate_limit(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request is allowed.
        Returns:
            (True, None) if allowed.
            (False, funky_message) if rate limited.
        """
        now = time.time()

        with self._lock:
            # 1. Check total session cap
            total = self._session_totals.get(client_id, 0)
            if total >= self.max_session:
                return False, random.choice(FUNKY_SESSION_CAP_RESPONSES)

            timestamps = self._request_history.get(client_id, [])

            # Prune timestamps older than 60 seconds
            recent = [t for t in timestamps if now - t < 60.0]

            # 2. Check debounce / minimum interval
            if recent:
                last_time = recent[-1]
                time_diff = now - last_time
                if time_diff < self.min_interval:
                    return False, random.choice(FUNKY_SPEED_RESPONSES)

            # 3. Check sliding-window RPM
            if len(recent) >= self.max_rpm:
                return False, random.choice(FUNKY_RPM_RESPONSES)

            # Request is allowed -> record it
            recent.append(now)
            self._request_history[client_id] = recent
            self._session_totals[client_id] = total + 1

            # Housekeeping: clean stale clients older than 15 minutes
            if len(self._request_history) > 500:
                self._cleanup(now)

            return True, None

    def _cleanup(self, now: float) -> None:
        """Purge records with no activity in 15 minutes."""
        stale_cutoff = now - 900.0
        stale_keys = [
            k for k, ts in self._request_history.items()
            if not ts or ts[-1] < stale_cutoff
        ]
        for k in stale_keys:
            self._request_history.pop(k, None)
            self._session_totals.pop(k, None)

    def reset_client(self, client_id: str) -> None:
        """Reset limits for a client (e.g. on clear conversation)."""
        with self._lock:
            self._request_history.pop(client_id, None)
            self._session_totals.pop(client_id, None)


# Singleton instance
_GLOBAL_RATE_LIMITER: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    global _GLOBAL_RATE_LIMITER
    if _GLOBAL_RATE_LIMITER is None:
        _GLOBAL_RATE_LIMITER = RateLimiter()
    return _GLOBAL_RATE_LIMITER
