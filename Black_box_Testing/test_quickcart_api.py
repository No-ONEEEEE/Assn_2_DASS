import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"

def get_headers(roll_number="123", user_id=None):
    headers = {"X-Roll-Number": str(roll_number)}
    if user_id is not None:
        headers["X-User-ID"] = str(user_id)
    return headers

@pytest.fixture(scope="session")
def valid_user_id():
    return 1

@pytest.fixture(scope="session")
def valid_product_id():
    return 1

@pytest.fixture(scope="session")
def valid_coupon_code():
    res = requests.get(f"{BASE_URL}/admin/coupons", headers=get_headers())
    if res.status_code == 200 and len(res.json()) > 0:
        first_coupon = res.json()[0]
        if isinstance(first_coupon, dict):
            return first_coupon.get("code") or first_coupon.get("coupon_code") or "SAVE10"
    return "SAVE10"

# --- AUTH AND HEADERS ---
def test_auth_missing_roll_number():
    assert requests.get(f"{BASE_URL}/admin/users").status_code == 401

def test_auth_invalid_roll_number_letters():
    assert requests.get(f"{BASE_URL}/admin/users", headers={"X-Roll-Number": "abc"}).status_code == 400

def test_auth_empty_roll_number():
    assert requests.get(f"{BASE_URL}/admin/users", headers={"X-Roll-Number": ""}).status_code in [400, 401]

def test_auth_missing_user_id():
    assert requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "123"}).status_code == 400

def test_auth_invalid_user_id_letters():
    assert requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "123", "X-User-ID": "abc"}).status_code == 400

def test_auth_negative_user_id():
    assert requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "123", "X-User-ID": "-5"}).status_code == 400

# --- ADMIN ---
def test_admin_get_users():
    assert requests.get(f"{BASE_URL}/admin/users", headers=get_headers()).status_code == 200

def test_admin_get_specific_user(valid_user_id):
    assert requests.get(f"{BASE_URL}/admin/users/{valid_user_id}", headers=get_headers()).status_code == 200

def test_admin_get_specific_user_invalid():
    assert requests.get(f"{BASE_URL}/admin/users/999999", headers=get_headers()).status_code == 404

def test_admin_get_carts():
    assert requests.get(f"{BASE_URL}/admin/carts", headers=get_headers()).status_code == 200

def test_admin_get_orders():
    assert requests.get(f"{BASE_URL}/admin/orders", headers=get_headers()).status_code == 200

def test_admin_get_products():
    assert requests.get(f"{BASE_URL}/admin/products", headers=get_headers()).status_code == 200

def test_admin_get_coupons():
    assert requests.get(f"{BASE_URL}/admin/coupons", headers=get_headers()).status_code == 200

def test_admin_get_tickets():
    assert requests.get(f"{BASE_URL}/admin/tickets", headers=get_headers()).status_code == 200

def test_admin_get_addresses():
    assert requests.get(f"{BASE_URL}/admin/addresses", headers=get_headers()).status_code == 200

# --- PROFILE ---
def test_profile_get(valid_user_id):
    assert requests.get(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id)).status_code == 200

def test_profile_update_valid(valid_user_id):
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={"name": "Alice Bob", "phone": "1234567890"}).status_code == 200

def test_profile_update_name_too_short(valid_user_id):
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={"name": "A", "phone": "1234567890"}).status_code == 400

def test_profile_update_name_max_bound(valid_user_id):
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={"name": "A" * 50, "phone": "1234567890"}).status_code == 200

def test_profile_update_name_too_long(valid_user_id):
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={"name": "A" * 51, "phone": "1234567890"}).status_code == 400

def test_profile_update_phone_too_short(valid_user_id):
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={"name": "Alice", "phone": "123456789"}).status_code == 400

def test_profile_update_phone_too_long(valid_user_id):
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={"name": "Alice", "phone": "12345678901"}).status_code == 400

def test_profile_update_phone_letters(valid_user_id):
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={"name": "Alice", "phone": "abcdefghij"}).status_code == 400

def test_profile_update_wrong_type(valid_user_id):
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={"name": 12345, "phone": 1234567890}).status_code == 400

def test_profile_update_missing_fields(valid_user_id):
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={"name": "Alice"}).status_code == 400

