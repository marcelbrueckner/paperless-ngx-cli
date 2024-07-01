from rich.highlighter import Highlighter

class NoneValueHighlighter(Highlighter):
    """Apply style to `None` value."""

    def highlight(self, text):
        """Highlights all occurences of `None` value"""

        text.highlight_regex(r"\bNone\b", "i purple")

highlight_none = NoneValueHighlighter()
