from pathlib import Path
import json
from cardcanvas import CardCanvas, Card
from dash import (
    html,
    dcc,
    callback,
    Input,
    State,
    Output,
    MATCH,
    ALL,
    Patch,
    callback_context,
    no_update,
)
import dash_mantine_components as dmc
import plotly.express as px
import plotly.io as pio
import pandas as pd
from dash_iconify import DashIconify

settings = {
    "title": "NYC Marathon",
    "subtitle": "Analyzing 2024 NYC Marathon",
    "start_config": json.loads(Path("layout.json").read_text()),
    "logo": "https://marathontours.com/wp-content/uploads/2023/03/tcs-new-york-city-marathon-logo.png",
    "grid_compact_type": "vertical",
    "grid_row_height": 120,
}

data = pd.read_hdf("data.hdf", "main")
position_data = pd.read_hdf("data.hdf", "positions")


class RacingCard(Card):
    title = "Marathon chart"
    description = "This card shows a chart of a marathon where x-axis is the distance and individual racers are plotted on the y-axis"
    icon = "mdi:file-document-edit"
    grid_settings = {"w": 4, "h": 2, "minW": 4, "minH": 2}

    def render(self):
        filtered_data = position_data.loc[
            position_data["name"].isin(self.settings.get("racers", ["Average Person"]))
        ]
        # Find time where the slowest person reaches the end
        # This has to be done since the original data contains position data for every
        # group of people at every time step until the last person reaches the end
        max_time = filtered_data.drop_duplicates(
            subset=[str(col) for col in filtered_data.columns if col != "time"]
        ).time.max() # type: ignore
        filtered_data = filtered_data[filtered_data["time"] <= max_time]

        fig = px.scatter(
            filtered_data,
            x="position",
            y="name",
            animation_frame="time",
            animation_group="name",
            size="count",
            color="gender",
            hover_name="name",
            size_max=55,
            range_x=[0, 27],
            template="mantine_light",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=15, b=0))
        fig.update_traces(marker=dict(sizemin=5))
        return dmc.Card(
            [
                dmc.Text(
                    self.settings.get("title", "Marathon chart"),
                    fz="30px",
                    fw=600,
                    c="blue",
                ),
                dmc.Text(
                    self.settings.get("description", "Groups of people racing"),
                    fw=600,
                    c="dimmed",
                ),
                dcc.Graph(
                    figure=fig,
                    id={"type": "card-control", "sub-type": "figure", "id": self.id},
                    className="no-drag",
                    responsive=True,
                    style={"height": "100%"},
                ),
            ],
            style={"height": "100%"},
            withBorder=True,
            shadow="xs",
        )

    def render_settings(self):
        return dmc.Stack(
            [
                dmc.MultiSelect(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "racers",
                    },
                    label="Racers",
                    value=self.settings.get("racers", ["Average Person"]),
                    searchable=True,
                    data=[
                        {"label": racer, "value": racer}
                        for racer in position_data["name"].unique()
                    ],
                ),
                dmc.TextInput(
                    id={"type": "card-settings", "id": self.id, "sub-id": "title"},
                    label="Title",
                    value=self.settings.get("title", "Marathon chart"),
                ),
                dmc.TextInput(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "description",
                    },
                    label="Description",
                    value=self.settings.get("description", "Groups of people racing"),
                ),
            ]
        )


class HistogramCard(Card):
    title = "Histogram"
    description = "This card shows a histogram of a given dataset"
    icon = "mdi:file-document-edit"
    grid_settings = {"w": 4, "h": 2, "minW": 4, "minH": 2}

    def render(self):
        column = self.settings.get("column", "overallTimeMinutes")
        color = self.settings.get("color", None)
        nbins = self.settings.get("bins", 20)
        figure = px.histogram(
            data,
            x=column,
            color=color,
            nbins=nbins,
            template="mantine_light",
        )
        figure.update_layout(margin=dict(l=0, r=0, t=15, b=0))
        return dmc.Card(
            [
                dmc.Text(
                    self.settings.get("title", "Histogram"), fz="30px", fw=600, c="blue"
                ),
                dmc.Text(
                    self.settings.get(
                        "description", f"Histogram of {column} coloured by {color}"
                    ),
                    fw=600,
                    c="dimmed",
                ),
                dcc.Graph(
                    figure=figure,
                    id={"type": "card-control", "sub-type": "figure", "id": self.id},
                    className="no-drag",
                    responsive=True,
                    style={"height": "100%"},
                ),
            ],
            style={"height": "100%"},
            withBorder=True,
            shadow="xs",
        )

    def render_settings(self):
        return dmc.Stack(
            [
                dmc.Select(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "column",
                    },
                    label="Column",
                    value=self.settings.get("column", "overallTimeMinutes"),
                    searchable=True,
                    # numeric columns in data
                    data=[
                        {"label": column, "value": column}
                        for column in data.select_dtypes(include="number").columns
                    ],
                ),
                dmc.Select(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "color",
                    },
                    label="Color",
                    value=self.settings.get("color", None),
                    searchable=True,
                    data=[
                        {"label": i, "value": i}
                        for i in data.select_dtypes(exclude="number").columns
                    ],
                ),
                dmc.NumberInput(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "bins",
                    },
                    label="Bins",
                    value=self.settings.get("bins", 20),
                    min=1,
                ),
                dmc.TextInput(
                    id={"type": "card-settings", "id": self.id, "sub-id": "title"},
                    label="Title",
                    value=self.settings.get("title", "Histogram"),
                ),
                dmc.TextInput(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "description",
                    },
                    label="Description",
                    value=self.settings.get("description", f"Histogram description"),
                ),
            ]
        )


