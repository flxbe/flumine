import unittest
from unittest import mock

from flumine.order.trade import Trade, OrderError


class TradeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_strategy = mock.Mock()
        self.mock_fill_kill = mock.Mock()
        self.mock_offset = mock.Mock()
        self.mock_green = mock.Mock()
        self.mock_stop = mock.Mock()
        self.trade = Trade(
            "1.234",
            567,
            self.mock_strategy,
            self.mock_fill_kill,
            self.mock_offset,
            self.mock_green,
            self.mock_stop,
        )

    def test_init(self):
        self.assertEqual(self.trade.market_id, "1.234")
        self.assertEqual(self.trade.selection_id, 567)
        self.assertEqual(self.trade.strategy, self.mock_strategy)
        self.assertEqual(self.trade.fill_kill, self.mock_fill_kill)
        self.assertEqual(self.trade.offset, self.mock_offset)
        self.assertEqual(self.trade.green, self.mock_green)
        self.assertEqual(self.trade.stop, self.mock_stop)
        self.assertEqual(self.trade.orders, [])

    def test_create_order(self):
        mock_order_type = mock.Mock()
        mock_order_type.EXCHANGE = "SYM"
        mock_order = mock.Mock()
        mock_order.EXCHANGE = "SYM"
        self.trade.create_order("BACK", mock_order_type, handicap=1, order=mock_order)
        self.assertEqual(self.trade.orders, [mock_order()])

    def test_create_order_error(self):
        mock_order_type = mock.Mock()
        mock_order_type.EXCHANGE = "SYM"
        mock_order = mock.Mock()
        mock_order.EXCHANGE = "MYS"
        with self.assertRaises(OrderError):
            self.trade.create_order(
                "BACK", mock_order_type, handicap=1, order=mock_order
            )

    def test_create_order_replacement(self):
        mock_order = mock.Mock()
        mock_order._update = {"new_price": 12}
        replacement_order = self.trade.create_order_replacement(mock_order)
        self.assertEqual(self.trade.orders, [replacement_order])

    def test_create_order_from_current_limit(self):
        mock_current_order = mock.Mock()
        mock_current_order.order_type = "LIMIT"
        order = self.trade.create_order_from_current(mock_current_order, "12345")
        self.assertEqual(order.bet_id, mock_current_order.bet_id)
        self.assertEqual(order.id, "12345")
        self.assertEqual(self.trade.orders, [order])

    def test_create_order_from_current_limit_on_close(self):
        mock_current_order = mock.Mock()
        mock_current_order.order_type = "LIMIT_ON_CLOSE"
        with self.assertRaises(NotImplementedError):
            self.trade.create_order_from_current(mock_current_order, "12345")

    def test_create_order_from_current_market_on_close(self):
        mock_current_order = mock.Mock()
        mock_current_order.order_type = "MARKET_ON_CLOSE"
        with self.assertRaises(NotImplementedError):
            self.trade.create_order_from_current(mock_current_order, "12345")

    def test_info(self):
        self.assertEqual(
            self.trade.info,
            {
                "id": self.trade.id,
                "orders": [],
                "status": None,
                "strategy": self.mock_strategy,
            },
        )