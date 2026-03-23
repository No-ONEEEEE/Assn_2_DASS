import pytest

from moneypoly.dice import Dice
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup


class StubPlayer:
    def __init__(self, name, balance=500):
        self.name = name
        self.balance = balance
        self.properties = []

    def deduct_money(self, amount):
        self.balance -= amount

    def add_money(self, amount):
        self.balance += amount

    def add_property(self, prop):
        self.properties.append(prop)

    def remove_property(self, prop):
        if prop in self.properties:
            self.properties.remove(prop)


# White-box branch/edge checks for section 1.3.
def test_dice_roll_can_reach_six(monkeypatch):
    values = iter([6, 6])

    def fake_randint(_a, _b):
        return next(values)

    monkeypatch.setattr("moneypoly.dice.random.randint", fake_randint)
    d = Dice()
    total = d.roll()

    assert d.die1 == 6
    assert d.die2 == 6
    assert total == 12


def test_player_move_awards_go_salary_when_passing_go():
    p = Player("P1")
    p.position = 39
    before = p.balance

    p.move(2)

    assert p.position == 1
    assert p.balance == before + 200


def test_property_group_requires_all_properties_owned_by_same_player():
    group = PropertyGroup("Brown", "brown")
    owner = StubPlayer("Owner")
    other = StubPlayer("Other")

    p1 = Property("A", 1, 60, 2, group)
    p2 = Property("B", 3, 60, 4, group)

    p1.owner = owner
    p2.owner = other

    assert group.all_owned_by(owner) is False


def test_buy_property_allows_exact_balance_purchase():
    g = Game(["A", "B"])
    buyer = g.players[0]
    prop = g.board.unowned_properties()[0]

    buyer.balance = prop.price

    ok = g.buy_property(buyer, prop)

    assert ok is True
    assert prop.owner == buyer
    assert buyer.balance == 0


def test_pay_rent_transfers_amount_to_owner():
    g = Game(["Tenant", "Owner"])
    tenant = g.players[0]
    owner = g.players[1]
    prop = g.board.unowned_properties()[0]
    prop.owner = owner

    before_tenant = tenant.balance
    before_owner = owner.balance
    rent = prop.get_rent()

    g.pay_rent(tenant, prop)

    assert tenant.balance == before_tenant - rent
    assert owner.balance == before_owner + rent


def test_find_winner_returns_highest_net_worth_player():
    g = Game(["A", "B", "C"])
    g.players[0].balance = 500
    g.players[1].balance = 2500
    g.players[2].balance = 1500

    winner = g.find_winner()

    assert winner == g.players[1]
