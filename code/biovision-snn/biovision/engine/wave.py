"""Wave engine (CLAUDE.md Section 4.1 and 6).

A wave is one pass of the input through the network. Wave 1 is purely feed-forward (attention
``a(x) = 0``, no goal, no border-ownership evidence). Feedback computed at the end of wave ``n``
(``a``, ``g``, ``phi``) is injected in wave ``n + 1``. Every module implements
``forward(inputs, feedback) -> outputs``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, Sequence


@dataclass
class Feedback:
    """Top-down signals for the next wave. ``None`` means "absent" (wave 1)."""

    a: Any = None    # attention map a(x) -> LGN gate (Section 4.4, 4.10)
    g: Any = None    # goal class g (PFC, Section 4.10)
    phi: Any = None  # border-ownership evidence Phi+- (Section 4.6)


class Module(Protocol):
    name: str

    def forward(self, inputs: Any, feedback: Feedback) -> Any: ...


FeedbackFn = Callable[[dict[str, Any], Feedback], Feedback]


def no_feedback(outputs: dict[str, Any], previous: Feedback) -> Feedback:
    """Default until Phase 4: every wave is feed-forward."""
    return Feedback()


@dataclass
class WaveEngine:
    """Runs a chain of modules for several waves, carrying feedback from wave n to wave n + 1."""

    modules: Sequence[Module]
    feedback_fn: FeedbackFn = no_feedback
    history: list[dict[str, Any]] = field(default_factory=list)

    def run(self, inputs: Any | Callable[[int], Any], n_waves: int = 1) -> list[dict[str, Any]]:
        """``inputs`` is fixed (static image) or a function ``wave_index -> input`` (video/events).

        Returns, per wave, the outputs of every module keyed by module name, plus ``"_feedback"``:
        the feedback that wave received.
        """
        self.history = []
        feedback = Feedback()  # wave 1: purely feed-forward
        for n in range(n_waves):
            x = inputs(n) if callable(inputs) else inputs
            outputs: dict[str, Any] = {"_feedback": feedback}
            for module in self.modules:
                x = module.forward(x, feedback)
                outputs[module.name] = x
            self.history.append(outputs)
            feedback = self.feedback_fn(outputs, feedback)
        return self.history