def generate_filter(column: pd.Series, input_id, default_value=None):
    """Creating a filter based on the column type and it's unique values
    Used in heatmap card to filter the data based on the column values
    """
    column = column.dropna()
    card_id = input_id["id"]
    filter_type = input_id["sub-id"]
    if column.dtype in ["object", "string", "bool", "category"]:
        sorted_unique = sorted(column.unique().tolist())
        if len(sorted_unique) > 300:
            return dmc.Text(
                "Too many unique values to show filter", fz="14px", fw=600, c="red"
            )
        return [
            dmc.Text("Filter", fz="14px", fw=600),
            dmc.ScrollArea(
                dmc.CheckboxGroup(
                    id={
                        "type": "card-settings",
                        "id": card_id,
                        "sub-id": f"{filter_type}-filter",
                    },
                    value=default_value or sorted_unique,
                    children=dmc.Stack(
                        [dmc.Checkbox(label=x, value=x) for x in sorted_unique]
                    ),
                ),
                h=250,
            ),
        ]
    return [
        dmc.Text("Filter", fz="14px", fw=600),
        dmc.RangeSlider(
            id={
                "type": "card-settings",
                "id": card_id,
                "sub-id": f"{filter_type}-filter",
            },
            value=default_value or [column.min(), column.max()],
            min=column.min(),
            max=column.max(),
            minRange=(column.max() - column.min()) / 100,
        ),
    ]


