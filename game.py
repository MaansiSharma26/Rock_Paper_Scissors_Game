import random
from dataclasses import dataclass
from typing import Literal
from google import genai  # ADK import


# STATE MODEL

@dataclass
class GameState:
    round: int = 1
    user_score: int = 0
    bot_score: int = 0
    user_bomb_used: bool = False
    bot_bomb_used: bool = False
    game_over: bool = False


state = GameState()
VALID_MOVES = {"rock", "paper", "scissors", "bomb"}
RoundWinner = Literal["user", "bot", "draw"]



# ADK TOOL DEFINITIONS

def validate_move(move: str) -> tuple[bool, str]:
    move = move.lower().strip()
    if move not in VALID_MOVES:
        return False, "Invalid move"
    if move == "bomb" and state.user_bomb_used:
        return False, "Bomb already used"
    return True, move


def resolve_round(user_move: str, bot_move: str) -> RoundWinner:
    if user_move == bot_move:
        return "draw"
    if user_move == "bomb":
        return "user"
    if bot_move == "bomb":
        return "bot"

    beats = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    return "user" if beats[user_move] == bot_move else "bot"


def update_game_state(user_move: str, bot_move: str, winner: RoundWinner) -> None:
    state.round += 1

    if user_move == "bomb":
        state.user_bomb_used = True
    if bot_move == "bomb":
        state.bot_bomb_used = True

    if winner == "user":
        state.user_score += 1
    elif winner == "bot":
        state.bot_score += 1

    if state.round > 3:
        state.game_over = True



# AGENT (ADK-STYLE ORCHESTRATOR)


class GameRefereeAgent:
    def explain_rules(self):
        print("\n🎮 Rock–Paper–Scissors–Plus")
        print("• Best of 3 rounds")
        print("• Moves: rock, paper, scissors, bomb")
        print("• Bomb beats all (once per player)")
        print("• Invalid input wastes the round\n")

    def get_user_intent(self) -> str:
        return input("Your move: ")

    def choose_bot_move(self) -> str:
        if state.bot_bomb_used:
            return random.choice(["rock", "paper", "scissors"])
        return random.choice(list(VALID_MOVES))

    def respond_round(self, user_move, bot_move, winner):
        print(f"\nRound {state.round - 1}")
        print(f"You played: {user_move}")
        print(f"Bot played: {bot_move}")
        print(f"Winner: {winner}")
        print(f"Score → You: {state.user_score} | Bot: {state.bot_score}\n")

    def respond_final(self):
        print("\n🏁 Game Over")
        print(f"Final Score → You: {state.user_score} | Bot: {state.bot_score}")
        if state.user_score > state.bot_score:
            print("🏆 You win!")
        elif state.bot_score > state.user_score:
            print("🤖 Bot wins!")
        else:
            print("🤝 Draw!")

    def run(self):
        self.explain_rules()

        while not state.game_over:
            user_input = self.get_user_intent()

            valid, result = validate_move(user_input)
            if not valid:
                print(f"❌ {result}. Round wasted.\n")
                state.round += 1
                if state.round > 3:
                    state.game_over = True
                continue

            user_move = result
            bot_move = self.choose_bot_move()
            winner = resolve_round(user_move, bot_move)
            update_game_state(user_move, bot_move, winner)
            self.respond_round(user_move, bot_move, winner)

        self.respond_final()


if __name__ == "__main__":
    GameRefereeAgent().run()
