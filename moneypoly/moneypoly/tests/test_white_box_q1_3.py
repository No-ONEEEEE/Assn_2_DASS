import pytest

from moneypoly.bank import Bank
from moneypoly.board import Board, SPECIAL_TILES
from moneypoly.cards import CardDeck
from moneypoly.config import GO_SALARY, JAIL_POSITION
from moneypoly.dice import Dice
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly import ui


class StubPlayer:
    def __init__(self, name, balance=500):
        self.name = name
        self.balance = balance
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail_cards = 0
        self.position = 0

    def deduct_money(self, amount):
        self.balance -= amount

    def add_money(self, amount):
        self.balance += amount

    def add_property(self, prop):
        if prop not in self.properties:
            self.properties.append(prop)

    def remove_property(self, prop):
        if prop in self.properties:
            self.properties.remove(prop)

    def count_properties(self):
        return len(self.properties)

    def net_worth(self):
        return self.balance

    def go_to_jail(self):
        self.position = JAIL_POSITION
        self.in_jail = True
        self.jail_turns = 0

    def move(self, steps):
        self.position = (self.position + steps) % 40


@pytest.fixture
def game3():
    return Game(["A", "B", "C"])


# ------------------------------
# Player: branches, states, edges
# ------------------------------
@pytest.mark.parametrize("amount", [0, 1, 2, 10, 50, 99, 100, 200, 500, 1000])
def test_player_add_money_positive_and_zero(amount):
    p = Player("P")
    start = p.balance
    p.add_money(amount)
    assert p.balance == start + amount


@pytest.mark.parametrize("amount", [0, 1, 2, 10, 50, 99, 100, 200, 500, 1000])
def test_player_deduct_money_positive_and_zero(amount):
    p = Player("P")
    start = p.balance
    p.deduct_money(amount)
    assert p.balance == start - amount


@pytest.mark.parametrize("amount", [-1, -2, -10, -999])
def test_player_add_money_negative_rejected(amount):
    p = Player("P")
    with pytest.raises(ValueError):
        p.add_money(amount)


@pytest.mark.parametrize("amount", [-1, -2, -10, -999])
def test_player_deduct_money_negative_rejected(amount):
    p = Player("P")
    with pytest.raises(ValueError):
        p.deduct_money(amount)


@pytest.mark.parametrize(
    "start,steps,expected_pos",
    [
        (0, 1, 1), (1, 1, 2), (5, 3, 8), (10, 4, 14), (15, 5, 20), (20, 2, 22),
        (25, 6, 31), (30, 1, 31), (31, 3, 34), (34, 4, 38), (36, 1, 37), (37, 2, 39),
    ],
)
def test_player_move_without_wrap_no_go_salary(start, steps, expected_pos):
    p = Player("P")
    p.position = start
    before = p.balance
    assert p.move(steps) == expected_pos
    assert p.balance == before


@pytest.mark.parametrize(
    "start,steps,expected_pos",
    [(39, 1, 0), (39, 2, 1), (38, 2, 0), (38, 3, 1), (35, 5, 0), (37, 6, 3), (20, 20, 0), (1, 40, 1)],
)
def test_player_move_with_wrap_gets_go_salary(start, steps, expected_pos):
    p = Player("P")
    p.position = start
    before = p.balance
    assert p.move(steps) == expected_pos
    assert p.balance == before + GO_SALARY


@pytest.mark.parametrize("start,steps", [(0, 0), (5, 0), (39, 0), (0, -1), (10, -2)])
def test_player_move_non_positive_no_go_salary(start, steps):
    p = Player("P")
    p.position = start
    before = p.balance
    p.move(steps)
    assert p.balance == before


@pytest.mark.parametrize("balance,expected", [(-1, True), (0, True), (1, False), (1500, False)])
def test_player_is_bankrupt_states(balance, expected):
    p = Player("P")
    p.balance = balance
    assert p.is_bankrupt() is expected


def test_player_property_add_remove_and_count():
    p = Player("P")
    grp = PropertyGroup("Brown", "brown")
    prop = Property("A", 1, 60, 2, grp)
    p.add_property(prop)
    p.add_property(prop)
    assert p.count_properties() == 1
    p.remove_property(prop)
    assert p.count_properties() == 0


def test_player_go_to_jail_state_reset():
    p = Player("P")
    p.jail_turns = 2
    p.go_to_jail()
    assert p.position == JAIL_POSITION
    assert p.in_jail is True
    assert p.jail_turns == 0


