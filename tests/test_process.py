import pytest
from pydantic import ValidationError
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models import CommodityTrade

def test_valid_trade_passes():
    """Test that a perfectly clean trade is accepted."""
    trade = CommodityTrade(
        Trade_ID="TRD-999",
        Date="2026-05-17",
        Commodity_Index="TTF",
        Counterparty="Glencore",
        Direction="BUY",
        Volume_MMBtu=15000,
        Price_USD=5.50
    )
    assert trade.Volume_MMBtu == 15000
    assert trade.Price_USD == 5.50

def test_negative_volume_fails():
    """Test that our risk controls catch negative volumes."""
    with pytest.raises(ValidationError):
        CommodityTrade(
            Trade_ID="TRD-888",
            Date="2026-05-17",
            Commodity_Index="NBP",
            Counterparty="Shell",
            Direction="SELL",
            Volume_MMBtu=-5000,  # This should trigger the failure
            Price_USD=6.00
        )

def test_missing_counterparty_fails():
    """Test that empty counterparties are blocked."""
    with pytest.raises(ValidationError):
        CommodityTrade(
            Trade_ID="TRD-777",
            Date="2026-05-17",
            Commodity_Index="Henry Hub",
            Counterparty="   ",  # Blank spaces should fail
            Direction="BUY",
            Volume_MMBtu=10000,
            Price_USD=4.20
        )