from django.db import models


class Page(models.Model):
    """Model storing the basic info on page.s that can be built with the page builder."""
    name = models.CharField(max_length=255)


class BaseElement(models.Model):
    """
    Abstract model that all other widgets inherits.

    It implements all shared fields such as paddings, margins, etc.
    """
    UNITS = (
        ('px', 'Pixels'),
        ('%', 'Percentage'),
        ('em', 'Em'),
        ('rem', 'Rem'),
    )
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)  # Order in which the widget is rendered in div
    # Padding fields
    padding_top = models.IntegerField(default=0)
    padding_bottom = models.IntegerField(default=0)
    padding_left = models.IntegerField(default=0)
    padding_right = models.IntegerField(default=0)
    # Margin fields
    margin_top = models.IntegerField(default=0)
    margin_bottom = models.IntegerField(default=0)
    margin_left = models.IntegerField(default=0)
    margin_right = models.IntegerField(default=0)
    background_color = models.CharField(max_length=10, default='#ffffff')
    z_index = models.IntegerField(default=0)
    visibility = models.CharField(max_length=50, default='visible')

    class Meta:
        abstract = True

    def render_widget(self, widget):
        return f"""
            <div class="pt-{self.padding_top} pb-{self.padding_bottom} pl-{self.padding_left} pr-{self.padding_right}">
                {widget}
            </div>
        """


class HeadingWidget(BaseElement):
    """Widget that renders a heading."""

    TAGS = (
        ('h1', 'H1'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4'),
        ('h5', 'H5'),
        ('h6', 'H6'),
    )
    name = models.CharField(max_length=55, default='Heading')
    icon = models.CharField(max_length=255, default='fa fa-heading')
    # Widgets main settings
    content = models.TextField()
    tag = models.CharField(max_length=2, default='h2', choices=TAGS)
    # Widgets specific styling options
    font_color = models.CharField(max_length=10, default='#000000')
    font_size = models.IntegerField(default=16)
    font_size_unit = models.CharField(max_length=255, choices=BaseElement.UNITS, default='px')
    font_family = models.CharField(max_length=255, default='Arial')
    font_weight = models.CharField(max_length=255, default='normal')
    font_letter_spacing = models.IntegerField(default=0)
    font_line_height = models.IntegerField(default=0)
    font_line_height_unit = models.CharField(max_length=255, choices=BaseElement.UNITS, default='px')

    def render_widget(self, widget):
        widget = f"""
            <{self.tag} class="">
                {self.content}
            </{self.tag}>
        """
        return super().render_widget(widget)