def test_player_status_line_contains_jail_marker():
    p = Player("P")
    p.in_jail = True
    line = p.status_line()
    assert "[JAILED]" in line


# ------------------------------
# Property and group behavior
# ------------------------------
def test_property_group_all_owned_by_requires_all_members():
    g = PropertyGroup("Brown", "brown")
    a = StubPlayer("A")
    b = StubPlayer("B")
    p1 = Property("P1", 1, 60, 2, g)
    p2 = Property("P2", 3, 60, 4, g)
    p1.owner = a
    p2.owner = b
    assert g.all_owned_by(a) is False
    p2.owner = a
    assert g.all_owned_by(a) is True


@pytest.mark.parametrize("mortgaged,owns_full_set,expected", [(False, False, 10), (False, True, 20), (True, False, 0), (True, True, 0)])
def test_property_get_rent_branches(mortgaged, owns_full_set, expected):
    g = PropertyGroup("Red", "red")
    owner = StubPlayer("O")
    other = Property("R2", 2, 200, 10, g)
    prop = Property("R1", 1, 200, 10, g)
    prop.is_mortgaged = mortgaged
    prop.owner = owner
    other.owner = owner if owns_full_set else None
    assert prop.get_rent() == expected


def test_property_mortgage_and_unmortgage_cycle():
    g = PropertyGroup("Blue", "blue")
    prop = Property("X", 1, 100, 10, g)
    assert prop.mortgage() == 50
    assert prop.is_mortgaged is True
    assert prop.mortgage() == 0
    assert prop.unmortgage() == 55
    assert prop.is_mortgaged is False
    assert prop.unmortgage() == 0


@pytest.mark.parametrize("owner,mortgaged,expected", [(None, False, True), (None, True, False), (object(), False, False), (object(), True, False)])
def test_property_is_available_states(owner, mortgaged, expected):
    g = PropertyGroup("Blue", "blue")
    prop = Property("X", 1, 100, 10, g)
    prop.owner = owner
    prop.is_mortgaged = mortgaged
    assert prop.is_available() is expected


def test_property_group_owner_counts_and_size():
    g = PropertyGroup("Orange", "orange")
    a = StubPlayer("A")
    b = StubPlayer("B")
    p1 = Property("P1", 1, 100, 5, g)
    p2 = Property("P2", 2, 100, 5, g)
    p3 = Property("P3", 3, 100, 5, g)
    p1.owner = a
    p2.owner = a
    p3.owner = b
    counts = g.get_owner_counts()
    assert counts[a] == 2
    assert counts[b] == 1
    assert g.size() == 3


# ------------------------------
# Board behavior and tile branches
# ------------------------------
@pytest.mark.parametrize("position,tile", sorted(SPECIAL_TILES.items()))
def test_board_special_tile_mapping(position, tile):
    b = Board()
    assert b.get_tile_type(position) == tile


@pytest.mark.parametrize("position", [1, 3, 6, 9, 11, 14, 19, 24, 29, 31, 34, 37, 39])
def test_board_property_tile_detection(position):
    b = Board()
    assert b.get_tile_type(position) == "property"
    assert b.get_property_at(position) is not None


@pytest.mark.parametrize("position", [12, 28])
def test_board_blank_tile_detection(position):
    b = Board()
    assert b.get_tile_type(position) == "blank"
    assert b.get_property_at(position) is None


@pytest.mark.parametrize("position,expected", [(0, True), (2, True), (7, True), (12, False), (39, False), (30, True)])
def test_board_is_special_tile(position, expected):
    b = Board()
    assert b.is_special_tile(position) is expected


def test_board_is_purchasable_branches():
    b = Board()
    prop = b.get_property_at(1)
    assert prop is not None
    assert b.is_purchasable(1) is True
    prop.is_mortgaged = True
    assert b.is_purchasable(1) is False
    prop.is_mortgaged = False
    prop.owner = StubPlayer("O")
    assert b.is_purchasable(1) is False
    assert b.is_purchasable(0) is False


def test_board_owned_and_unowned_lists_partition():
    b = Board()
    owner = StubPlayer("O")
    first = b.properties[0]
    second = b.properties[1]
    first.owner = owner
    second.owner = owner
    owned = b.properties_owned_by(owner)
    unowned = b.unowned_properties()
    assert first in owned and second in owned
    assert first not in unowned and second not in unowned
    assert len(owned) + len(unowned) == len(b.properties)


