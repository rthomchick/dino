"""Terminal chat with Dino — for testing personality and tool flow."""
import asyncio
import uuid
from src.agent.dino import DinoAgent


async def main() -> None:
    agent = DinoAgent()
    conversation_id = f"cli-{uuid.uuid4().hex[:8]}"

    print("\nDino's Vegas Dining Concierge")
    print("Type 'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCiao.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Ciao.")
            break

        response = await agent.chat(user_input, conversation_id)
        print(f"\nDino: {response.message}\n")

        if response.restaurant_cards:
            print(f"  [{len(response.restaurant_cards)} restaurant card(s) returned]\n")
        if response.booking_confirmation:
            conf = response.booking_confirmation
            print(f"  [Booking confirmed: {conf.get('confirmation_number')} @ {conf.get('restaurant')}]\n")
        if response.calendar_event:
            print(f"  [Calendar updated]\n")


if __name__ == "__main__":
    asyncio.run(main())