class HeatMap(Card):
    title = "Heatmap"
    description = "This card shows a heatmap of a given dataset"
    icon = "mdi:file-document-edit"
    grid_settings = {"w": 4, "h": 2, "minW": 4, "minH": 2}

    def render(self):
        x = self.settings.get("x", "minutesPerKM")
        x_filter = self.settings.get("x-filter", None)
        y = self.settings.get("y", "ageBand")
        y_filter = self.settings.get("y-filter", None)
        nbinsx = self.settings.get("nbinsx", 20)
        nbinsy = self.settings.get("nbinsy", 20)
        filtered_data = data.loc[:, [x, y]]
        if x_filter is not None:
            if filtered_data[x].dtype in ["object", "string", "bool", "category"]:
                filtered_data = filtered_data[filtered_data[x].isin(x_filter)]
            else:
                filtered_data = filtered_data[
                    (filtered_data[x] >= x_filter[0])
                    & (filtered_data[x] <= x_filter[1])
                ]
        if y_filter is not None:
            if filtered_data[y].dtype in ["object", "string", "bool", "category"]:
                filtered_data = filtered_data[filtered_data[y].isin(y_filter)]
            else:
                filtered_data = filtered_data[
                    (filtered_data[y] >= y_filter[0])
                    & (filtered_data[y] <= y_filter[1])
                ]
        figure = px.density_heatmap(
            filtered_data,
            x=x,
            y=y,
            nbinsx=nbinsx,
            nbinsy=nbinsy,
            template="mantine_light",
        )
        figure.update_layout(margin=dict(l=0, r=0, t=15, b=0))
        return dmc.Card(
            [
                dmc.Text(
                    self.settings.get("title", "Heatmap"), fz="30px", fw=600, c="blue"
                ),
                dmc.Text(
                    self.settings.get("description", f"Heatmap of {x} vs {y}"),
                    fw=600,
                    c="dimmed",
                ),
                dcc.Graph(
                    figure=figure,
                    id={"type": "card-control", "sub-type": "figure", "id": self.id},
                    className="no-drag",
                    responsive=True,
                    style={"height": "100%"},
                ),
            ],
            style={"height": "100%"},
            withBorder=True,
            shadow="xs",
        )

    def render_settings(self):
        return dmc.Stack(
            [
                dmc.Select(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "x",
                    },
                    label="X",
                    value=self.settings.get("x", "minutesPerKM"),
                    searchable=True,
                    # numeric columns in data
                    data=[
                        {"label": column, "value": column} for column in data.columns
                    ],
                ),
                html.Div(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "container": "x-filter",
                    },
                    children=generate_filter(
                        data[self.settings.get("x", "minutesPerKM")],
                        {"type": "card-settings", "id": self.id, "sub-id": "x"},
                        default_value=self.settings.get("x-filter", None),
                    ),
                ),
                dmc.Select(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "y",
                    },
                    label="Y",
                    value=self.settings.get("y", "ageBand"),
                    searchable=True,
                    data=[{"label": i, "value": i} for i in data.columns],
                ),
                html.Div(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "container": "y-filter",
                    },
                    children=generate_filter(
                        data[self.settings.get("y", "ageBand")],
                        {"type": "card-settings", "id": self.id, "sub-id": "y"},
                        default_value=self.settings.get("y-filter", None),
                    ),
                ),
                dmc.NumberInput(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "nbinsx",
                    },
                    label="Number of bins in x direction",
                    value=self.settings.get("nbinsx", 20),
                    min=5,
                ),
                dmc.NumberInput(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "nbinsy",
                    },
                    label="Number of bins in y direction",
                    value=self.settings.get("nbinsy", 20),
                    min=5,
                ),
                dmc.TextInput(
                    id={"type": "card-settings", "id": self.id, "sub-id": "title"},
                    label="Title",
                    value=self.settings.get("title", "Heatmap"),
                ),
                dmc.TextInput(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "description",
                    },
                    label="Description",
                    value=self.settings.get("description", f"Heatmap description"),
                ),
            ]
        )

    @callback(
        Output(
            {"type": "card-settings", "id": MATCH, "container": "x-filter"}, "children"
        ),
        Input({"type": "card-settings", "id": MATCH, "sub-id": "x"}, "value"),
    )
    def update_filter_x(value):
        """If the column is categorical, show a dropdown to filter the data
        else if data is numeric, show a slider to filter the data"""
        column = data[value]
        # get the input id
        ctx = callback_context
        if not ctx.triggered_id:
            return no_update
        input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
        return generate_filter(column, input_id)

    @callback(
        Output(
            {"type": "card-settings", "id": MATCH, "container": "y-filter"}, "children"
        ),
        Input({"type": "card-settings", "id": MATCH, "sub-id": "y"}, "value"),
    )
    def update_filter_y(value):
        column = data[value]
        ctx = callback_context
        if not ctx.triggered_id:
            return no_update
        input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
        return generate_filter(column, input_id)


class ViolinCard(Card):
    title = "Violin"
    description = "This card shows a violin plot of a given dataset"
    icon = "mdi:file-document-edit"
    grid_settings = {"w": 4, "h": 2, "minW": 4, "minH": 2}

    def render(self):
        x = self.settings.get("x", "ageBand")
        y = self.settings.get("y", "overallTimeMinutes")
        fig = px.violin(
            data,
            x=x,
            y=y,
            template="mantine_light",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=15, b=0))
        fig.update_xaxes(
            categoryorder="array",
            categoryarray=data[x].unique(),
        )
        return dmc.Card(
            [
                dmc.Text(
                    self.settings.get("title", "Violin plot"),
                    fz="30px",
                    fw=600,
                    c="blue",
                ),
                dmc.Text(
                    self.settings.get("description", f"Violin plot of {y} by {x}"),
                    fw=600,
                    c="dimmed",
                ),
                dcc.Graph(
                    figure=fig,
                    id={"type": "card-control", "sub-type": "figure", "id": self.id},
                    className="no-drag",
                    responsive=True,
                    style={"height": "100%"},
                ),
            ],
            style={"height": "100%"},
            withBorder=True,
            shadow="xs",
        )

    def render_settings(self):
        return dmc.Stack(
            [
                dmc.Select(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "x",
                    },
                    label="X",
                    value=self.settings.get("x", "ageBand"),
                    searchable=True,
                    data=[
                        {"label": column, "value": column} for column in data.columns
                    ],
                ),
                dmc.Select(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "y",
                    },
                    label="Y",
                    value=self.settings.get("y", "overallTimeMinutes"),
                    searchable=True,
                    # numeric columns in data
                    data=[
                        {"label": column, "value": column}
                        for column in data.select_dtypes(include="number").columns
                    ],
                ),
                dmc.TextInput(
                    id={"type": "card-settings", "id": self.id, "sub-id": "title"},
                    label="Title",
                    value=self.settings.get("title", "Violin plot"),
                ),
                dmc.TextInput(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "description",
                    },
                    label="Description",
                    value=self.settings.get("description", f"Violin plot description"),
                ),
            ]
        )