# ------------------------------
# Bank behavior and edge values
# ------------------------------
@pytest.mark.parametrize("amount", [0, 1, 10, 100, 500, -1, -10])
def test_bank_collect_updates_balance_and_total(amount):
    bank = Bank()
    before = bank.get_balance()
    bank.collect(amount)
    assert bank.get_balance() == before + amount


@pytest.mark.parametrize("amount", [0, -1, -100])
def test_bank_payout_non_positive_returns_zero(amount):
    bank = Bank()
    before = bank.get_balance()
    assert bank.pay_out(amount) == 0
    assert bank.get_balance() == before


def test_bank_payout_positive_and_insufficient():
    bank = Bank()
    before = bank.get_balance()
    assert bank.pay_out(100) == 100
    assert bank.get_balance() == before - 100
    with pytest.raises(ValueError):
        bank.pay_out(10**9)


@pytest.mark.parametrize("loan", [0, -10, 1, 20, 99])
def test_bank_give_loan_records_positive_only(loan):
    bank = Bank()
    p = StubPlayer("P", balance=0)
    before = p.balance
    bank.give_loan(p, loan)
    if loan > 0:
        assert p.balance == before + loan
    else:
        assert p.balance == before


def test_bank_loan_count_and_total():
    bank = Bank()
    p = StubPlayer("P", balance=0)
    bank.give_loan(p, 10)
    bank.give_loan(p, 20)
    assert bank.loan_count() == 2
    assert bank.total_loans_issued() == 30


# ------------------------------
# Cards and deck behavior
# ------------------------------
def test_card_deck_draw_cycles_and_len():
    deck = CardDeck([
        {"action": "collect", "value": 1, "description": "A"},
        {"action": "pay", "value": 2, "description": "B"},
    ])
    assert len(deck) == 2
    assert deck.draw()["description"] == "A"
    assert deck.draw()["description"] == "B"
    assert deck.draw()["description"] == "A"


def test_card_deck_empty_behaviors():
    deck = CardDeck([])
    assert deck.draw() is None
    assert deck.peek() is None
    assert deck.cards_remaining() == 0


@pytest.mark.parametrize("draws,remaining", [(0, 2), (1, 1), (2, 2), (3, 1), (4, 2), (5, 1)])
def test_card_deck_cards_remaining_cycles(draws, remaining):
    deck = CardDeck([
        {"action": "collect", "value": 1, "description": "A"},
        {"action": "pay", "value": 2, "description": "B"},
    ])
    for _ in range(draws):
        deck.draw()
    assert deck.cards_remaining() == remaining


def test_card_deck_reshuffle_resets_index(monkeypatch):
    deck = CardDeck([
        {"action": "collect", "value": 1, "description": "A"},
        {"action": "pay", "value": 2, "description": "B"},
    ])
    deck.draw()
    called = {"ok": False}

    def fake_shuffle(cards):
        called["ok"] = True
        cards.reverse()

    monkeypatch.setattr("moneypoly.cards.random.shuffle", fake_shuffle)
    deck.reshuffle()
    assert called["ok"] is True
    assert deck.index == 0
    assert deck.peek()["description"] == "B"


# ------------------------------
# Game: critical decision paths
# ------------------------------
@pytest.mark.parametrize("balance_delta,expected", [(-1, False), (0, True), (10, True), (100, True)])
def test_game_buy_property_affordability_boundary(game3, balance_delta, expected):
    buyer = game3.players[0]
    prop = game3.board.unowned_properties()[0]
    buyer.balance = prop.price + balance_delta
    before_bank = game3.bank.get_balance()
    ok = game3.buy_property(buyer, prop)
    assert ok is expected
    if expected:
        assert prop.owner == buyer
        assert game3.bank.get_balance() == before_bank + prop.price
    else:
        assert prop.owner is None


def test_game_pay_rent_branches(game3):
    tenant = game3.players[0]
    owner = game3.players[1]
    prop = game3.board.unowned_properties()[0]

    # owner none -> no effect
    prop.owner = None
    b1 = tenant.balance
    game3.pay_rent(tenant, prop)
    assert tenant.balance == b1

    # mortgaged -> no effect
    prop.owner = owner
    prop.is_mortgaged = True
    b2t, b2o = tenant.balance, owner.balance
    game3.pay_rent(tenant, prop)
    assert tenant.balance == b2t and owner.balance == b2o

    # normal transfer
    prop.is_mortgaged = False
    rent = prop.get_rent()
    game3.pay_rent(tenant, prop)
    assert tenant.balance == b2t - rent
    assert owner.balance == b2o + rent


