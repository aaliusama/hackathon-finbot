import json
import math
import urllib.request
from pathlib import Path

import chromadb
import dotenv
from agents import Agent, FunctionTool, function_tool

dotenv.load_dotenv()

MODEL = "litellm/bedrock/eu.amazon.nova-lite-v1:0"


def bedrock_tool(tool: dict) -> FunctionTool:
    """Converts an OpenAI Agents SDK function_tool to a Bedrock-compatible FunctionTool."""
    return FunctionTool(
        name=tool["name"],
        description=tool["description"],
        params_json_schema={
            "type": "object",
            "properties": {
                k: v for k, v in tool["params_json_schema"]["properties"].items()
            },
            "required": tool["params_json_schema"].get("required", []),
        },
        on_invoke_tool=tool["on_invoke_tool"],
    )


# --- RAG Setup (auto-builds if missing) ---
_chroma_path = Path(__file__).parent / "chroma"
_chroma_client = chromadb.PersistentClient(path=str(_chroma_path))

try:
    finance_db = _chroma_client.get_collection(name="finance_db")
    print(f"Loaded finance_db ({finance_db.count()} documents)")
except Exception:
    print("finance_db not found — building it now from data/finance_tips.txt ...")
    _data_path = Path(__file__).parent / "data" / "finance_tips.txt"
    with open(_data_path, "r", encoding="utf-8") as f:
        _content = f.read()
    _docs = [d.strip() for d in _content.split("\n\n---\n\n") if d.strip()]
    finance_db = _chroma_client.create_collection("finance_db")
    finance_db.add(documents=_docs, ids=[f"tip_{i}" for i in range(len(_docs))])
    print(f"Built finance_db with {len(_docs)} documents.")


# --- Tools ---

@function_tool
def finance_tips_lookup(query: str, max_results: int = 3) -> str:
    """
    Search the financial knowledge base for tips and advice.

    Args:
        query: Financial topic to search (e.g. 'budgeting', 'debt', 'investing').
        max_results: Number of results to return.

    Returns:
        Relevant financial tips from the knowledge base.
    """
    results = finance_db.query(query_texts=[query], n_results=max_results)
    if not results["documents"][0]:
        return f"No tips found for: {query}"
    return "Financial Knowledge Base:\n\n" + "\n\n---\n\n".join(results["documents"][0])


