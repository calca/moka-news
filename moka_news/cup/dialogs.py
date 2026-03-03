"""Modal dialogs used across the Cup TUI."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, Button, ProgressBar
from typing import Optional

from moka_news import __version__


class ConfirmationDialog(ModalScreen[bool]):
    """Modal dialog for confirming actions"""

    DEFAULT_CSS = """
    ConfirmationDialog {
        align: center middle;
    }
    
    #dialog-container {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 2;
    }
    
    #dialog-message {
        padding: 1 2;
        width: 100%;
        content-align: center middle;
    }
    
    #button-container {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
    }
    
    Button {
        margin: 0 1;
    }
    """

    def __init__(self, message: str, title: str = "Confirmation"):
        super().__init__()
        self.message = message
        self.dialog_title = title

    def compose(self) -> ComposeResult:
        """Create the dialog layout"""
        with Vertical(id="dialog-container"):
            yield Static(f"[bold]{self.dialog_title}[/bold]", id="dialog-title")
            yield Static(self.message, id="dialog-message")
            with Horizontal(id="button-container"):
                yield Button("Yes", variant="success", id="yes-button")
                yield Button("No", variant="error", id="no-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "yes-button":
            self.dismiss(True)
        elif event.button.id == "no-button":
            self.dismiss(False)

    def on_key(self, event) -> None:
        """Handle keyboard input"""
        if event.key == "y":
            self.dismiss(True)
        elif event.key == "n" or event.key == "escape":
            self.dismiss(False)


class LoadingDialog(ModalScreen):
    """Modal dialog showing loading progress"""

    DEFAULT_CSS = """
    LoadingDialog {
        align: center middle;
    }
    
    #loading-container {
        width: 50;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 2;
    }
    
    #loading-message {
        padding: 1 2;
        width: 100%;
        content-align: center middle;
    }
    
    #progress-container {
        width: 100%;
        padding: 1 2;
    }
    
    ProgressBar {
        width: 100%;
        margin: 1 0;
    }
    """

    def __init__(self, message: str = "Loading..."):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Create the loading dialog layout"""
        with Vertical(id="loading-container"):
            yield Static(f"[bold]🔄 {self.message}[/bold]", id="loading-message")
            with Vertical(id="progress-container"):
                yield ProgressBar(show_eta=False, show_percentage=False)

    def on_mount(self) -> None:
        """Start the progress bar animation"""
        progress_bar = self.query_one(ProgressBar)
        progress_bar.update(progress=None)

    def update_message(self, new_message: str) -> None:
        """Update the loading message"""
        self.message = new_message
        try:
            message_widget = self.query_one("#loading-message", Static)
            message_widget.update(f"[bold]🔄 {new_message}[/bold]")
        except Exception:
            pass  # Widget might not be mounted yet


class InfoDialog(ModalScreen[bool]):
    """Modal dialog showing application info"""

    DEFAULT_CSS = """
    InfoDialog {
        align: center middle;
    }
    
    #info-container {
        width: 70;
        height: 26;
        border: thick $primary;
        background: $panel;
        padding: 2;
    }
    
    #info-buttons {
        dock: bottom;
        width: 100%;
        height: 3;
        padding: 1 0;
        content-align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        editorials_dir: Optional[str] = None,
        posters_dir: Optional[str] = None,
        logs_dir: Optional[str] = None,
    ):
        super().__init__()
        self.config_path = config_path or "Not specified"
        self.editorials_dir = editorials_dir or "Default location"
        self.posters_dir = posters_dir or "Default location"
        self.logs_dir = logs_dir or "Default location"

    def compose(self) -> ComposeResult:
        """Create the info dialog layout"""
        with Vertical(id="info-container"):
            yield Static(
                f"[bold]☕ MoKa News - Application Info[/bold]\n\n"
                f"[bold]Version:[/bold] {__version__}\n\n"
                f"[bold]Configuration File:[/bold]\n{self.config_path}\n\n"
                f"[bold]Editorials Directory:[/bold]\n{self.editorials_dir}\n\n"
                f"[bold]Posters Directory:[/bold]\n{self.posters_dir}\n\n"
                f"[bold]Logs Directory:[/bold]\n{self.logs_dir}\n\n"
                f"[dim]Press ESC or click OK to close[/dim]"
            )
            with Horizontal(id="info-buttons"):
                yield Button("OK", variant="primary", id="ok-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-button":
            self.dismiss(True)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(True)
