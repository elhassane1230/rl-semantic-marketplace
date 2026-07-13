import asyncio

from marketplace.messages import Message, Performative
from marketplace.runtime import Agent, Behaviour, MessageBus


def test_message_delivery():
    async def scenario():
        bus = MessageBus()
        a = Agent("a", bus)
        Agent("b", bus)
        await bus.deliver(Message("a", "b", Performative.CFP, {"x": 1}))
        # deliver to b's inbox
        assert bus._inboxes["b"].qsize() == 1
        assert a.inbox.qsize() == 0
    asyncio.run(scenario())


def test_behaviour_send_receive():
    results = []

    class Sender(Behaviour):
        async def run(self):
            await self.send(Message(self.agent.name, "recv", Performative.PROPOSE,
                                    {"price": 5}))

    class Receiver(Behaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            results.append(msg)

    async def scenario():
        bus = MessageBus()
        s = Agent("send", bus)
        r = Agent("recv", bus)
        s.add_behaviour(Sender())
        r.add_behaviour(Receiver())
        await asyncio.gather(s.run(), r.run())

    asyncio.run(scenario())
    assert results[0] is not None
    assert results[0].content["price"] == 5
    assert results[0].performative == Performative.PROPOSE


def test_message_reply_targets_sender():
    m = Message("buyer", "seller", Performative.PROPOSE, {"price": 5})
    r = m.reply("seller", Performative.ACCEPT)
    assert r.receiver == "buyer" and r.sender == "seller"
    assert r.performative == Performative.ACCEPT
