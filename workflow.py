"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

def discount(data):
    from decimal import Decimal
    years, basket = data['member_years'], Decimal(data['basket_usd'])
    if type(years) is not int or years < 0 or not basket.is_finite() or basket < 0:
        raise ValueError('Invalid membership or basket')
    rate = Decimal('.10') if years >= 2 else Decimal('.05')
    amount = min(Decimal('20'), basket * rate).quantize(Decimal('.01'))
    return {'discount_usd': str(amount), 'payable_usd': str(basket - amount), 'rule': '10% for 2+ years, otherwise 5%; maximum 20 USD'}


async def run(agent, data):
    decision = discount(data)
    options = in_process_tool('discount', 'Apply the documented loyalty discount rules.', {'member_years': int, 'basket_usd': str}, discount) if agent.live else None
    explanation = await agent.ask('explain_discount', 'Use the discount tool and explain the exact rule result; do not override its numeric decision.', data,
                                 'The three-year member receives a 12.00 USD discount and pays 108.00 USD.', sdk=options)
    return {'rule_decision': decision, 'explanation': explanation}
