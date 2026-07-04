# Library Management Architecture (Odoo 16)

## Goal

Build a production-ready Library Management module based on **Product**
and **Stock** instead of reinventing inventory.

## Principles

-   Reuse `product`, `stock`, `mail`, `portal`.
-   Library manages business logic.
-   Inventory manages quantities and locations.
-   One physical copy has one unique ID.

## Architecture

``` text
product.template (Book Title)
    ├── ISBN
    ├── Author
    ├── Publisher
    ├── Category
    └── Metadata

        1:N

library.book.copy (Physical Copy)
    ├── Copy Code
    ├── Barcode
    ├── Shelf
    ├── Condition
    ├── State
    └── Current Location

library.member
      │
library.borrow
      │
library.borrow.line
      │
library.book.copy
      │
stock.move
      │
stock.picking
```

## Project Structure

``` text
library_management/
├── models/
│   ├── product_template.py
│   ├── product_product.py
│   ├── library_book_copy.py
│   ├── library_author.py
│   ├── library_category.py
│   ├── library_publisher.py
│   ├── library_shelf.py
│   ├── library_member.py
│   ├── library_borrow.py
│   ├── library_borrow_line.py
│   ├── library_return.py
│   ├── library_fine.py
│   ├── stock_move.py
│   ├── stock_picking.py
│   └── res_config_settings.py
├── views/
├── security/
├── data/
├── report/
├── wizard/
└── static/src/{js,xml,scss}
```

## Core Models

### product.template

Represents a book title.

Fields: - name - isbn - author_id - publisher_id - category_id -
publish_year - language - edition - image_1920

### library.book.copy

Represents one physical copy.

Fields: - code - product_id - barcode - shelf_id - state - condition -
active

### library.member

Library reader information.

### library.borrow

Borrow document.

States: - draft - approved - borrowed - returned - cancelled

### library.borrow.line

Each line references exactly one `library.book.copy`.

### library.fine

Stores late/lost/damaged penalties.

## Inventory Flow

``` text
Receive Books
      ↓
Library Shelf
      ↓
Borrow Approval
      ↓
Stock Picking
      ↓
Stock Move
      ↓
Borrowed Location
      ↓
Return
      ↓
Shelf
```

## Dashboard

-   Books
    -   Total titles
    -   Total copies
    -   Available
    -   Borrowed
    -   Lost
    -   Damaged
-   Members
-   Borrow
-   Inventory

## Roles

-   Administrator
-   Librarian
-   Member

## Future Roadmap

-   Website catalog
-   Portal
-   Online reservation
-   Chat
-   QR/RFID
-   Multi-branch
-   Mobile app
-   AI recommendation

## Development Order

1.  Product inheritance
2.  Book copy
3.  Author/Publisher/Category/Shelf
4.  Member
5.  Borrow
6.  Return
7.  Fine
8.  Dashboard
9.  Reports
10. Website/Portal
