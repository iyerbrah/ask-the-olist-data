# Olist database notes

Orders placed on the Olist marketplace in Brazil. Purchases run from 2016-09-04 to
2018-10-17; almost all are between January 2017 and August 2018. Money is in Brazilian reais.

## Tables

### orders — one row per order (99,441)
- order_id: primary key
- customer_id: joins to customers.customer_id
- order_status: delivered (97% of orders), shipped, canceled, unavailable, invoiced, processing, created, approved
- order_purchase_timestamp: when the customer placed the order; use this for "when was it ordered"
- order_approved_at: when payment was approved; can be null
- order_delivered_carrier_date: when the seller handed it to the carrier; can be null
- order_delivered_customer_date: when the customer received it; null for most undelivered orders
- order_estimated_delivery_date: the delivery date promised at purchase

### order_items — one row per item in an order (112,650)
- order_id, order_item_id: together the primary key; order_item_id counts 1, 2, 3... within an order
- product_id: joins to products.product_id
- seller_id: joins to sellers.seller_id; one order can have items from several sellers
- shipping_limit_date: deadline for the seller to hand the item to the carrier
- price: item price, excluding freight
- freight_value: freight charged for this item
- There is no quantity column: two units of a product are two rows.
- 775 orders (mostly unavailable or canceled) have no rows here.

### order_payments — one row per payment on an order (103,886)
- order_id: joins to orders.order_id
- payment_sequential: 1, 2, 3... when an order is paid in several payments
- payment_type: credit_card, boleto, voucher, debit_card, not_defined
- payment_installments: number of credit card installments (0 to 24)
- payment_value: amount of this payment; an order's payments sum to about its price plus freight
- About 3,000 orders have more than one payment row.

### order_reviews — one row per review (99,224)
- review_id: NOT unique; one review can cover several orders
- order_id: joins to orders.order_id; a few orders have more than one review
- review_score: 1 (worst) to 5 (best)
- review_comment_title, review_comment_message: free text in Portuguese; mostly null
- review_creation_date: when the review survey was sent
- review_answer_timestamp: when the customer answered

### customers — one row per order's customer record (99,441)
- customer_id: a new id for every order; only useful for joining to orders
- customer_unique_id: the actual person; 96,096 distinct values
- customer_zip_code_prefix: first 5 digits of the zip code, stored as text
- customer_city: lowercase, no accents (for example 'sao paulo')
- customer_state: two-letter state code (for example 'SP'); 27 states

### products — one row per product (32,951)
- product_id: primary key
- product_category_name: category in Portuguese; null for 610 products
- product_name_lenght, product_description_lenght: character counts (misspelled in the source data)
- product_photos_qty: number of listing photos
- product_weight_g, product_length_cm, product_height_cm, product_width_cm: package size
- There is no product name, only the id and category.

### sellers — one row per seller (3,095)
- seller_id: primary key
- seller_zip_code_prefix, seller_city, seller_state: same formats as for customers

### product_category_name_translation — one row per category (71)
- product_category_name: joins to products.product_category_name
- product_category_name_english: English name in snake_case (for example 'health_beauty')
- Two Portuguese categories have no translation row.

## Rules

- "Revenue" or "sales" means SUM(order_items.price) for orders with order_status = 'delivered'.
  Freight is not revenue unless the question asks for it.
- Counting "orders" means all statuses unless the question names a status.
- Counting "customers" means COUNT(DISTINCT customer_unique_id), never customer_id.
- When a question asks for a category, use product_category_name_english.
- An order is "late" when order_delivered_customer_date > order_estimated_delivery_date.
- Delivery time is order_delivered_customer_date minus order_purchase_timestamp.
- Never join order_items and order_payments in the same query level: both have several rows
  per order, so the join multiplies rows and inflates sums. Aggregate one of them per order
  first, or filter with IN / EXISTS.
- The same applies to order_reviews joined with order_items.

## What this data cannot answer

Costs, profit or margins; product names; customer names, age or gender; seller names;
stock levels; marketing channels or website traffic; returns or refunds; carrier companies;
discounts or coupon codes.