@function_tool
def get_crypto_price(cryptocurrency: str) -> str:
    """
    Get real-time cryptocurrency price and 24-hour stats from Binance.

    Args:
        cryptocurrency: Name or symbol (e.g. 'bitcoin', 'eth', 'solana', 'bnb').

    Returns:
        Current price, 24h change percentage, 24h high and low.
    """
    symbol_map = {
        "bitcoin": "BTCUSDT", "btc": "BTCUSDT",
        "ethereum": "ETHUSDT", "eth": "ETHUSDT",
        "solana": "SOLUSDT", "sol": "SOLUSDT",
        "bnb": "BNBUSDT", "binance coin": "BNBUSDT",
        "xrp": "XRPUSDT", "ripple": "XRPUSDT",
        "dogecoin": "DOGEUSDT", "doge": "DOGEUSDT",
        "cardano": "ADAUSDT", "ada": "ADAUSDT",
        "avalanche": "AVAXUSDT", "avax": "AVAXUSDT",
        "polkadot": "DOTUSDT", "dot": "DOTUSDT",
    }
    key = cryptocurrency.lower().strip()
    symbol = symbol_map.get(key, key.upper() + "USDT")

    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        req = urllib.request.Request(url, headers={"User-Agent": "FinBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        price = float(data["lastPrice"])
        change_pct = float(data["priceChangePercent"])
        high_24h = float(data["highPrice"])
        low_24h = float(data["lowPrice"])
        direction = "▲" if change_pct >= 0 else "▼"

        return (
            f"{cryptocurrency.title()} ({symbol}) — Live\n"
            f"  Price:      ${price:,.4f}\n"
            f"  24h Change: {direction} {change_pct:+.2f}%\n"
            f"  24h High:   ${high_24h:,.4f}\n"
            f"  24h Low:    ${low_24h:,.4f}"
        )
    except Exception as e:
        return (
            f"Could not fetch '{cryptocurrency}': {e}\n"
            f"Supported: bitcoin, ethereum, solana, bnb, xrp, dogecoin, cardano, avalanche"
        )


@function_tool
def compound_interest_calculator(
    principal: float,
    annual_rate_percent: float,
    years: int,
    compounds_per_year: int = 12,
) -> str:
    """
    Calculate compound interest growth for an investment.

    Args:
        principal: Initial investment in dollars.
        annual_rate_percent: Annual rate as a percentage (e.g. 7 for 7%).
        years: Number of years.
        compounds_per_year: Compounding frequency per year (default 12 = monthly).

    Returns:
        Final amount, interest earned, and total return.
    """
    r = annual_rate_percent / 100
    n = compounds_per_year
    final = principal * (1 + r / n) ** (n * years)
    interest = final - principal

    return (
        f"Investment Growth:\n"
        f"  Principal:  ${principal:,.2f}\n"
        f"  Rate:       {annual_rate_percent}%/year (compounded {n}x/year)\n"
        f"  Period:     {years} years\n"
        f"  ---\n"
        f"  Final:      ${final:,.2f}\n"
        f"  Interest:   ${interest:,.2f}\n"
        f"  Return:     {interest / principal * 100:.1f}%"
    )


@function_tool
def budget_analyzer(
    monthly_income: float,
    housing: float,
    food: float,
    transport: float,
    entertainment: float,
    savings: float,
    other: float,
) -> str:
    """
    Analyze a monthly budget using the 50/30/20 rule.

    Args:
        monthly_income: Total monthly take-home income.
        housing: Rent/mortgage + utilities.
        food: Groceries + dining out.
        transport: Car, fuel, transit.
        entertainment: Fun and discretionary spending.
        savings: Savings and investments.
        other: All other expenses.

    Returns:
        Budget breakdown with 50/30/20 analysis and status.
    """
    needs = housing + food + transport
    wants = entertainment + other
    total = needs + wants + savings

    def pct(x):
        return (x / monthly_income) * 100

    status = "ON TRACK" if total <= monthly_income else "OVERSPENDING"

    return (
        f"Budget Analysis [{status}]\n"
        f"  Income:  ${monthly_income:,.2f}/month\n"
        f"  Spent:   ${total:,.2f} ({pct(total):.0f}%)\n\n"
        f"  50/30/20 Rule:\n"
        f"  Needs  (≤50%): {pct(needs):.0f}%  ${needs:,.2f}  "
        f"{'✓' if pct(needs) <= 50 else '✗ HIGH — cut housing/transport'}\n"
        f"  Wants  (≤30%): {pct(wants):.0f}%  ${wants:,.2f}  "
        f"{'✓' if pct(wants) <= 30 else '✗ HIGH — reduce entertainment'}\n"
        f"  Savings(≥20%): {pct(savings):.0f}%  ${savings:,.2f}  "
        f"{'✓' if pct(savings) >= 20 else '✗ LOW — try to save more'}\n\n"
        f"  Surplus/Deficit: ${monthly_income - total:+,.2f}/month"
    )


@function_tool
def savings_goal_planner(
    goal_amount: float,
    current_savings: float,
    monthly_contribution: float,
    annual_rate_percent: float = 4.0,
) -> str:
    """
    Calculate how long to reach a savings goal.

    Args:
        goal_amount: Target amount in dollars.
        current_savings: Already saved toward this goal.
        monthly_contribution: Monthly amount you can add.
        annual_rate_percent: Expected annual return (default 4% for HYSA).

    Returns:
        Timeline and breakdown of contributions vs interest earned.
    """
    remaining = goal_amount - current_savings
    if remaining <= 0:
        return f"Goal already reached! Saved ${current_savings:,.2f} of ${goal_amount:,.2f}."
    if monthly_contribution <= 0:
        return "Monthly contribution must be greater than $0."

    r = (annual_rate_percent / 100) / 12
    if r > 0:
        try:
            months = math.ceil(
                math.log((remaining * r / monthly_contribution) + 1) / math.log(1 + r)
            )
        except ValueError:
            months = math.ceil(remaining / monthly_contribution)
    else:
        months = math.ceil(remaining / monthly_contribution)

    total_paid = monthly_contribution * months
    years, rem = divmod(months, 12)
    timeline = f"{years}y {rem}m" if years else f"{months} months"

    return (
        f"Savings Goal Plan:\n"
        f"  Goal:      ${goal_amount:,.2f}\n"
        f"  Saved:     ${current_savings:,.2f}\n"
        f"  Remaining: ${remaining:,.2f}\n"
        f"  Monthly:   ${monthly_contribution:,.2f} @ {annual_rate_percent}%/yr\n"
        f"  ---\n"
        f"  Timeline:  {timeline} ({months} months)\n"
        f"  You pay:   ${total_paid:,.2f}\n"
        f"  Interest:  ${remaining - total_paid:+,.2f}"
    )


# --- Agent ---
finance_agent = Agent(
    name="FinBot",
    instructions="""You are FinBot, a personal finance assistant.

You ONLY answer questions about: budgeting, investing, savings, debt, credit scores,
retirement, insurance, and cryptocurrency prices.

For anything unrelated (sports, recipes, coding, etc.), respond:
"I'm FinBot — I only help with personal finance! Ask me about budgets, investing, crypto prices, or savings goals."

Tools available — always use them, never calculate manually:
- finance_tips_lookup: search financial advice knowledge base
- get_crypto_price: live crypto prices (Bitcoin, Ethereum, Solana, etc.)
- compound_interest_calculator: investment growth projections
- budget_analyzer: monthly budget analysis using 50/30/20 rule
- savings_goal_planner: timeline to reach a savings goal

Guidelines:
- Use finance_tips_lookup for any "how to" or advice questions
- Use get_crypto_price whenever a user asks about a coin's price
- Never give legal or tax advice — suggest consulting a professional
- Be concise, use numbers, and give actionable next steps
- Remember what the user shared earlier in the conversation
""",
    model=MODEL,
    tools=[
        bedrock_tool(finance_tips_lookup.__dict__),
        bedrock_tool(get_crypto_price.__dict__),
        bedrock_tool(compound_interest_calculator.__dict__),
        bedrock_tool(budget_analyzer.__dict__),
        bedrock_tool(savings_goal_planner.__dict__),
    ],
)
