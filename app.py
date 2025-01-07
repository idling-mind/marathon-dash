from pathlib import Path
import json
from cardcanvas import CardCanvas, Card
from dash import html, dcc, callback, Input, State, Output, MATCH
import dash_mantine_components as dmc
import plotly.express as px
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
        data = position_data[
            position_data["name"].isin(self.settings.get("racers", ["Average Person"]))
        ]
        fig = px.scatter(
            data,
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
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        fig.update_traces(marker=dict(sizemin=5))
        return dmc.Card(
            dcc.Graph(
                figure=fig,
                className="no-drag",
                responsive=True,
                style={"height": "100%"},
            ),
            style={"height": "100%"},
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
                )
            ]
        )


class HistogramCard(Card):
    title = "Histogram"
    description = "This card shows a histogram of a given dataset"
    icon = "mdi:file-document-edit"
    grid_settings = {"w": 4, "h": 2, "minW": 4, "minH": 2}

    def render(self):
        figure = px.histogram(
            data,
            x=self.settings.get("column", "overallTimeMinutes"),
            color=self.settings.get("color", None),
            nbins=self.settings.get("bins", 10),
            template="mantine_light",
        )
        figure.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        return dmc.Card(
            dcc.Graph(
                figure=figure,
                className="no-drag",
                responsive=True,
                style={"height": "100%"},
            ),
            style={"height": "100%"},
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
            ]
        )


class ViolinCard(Card):
    title = "Violin"
    description = "This card shows a violin plot of a given dataset"
    icon = "mdi:file-document-edit"
    grid_settings = {"w": 4, "h": 2, "minW": 4, "minH": 2}

    def render(self):
        fig = px.violin(
            data,
            x=self.settings.get("x", "ageBand"),
            y=self.settings.get("y", "overallTimeMinutes"),
            template="mantine_light",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        fig.update_xaxes(
            categoryorder="array",
            categoryarray=data[self.settings.get("x", "ageBand")].unique(),
        )
        return dmc.Card(
            dcc.Graph(
                figure=fig,
                className="no-drag",
                responsive=True,
                style={"height": "100%"},
            ),
            style={"height": "100%"},
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
                            dmc.ThemeIcon(
                                DashIconify(icon=icon, width=50),
                                size=50,
                                variant="light",
                            ),
                            dmc.Text(highlight_value, fz="50px", fw=500, c="blue"),
                        ],
                        wrap="nowrap",
                    ),
                    dmc.Group(
                        children=[
                            dmc.Text(
                                suffix,
                                c="dimmed",
                                fz="14px",
                                fw=400,
                            )
                        ],
                        justify="flex-end",
                    ),
                ],
                style={"height": "100%", "background": "white"},
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
                    label="Column",
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


canvas = CardCanvas(settings)
canvas.card_manager.register_card_class(RacingCard)
canvas.card_manager.register_card_class(HistogramCard)
canvas.card_manager.register_card_class(ViolinCard)
canvas.card_manager.register_card_class(HightlightCard)

if __name__ == "__main__":
    canvas.app.run_server(debug=True)