def test_game_mortgage_and_unmortgage_paths(game3):
    player = game3.players[0]
    other = game3.players[1]
    prop = game3.board.unowned_properties()[0]

    # not owner
    assert game3.mortgage_property(player, prop) is False

    # owner success
    prop.owner = player
    player.add_property(prop)
    bal = player.balance
    assert game3.mortgage_property(player, prop) is True
    assert player.balance > bal

    # already mortgaged
    assert game3.mortgage_property(player, prop) is False

    # unmortgage not owner
    assert game3.unmortgage_property(other, prop) is False

    # unmortgage insufficient
    player.balance = 0
    assert game3.unmortgage_property(player, prop) is False

    # unmortgage success
    player.balance = 10**5
    assert game3.unmortgage_property(player, prop) is True


def test_game_trade_paths(game3):
    seller = game3.players[0]
    buyer = game3.players[1]
    prop = game3.board.unowned_properties()[0]

    # seller does not own
    assert game3.trade(seller, buyer, prop, 10) is False

    prop.owner = seller
    seller.add_property(prop)

    # buyer cannot afford
    buyer.balance = 5
    assert game3.trade(seller, buyer, prop, 10) is False

    # success
    buyer.balance = 100
    assert game3.trade(seller, buyer, prop, 10) is True
    assert prop.owner == buyer


def test_game_check_bankruptcy_eliminates_player(game3):
    p = game3.players[0]
    p.balance = 0
    prop = game3.board.unowned_properties()[0]
    prop.owner = p
    p.add_property(prop)
    game3._check_bankruptcy(p)
    assert p.is_eliminated is True
    assert p not in game3.players
    assert prop.owner is None


def test_game_find_winner_with_and_without_players(game3):
    game3.players[0].balance = 100
    game3.players[1].balance = 200
    game3.players[2].balance = 150
    assert game3.find_winner() == game3.players[1]
    game3.players.clear()
    assert game3.find_winner() is None


def test_game_apply_card_collect_and_pay(game3):
    p = game3.players[0]
    b = p.balance
    game3._apply_card(p, {"description": "c", "action": "collect", "value": 50})
    assert p.balance == b + 50
    game3._apply_card(p, {"description": "p", "action": "pay", "value": 20})
    assert p.balance == b + 30


def test_game_apply_card_jail_and_jail_free(game3):
    p = game3.players[0]
    game3._apply_card(p, {"description": "j", "action": "jail", "value": 0})
    assert p.in_jail is True
    game3._apply_card(p, {"description": "f", "action": "jail_free", "value": 0})
    assert p.get_out_of_jail_cards >= 1


def test_game_apply_card_move_to_property_triggers_handler(game3, monkeypatch):
    p = game3.players[0]
    called = {"count": 0}

    def fake_handle(player, prop):
        called["count"] += 1

    monkeypatch.setattr(game3, "_handle_property_tile", fake_handle)
    p.position = 39
    game3._apply_card(p, {"description": "m", "action": "move_to", "value": 1})
    assert p.position == 1
    assert called["count"] == 1


def test_game_apply_card_move_to_pass_go_salary(game3):
    p = game3.players[0]
    p.position = 39
    before = p.balance
    game3._apply_card(p, {"description": "m", "action": "move_to", "value": 0})
    assert p.position == 0
    assert p.balance == before + GO_SALARY


def test_game_apply_card_birthday_and_collect_from_all(game3):
    p = game3.players[0]
    o1 = game3.players[1]
    o2 = game3.players[2]
    o1.balance = 100
    o2.balance = 5
    start = p.balance
    game3._apply_card(p, {"description": "b", "action": "birthday", "value": 10})
    assert p.balance == start + 10
    game3._apply_card(p, {"description": "a", "action": "collect_from_all", "value": 10})
    assert p.balance == start + 20


def test_game_handle_jail_turn_use_card_path(game3, monkeypatch):
    p = game3.players[0]
    p.in_jail = True
    p.get_out_of_jail_cards = 1
    monkeypatch.setattr("moneypoly.ui.confirm", lambda _msg: True)
    monkeypatch.setattr(game3.dice, "roll", lambda: 4)
    monkeypatch.setattr(game3, "_move_and_resolve", lambda _p, _r: None)
    game3._handle_jail_turn(p)
    assert p.in_jail is False
    assert p.get_out_of_jail_cards == 0


