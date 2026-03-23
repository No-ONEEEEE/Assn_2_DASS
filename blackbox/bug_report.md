# Comprehensive Bug Report: QuickCart REST API

Based on black-box testing against the running QuickCart server, the following 16 explicit bugs were observed deviating from the QuickCart specification.

---

## Bug 1: Profile Phone Number Accepts Alphabetical Characters
* **Endpoint tested:** `PUT /api/v1/profile`
* **Request payload:**
  * **Method:** PUT
  * **URL:** `http://localhost:8080/api/v1/profile`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"name": "Alice", "phone": "abcdefghij"}`
* **Expected result:** 400 Bad Request (phone must be exactly 10 digits)
* **Actual result observed:** 200 OK
* **Failure detail:** Non-numeric phone input was accepted and profile update succeeded.

## Bug 2: Valid Address Addition Rejected Improperly
* **Endpoint tested:** `POST /api/v1/addresses`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/addresses`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"label": "HOME", "street": "123 Main St", "city": "Metropolis", "pincode": "123456"}`
* **Expected result:** 200 OK (valid address should be created)
* **Actual result observed:** 400 Bad Request
* **Failure detail:** Valid input matching documented constraints is rejected.

## Bug 3: Street Minimum Bound Calculation Error (5 Characters Rejected)
* **Endpoint tested:** `POST /api/v1/addresses`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/addresses`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"label": "HOME", "street": "12345", "city": "Metropolis", "pincode": "123456"}`
* **Expected result:** 200 OK (street length 5 is lower inclusive bound)
* **Actual result observed:** 400 Bad Request
* **Failure detail:** Lower boundary value for street length is rejected.

## Bug 4: Street Maximum Bound Calculation Error (100 Characters Rejected)
* **Endpoint tested:** `POST /api/v1/addresses`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/addresses`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"label": "HOME", "street": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "city": "Metropolis", "pincode": "123456"}`
* **Expected result:** 200 OK (street length 100 is upper inclusive bound)
* **Actual result observed:** 400 Bad Request
* **Failure detail:** Upper boundary value for street length is rejected.

## Bug 5: Invalid Pincode Limits Allowed (Too Short)
* **Endpoint tested:** `POST /api/v1/addresses`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/addresses`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"label": "HOME", "street": "123 Main St", "city": "Metropolis", "pincode": "12345"}`
* **Expected result:** 400 Bad Request (pincode must be exactly 6 digits)
* **Actual result observed:** 200 OK
* **Failure detail:** Pincode shorter than 6 digits is accepted.

## Bug 6: Invalid Pincode Limits Allowed (Too Long)
* **Endpoint tested:** `POST /api/v1/addresses`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/addresses`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"label": "HOME", "street": "123 Main St", "city": "Metropolis", "pincode": "1234567"}`
* **Expected result:** 400 Bad Request (pincode must be exactly 6 digits)
* **Actual result observed:** 200 OK
* **Failure detail:** Pincode longer than 6 digits is accepted.

## Bug 7: Cart Add with Exact Zero Quantity Accepted
* **Endpoint tested:** `POST /api/v1/cart/add`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/cart/add`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"product_id": 1, "quantity": 0}`
* **Expected result:** 400 Bad Request (quantity must be at least 1)
* **Actual result observed:** 200 OK
* **Failure detail:** Quantity 0 is accepted in cart add.

## Bug 8: Cart Add with Negative Quantity Accepted
* **Endpoint tested:** `POST /api/v1/cart/add`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/cart/add`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"product_id": 1, "quantity": -5}`
* **Expected result:** 400 Bad Request (quantity must be at least 1)
* **Actual result observed:** 200 OK
* **Failure detail:** Negative quantity is accepted in cart add.

## Bug 9: Updating Cart that Doesn't Exist Returns Incorrect Status
* **Endpoint tested:** `POST /api/v1/cart/update`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/cart/update`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"product_id": 999999, "quantity": 2}`
* **Expected result:** 404 Not Found (updating non-existent cart item should fail)
* **Actual result observed:** 200 OK
* **Failure detail:** Update call succeeds for product not present in cart.

## Bug 10: Applying Invalid Coupon Code Returns 400 instead of 404
* **Endpoint tested:** `POST /api/v1/coupon/apply`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/coupon/apply`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"code": "INVALID_CODE_123"}`
* **Expected result:** 404 Not Found (invalid/non-existent coupon should be treated as missing resource)
* **Actual result observed:** 400 Bad Request
* **Failure detail:** Server returns 400 instead of not-found semantics.

## Bug 11: Review Created with Zero Rating
* **Endpoint tested:** `POST /api/v1/products/1/reviews`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/products/1/reviews`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"rating": 0, "comment": "Okayish"}`
* **Expected result:** 400 Bad Request (rating must be in range 1-5)
* **Actual result observed:** 200 OK
* **Failure detail:** Out-of-range low rating is accepted.

## Bug 12: Review Created with Rating Over Boundaries Limitation (6)
* **Endpoint tested:** `POST /api/v1/products/1/reviews`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/products/1/reviews`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"rating": 6, "comment": "Okayish"}`
* **Expected result:** 400 Bad Request (rating must be in range 1-5)
* **Actual result observed:** 200 OK
* **Failure detail:** Out-of-range high rating is accepted.

## Bug 13: Creating a Review for a Non-Existent Product Appears Successful
* **Endpoint tested:** `POST /api/v1/products/{product_id}/reviews`
* **Request payload:**
  * **Method:** POST
  * **URL:** `http://localhost:8080/api/v1/products/999999/reviews`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Body:** `{"rating": 4, "comment": "Nice"}`
