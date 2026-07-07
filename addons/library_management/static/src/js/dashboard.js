/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { Component, onWillStart, useState, useRef, onMounted } from "@odoo/owl";

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
        if (this.renderCharts) {
            this.renderCharts();
        }
    }
}

export class LibraryDashboard extends LibraryStatsComponent {
    setup() {
        super.setup();
        this.weeklyChartRef = useRef("weeklyChart");
        this.monthlyChartRef = useRef("monthlyChart");
        this.doughnutChartRef = useRef("doughnutChart");
        this.charts = [];

        onMounted(() => {
            this.renderCharts();
        });
    }

    renderCharts() {
        if (!window.Chart) {
            console.warn("Chart.js not found");
            return;
        }

        // Clean up previous charts if any
        this.charts.forEach(chart => {
            try {
                chart.destroy();
            } catch (e) {}
        });
        this.charts = [];

        // Chart 1: Weekly Borrow Trend
        const weeklyCtx = this.weeklyChartRef.el;
        if (weeklyCtx && this.state.borrows && this.state.borrows.weekly_data) {
            const data = this.state.borrows.weekly_data;
            const labels = data.map(d => d.label);
            const values = data.map(d => d.count);

            const weeklyChart = new Chart(weeklyCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Loans',
                        data: values,
                        borderColor: '#0d9488', // teal-600
                        backgroundColor: 'rgba(13, 148, 136, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#0d9488',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            padding: 8,
                            displayColors: false,
                        }
                    },
                    scales: {
                        x: { 
                            grid: { display: false },
                            ticks: { font: { size: 11 } }
                        },
                        y: { 
                            beginAtZero: true,
                            ticks: { 
                                stepSize: 1,
                                font: { size: 11 }
                            }
                        }
                    }
                }
            });
            this.charts.push(weeklyChart);
        }

        // Chart 2: Monthly Borrow Trend
        const monthlyCtx = this.monthlyChartRef.el;
        if (monthlyCtx && this.state.borrows && this.state.borrows.monthly_data) {
            const data = this.state.borrows.monthly_data;
            const labels = data.map(d => d.label);
            const values = data.map(d => d.count);

            const monthlyChart = new Chart(monthlyCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Loans',
                        data: values,
                        backgroundColor: 'rgba(99, 102, 241, 0.85)', // indigo-500
                        hoverBackgroundColor: '#4f46e5', // indigo-600
                        borderRadius: 4,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            padding: 8,
                            displayColors: false,
                        }
                    },
                    scales: {
                        x: { 
                            grid: { display: false },
                            ticks: { font: { size: 11 } }
                        },
                        y: { 
                            beginAtZero: true,
                            ticks: { 
                                stepSize: 1,
                                font: { size: 11 }
                            }
                        }
                    }
                }
            });
            this.charts.push(monthlyChart);
        }

        // Chart 3: Book Copy Status Distribution (Doughnut Chart)
        const doughnutCtx = this.doughnutChartRef.el;
        if (doughnutCtx && this.state.books) {
            const books = this.state.books;
            const available = books.available || 0;
            const borrowed = books.borrowed || 0;
            const lost = books.lost || 0;
            const damaged = books.damaged || 0;

            const doughnutChart = new Chart(doughnutCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Available', 'Borrowed', 'Lost', 'Damaged'],
                    datasets: [{
                        data: [available, borrowed, lost, damaged],
                        backgroundColor: [
                            '#10b981', // green-500
                            '#3b82f6', // blue-500
                            '#ef4444', // red-500
                            '#f59e0b', // yellow-500
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff',
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 10,
                                font: { size: 11, family: 'Inter, system-ui' },
                                padding: 12
                            }
                        },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            padding: 8,
                        }
                    },
                    cutout: '70%',
                }
            });
            this.charts.push(doughnutChart);
        }
    }
}
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