class HightlightCard(Card):
    title = "Highlight"
    description = "This card shows a highlight of a given dataset"
    icon = "mdi:file-document-edit"

    def render(self):
        column_to_summarize = self.settings.get("column", "gender")
        aggregation = self.settings.get("aggregation", "count")
        filter_value = self.settings.get("column-filter", None)
        filtered = data
        if filter_value is not None:
            filtered = data[data[column_to_summarize] == filter_value]
        highlight_value = filtered[column_to_summarize].agg(aggregation)
        if isinstance(highlight_value, float):
            highlight_value = round(highlight_value, 2)
        icon = self.settings.get("icon", "mdi:star")
        suffix = self.settings.get("suffix", "Number of participants")
        return (
            dmc.Card(
                [
                    dmc.Group(
                        children=[
                            dmc.Text(
                                suffix,
                                c="dimmed",
                                fz="14px",
                                fw=400,
                            )
                        ],
                        # justify="flex-end",
                    ),
                    dmc.Group(
                        children=[
                            dmc.Text(highlight_value, fz="40px", fw=600, c="blue"),
                            dmc.ThemeIcon(
                                DashIconify(icon=icon, width=50),
                                size=50,
                                radius="xl",
                                variant="light",
                            ),
                        ],
                        justify="space-between",
                        wrap="nowrap",
                    ),
                ],
                style={"height": "100%"},
                withBorder=True,
                shadow="xs",
            ),
        )

    def render_settings(self):
        return dmc.Stack(
            [
                dmc.Select(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "column",
                    },
                    label="Column",
                    value=self.settings.get("column", "gender"),
                    searchable=True,
                    data=[
                        {"label": column, "value": column} for column in data.columns
                    ],
                ),
                dmc.Select(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "column-filter",
                    },
                    label="Column Filter",
                    value=self.settings.get("column-filter", None),
                    searchable=True,
                    data=[
                        {"label": str(item), "value": str(item)}
                        for item in data["gender"].unique()
                    ],
                    limit=10,
                ),
                dmc.Select(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "aggregation",
                    },
                    label="Aggregation",
                    value=self.settings.get("aggregation", "count"),
                    searchable=True,
                    data=[
                        {"label": "Count", "value": "count"},
                        {"label": "Mean", "value": "mean"},
                        {"label": "Sum", "value": "sum"},
                        {"label": "Min", "value": "min"},
                        {"label": "Max", "value": "max"},
                    ],
                ),
                dmc.TextInput(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "suffix",
                    },
                    label="Suffix",
                    value=self.settings.get("suffix", "Number of participants"),
                ),
                dmc.TextInput(
                    id={
                        "type": "card-settings",
                        "id": self.id,
                        "sub-id": "icon",
                    },
                    label="Icon",
                    value=self.settings.get("icon", "mdi:star"),
                ),
                html.A(
                    "Icon list",
                    href="https://icon-sets.iconify.design/mdi/?keyword=mdi",
                    target="_blank",
                ),
            ]
        )

    @callback(
        Output(
            {"type": "card-settings", "id": MATCH, "sub-id": "column-filter"}, "data"
        ),
        Input({"type": "card-settings", "id": MATCH, "sub-id": "column"}, "value"),
    )
    def update_column_filter(column):
        return [
            {"label": str(item), "value": str(item)} for item in data[column].unique()
        ]

@callback(
    Output({"type": "card-control", "sub-type": "figure", "id": ALL}, "figure"),
    Input("mantine-provider", "forceColorScheme"),
    State({"type": "card-control", "sub-type": "figure", "id": ALL}, "id"),
)
def update_color_scheme(color_scheme, figure_ids):
    template = pio.templates["mantine_light"] if color_scheme == "light" else pio.templates["mantine_dark"]
    patched_figures = []
    for _ in figure_ids:
        patched_figure = Patch()
        patched_figure["layout"]["template"] = template
        patched_figures.append(patched_figure)
    return patched_figures


canvas = CardCanvas(settings)
canvas.card_manager.register_card_class(RacingCard)
canvas.card_manager.register_card_class(HistogramCard)
canvas.card_manager.register_card_class(HeatMap)
canvas.card_manager.register_card_class(ViolinCard)
canvas.card_manager.register_card_class(HightlightCard)
server = canvas.app.server

if __name__ == "__main__":
    canvas.app.run_server(debug=True)
