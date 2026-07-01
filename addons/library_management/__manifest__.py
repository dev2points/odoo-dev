{
    "name": "Library Management",
    "version": "16.0.1.0.0",
    "category": "Services/Library",
    "summary": "Manage books, members, borrowing, and library KPIs",
    "author": "Codex",
    "depends": ["base", "web"],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/author_views.xml",
        "views/category_views.xml",
        "views/book_views.xml",
        "views/member_views.xml",
        "views/borrow_views.xml",
        "views/dashboard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "library_management/static/src/js/dashboard.js",
            "library_management/static/src/xml/dashboard.xml",
            "library_management/static/src/css/dashboard.css",
        ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