# --- ADDRESSES ---
def test_addresses_valid_add(valid_user_id):
    payload = {"label": "HOME", "street": "123 Main St", "city": "Metropolis", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 200
    assert "address_id" in res.json()

def test_addresses_invalid_label(valid_user_id):
    payload = {"label": "CAMPUS", "street": "123 Main St", "city": "Metropolis", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_addresses_lower_label(valid_user_id):
    payload = {"label": "home", "street": "123 Main St", "city": "Metropolis", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_addresses_street_min_bound(valid_user_id):
    payload = {"label": "HOME", "street": "12345", "city": "Metropolis", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 200

def test_addresses_street_too_short(valid_user_id):
    payload = {"label": "HOME", "street": "1234", "city": "Metropolis", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_addresses_street_max_bound(valid_user_id):
    payload = {"label": "HOME", "street": "A" * 100, "city": "Metropolis", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 200

def test_addresses_street_too_long(valid_user_id):
    payload = {"label": "HOME", "street": "A" * 101, "city": "Metropolis", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_addresses_city_too_short(valid_user_id):
    payload = {"label": "HOME", "street": "123456", "city": "A", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_addresses_city_too_long(valid_user_id):
    payload = {"label": "HOME", "street": "123456", "city": "A" * 51, "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_addresses_pincode_too_short(valid_user_id):
    payload = {"label": "HOME", "street": "123 Main St", "city": "Metropolis", "pincode": "12345"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_addresses_pincode_too_long(valid_user_id):
    payload = {"label": "HOME", "street": "123 Main St", "city": "Metropolis", "pincode": "1234567"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_addresses_pincode_letters(valid_user_id):
    payload = {"label": "HOME", "street": "123 Main St", "city": "Metropolis", "pincode": "abcdef"}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_addresses_pincode_int_type(valid_user_id):
    payload = {"label": "HOME", "street": "123 Main St", "city": "Metropolis", "pincode": 123456}
    assert requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_address_update_unallowed_fields(valid_user_id):
    # Setup
    payload = {"label": "HOME", "street": "123 Main St", "city": "Metropolis", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload)
    if res.status_code == 200:
        addr_id = res.json().get("address_id")
        update_payload = {"label": "OFFICE", "street": "New Street", "city": "Gotham", "pincode": "654321", "is_default": True}
        upd = requests.put(f"{BASE_URL}/addresses/{addr_id}", headers=get_headers(user_id=valid_user_id), json=update_payload)
        
        # Verify forbidden fields aren't changed
        check = requests.get(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id))
        if check.status_code == 200:
            for a in check.json():
                if a["address_id"] == addr_id:
                    assert a["label"] == "HOME", "Label should not have updated"
                    assert a["city"] == "Metropolis", "City should not have updated"

def test_addresses_delete_non_existent(valid_user_id):
    assert requests.delete(f"{BASE_URL}/addresses/999999", headers=get_headers(user_id=valid_user_id)).status_code == 404

# --- PRODUCTS ---
def test_products_list(valid_user_id):
    assert requests.get(f"{BASE_URL}/products", headers=get_headers(user_id=valid_user_id)).status_code == 200

def test_products_list_inactive(valid_user_id):
    res = requests.get(f"{BASE_URL}/products", headers=get_headers(user_id=valid_user_id))
    if res.status_code == 200:
        for p in res.json():
            assert p.get("is_active") is not False, "Inactive products should not be returned"

def test_product_get_invalid_id(valid_user_id):
    assert requests.get(f"{BASE_URL}/products/999999", headers=get_headers(user_id=valid_user_id)).status_code == 404

# --- CART ---
def test_cart_add_valid(valid_user_id, valid_product_id):
    payload = {"product_id": valid_product_id, "quantity": 1}
    assert requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 200

def test_cart_add_same_product_accumulates(valid_user_id, valid_product_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    payload = {"product_id": valid_product_id, "quantity": 1}
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json=payload)
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json=payload)
    res = requests.get(f"{BASE_URL}/cart", headers=get_headers(user_id=valid_user_id))
    if res.status_code == 200:
        items = res.json().get("items", [])
        if items:
            assert items[0]["quantity"] == 2

def test_cart_add_zero_quantity(valid_user_id, valid_product_id):
    payload = {"product_id": valid_product_id, "quantity": 0}
    assert requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_cart_add_negative_quantity(valid_user_id, valid_product_id):
    payload = {"product_id": valid_product_id, "quantity": -5}
    assert requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_cart_add_string_quantity(valid_user_id, valid_product_id):
    payload = {"product_id": valid_product_id, "quantity": "1"}
    assert requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_cart_add_huge_quantity(valid_user_id, valid_product_id):
    payload = {"product_id": valid_product_id, "quantity": 999999999}
    assert requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_cart_add_non_existent_product(valid_user_id):
    payload = {"product_id": 999999, "quantity": 1}
    assert requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 404

def test_cart_update_zero_quantity(valid_user_id, valid_product_id):
    payload = {"product_id": valid_product_id, "quantity": 1}
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json=payload)
    payload_update = {"product_id": valid_product_id, "quantity": 0}
    assert requests.post(f"{BASE_URL}/cart/update", headers=get_headers(user_id=valid_user_id), json=payload_update).status_code == 400

def test_cart_update_non_existent(valid_user_id):
    payload = {"product_id": 999999, "quantity": 2}
    assert requests.post(f"{BASE_URL}/cart/update", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 404

def test_cart_remove_non_existent(valid_user_id):
    payload = {"product_id": 999999}
    assert requests.post(f"{BASE_URL}/cart/remove", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 404

def test_cart_clear_twice(valid_user_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    assert requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id)).status_code == 200

# --- COUPONS ---
def test_coupon_apply_invalid(valid_user_id):
    payload = {"code": "INVALID_CODE_123"}
    assert requests.post(f"{BASE_URL}/coupon/apply", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 404

def test_coupon_apply_empty(valid_user_id):
    payload = {"code": ""}
    assert requests.post(f"{BASE_URL}/coupon/apply", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_coupon_remove(valid_user_id):
    assert requests.post(f"{BASE_URL}/coupon/remove", headers=get_headers(user_id=valid_user_id)).status_code == 200

# --- CHECKOUT ---
def test_checkout_invalid_method(valid_user_id):
    payload = {"payment_method": "BITCOIN"}
    assert requests.post(f"{BASE_URL}/checkout", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_checkout_empty_cart(valid_user_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    payload = {"payment_method": "COD"}
    assert requests.post(f"{BASE_URL}/checkout", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_checkout_missing_method(valid_user_id):
    payload = {}
    assert requests.post(f"{BASE_URL}/checkout", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

# --- WALLET ---
def test_wallet_add_valid(valid_user_id):
    payload = {"amount": 500}
    assert requests.post(f"{BASE_URL}/wallet/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 200

def test_wallet_add_zero(valid_user_id):
    payload = {"amount": 0}
    assert requests.post(f"{BASE_URL}/wallet/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_wallet_add_negative(valid_user_id):
    payload = {"amount": -100}
    assert requests.post(f"{BASE_URL}/wallet/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_wallet_add_over_limit(valid_user_id):
    payload = {"amount": 100001}
    assert requests.post(f"{BASE_URL}/wallet/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_wallet_add_string(valid_user_id):
    payload = {"amount": "500"}
    assert requests.post(f"{BASE_URL}/wallet/add", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_wallet_pay_insufficient(valid_user_id):
    payload = {"amount": 99999999}
    assert requests.post(f"{BASE_URL}/wallet/pay", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_wallet_pay_zero(valid_user_id):
    payload = {"amount": 0}
    assert requests.post(f"{BASE_URL}/wallet/pay", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_wallet_pay_negative(valid_user_id):
    payload = {"amount": -100}
    assert requests.post(f"{BASE_URL}/wallet/pay", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

# --- LOYALTY ---
def test_loyalty_get(valid_user_id):
    assert requests.get(f"{BASE_URL}/loyalty", headers=get_headers(user_id=valid_user_id)).status_code == 200

def test_loyalty_redeem_zero(valid_user_id):
    payload = {"amount": 0}
    assert requests.post(f"{BASE_URL}/loyalty/redeem", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_loyalty_redeem_negative(valid_user_id):
    payload = {"amount": -10}
    assert requests.post(f"{BASE_URL}/loyalty/redeem", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_loyalty_redeem_insufficient(valid_user_id):
    payload = {"amount": 99999999}
    assert requests.post(f"{BASE_URL}/loyalty/redeem", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

# --- ORDERS ---
def test_orders_list(valid_user_id):
    assert requests.get(f"{BASE_URL}/orders", headers=get_headers(user_id=valid_user_id)).status_code == 200

def test_orders_get_non_existent(valid_user_id):
    assert requests.get(f"{BASE_URL}/orders/999999", headers=get_headers(user_id=valid_user_id)).status_code == 404

def test_orders_cancel_non_existent(valid_user_id):
    assert requests.post(f"{BASE_URL}/orders/999999/cancel", headers=get_headers(user_id=valid_user_id)).status_code == 404

# --- REVIEWS ---
def test_reviews_add_valid(valid_user_id, valid_product_id):
    payload = {"rating": 5, "comment": "Great product"}
    res = requests.post(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code in [200, 400] 

def test_reviews_add_rating_zero(valid_user_id, valid_product_id):
    payload = {"rating": 0, "comment": "Okayish"}
    assert requests.post(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_reviews_add_rating_six(valid_user_id, valid_product_id):
    payload = {"rating": 6, "comment": "Okayish"}
    assert requests.post(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_reviews_add_rating_float(valid_user_id, valid_product_id):
    payload = {"rating": 4.5, "comment": "Okayish"}
    assert requests.post(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_reviews_add_comment_empty(valid_user_id, valid_product_id):
    payload = {"rating": 4, "comment": ""}
    assert requests.post(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_reviews_add_comment_too_long(valid_user_id, valid_product_id):
    payload = {"rating": 4, "comment": "A" * 201}
    assert requests.post(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_reviews_add_product_not_exist(valid_user_id):
    payload = {"rating": 4, "comment": "Nice"}
    assert requests.post(f"{BASE_URL}/products/999999/reviews", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 404

# --- SUPPORT TICKETS ---
def test_support_ticket_valid(valid_user_id):
    payload = {"subject": "Need Help With Order", "message": "My order has not arrived yet."}
    assert requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 200

def test_support_ticket_subject_too_short(valid_user_id):
    payload = {"subject": "Hi", "message": "My order has not arrived yet."}
    assert requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_support_ticket_subject_too_long(valid_user_id):
    payload = {"subject": "A" * 101, "message": "My order has not arrived yet."}
    assert requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_support_ticket_message_empty(valid_user_id):
    payload = {"subject": "Need Help", "message": ""}
    assert requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_support_ticket_message_too_long(valid_user_id):
    payload = {"subject": "Need Help", "message": "A" * 501}
    assert requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 400

def test_support_ticket_invalid_status_transition(valid_user_id):
    payload = {"subject": "Need Help", "message": "My order has not arrived yet."}
    res = requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload)
    if res.status_code == 200:
        ticket_id = res.json().get("ticket_id")
        
        # Try moving straight from OPEN to CLOSED
        payload_update = {"status": "CLOSED"}
        assert requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=get_headers(user_id=valid_user_id), json=payload_update).status_code == 400
        
        # Try invalid string
        payload_update = {"status": "RESOLVED"}
        assert requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=get_headers(user_id=valid_user_id), json=payload_update).status_code == 400


# --- MORE EXPLORATORY COVERAGE ---
def _get_first_two_active_products(user_id):
    res = requests.get(f"{BASE_URL}/products", headers=get_headers(user_id=user_id))
    if res.status_code != 200:
        return []
    products = res.json()
    if not isinstance(products, list):
        return []
    return [p for p in products if p.get("product_id") is not None][:2]


def test_auth_roll_number_with_spaces():
    with pytest.raises(requests.exceptions.InvalidHeader):
        requests.get(f"{BASE_URL}/admin/users", headers={"X-Roll-Number": " 123 "})


def test_auth_roll_number_float_string():
    assert requests.get(f"{BASE_URL}/admin/users", headers={"X-Roll-Number": "123.4"}).status_code == 400


def test_auth_user_id_zero_not_allowed():
    headers = {"X-Roll-Number": "123", "X-User-ID": "0"}
    assert requests.get(f"{BASE_URL}/profile", headers=headers).status_code == 400


def test_admin_endpoints_ignore_user_id_header(valid_user_id):
    headers = get_headers(user_id=valid_user_id)
    assert requests.get(f"{BASE_URL}/admin/products", headers=headers).status_code == 200


def test_profile_update_name_min_bound(valid_user_id):
    payload = {"name": "Ab", "phone": "9998887776"}
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 200


def test_profile_update_phone_exact_10_digits(valid_user_id):
    payload = {"name": "Boundary User", "phone": "0123456789"}
    assert requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json=payload).status_code == 200


def test_addresses_get_returns_list(valid_user_id):
    res = requests.get(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_addresses_only_one_default(valid_user_id):
    a1 = {
        "label": "HOME",
        "street": "11 Default Lane",
        "city": "Hyd",
        "pincode": "111111",
        "is_default": True,
    }
    a2 = {
        "label": "OFFICE",
        "street": "22 Default Lane",
        "city": "Hyd",
        "pincode": "222222",
        "is_default": True,
    }
    r1 = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=a1)
    r2 = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=a2)
    if r1.status_code != 200 or r2.status_code != 200:
        pytest.skip("Address creation did not succeed; cannot verify default uniqueness")

    res = requests.get(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    defaults = [a for a in res.json() if a.get("is_default") is True]
    assert len(defaults) == 1


def test_addresses_update_returns_new_data(valid_user_id):
    create_payload = {
        "label": "OTHER",
        "street": "99 Old Street",
        "city": "Town",
        "pincode": "333333",
    }
    created = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=create_payload)
    if created.status_code != 200:
        pytest.skip("Address creation did not succeed; cannot verify update response")

    addr_id = created.json().get("address_id")
    update_payload = {"street": "99 New Street", "is_default": False}
    updated = requests.put(f"{BASE_URL}/addresses/{addr_id}", headers=get_headers(user_id=valid_user_id), json=update_payload)
    assert updated.status_code == 200

    body = updated.json()
    if isinstance(body, dict):
        street = body.get("street") or body.get("address", {}).get("street")
        if street is not None:
            assert street == "99 New Street"


def test_products_filter_unknown_category_returns_empty_or_404(valid_user_id):
    res = requests.get(f"{BASE_URL}/products?category=THIS_DOES_NOT_EXIST", headers=get_headers(user_id=valid_user_id))
    assert res.status_code in [200, 404]
    if res.status_code == 200:
        assert isinstance(res.json(), list)


def test_products_search_special_chars(valid_user_id):
    res = requests.get(f"{BASE_URL}/products?search=%40%23%24notreal", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_products_sort_price_asc(valid_user_id):
    res = requests.get(f"{BASE_URL}/products?sort=price_asc", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    prices = [p.get("price") for p in res.json() if isinstance(p, dict) and isinstance(p.get("price"), (int, float))]
    if len(prices) >= 2:
        assert prices == sorted(prices)


def test_products_sort_price_desc(valid_user_id):
    res = requests.get(f"{BASE_URL}/products?sort=price_desc", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    prices = [p.get("price") for p in res.json() if isinstance(p, dict) and isinstance(p.get("price"), (int, float))]
    if len(prices) >= 2:
        assert prices == sorted(prices, reverse=True)


def test_product_price_matches_admin(valid_user_id):
    user_products = requests.get(f"{BASE_URL}/products", headers=get_headers(user_id=valid_user_id))
    admin_products = requests.get(f"{BASE_URL}/admin/products", headers=get_headers())
    if user_products.status_code != 200 or admin_products.status_code != 200:
        pytest.skip("Product endpoints unavailable for price parity check")

    admin_map = {}
    for p in admin_products.json():
        if isinstance(p, dict):
            admin_map[p.get("product_id")] = p.get("price")

    for p in user_products.json():
        pid = p.get("product_id")
        if pid in admin_map:
            assert p.get("price") == admin_map[pid]


def test_cart_get_structure(valid_user_id):
    res = requests.get(f"{BASE_URL}/cart", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    assert isinstance(res.json(), dict)


def test_cart_update_negative_quantity(valid_user_id, valid_product_id):
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id, "quantity": 1})
    res = requests.post(
        f"{BASE_URL}/cart/update",
        headers=get_headers(user_id=valid_user_id),
        json={"product_id": valid_product_id, "quantity": -1},
    )
    assert res.status_code == 400


def test_cart_update_string_quantity(valid_user_id, valid_product_id):
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id, "quantity": 1})
    res = requests.post(
        f"{BASE_URL}/cart/update",
        headers=get_headers(user_id=valid_user_id),
        json={"product_id": valid_product_id, "quantity": "2"},
    )
    assert res.status_code == 400


def test_cart_remove_existing_item(valid_user_id, valid_product_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id, "quantity": 1})
    remove = requests.post(f"{BASE_URL}/cart/remove", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id})
    assert remove.status_code == 200


def test_cart_item_subtotal_correct(valid_user_id):
    products = _get_first_two_active_products(valid_user_id)
    if not products:
        pytest.skip("No products available for cart subtotal test")

    product = products[0]
    pid = product.get("product_id")
    price = product.get("price")
    if pid is None or not isinstance(price, (int, float)):
        pytest.skip("Product payload missing product_id or price")

    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": pid, "quantity": 3})
    cart = requests.get(f"{BASE_URL}/cart", headers=get_headers(user_id=valid_user_id))
    assert cart.status_code == 200

    items = cart.json().get("items", [])
    match = next((i for i in items if i.get("product_id") == pid), None)
    if not match:
        pytest.skip("Added product not found in cart response")

    subtotal = match.get("subtotal")
    if isinstance(subtotal, (int, float)):
        assert subtotal == 3 * price


def test_cart_total_includes_all_items(valid_user_id):
    products = _get_first_two_active_products(valid_user_id)
    if len(products) < 2:
        pytest.skip("Need at least 2 products for total aggregation test")

    p1, p2 = products[0], products[1]
    if not isinstance(p1.get("price"), (int, float)) or not isinstance(p2.get("price"), (int, float)):
        pytest.skip("Products missing numeric price")

    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": p1["product_id"], "quantity": 1})
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": p2["product_id"], "quantity": 2})
    cart = requests.get(f"{BASE_URL}/cart", headers=get_headers(user_id=valid_user_id))
    assert cart.status_code == 200

    items = cart.json().get("items", [])
    calculated = 0
    for item in items:
        qty = item.get("quantity")
        unit = item.get("unit_price") if item.get("unit_price") is not None else item.get("price")
        if isinstance(qty, (int, float)) and isinstance(unit, (int, float)):
            calculated += qty * unit

    total = cart.json().get("total")
    if isinstance(total, (int, float)) and calculated > 0:
        assert total == calculated


def test_coupon_apply_missing_code_field(valid_user_id):
    res = requests.post(f"{BASE_URL}/coupon/apply", headers=get_headers(user_id=valid_user_id), json={})
    assert res.status_code == 400


def test_coupon_apply_without_cart_items(valid_user_id, valid_coupon_code):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    res = requests.post(
        f"{BASE_URL}/coupon/apply",
        headers=get_headers(user_id=valid_user_id),
        json={"code": valid_coupon_code},
    )
    assert res.status_code in [400, 404]


def test_checkout_cod_over_limit_rejected(valid_user_id):
    products = _get_first_two_active_products(valid_user_id)
    if not products:
        pytest.skip("No products available for COD limit test")

    product = max(products, key=lambda p: p.get("price", 0))
    price = product.get("price", 0)
    pid = product.get("product_id")
    if not isinstance(price, (int, float)) or price <= 0 or pid is None:
        pytest.skip("Invalid product data for COD limit test")

    qty = int(6000 / price) + 1
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    add = requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": pid, "quantity": qty})
    if add.status_code != 200:
        pytest.skip("Could not add enough items for COD limit test")

    res = requests.post(f"{BASE_URL}/checkout", headers=get_headers(user_id=valid_user_id), json={"payment_method": "COD"})
    assert res.status_code == 400


def test_checkout_wallet_or_card_happy_path_or_insufficient(valid_user_id, valid_product_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id, "quantity": 1})
    res = requests.post(f"{BASE_URL}/checkout", headers=get_headers(user_id=valid_user_id), json={"payment_method": "WALLET"})
    assert res.status_code in [200, 400]


def test_wallet_get_balance_shape(valid_user_id):
    res = requests.get(f"{BASE_URL}/wallet", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, dict)
    if "balance" in body:
        assert isinstance(body["balance"], (int, float))


def test_wallet_pay_missing_amount(valid_user_id):
    res = requests.post(f"{BASE_URL}/wallet/pay", headers=get_headers(user_id=valid_user_id), json={})
    assert res.status_code == 400


def test_loyalty_get_shape(valid_user_id):
    res = requests.get(f"{BASE_URL}/loyalty", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    assert isinstance(res.json(), dict)


def test_orders_invoice_non_existent(valid_user_id):
    res = requests.get(f"{BASE_URL}/orders/999999/invoice", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 404


def test_orders_list_items_shape(valid_user_id):
    res = requests.get(f"{BASE_URL}/orders", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_reviews_get_non_existent_product(valid_user_id):
    res = requests.get(f"{BASE_URL}/products/999999/reviews", headers=get_headers(user_id=valid_user_id))
    assert res.status_code in [404, 200]


def test_reviews_average_rating_decimal_or_zero(valid_user_id, valid_product_id):
    res = requests.get(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    body = res.json()
    if isinstance(body, dict) and "average_rating" in body:
        avg = body["average_rating"]
        assert isinstance(avg, (int, float))
        assert avg >= 0


def test_support_ticket_status_flow_open_to_in_progress_to_closed(valid_user_id):
    create_payload = {"subject": "Track status flow", "message": "Please help with status lifecycle."}
    created = requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=create_payload)
    if created.status_code != 200:
        pytest.skip("Ticket creation failed; cannot validate status lifecycle")

    ticket_id = created.json().get("ticket_id")
    if not ticket_id:
        pytest.skip("Ticket id missing in response")

    r1 = requests.put(
        f"{BASE_URL}/support/tickets/{ticket_id}",
        headers=get_headers(user_id=valid_user_id),
        json={"status": "IN_PROGRESS"},
    )
    r2 = requests.put(
        f"{BASE_URL}/support/tickets/{ticket_id}",
        headers=get_headers(user_id=valid_user_id),
        json={"status": "CLOSED"},
    )
    assert r1.status_code == 200
    assert r2.status_code == 200


def test_support_ticket_cannot_reopen_closed(valid_user_id):
    create_payload = {"subject": "No reopen", "message": "Trying to reopen closed ticket."}
    created = requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=create_payload)
    if created.status_code != 200:
        pytest.skip("Ticket creation failed; cannot validate reopen behavior")

    ticket_id = created.json().get("ticket_id")
    if not ticket_id:
        pytest.skip("Ticket id missing in response")

    requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=get_headers(user_id=valid_user_id), json={"status": "IN_PROGRESS"})
    requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=get_headers(user_id=valid_user_id), json={"status": "CLOSED"})
    reopen = requests.put(
        f"{BASE_URL}/support/tickets/{ticket_id}",
        headers=get_headers(user_id=valid_user_id),
        json={"status": "OPEN"},
    )
    assert reopen.status_code == 400


# --- STRESS EXPLORATORY COVERAGE ---
def test_profile_update_empty_body(valid_user_id):
    res = requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json={})
    assert res.status_code == 400


def test_profile_update_phone_with_spaces(valid_user_id):
    payload = {"name": "Alice", "phone": "12345 6789"}
    res = requests.put(f"{BASE_URL}/profile", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 400


def test_addresses_missing_label(valid_user_id):
    payload = {"street": "123 Main St", "city": "Metropolis", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 400


def test_addresses_missing_street(valid_user_id):
    payload = {"label": "HOME", "city": "Metropolis", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 400


def test_addresses_missing_city(valid_user_id):
    payload = {"label": "HOME", "street": "123 Main St", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 400


def test_addresses_missing_pincode(valid_user_id):
    payload = {"label": "HOME", "street": "123 Main St", "city": "Metropolis"}
    res = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 400


def test_addresses_city_min_bound(valid_user_id):
    payload = {"label": "HOME", "street": "123 Main St", "city": "AB", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 200


def test_addresses_city_max_bound(valid_user_id):
    payload = {"label": "HOME", "street": "123 Main St", "city": "A" * 50, "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 200


def test_products_invalid_sort_param(valid_user_id):
    res = requests.get(f"{BASE_URL}/products?sort=unknown_sort", headers=get_headers(user_id=valid_user_id))
    assert res.status_code in [200, 400]


def test_products_invalid_product_id_type(valid_user_id):
    res = requests.get(f"{BASE_URL}/products/abc", headers=get_headers(user_id=valid_user_id))
    assert res.status_code in [400, 404]


def test_cart_add_missing_product_id(valid_user_id):
    res = requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"quantity": 1})
    assert res.status_code == 400


def test_cart_add_missing_quantity(valid_user_id, valid_product_id):
    res = requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id})
    assert res.status_code == 400


def test_cart_update_missing_product_id(valid_user_id):
    res = requests.post(f"{BASE_URL}/cart/update", headers=get_headers(user_id=valid_user_id), json={"quantity": 2})
    assert res.status_code == 400


def test_cart_update_missing_quantity(valid_user_id, valid_product_id):
    res = requests.post(f"{BASE_URL}/cart/update", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id})
    assert res.status_code == 400


def test_cart_remove_missing_product_id(valid_user_id):
    res = requests.post(f"{BASE_URL}/cart/remove", headers=get_headers(user_id=valid_user_id), json={})
    assert res.status_code == 400


def test_coupon_apply_missing_body(valid_user_id):
    res = requests.post(f"{BASE_URL}/coupon/apply", headers=get_headers(user_id=valid_user_id), json=None)
    assert res.status_code in [400, 415]


def test_coupon_apply_code_type_number(valid_user_id):
    res = requests.post(f"{BASE_URL}/coupon/apply", headers=get_headers(user_id=valid_user_id), json={"code": 12345})
    assert res.status_code == 400


def test_checkout_payment_method_lowercase_rejected(valid_user_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    res = requests.post(f"{BASE_URL}/checkout", headers=get_headers(user_id=valid_user_id), json={"payment_method": "cod"})
    assert res.status_code == 400


def test_checkout_card_sets_paid_when_success(valid_user_id, valid_product_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    add = requests.post(
        f"{BASE_URL}/cart/add",
        headers=get_headers(user_id=valid_user_id),
        json={"product_id": valid_product_id, "quantity": 1},
    )
    if add.status_code != 200:
        pytest.skip("Unable to prepare cart for CARD checkout")

    checkout = requests.post(
        f"{BASE_URL}/checkout",
        headers=get_headers(user_id=valid_user_id),
        json={"payment_method": "CARD"},
    )
    if checkout.status_code != 200:
        pytest.skip("CARD checkout did not succeed in this environment")

    orders = requests.get(f"{BASE_URL}/orders", headers=get_headers(user_id=valid_user_id))
    assert orders.status_code == 200
    all_orders = orders.json()
    if not all_orders:
        pytest.skip("No orders returned after successful checkout")

    latest = all_orders[-1]
    pay_status = latest.get("payment_status")
    if pay_status is not None:
        assert pay_status == "PAID"


def test_checkout_cod_sets_pending_when_success(valid_user_id, valid_product_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    add = requests.post(
        f"{BASE_URL}/cart/add",
        headers=get_headers(user_id=valid_user_id),
        json={"product_id": valid_product_id, "quantity": 1},
    )
    if add.status_code != 200:
        pytest.skip("Unable to prepare cart for COD checkout")

    checkout = requests.post(
        f"{BASE_URL}/checkout",
        headers=get_headers(user_id=valid_user_id),
        json={"payment_method": "COD"},
    )
    if checkout.status_code != 200:
        pytest.skip("COD checkout did not succeed in this environment")

    orders = requests.get(f"{BASE_URL}/orders", headers=get_headers(user_id=valid_user_id))
    assert orders.status_code == 200
    all_orders = orders.json()
    if not all_orders:
        pytest.skip("No orders returned after successful checkout")

    latest = all_orders[-1]
    pay_status = latest.get("payment_status")
    if pay_status is not None:
        assert pay_status == "PENDING"


def test_wallet_add_exact_upper_bound(valid_user_id):
    res = requests.post(f"{BASE_URL}/wallet/add", headers=get_headers(user_id=valid_user_id), json={"amount": 100000})
    assert res.status_code == 200


def test_wallet_pay_string_amount(valid_user_id):
    res = requests.post(f"{BASE_URL}/wallet/pay", headers=get_headers(user_id=valid_user_id), json={"amount": "10"})
    assert res.status_code == 400


def test_wallet_exact_deduction(valid_user_id):
    before_res = requests.get(f"{BASE_URL}/wallet", headers=get_headers(user_id=valid_user_id))
    if before_res.status_code != 200:
        pytest.skip("Cannot read wallet before deduction test")

    before = before_res.json().get("balance")
    if not isinstance(before, (int, float)):
        pytest.skip("Wallet response missing numeric balance")

    top_up = requests.post(f"{BASE_URL}/wallet/add", headers=get_headers(user_id=valid_user_id), json={"amount": 50})
    if top_up.status_code != 200:
        pytest.skip("Cannot top up wallet for deduction test")

    pay = requests.post(f"{BASE_URL}/wallet/pay", headers=get_headers(user_id=valid_user_id), json={"amount": 20})
    if pay.status_code != 200:
        pytest.skip("Wallet pay rejected; cannot verify exact deduction")

    after_res = requests.get(f"{BASE_URL}/wallet", headers=get_headers(user_id=valid_user_id))
    assert after_res.status_code == 200
    after = after_res.json().get("balance")
    if isinstance(after, (int, float)):
        assert after == before + 30


def test_loyalty_redeem_missing_amount(valid_user_id):
    res = requests.post(f"{BASE_URL}/loyalty/redeem", headers=get_headers(user_id=valid_user_id), json={})
    assert res.status_code == 400


def test_reviews_comment_min_bound(valid_user_id, valid_product_id):
    payload = {"rating": 4, "comment": "A"}
    res = requests.post(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code in [200, 400]


def test_reviews_comment_exact_max_bound(valid_user_id, valid_product_id):
    payload = {"rating": 4, "comment": "A" * 200}
    res = requests.post(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code in [200, 400]


def test_support_ticket_missing_subject(valid_user_id):
    payload = {"message": "Need help with an order"}
    res = requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 400


def test_support_ticket_missing_message(valid_user_id):
    payload = {"subject": "Need help"}
    res = requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload)
    assert res.status_code == 400


def test_support_ticket_new_status_is_open(valid_user_id):
    payload = {"subject": "Check default status", "message": "Please verify status initialization"}
    created = requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload)
    if created.status_code != 200:
        pytest.skip("Ticket creation failed; cannot verify default status")

    body = created.json()
    status = body.get("status")
    if status is not None:
        assert status == "OPEN"


def test_support_ticket_in_progress_cannot_go_back_to_open(valid_user_id):
    payload = {"subject": "Transition validation", "message": "Please validate transition constraints"}
    created = requests.post(f"{BASE_URL}/support/ticket", headers=get_headers(user_id=valid_user_id), json=payload)
    if created.status_code != 200:
        pytest.skip("Ticket creation failed; cannot validate transition")

    ticket_id = created.json().get("ticket_id")
    if not ticket_id:
        pytest.skip("ticket_id missing from create response")

    forward = requests.put(
        f"{BASE_URL}/support/tickets/{ticket_id}",
        headers=get_headers(user_id=valid_user_id),
        json={"status": "IN_PROGRESS"},
    )
    if forward.status_code != 200:
        pytest.skip("Could not move ticket to IN_PROGRESS")

    backward = requests.put(
        f"{BASE_URL}/support/tickets/{ticket_id}",
        headers=get_headers(user_id=valid_user_id),
        json={"status": "OPEN"},
    )
    assert backward.status_code == 400


# --- DEEP BUG-HUNT COVERAGE ---
def _maybe_get_json(res):
    try:
        return res.json()
    except Exception:
        return None


def test_auth_roll_number_plus_sign_invalid():
    res = requests.get(f"{BASE_URL}/admin/users", headers={"X-Roll-Number": "+123"})
    assert res.status_code == 400


def test_auth_roll_number_decimal_invalid():
    res = requests.get(f"{BASE_URL}/admin/users", headers={"X-Roll-Number": "12.0"})
    assert res.status_code == 400


def test_auth_user_id_non_existing(valid_user_id):
    headers = get_headers(user_id=valid_user_id + 999999)
    res = requests.get(f"{BASE_URL}/profile", headers=headers)
    assert res.status_code in [400, 404]


def test_admin_users_response_shape():
    res = requests.get(f"{BASE_URL}/admin/users", headers=get_headers())
    assert res.status_code == 200
    data = _maybe_get_json(res)
    assert isinstance(data, list)
    if data:
        assert isinstance(data[0], dict)


def test_admin_user_by_id_contains_requested_user(valid_user_id):
    res = requests.get(f"{BASE_URL}/admin/users/{valid_user_id}", headers=get_headers())
    assert res.status_code == 200
    body = _maybe_get_json(res)
    if isinstance(body, dict) and "user_id" in body:
        assert body["user_id"] == valid_user_id


def test_addresses_update_street_persists(valid_user_id):
    create_payload = {"label": "OTHER", "street": "Old Persist Street", "city": "Hyd", "pincode": "444444"}
    created = requests.post(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id), json=create_payload)
    if created.status_code != 200:
        pytest.skip("Address creation failed")

    addr_id = created.json().get("address_id")
    if not addr_id:
        pytest.skip("address_id missing")

    upd = requests.put(
        f"{BASE_URL}/addresses/{addr_id}",
        headers=get_headers(user_id=valid_user_id),
        json={"street": "New Persist Street", "is_default": False},
    )
    assert upd.status_code == 200

    all_addr = requests.get(f"{BASE_URL}/addresses", headers=get_headers(user_id=valid_user_id))
    assert all_addr.status_code == 200
    rows = all_addr.json()
    found = next((r for r in rows if r.get("address_id") == addr_id), None)
    if found:
        assert found.get("street") == "New Persist Street"


def test_products_search_case_insensitive(valid_user_id):
    p1 = requests.get(f"{BASE_URL}/products?search=apple", headers=get_headers(user_id=valid_user_id))
    p2 = requests.get(f"{BASE_URL}/products?search=APPLE", headers=get_headers(user_id=valid_user_id))
    assert p1.status_code == 200
    assert p2.status_code == 200
    d1 = _maybe_get_json(p1)
    d2 = _maybe_get_json(p2)
    if isinstance(d1, list) and isinstance(d2, list):
        assert len(d1) == len(d2)


def test_products_single_product_has_exact_price_match(valid_user_id):
    plist = requests.get(f"{BASE_URL}/products", headers=get_headers(user_id=valid_user_id))
    if plist.status_code != 200:
        pytest.skip("products endpoint unavailable")
    arr = plist.json()
    if not arr:
        pytest.skip("no active products")
    pid = arr[0].get("product_id")
    list_price = arr[0].get("price")
    if pid is None:
        pytest.skip("product_id missing")

    single = requests.get(f"{BASE_URL}/products/{pid}", headers=get_headers(user_id=valid_user_id))
    assert single.status_code == 200
    body = single.json()
    if isinstance(body, dict) and "price" in body and list_price is not None:
        assert body["price"] == list_price


def test_cart_update_positive_quantity_persists(valid_user_id, valid_product_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    add = requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id, "quantity": 1})
    if add.status_code != 200:
        pytest.skip("cannot prepare cart")

    upd = requests.post(f"{BASE_URL}/cart/update", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id, "quantity": 3})
    assert upd.status_code == 200

    cart = requests.get(f"{BASE_URL}/cart", headers=get_headers(user_id=valid_user_id))
    assert cart.status_code == 200
    items = cart.json().get("items", [])
    row = next((i for i in items if i.get("product_id") == valid_product_id), None)
    if row:
        assert row.get("quantity") == 3


def test_cart_remove_existing_product_disappears(valid_user_id, valid_product_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    add = requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id, "quantity": 1})
    if add.status_code != 200:
        pytest.skip("cannot prepare cart")

    rem = requests.post(f"{BASE_URL}/cart/remove", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id})
    assert rem.status_code == 200

    cart = requests.get(f"{BASE_URL}/cart", headers=get_headers(user_id=valid_user_id))
    assert cart.status_code == 200
    ids = [i.get("product_id") for i in cart.json().get("items", [])]
    assert valid_product_id not in ids


def test_cart_clear_empties_items(valid_user_id, valid_product_id):
    requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id, "quantity": 1})
    clr = requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    assert clr.status_code == 200

    cart = requests.get(f"{BASE_URL}/cart", headers=get_headers(user_id=valid_user_id))
    assert cart.status_code == 200
    assert len(cart.json().get("items", [])) == 0


def test_coupon_remove_idempotent(valid_user_id):
    r1 = requests.post(f"{BASE_URL}/coupon/remove", headers=get_headers(user_id=valid_user_id))
    r2 = requests.post(f"{BASE_URL}/coupon/remove", headers=get_headers(user_id=valid_user_id))
    assert r1.status_code == 200
    assert r2.status_code == 200


def test_checkout_rejects_numeric_payment_method(valid_user_id):
    res = requests.post(f"{BASE_URL}/checkout", headers=get_headers(user_id=valid_user_id), json={"payment_method": 1})
    assert res.status_code == 400


def test_checkout_success_clears_cart(valid_user_id, valid_product_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=get_headers(user_id=valid_user_id))
    add = requests.post(f"{BASE_URL}/cart/add", headers=get_headers(user_id=valid_user_id), json={"product_id": valid_product_id, "quantity": 1})
    if add.status_code != 200:
        pytest.skip("could not add product")

    chk = requests.post(f"{BASE_URL}/checkout", headers=get_headers(user_id=valid_user_id), json={"payment_method": "CARD"})
    if chk.status_code != 200:
        pytest.skip("checkout not successful in this state")

    cart = requests.get(f"{BASE_URL}/cart", headers=get_headers(user_id=valid_user_id))
    assert cart.status_code == 200
    assert len(cart.json().get("items", [])) == 0


def test_orders_get_existing_order_if_available(valid_user_id):
    all_orders = requests.get(f"{BASE_URL}/orders", headers=get_headers(user_id=valid_user_id))
    if all_orders.status_code != 200:
        pytest.skip("orders endpoint unavailable")
    rows = all_orders.json()
    if not rows:
        pytest.skip("no existing orders")

    oid = rows[-1].get("order_id")
    if oid is None:
        pytest.skip("order_id missing")
    single = requests.get(f"{BASE_URL}/orders/{oid}", headers=get_headers(user_id=valid_user_id))
    assert single.status_code == 200
    body = single.json()
    if isinstance(body, dict) and "order_id" in body:
        assert body["order_id"] == oid


def test_orders_invoice_math_if_order_available(valid_user_id):
    all_orders = requests.get(f"{BASE_URL}/orders", headers=get_headers(user_id=valid_user_id))
    if all_orders.status_code != 200:
        pytest.skip("orders endpoint unavailable")
    rows = all_orders.json()
    if not rows:
        pytest.skip("no orders available")

    oid = rows[-1].get("order_id")
    if oid is None:
        pytest.skip("order_id missing")
    invoice = requests.get(f"{BASE_URL}/orders/{oid}/invoice", headers=get_headers(user_id=valid_user_id))
    if invoice.status_code != 200:
        pytest.skip("invoice endpoint not available for selected order")

    data = invoice.json()
    subtotal = data.get("subtotal") if isinstance(data, dict) else None
    gst = data.get("gst") if isinstance(data, dict) else None
    total = data.get("total") if isinstance(data, dict) else None
    if isinstance(subtotal, (int, float)) and isinstance(gst, (int, float)) and isinstance(total, (int, float)):
        assert subtotal + gst == total


def test_wallet_balance_never_negative_after_failed_pay(valid_user_id):
    before = requests.get(f"{BASE_URL}/wallet", headers=get_headers(user_id=valid_user_id))
    if before.status_code != 200:
        pytest.skip("wallet endpoint unavailable")
    b = before.json().get("balance")
    if not isinstance(b, (int, float)):
        pytest.skip("wallet balance missing")

    fail = requests.post(f"{BASE_URL}/wallet/pay", headers=get_headers(user_id=valid_user_id), json={"amount": 10**9})
    if fail.status_code != 400:
        pytest.skip("insufficient wallet case not triggered")

    after = requests.get(f"{BASE_URL}/wallet", headers=get_headers(user_id=valid_user_id))
    assert after.status_code == 200
    a = after.json().get("balance")
    if isinstance(a, (int, float)):
        assert a >= 0
        assert a == b


def test_loyalty_redeem_one_point_boundary(valid_user_id):
    points_res = requests.get(f"{BASE_URL}/loyalty", headers=get_headers(user_id=valid_user_id))
    if points_res.status_code != 200:
        pytest.skip("loyalty endpoint unavailable")
    points = points_res.json().get("points", 0)
    if not isinstance(points, int) or points < 1:
        pytest.skip("not enough points for boundary redeem")

    redeem = requests.post(f"{BASE_URL}/loyalty/redeem", headers=get_headers(user_id=valid_user_id), json={"amount": 1})
    assert redeem.status_code == 200


def test_reviews_list_shape(valid_user_id, valid_product_id):
    res = requests.get(f"{BASE_URL}/products/{valid_product_id}/reviews", headers=get_headers(user_id=valid_user_id))
    assert res.status_code == 200
    body = _maybe_get_json(res)
    assert isinstance(body, dict)
    if "reviews" in body:
        assert isinstance(body["reviews"], list)


def test_reviews_add_missing_comment(valid_user_id, valid_product_id):
    res = requests.post(
        f"{BASE_URL}/products/{valid_product_id}/reviews",
        headers=get_headers(user_id=valid_user_id),
        json={"rating": 4},
    )
    assert res.status_code == 400


def test_reviews_add_missing_rating(valid_user_id, valid_product_id):
    res = requests.post(
        f"{BASE_URL}/products/{valid_product_id}/reviews",
        headers=get_headers(user_id=valid_user_id),
        json={"comment": "Looks good"},
    )
    assert res.status_code == 400


def test_support_ticket_list_contains_created_ticket(valid_user_id):
    create = requests.post(
        f"{BASE_URL}/support/ticket",
        headers=get_headers(user_id=valid_user_id),
        json={"subject": "List visibility check", "message": "Ensure ticket appears in list"},
    )
    if create.status_code != 200:
        pytest.skip("cannot create ticket")

    tid = create.json().get("ticket_id")
    if tid is None:
        pytest.skip("ticket_id missing")

    listing = requests.get(f"{BASE_URL}/support/tickets", headers=get_headers(user_id=valid_user_id))
    assert listing.status_code == 200
    rows = listing.json()
    if isinstance(rows, list):
        ids = [r.get("ticket_id") for r in rows if isinstance(r, dict)]
        assert tid in ids


def test_support_ticket_update_non_existent(valid_user_id):
    res = requests.put(
        f"{BASE_URL}/support/tickets/999999",
        headers=get_headers(user_id=valid_user_id),
        json={"status": "IN_PROGRESS"},
    )
    assert res.status_code == 404


def test_support_ticket_message_exact_persistence(valid_user_id):
    unique_msg = "Exact message persistence: []{}() !@# 123"
    create = requests.post(
        f"{BASE_URL}/support/ticket",
        headers=get_headers(user_id=valid_user_id),
        json={"subject": "Persistence check", "message": unique_msg},
    )
    if create.status_code != 200:
        pytest.skip("cannot create ticket")

    tid = create.json().get("ticket_id")
    listing = requests.get(f"{BASE_URL}/support/tickets", headers=get_headers(user_id=valid_user_id))
    if listing.status_code != 200:
        pytest.skip("cannot list tickets")

    rows = listing.json()
    row = next((r for r in rows if isinstance(r, dict) and r.get("ticket_id") == tid), None)
    if row and "message" in row:
        assert row["message"] == unique_msg
