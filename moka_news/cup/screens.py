"""Screens used by the Cup TUI."""

from typing import List, Dict, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Label, ListView, ListItem


class EditorialListScreen(Screen):
    """Screen for browsing past editorials"""

    BINDINGS = [
        Binding("escape", "dismiss", "Back", priority=True),
        ("q", "dismiss", "Back"),
    ]

    CSS = """
    EditorialListScreen {
        align: center middle;
    }
    
    #editorial-list-container {
        width: 80%;
        height: 80%;
        border: solid $primary;
        background: $panel;
        padding: 1;
    }
    
    ListView {
        height: 100%;
    }
    
    ListItem {
        padding: 1 2;
    }
    
    ListItem:hover {
        background: $boost;
    }
    """

    def __init__(self, editorials: List[Dict[str, Any]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editorials = editorials
        self.selected_editorial = None

    def compose(self) -> ComposeResult:
        yield Header()

        with VerticalScroll(id="editorial-list-container"):
            if self.editorials:
                items = []
                for editorial in self.editorials:
                    timestamp = editorial["timestamp"]
                    date_str = timestamp.strftime("%A, %B %d, %Y at %H:%M")
                    title = editorial.get("title", "Untitled")
                    item = ListItem(
                        Label(f"[bold]{title}[/bold]\n[dim]{date_str}[/dim]")
                    )
                    item.editorial_data = editorial
                    items.append(item)

                yield ListView(*items)
            else:
                yield Static(
                    "[bold]No past editorials found[/bold]\n\n"
                    "Editorials will appear here after they are generated.",
                    id="empty-state",
                )

        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if hasattr(event.item, "editorial_data"):
            self.selected_editorial = event.item.editorial_data
            self.dismiss(self.selected_editorial)

    def action_dismiss(self) -> None:
        self.dismiss(None)
