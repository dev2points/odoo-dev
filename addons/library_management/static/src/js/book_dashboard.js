/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { Component, onWillStart, useState } from "@odoo/owl";

export class BookDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            total_books: 0,
            available_books: 0,
            borrowed_books: 0,
            lost_books: 0,
            damaged_books: 0,
            category_data: [],
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        const dashboardData = await this.orm.call("library.book", "get_book_dashboard_data", [], {});
        Object.assign(this.state, dashboardData, { loading: false });
    }
}
BookDashboard.template = "library_management.BookDashboard";

class LibraryBookListController extends ListController {}
LibraryBookListController.template = "library_management.BookListView";
LibraryBookListController.components = {
    ...ListController.components,
    BookDashboard,
};

class LibraryBookKanbanController extends KanbanController {}
LibraryBookKanbanController.template = "library_management.BookKanbanView";
LibraryBookKanbanController.components = {
    ...KanbanController.components,
    BookDashboard,
};

registry.category("actions").add("library_management.book_dashboard", BookDashboard, { force: true });
registry.category("actions").add("library_management.dashboard", BookDashboard, { force: true });
registry.category("views").add("library_book_list", {
    ...listView,
    Controller: LibraryBookListController,
}, { force: true });
registry.category("views").add("library_book_kanban", {
    ...kanbanView,
    Controller: LibraryBookKanbanController,
}, { force: true });
