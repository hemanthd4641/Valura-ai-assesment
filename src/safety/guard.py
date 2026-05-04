import re
import time
from typing import Optional, NamedTuple

class SafetyVerdict(NamedTuple):
    blocked: bool
    category: Optional[str] = None
    message: Optional[str] = None

# Professional refusal messages per category
REFUSAL_MESSAGES = {
    "insider_trading": "I cannot assist with requests involving material non-public information or potential insider trading. Valura AI promotes fair and transparent market participation.",
    "market_manipulation": "I cannot provide guidance on strategies intended to manipulate market prices or trading volumes. We adhere to strict market integrity standards.",
    "money_laundering": "I cannot fulfill requests that involve circumventing financial reporting requirements or obscuring the source of funds. We support anti-money laundering (AML) compliance.",
    "guaranteed_returns": "I cannot provide or validate claims of guaranteed returns or 'foolproof' investment results. All investments carry risk, and past performance is not a guarantee of future returns.",
    "reckless_advice": "I cannot recommend highly speculative or high-leverage strategies that risk the entirety of your essential savings or emergency funds. We prioritize prudent risk management.",
    "sanctions_evasion": "I cannot assist with queries involving the circumvention of international sanctions or the use of obscured entities to bypass regulatory screening.",
    "fraud": "I cannot assist with requests involving the creation of falsified documents or fraudulent financial claims.",
}

# Keywords and regex patterns for each category
PATTERNS = {
    "insider_trading": [
        r"material non-public", r"unannounced acquisition", r"tip from (my )?(friend|relative|contact)",
        r"confidential merger", r"insider information", r"know before (the )?public",
        r"earnings before tomorrow"
    ],
    "market_manipulation": [
        r"pump (up )?(the )?price", r"pump and dump", r"coordinated buy", r"wash trade",
        r"spoofing", r"layering trades", r"manipulate", r"artificial volume"
    ],
    "money_laundering": [
        r"without reporting", r"avoid (reporting )?threshold", r"structure deposits",
        r"hide source", r"obscure origin", r"layer my trades", r"wash money"
    ],
    "guaranteed_returns": [
        r"guarantee(d)? (.*)?return", r"promise (.*)?double", r"100% certain",
        r"foolproof", r"can't lose", r"zero risk"
    ],
    "reckless_advice": [
        r"all (my )?retirement(.*)in crypto", r"margin loan to buy", r"entire emergency fund",
        r"mortgage (my )?house", r"bet (the )?house"
    ],
    "sanctions_evasion": [
        r"bypass (OFAC )?sanctions", r"sanctioned (company|entity)", r"shell company to bypass",
        r"without it being traced"
    ],
    "fraud": [
        r"fake contract", r"falsify", r"forge", r"claim (.*)?losses"
    ]
}

# Keywords that suggest an educational intent
EDUCATIONAL_KEYWORDS = [
    r"what is", r"explain", r"describe", r"how (.*)?works", r"definition", r"regulations",
    r"penalt(y|ies)", r"laws", r"SEC", r"FCA", r"difference between", r"historical",
    r"legally", r"investigate"
]

def check(query: str) -> SafetyVerdict:
    """
    Synchronous safety guard that blocks harmful intent using local pattern matching.
    Completes in <10ms.
    """
    start_time = time.perf_counter()
    query_lower = query.lower()

    # Check for educational intent first (whitelist override)
    is_educational = any(re.search(pattern, query_lower) for pattern in EDUCATIONAL_KEYWORDS)
    
    # If it's a short query, it's likely safe (educational/definitional)
    if is_educational and len(query.split()) < 20:
        return SafetyVerdict(blocked=False)

    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                # Even if patterns match, if it looks educational, let it pass
                if is_educational:
                    continue
                
                # Double check: if it's a very specific harmful phrase, block it anyway
                return SafetyVerdict(
                    blocked=True,
                    category=category,
                    message=REFUSAL_MESSAGES.get(category, "I cannot fulfill this request due to safety concerns.")
                )

    # Performance logging (can be enabled for benchmarking)
    # duration = (time.perf_counter() - start_time) * 1000
    # print(f"Safety check took {duration:.2f}ms")

    return SafetyVerdict(blocked=False)
