/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { Component, onWillStart, useState } from "@odoo/owl";

class LibraryStatsComponent extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            overview: {},
            books: {},
            copies: {},
            members: {},
            borrows: {},
            catalog: {},
        });

        onWillStart(async () => {
            await this.loadStats();
        });
    }

    async loadStats() {
        this.state.loading = true;
        const stats = await this.orm.call("library.borrow", "get_library_dashboard_data", [], {});
        Object.assign(this.state, stats, { loading: false });
    }
}

export class LibraryDashboard extends LibraryStatsComponent {}
LibraryDashboard.template = "library_management.Dashboard";

export class BookSummary extends LibraryStatsComponent {}
BookSummary.template = "library_management.BookSummary";

export class DashboardOverview extends LibraryStatsComponent {}
DashboardOverview.template = "library_management.DashboardOverview";

export class CopySummary extends LibraryStatsComponent {}
CopySummary.template = "library_management.CopySummary";

export class MemberSummary extends LibraryStatsComponent {}
MemberSummary.template = "library_management.MemberSummary";

export class BorrowSummary extends LibraryStatsComponent {}
BorrowSummary.template = "library_management.BorrowSummary";

export class CatalogSummary extends LibraryStatsComponent {}
CatalogSummary.template = "library_management.CatalogSummary";

export class ShelfSummary extends LibraryStatsComponent {}
ShelfSummary.template = "library_management.ShelfSummary";

LibraryDashboard.components = {
    DashboardOverview,
    BookSummary,
    CopySummary,
    MemberSummary,
    BorrowSummary,
    CatalogSummary,
    ShelfSummary,
};

class LibraryBookListController extends ListController {}
LibraryBookListController.template = "library_management.BookListView";
LibraryBookListController.components = {
    ...ListController.components,
    BookSummary,
};

class LibraryBookKanbanController extends KanbanController {}
LibraryBookKanbanController.template = "library_management.BookKanbanView";
LibraryBookKanbanController.components = {
    ...KanbanController.components,
    BookSummary,
};

class LibraryCopyListController extends ListController {}
LibraryCopyListController.template = "library_management.CopyListView";
LibraryCopyListController.components = {
    ...ListController.components,
    CopySummary,
};

class LibraryCopyKanbanController extends KanbanController {}
LibraryCopyKanbanController.template = "library_management.CopyKanbanView";
LibraryCopyKanbanController.components = {
    ...KanbanController.components,
    CopySummary,
};

class LibraryMemberListController extends ListController {}
LibraryMemberListController.template = "library_management.MemberListView";
LibraryMemberListController.components = {
    ...ListController.components,
    MemberSummary,
};

class LibraryBorrowListController extends ListController {}
LibraryBorrowListController.template = "library_management.BorrowListView";
LibraryBorrowListController.components = {
    ...ListController.components,
    BorrowSummary,
};

class LibraryBorrowKanbanController extends KanbanController {}
LibraryBorrowKanbanController.template = "library_management.BorrowKanbanView";
LibraryBorrowKanbanController.components = {
    ...KanbanController.components,
    BorrowSummary,
};

class LibraryCatalogListController extends ListController {}
LibraryCatalogListController.template = "library_management.CatalogListView";
LibraryCatalogListController.components = {
    ...ListController.components,
    CatalogSummary,
};

class LibraryShelfListController extends ListController {}
LibraryShelfListController.template = "library_management.ShelfListView";
LibraryShelfListController.components = {
    ...ListController.components,
    ShelfSummary,
};

registry.category("actions").add("library_management.dashboard", LibraryDashboard, { force: true });
registry.category("views").add("library_book_list", {
    ...listView,
    Controller: LibraryBookListController,
}, { force: true });
registry.category("views").add("library_book_kanban", {
    ...kanbanView,
    Controller: LibraryBookKanbanController,
}, { force: true });
registry.category("views").add("library_copy_list", {
    ...listView,
    Controller: LibraryCopyListController,
}, { force: true });
registry.category("views").add("library_copy_kanban", {
    ...kanbanView,
    Controller: LibraryCopyKanbanController,
}, { force: true });
registry.category("views").add("library_member_list", {
    ...listView,
    Controller: LibraryMemberListController,
}, { force: true });
registry.category("views").add("library_borrow_list", {
    ...listView,
    Controller: LibraryBorrowListController,
}, { force: true });
registry.category("views").add("library_borrow_kanban", {
    ...kanbanView,
    Controller: LibraryBorrowKanbanController,
}, { force: true });
registry.category("views").add("library_catalog_list", {
    ...listView,
    Controller: LibraryCatalogListController,
}, { force: true });
registry.category("views").add("library_shelf_list", {
    ...listView,
    Controller: LibraryShelfListController,
}, { force: true });