def test_game_handle_jail_turn_pay_fine_path(game3, monkeypatch):
    p = game3.players[0]
    p.in_jail = True
    p.get_out_of_jail_cards = 0
    calls = iter([True])
    monkeypatch.setattr("moneypoly.ui.confirm", lambda _msg: next(calls))
    monkeypatch.setattr(game3.dice, "roll", lambda: 5)
    monkeypatch.setattr(game3, "_move_and_resolve", lambda _p, _r: None)
    game3._handle_jail_turn(p)
    assert p.in_jail is False


def test_game_handle_jail_turn_mandatory_release_after_three_turns(game3, monkeypatch):
    p = game3.players[0]
    p.in_jail = True
    p.jail_turns = 2
    monkeypatch.setattr("moneypoly.ui.confirm", lambda _msg: False)
    monkeypatch.setattr(game3.dice, "roll", lambda: 2)
    monkeypatch.setattr(game3, "_move_and_resolve", lambda _p, _r: None)
    game3._handle_jail_turn(p)
    assert p.in_jail is False
    assert p.jail_turns == 0


def test_game_play_turn_branches(game3, monkeypatch):
    p = game3.current_player()

    # jail branch
    p.in_jail = True
    called = {"jail": 0}
    monkeypatch.setattr(game3, "_handle_jail_turn", lambda _p: called.__setitem__("jail", called["jail"] + 1))
    game3.play_turn()
    assert called["jail"] == 1

    # doubles streak to jail branch
    p = game3.current_player()
    p.in_jail = False

    def fake_roll():
        game3.dice.doubles_streak = 3
        return 4

    monkeypatch.setattr(game3.dice, "roll", fake_roll)
    monkeypatch.setattr(game3.dice, "is_doubles", lambda: True)
    game3.play_turn()
    assert p.in_jail is True


def test_game_interactive_menu_dispatches_options(game3, monkeypatch):
    p = game3.players[0]
    seq = iter([1, 2, 3, 4, 5, 6, 10, 0])
    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _msg, default=0: next(seq))
    counters = {"m": 0, "u": 0, "t": 0, "l": 0, "s": 0, "b": 0}
    monkeypatch.setattr("moneypoly.ui.print_standings", lambda _players: counters.__setitem__("s", counters["s"] + 1))
    monkeypatch.setattr("moneypoly.ui.print_board_ownership", lambda _board: counters.__setitem__("b", counters["b"] + 1))
    monkeypatch.setattr(game3, "_menu_mortgage", lambda _p: counters.__setitem__("m", counters["m"] + 1))
    monkeypatch.setattr(game3, "_menu_unmortgage", lambda _p: counters.__setitem__("u", counters["u"] + 1))
    monkeypatch.setattr(game3, "_menu_trade", lambda _p: counters.__setitem__("t", counters["t"] + 1))
    monkeypatch.setattr(game3.bank, "give_loan", lambda _p, _a: counters.__setitem__("l", counters["l"] + 1))
    game3.interactive_menu(p)
    assert counters == {"m": 1, "u": 1, "t": 1, "l": 1, "s": 1, "b": 1}


# ------------------------------
# UI helpers
# ------------------------------
def test_ui_format_currency():
    assert ui.format_currency(1500) == "$1,500"


@pytest.mark.parametrize("typed,expected", [("10", 10), ("0", 0), ("-5", -5), ("abc", 7), ("", 7), ("12.3", 7)])
def test_ui_safe_int_input(typed, expected, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _msg: typed)
    assert ui.safe_int_input("x", default=7) == expected


@pytest.mark.parametrize("typed,expected", [("y", True), ("Y", True), (" n ", False), ("yes", False)])
def test_ui_confirm(typed, expected, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _msg: typed)
    assert ui.confirm("x") is expected


def test_ui_print_helpers_emit_output(capsys):
    b = Board()
    p = Player("P")
    ui.print_banner("Title")
    ui.print_player_card(p)
    ui.print_standings([p])
    ui.print_board_ownership(b)
    out = capsys.readouterr().out
    assert "Title" in out
    assert "Player" in out
    assert "Standings" in out
    assert "Property Register" in out
