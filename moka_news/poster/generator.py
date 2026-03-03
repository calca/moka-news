"""Poster generator — orchestrates template, rendering, fonts and text into posters."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from PIL import Image, ImageDraw, ImageFont

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import qrcode

    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

from moka_news.logger import get_logger
from moka_news.paths import APP_CONFIG_DIR
from moka_news.poster.template import PosterTemplate, PosterGenerationError
from moka_news.poster.rendering import (
    create_gradient_background,
    draw_rounded_box_with_shadow,
)
from moka_news.poster.fonts import load_font, fit_font_size
from moka_news.poster import text as poster_text

logger = get_logger(__name__)


class PosterGenerator:
    """Generates shareable social posters from editorial content."""

    def __init__(
        self,
        config: Dict[str, Any],
        posters_dir: Optional[Path] = None,
        templates_dir: Optional[Path] = None,
    ):
        if not PIL_AVAILABLE:
            raise PosterGenerationError(
                "Pillow library is required for poster generation. "
                "Install with: pip install Pillow"
            )

        self.config = config

        if posters_dir:
            self.posters_dir = Path(posters_dir)
        else:
            self.posters_dir = APP_CONFIG_DIR / "posters"

        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            package_dir = Path(__file__).parent.parent
            self.templates_dir = package_dir / "templates"

        self.posters_dir.mkdir(parents=True, exist_ok=True)
        if not self.templates_dir.exists():
            self._create_default_templates()

        self.generation_method = "local"
        self.default_template = config.get("default_template", "story")
        self.logo_path_override = config.get("logo_path") or config.get(
            "local", {}
        ).get("logo_path")
        requested_method = config.get("method", "local")
        if requested_method != "local":
            logger.warning(
                "Poster method %r is no longer supported, using local rendering.",
                requested_method,
            )

        if self.default_template == "story":
            story_template = self.templates_dir / "story.json"
            if not story_template.exists():
                self._create_default_templates()

        logger.info("PosterGenerator initialized:")
        logger.info(f"  - Method: {self.generation_method}")
        logger.info(f"  - Default template: {self.default_template}")
        logger.info(f"  - Posters directory: {self.posters_dir}")
        logger.info(f"  - Templates directory: {self.templates_dir}")

    # -- template helpers ----------------------------------------------------

    def _create_default_templates(self):
        """Create default template files if templates directory doesn't exist."""
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        template = {
            "name": "Story",
            "description": "Vertical 4:5 layout optimized for readability",
            "layout": {
                "width": 1080,
                "height": 1350,
                "padding": 72,
                "line_spacing": 1.32,
            },
            "gradient": {"enabled": True, "type": "vertical", "preset": "warm"},
            "content_box": {
                "enabled": True,
                "background": "#ffffff",
                "padding": 56,
                "border_radius": 24,
                "shadow": {
                    "offset_x": 6,
                    "offset_y": 6,
                    "blur": 16,
                    "color": "rgba(0,0,0,0.16)",
                },
            },
            "colors": {
                "background": "#111827",
                "text": "#1f2937",
                "accent": "#be123c",
                "secondary": "#475569",
            },
            "typography": {
                "title_size": 76,
                "summary_size": 34,
                "metadata_size": 22,
                "title_single_line": False,
                "title_max_lines": 2,
                "title_min_size": 46,
                "title_max_size": 76,
                "summary_min_size": 12,
                "summary_max_size": 34,
                "font_family": "arial",
                "font_file": "OpenSans-Regular.ttf",
                "bold_font_file": "OpenSans-Bold.ttf",
            },
            "elements": {
                "qr_code": False,
                "timestamp": False,
                "source": True,
                "editorial_date": True,
                "logo": True,
                "logo_position": "bottom_right",
                "qr_position": "bottom_center",
            },
        }

        template_path = self.templates_dir / "story.json"
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2)

        logger.info(f"Created 1 default template in {self.templates_dir}")

    def list_templates(self) -> List[str]:
        """List available template names."""
        if not self.templates_dir.exists():
            return []
        return sorted(t.stem for t in self.templates_dir.glob("*.json"))

    def load_template(self, template_name: str) -> PosterTemplate:
        """Load a specific template by name."""
        template_path = self.templates_dir / f"{template_name}.json"
        if not template_path.exists():
            available = self.list_templates()
            raise PosterGenerationError(
                f"Template '{template_name}' not found. "
                f"Available templates: {', '.join(available)}"
            )
        return PosterTemplate.from_file(template_path)

    # -- public entry point --------------------------------------------------

    def generate_poster(
        self,
        editorial: Dict[str, Any],
        template_name: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Generate a poster from editorial content."""
        return self._generate_local_poster(editorial, template_name, custom_options)

    # -- font helpers (delegates) --------------------------------------------

    def _load_font(
        self,
        font_file: Optional[str],
        font_family: str,
        size: int,
    ) -> "ImageFont.ImageFont":
        return load_font(font_file, font_family, size)

    def _fit_font_size(
        self,
        draw,
        text,
        font_file,
        font_family,
        max_width,
        max_height,
        line_spacing=1.3,
        min_size=12,
        max_size=220,
    ):
        return fit_font_size(
            draw,
            text,
            font_file,
            font_family,
            max_width,
            max_height,
            line_spacing,
            min_size,
            max_size,
        )

    def _fit_single_line_font_size(
        self,
        draw,
        text,
        font_file,
        font_family,
        max_width,
        max_height,
        min_size=12,
        max_size=220,
    ):
        return fit_font_size(
            draw,
            text,
            font_file,
            font_family,
            max_width,
            max_height,
            min_size=min_size,
            max_size=max_size,
            single_line=True,
        )

    def _fit_font_size_with_line_limit(
        self,
        draw,
        text,
        font_file,
        font_family,
        max_width,
        max_height,
        max_lines,
        line_spacing=1.3,
        min_size=12,
        max_size=220,
    ):
        return fit_font_size(
            draw,
            text,
            font_file,
            font_family,
            max_width,
            max_height,
            line_spacing,
            min_size,
            max_size,
            max_lines=max_lines,
        )

    def _fit_font_size_for_paragraphs(
        self,
        draw,
        text,
        font_file,
        font_family,
        max_width,
        max_height,
        line_spacing=1.3,
        min_size=12,
        max_size=220,
        paragraph_gap_factor=0.4,
    ):
        return fit_font_size(
            draw,
            text,
            font_file,
            font_family,
            max_width,
            max_height,
            line_spacing,
            min_size,
            max_size,
            paragraph_mode=True,
            paragraph_gap_factor=paragraph_gap_factor,
        )

    # -- text helpers (delegates) --------------------------------------------

    def _wrap_text(self, draw, text, font, max_width):
        return poster_text.wrap_text(draw, text, font, max_width)

    @staticmethod
    def _truncate_single_line_text(draw, text, font, max_width):
        return poster_text.truncate_single_line_text(draw, text, font, max_width)

    def _limit_wrapped_lines(self, draw, text, font, max_width, max_lines):
        return poster_text.limit_wrapped_lines(draw, text, font, max_width, max_lines)

    def _parse_rich_text(self, text):
        return poster_text.parse_rich_text(text)

    def _wrap_rich_lines(self, draw, segments, regular_font, bold_font, max_width):
        return poster_text.wrap_rich_lines(
            draw, segments, regular_font, bold_font, max_width
        )

    def _extract_poster_paragraph(self, markdown_content):
        return poster_text.extract_poster_paragraph(markdown_content)

    @staticmethod
    def _extract_title_and_body(content):
        return poster_text.extract_title_and_body(content)

    def _clean_content_for_poster(self, content):
        return poster_text.clean_content_for_poster(content)

    def _format_body_for_readability(self, text):
        return poster_text.format_body_for_readability(text)

    @staticmethod
    def _split_paragraphs(text):
        return poster_text.split_paragraphs(text)

    def _get_fallback_font_candidates(self, font_family):
        from moka_news.poster.fonts import _get_fallback_font_candidates

        return _get_fallback_font_candidates(font_family)

    # -- editorial date helpers -----------------------------------------------

    @staticmethod
    def _parse_editorial_datetime(value: Any) -> Optional[datetime]:
        """Best-effort parse of editorial timestamp values."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(value)
            except (OverflowError, OSError, ValueError):
                return None
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return None
            normalized = raw
            if normalized.endswith("Z"):
                normalized = normalized[:-1] + "+00:00"
            candidates = [normalized]
            if " " in normalized and "T" not in normalized:
                candidates.append(normalized.replace(" ", "T", 1))
            for candidate in candidates:
                try:
                    return datetime.fromisoformat(candidate)
                except ValueError:
                    continue
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d_%H-%M"):
                try:
                    return datetime.strptime(raw, fmt)
                except ValueError:
                    continue
        return None

    def _get_editorial_date_label(self, editorial: Dict[str, Any]) -> str:
        """Return formatted editorial date for footer display."""
        parsed = self._parse_editorial_datetime(editorial.get("timestamp"))
        if parsed is None:
            parsed = datetime.now()
        return parsed.strftime("%B %d, %Y")

    # -- logo ----------------------------------------------------------------

    def _resolve_logo_path(self) -> Optional[Path]:
        """Resolve logo path from config override or known project locations."""
        candidates: List[Path] = []
        if self.logo_path_override:
            candidates.append(Path(self.logo_path_override).expanduser())
        package_dir = Path(__file__).resolve().parent.parent
        candidates.append(package_dir.parent / "assets" / "moka-news-logo.png")
        candidates.append(package_dir / "assets" / "moka-news-logo.png")
        for candidate in candidates:
            try:
                if candidate.exists() and candidate.is_file():
                    return candidate
            except OSError:
                continue
        return None

    def _add_logo(self, img, template, draw_x, draw_y, max_width, total_draw_h):
        """Add branded logo to poster if enabled and available."""
        if not template.show_logo:
            return img
        logo_path = self._resolve_logo_path()
        if logo_path is None:
            logger.debug("Logo not found, skipping logo rendering.")
            return img
        try:
            with Image.open(logo_path) as logo_raw:
                logo_img = logo_raw.convert("RGBA")
        except Exception as exc:
            logger.warning("Could not load logo %s: %s", logo_path, exc)
            return img

        logo_w = getattr(logo_img, "width", 0)
        logo_h = getattr(logo_img, "height", 0)
        if not isinstance(logo_w, (int, float)) or not isinstance(logo_h, (int, float)):
            return img
        if logo_w <= 0 or logo_h <= 0:
            return img

        max_logo_w = max(80, int(max_width * 0.24))
        max_logo_h = max(40, int(total_draw_h * 0.10))
        scale = min(max_logo_w / logo_w, max_logo_h / logo_h, 1.0)
        target_w = max(1, int(logo_w * scale))
        target_h = max(1, int(logo_h * scale))
        resampling = getattr(Image, "Resampling", Image)
        logo_img = logo_img.resize((target_w, target_h), resampling.LANCZOS)
        alpha = logo_img.getchannel("A").point(lambda p: int(p * 0.92))
        logo_img.putalpha(alpha)

        if template.logo_position == "top_left":
            logo_x, logo_y = draw_x, draw_y
        elif template.logo_position == "top_right":
            logo_x, logo_y = draw_x + max_width - target_w, draw_y
        elif template.logo_position == "bottom_left":
            logo_x, logo_y = draw_x, draw_y + total_draw_h - target_h
        else:
            logo_x = draw_x + max_width - target_w
            logo_y = draw_y + total_draw_h - target_h

        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img.alpha_composite(logo_img, (logo_x, logo_y))
        return img

    # -- QR code -------------------------------------------------------------

    def _add_qr_code(self, img, url, template):
        """Add QR code to the poster."""
        if not QRCODE_AVAILABLE:
            return
        qr = qrcode.QRCode(version=1, box_size=3, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(
            fill_color=template.text_color,
            back_color=template.background_color,
        )
        qr_size = 120
        qr_img = qr_img.resize((qr_size, qr_size))
        positions = {
            "bottom_right": (
                template.width - qr_size - template.padding,
                template.height - qr_size - template.padding,
            ),
            "bottom_left": (
                template.padding,
                template.height - qr_size - template.padding,
            ),
            "top_right": (
                template.width - qr_size - template.padding,
                template.padding,
            ),
            "bottom_center": (
                (template.width - qr_size) // 2,
                template.height - qr_size - template.padding,
            ),
        }
        qr_pos = positions.get(
            template.qr_position,
            positions["bottom_right"],
        )
        if qr_img.mode != "RGBA":
            qr_img = qr_img.convert("RGBA")
        img.paste(qr_img, qr_pos, qr_img)

    def _apply_custom_options(self, template: PosterTemplate, custom_options) -> None:
        """Apply runtime custom options to template attributes."""
        if not custom_options:
            return
        for key, value in custom_options.items():
            if key == "gradient" and isinstance(value, dict):
                for gk, gv in value.items():
                    attr = f"gradient_{gk}"
                    if hasattr(template, attr):
                        setattr(template, attr, gv)
            elif key == "content_box" and isinstance(value, dict):
                for ck, cv in value.items():
                    if ck == "shadow" and isinstance(cv, dict):
                        for sk, sv in cv.items():
                            attr = f"shadow_{sk}"
                            if hasattr(template, attr):
                                setattr(template, attr, sv)
                    else:
                        attr = f"content_box_{ck}"
                        if hasattr(template, attr):
                            setattr(template, attr, cv)
            elif hasattr(template, key):
                setattr(template, key, value)

    def _create_canvas(self, template: PosterTemplate):
        """Create base image and return drawing layout metrics."""
        if template.gradient_enabled and template.gradient_colors:
            img = create_gradient_background(
                template.width,
                template.height,
                template.gradient_colors,
                template.gradient_type,
            )
        else:
            img = Image.new(
                "RGB", (template.width, template.height), template.background_color
            )

        box_height = None
        if template.content_box_enabled:
            box_width = int(template.width * 0.9)
            margin = (template.width - box_width) // 2
            box_x, box_y = margin, margin
            box_height = template.height - (2 * margin)

            shadow_config = {
                "offset_x": template.shadow_offset_x,
                "offset_y": template.shadow_offset_y,
                "blur": template.shadow_blur,
                "color": template.shadow_color,
            }
            img = draw_rounded_box_with_shadow(
                img,
                (box_x, box_y),
                (box_width, box_height),
                template.content_box_radius,
                shadow_config,
                template.content_box_background,
            )

            content_padding = template.content_box_padding
            draw_x = box_x + content_padding
            draw_y = box_y + content_padding
            max_width = box_width - (content_padding * 2)
        else:
            draw_x = template.padding
            draw_y = template.padding
            max_width = template.width - (template.padding * 2)

        total_draw_h = (
            box_height - (template.content_box_padding * 2)
            if template.content_box_enabled and box_height is not None
            else template.height - (template.padding * 2)
        )
        return img, draw_x, draw_y, max_width, total_draw_h

    def _extract_poster_content(self, editorial: Dict[str, Any]):
        """Extract title/body content from editorial payload."""
        content = str(editorial.get("content") or "")
        title = str(editorial.get("title") or "Morning Editorial").strip()
        title_from_content, _ = poster_text.extract_title_and_body(content)
        if title_from_content:
            title = title_from_content
        clean_content = poster_text.extract_poster_paragraph(content)
        body_content = poster_text.format_body_for_readability(clean_content)
        return title, body_content

    def _compute_layout_zones(self, template: PosterTemplate, total_draw_h: int):
        """Compute title/body/footer drawing zones."""
        footer_line_h = template.metadata_font_size + 8
        footer_lines = (
            int(template.show_timestamp)
            + int(template.show_source)
            + int(template.show_source and template.show_editorial_date)
        )
        footer_zone_h = max(footer_lines * footer_line_h + 20, 20)
        divider_zone_h = 32

        usable_h = total_draw_h - footer_zone_h - divider_zone_h
        title_ratio = 0.14 if template.title_single_line else 0.30
        title_zone_h = max(int(usable_h * title_ratio), 40)
        body_zone_h = usable_h - title_zone_h
        return footer_line_h, footer_zone_h, title_zone_h, body_zone_h

    def _build_fonts(
        self,
        draw,
        template: PosterTemplate,
        title: str,
        body_content: str,
        max_width: int,
        title_zone_h: int,
        body_zone_h: int,
    ):
        """Auto-fit and load title/body/footer fonts."""
        metadata_font = load_font(
            template.font_file,
            template.font_family,
            template.metadata_font_size,
        )
        width_scale = max(0.6, template.width / 1080.0)
        title_min = max(16, int(template.title_min_size * width_scale))
        title_max = max(title_min, int(template.title_max_size * width_scale))

        if template.title_single_line:
            title_font_size = fit_font_size(
                draw,
                title,
                template.font_file,
                template.font_family,
                max_width,
                title_zone_h,
                min_size=title_min,
                max_size=title_max,
                single_line=True,
            )
        elif template.title_max_lines > 0:
            title_font_size = fit_font_size(
                draw,
                title,
                template.font_file,
                template.font_family,
                max_width,
                title_zone_h,
                template.line_spacing,
                min_size=title_min,
                max_size=title_max,
                max_lines=template.title_max_lines,
            )
        else:
            title_font_size = fit_font_size(
                draw,
                title,
                template.font_file,
                template.font_family,
                max_width,
                title_zone_h,
                template.line_spacing,
                min_size=title_min,
                max_size=title_max,
            )
        title_font = load_font(
            template.bold_font_file, template.font_family, title_font_size
        )

        plain_body = re.sub(r"\*\*([^*]+)\*\*", r"\1", body_content)
        body_min = max(8, int(template.summary_min_size * width_scale))
        body_max = max(body_min, int(template.summary_max_size * width_scale))
        body_intro_gap = 10
        body_fit_height = max(1, body_zone_h - body_intro_gap)
        body_font_size = fit_font_size(
            draw,
            plain_body,
            template.bold_font_file,
            template.font_family,
            max_width,
            body_fit_height,
            template.line_spacing,
            min_size=body_min,
            max_size=body_max,
            paragraph_mode=True,
        )
        summary_font = load_font(
            template.font_file, template.font_family, body_font_size
        )
        summary_bold_font = load_font(
            template.bold_font_file, template.font_family, body_font_size
        )
        return (
            metadata_font,
            title_font,
            summary_font,
            summary_bold_font,
            body_intro_gap,
            body_fit_height,
        )

    def _draw_title_and_divider(
        self,
        draw,
        template: PosterTemplate,
        title: str,
        title_font,
        draw_x: int,
        draw_y: int,
        max_width: int,
        body_intro_gap: int,
    ) -> int:
        """Draw title and divider, return body start Y."""
        current_y = draw_y
        if template.title_single_line:
            title_lines = [
                poster_text.truncate_single_line_text(
                    draw, title, title_font, max_width
                )
            ]
        elif template.title_max_lines > 0:
            title_lines = poster_text.limit_wrapped_lines(
                draw,
                title,
                title_font,
                max_width,
                template.title_max_lines,
            )
        else:
            title_lines = poster_text.wrap_text(draw, title, title_font, max_width)
        for line in title_lines:
            draw.text(
                (draw_x, current_y), line, fill=template.accent_color, font=title_font
            )
            bbox = draw.textbbox((draw_x, current_y), line, font=title_font)
            current_y += int((bbox[3] - bbox[1]) * template.line_spacing)

        current_y += 12
        draw.line(
            [(draw_x, current_y), (draw_x + max_width, current_y)],
            fill=template.accent_color,
            width=3,
        )
        current_y += 17 + body_intro_gap
        return current_y

    def _draw_body_text(
        self,
        draw,
        template: PosterTemplate,
        body_content: str,
        summary_font,
        summary_bold_font,
        draw_x: int,
        start_y: int,
        max_width: int,
        body_fit_height: int,
    ) -> None:
        """Draw wrapped body text with rich formatting support."""
        current_y = start_y
        body_max_y = current_y + body_fit_height
        body_paragraphs = poster_text.split_paragraphs(body_content)
        line_probe_bbox = draw.textbbox((0, 0), "Ag", font=summary_font)
        paragraph_gap_h = max(4, int((line_probe_bbox[3] - line_probe_bbox[1]) * 0.4))

        stop_render = False
        for pidx, paragraph in enumerate(body_paragraphs):
            rich_segments = poster_text.parse_rich_text(paragraph)
            rich_lines = poster_text.wrap_rich_lines(
                draw,
                rich_segments,
                summary_font,
                summary_bold_font,
                max_width,
            )
            for line_tokens in rich_lines:
                if current_y > body_max_y:
                    stop_render = True
                    break
                x = draw_x
                line_h = 0
                for token_text, _is_bold, token_font in line_tokens:
                    draw.text(
                        (x, current_y),
                        token_text,
                        fill=template.text_color,
                        font=token_font,
                    )
                    bbox = draw.textbbox((x, current_y), token_text, font=token_font)
                    x += bbox[2] - bbox[0]
                    token_h = bbox[3] - bbox[1]
                    if token_h > line_h:
                        line_h = token_h
                current_y += int(line_h * template.line_spacing)
            if stop_render:
                break
            if pidx < len(body_paragraphs) - 1:
                if current_y + paragraph_gap_h > body_max_y:
                    break
                current_y += paragraph_gap_h

    def _draw_footer(
        self,
        draw,
        template: PosterTemplate,
        editorial: Dict[str, Any],
        metadata_font,
        draw_x: int,
        draw_y: int,
        total_draw_h: int,
        footer_zone_h: int,
        footer_line_h: int,
    ) -> None:
        """Draw footer metadata lines."""
        footer_y = draw_y + total_draw_h - footer_zone_h + 20
        if template.show_timestamp:
            ts = datetime.now().strftime("%B %d, %Y")
            draw.text(
                (draw_x, footer_y),
                f"Generated: {ts}",
                fill=template.secondary_color,
                font=metadata_font,
            )
            footer_y += footer_line_h
        if template.show_source:
            draw.text(
                (draw_x, footer_y),
                "MoKa News Editorial",
                fill=template.secondary_color,
                font=metadata_font,
            )
            footer_y += footer_line_h
            if template.show_editorial_date:
                editorial_date = self._get_editorial_date_label(editorial)
                draw.text(
                    (draw_x, footer_y),
                    f"Editorial date: {editorial_date}",
                    fill=template.secondary_color,
                    font=metadata_font,
                )

    # -- local poster generation ----------------------------------------------

    def _generate_local_poster(
        self,
        editorial: Dict[str, Any],
        template_name: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Generate poster locally using PIL/Pillow."""
        logger.info(
            f"_generate_local_poster: start "
            f"(template={template_name or self.default_template!r})"
        )
        template_name = template_name or self.default_template
        template = self.load_template(template_name)
        logger.debug(
            f"Template loaded: {template.name} ({template.width}x{template.height}), "
            f"gradient={template.gradient_enabled}, content_box={template.content_box_enabled}"
        )
        self._apply_custom_options(template, custom_options)

        img, draw_x, draw_y, max_width, total_draw_h = self._create_canvas(template)
        draw = ImageDraw.Draw(img)
        title, body_content = self._extract_poster_content(editorial)
        footer_line_h, footer_zone_h, title_zone_h, body_zone_h = self._compute_layout_zones(
            template, total_draw_h
        )
        (
            metadata_font,
            title_font,
            summary_font,
            summary_bold_font,
            body_intro_gap,
            body_fit_height,
        ) = self._build_fonts(
            draw,
            template,
            title,
            body_content,
            max_width,
            title_zone_h,
            body_zone_h,
        )
        body_start_y = self._draw_title_and_divider(
            draw,
            template,
            title,
            title_font,
            draw_x,
            draw_y,
            max_width,
            body_intro_gap,
        )
        self._draw_body_text(
            draw,
            template,
            body_content,
            summary_font,
            summary_bold_font,
            draw_x,
            body_start_y,
            max_width,
            body_fit_height,
        )
        self._draw_footer(
            draw,
            template,
            editorial,
            metadata_font,
            draw_x,
            draw_y,
            total_draw_h,
            footer_zone_h,
            footer_line_h,
        )

        # Logo
        img = self._add_logo(
            img,
            template,
            draw_x=draw_x,
            draw_y=draw_y,
            max_width=max_width,
            total_draw_h=total_draw_h,
        )

        # Save
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{timestamp}_poster.png"
        output_path = self.posters_dir / filename

        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background

        img.save(output_path, "PNG", optimize=True)
        logger.info(f"_generate_local_poster: saved → {output_path}")
        return output_path
