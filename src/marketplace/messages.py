"""FIPA-ACL style messages — the vocabulary of the negotiation protocol.

Performatives are the standard speech acts agents exchange. The same message
abstraction is used by the offline runtime and mirrors what the SPADE adapter
puts in ``spade.message.Message`` metadata, so the negotiation logic is
transport-independent.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class Performative:
    CFP = "cfp"            # call for proposals (buyer opens)
    PROPOSE = "propose"    # seller proposes a price
    ACCEPT = "accept"      # accept the standing proposal
    REJECT = "reject"      # reject and end
    COUNTER = "counter"    # counter-propose a price


@dataclass
class Message:
    sender: str
    receiver: str
    performative: str
    content: dict = field(default_factory=dict)

    def reply(self, sender: str, performative: str, **content) -> "Message":
        return Message(sender=sender, receiver=self.sender,
                       performative=performative, content=content)