* **Expected result:** 404 Not Found (cannot create review for missing product)
* **Actual result observed:** 200 OK
* **Failure detail:** Review creation succeeds even for non-existent product id.

## Bug 14: Product Price Mismatch Between User and Admin Endpoints
* **Endpoints tested:** `GET /api/v1/products`, `GET /api/v1/admin/products`
* **Request payload:**
  * **Method:** GET
  * **URL 1:** `http://localhost:8080/api/v1/products`
  * **URL 2:** `http://localhost:8080/api/v1/admin/products`
  * **Headers URL 1:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
  * **Headers URL 2:** `{"X-Roll-Number": "123"}`
* **Expected result:** For the same `product_id`, the `price` should be identical on both endpoints.
* **Actual result observed:** Price mismatch detected for same product (`100` from user endpoint vs `95` from admin endpoint).

## Bug 15: Cart Item Subtotal Is Incorrect
* **Endpoint tested:** `GET /api/v1/cart` (after add)
* **Request payload:**
  * **Step 1 Method:** POST
  * **Step 1 URL:** `http://localhost:8080/api/v1/cart/add`
  * **Step 1 Body:** `{"product_id": <valid_product_id>, "quantity": 3}`
  * **Step 2 Method:** GET
  * **Step 2 URL:** `http://localhost:8080/api/v1/cart`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
* **Expected result:** Item `subtotal` should be exactly `quantity * unit_price`.
* **Actual result observed:** API returned subtotal `104` when expected subtotal was `360` (`3 * 120`).

## Bug 16: Cart Total Does Not Include All Item Subtotals
* **Endpoint tested:** `GET /api/v1/cart` (after adding multiple items)
* **Request payload:**
  * **Step 1 Method:** POST
  * **Step 1 URL:** `http://localhost:8080/api/v1/cart/add`
  * **Step 1 Body:** first product quantity `1`
  * **Step 2 Method:** POST
  * **Step 2 URL:** `http://localhost:8080/api/v1/cart/add`
  * **Step 2 Body:** second product quantity `2`
  * **Step 3 Method:** GET
  * **Step 3 URL:** `http://localhost:8080/api/v1/cart`
  * **Headers:** `{"X-Roll-Number": "123", "X-User-ID": "1"}`
* **Expected result:** Cart `total` should equal the sum of all line item subtotals.
* **Actual result observed:** API returned total `120` while calculated total from items was `380`.

## Execution Note (Latest Expanded Run)
An additional large exploratory suite was added and executed from `test_quickcart_api.py`, but the server at `localhost:8080` was unreachable during that run (`Connection refused`).

Because of that infrastructure issue, no additional behavior-level bugs beyond Bug 16 could be confirmed and appended from that specific run.
