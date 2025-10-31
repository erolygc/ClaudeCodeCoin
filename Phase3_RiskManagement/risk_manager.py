"""
Risk Management System
Core risk management functionality
"""

from typing import Dict, List, Optional
from datetime import datetime


class RiskManager:
    """
    Central risk management system
    """

    def __init__(self, capital: float = 10000.0):
        """
        Initialize risk manager

        Args:
            capital: Initial trading capital
        """
        self.capital = capital
        self.max_position_risk = 0.02  # 2% per trade
        self.max_portfolio_risk = 0.06  # 6% total
        self.max_drawdown = 0.15  # 15% max drawdown
        self.max_leverage = 3.0
        self.max_positions = 10
        self.min_risk_reward = 2.0

        self.open_positions = []
        self.equity_high = capital
        self.current_drawdown = 0.0

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        risk_percent: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate optimal position size

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_percent: Risk percentage (default: max_position_risk)

        Returns:
            Dict with position details
        """
        if risk_percent is None:
            risk_percent = self.max_position_risk

        risk_amount = self.capital * risk_percent
        stop_distance = abs(entry_price - stop_loss) / entry_price

        if stop_distance == 0:
            return {'size': 0, 'error': 'Invalid stop loss'}

        position_value = risk_amount / stop_distance
        position_size = position_value / entry_price

        return {
            'size': position_size,
            'value': position_value,
            'risk_amount': risk_amount,
            'risk_percent': risk_percent,
            'stop_distance_pct': stop_distance * 100
        }

    def calculate_kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Calculate Kelly Criterion for optimal position sizing

        Args:
            win_rate: Win rate (0-1)
            avg_win: Average win amount
            avg_loss: Average loss amount

        Returns:
            Kelly percentage
        """
        if avg_loss == 0:
            return 0

        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        # Apply fraction (usually 1/4 or 1/2 Kelly)
        kelly_fraction = kelly * 0.5  # Half Kelly for safety

        return max(0, min(kelly_fraction, self.max_position_risk * 2))

    def can_open_position(self, position_size: float, position_value: float) -> bool:
        """
        Check if new position can be opened within risk limits

        Args:
            position_size: Position size
            position_value: Position value in USD

        Returns:
            True if position can be opened
        """
        # Check max positions
        if len(self.open_positions) >= self.max_positions:
            return False

        # Check portfolio risk
        total_exposure = sum(p['value'] for p in self.open_positions) + position_value
        if total_exposure / self.capital > self.max_portfolio_risk:
            return False

        # Check drawdown
        if self.current_drawdown >= self.max_drawdown:
            return False

        return True

    def update_equity(self, current_equity: float):
        """
        Update equity and calculate drawdown

        Args:
            current_equity: Current account equity
        """
        if current_equity > self.equity_high:
            self.equity_high = current_equity

        self.current_drawdown = (self.equity_high - current_equity) / self.equity_high
        self.capital = current_equity

    def add_position(self, position: Dict):
        """Add position to tracking"""
        self.open_positions.append(position)

    def remove_position(self, position_id: str):
        """Remove position from tracking"""
        self.open_positions = [p for p in self.open_positions if p['id'] != position_id]

    def get_risk_report(self) -> Dict:
        """
        Generate risk management report

        Returns:
            Risk report dict
        """
        total_exposure = sum(p.get('value', 0) for p in self.open_positions)

        return {
            'capital': self.capital,
            'equity_high': self.equity_high,
            'current_drawdown': self.current_drawdown,
            'max_drawdown': self.max_drawdown,
            'open_positions': len(self.open_positions),
            'max_positions': self.max_positions,
            'total_exposure': total_exposure,
            'exposure_percent': total_exposure / self.capital if self.capital > 0 else 0,
            'risk_status': 'OK' if self.current_drawdown < self.max_drawdown else 'WARNING',
            'timestamp': datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    # Example usage
    rm = RiskManager(capital=10000)

    # Calculate position size
    position = rm.calculate_position_size(
        entry_price=100,
        stop_loss=95,  # 5% stop
        risk_percent=0.02  # 2% risk
    )

    print("Position Sizing:")
    print(f"  Size: {position['size']:.2f} units")
    print(f"  Value: ${position['value']:.2f}")
    print(f"  Risk Amount: ${position['risk_amount']:.2f}")
    print(f"  Stop Distance: {position['stop_distance_pct']:.2f}%")
    print()

    # Kelly Criterion
    kelly = rm.calculate_kelly_criterion(
        win_rate=0.60,
        avg_win=150,
        avg_loss=100
    )
    print(f"Kelly Criterion: {kelly:.2%}")
    print()

    # Risk report
    report = rm.get_risk_report()
    print("Risk Report:")
    for key, value in report.items():
        print(f"  {key}: {value}")
