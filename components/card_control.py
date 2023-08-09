import dash.html as html
import dash.dcc as dcc
def generate_control_card(dict_control_info, control_data, id="control-card"):
    """

    :return: Uma DIV que contem os controles da dashboard.
    """
    return html.Div(
        id=id,
        children=[
            html.Div(
                [
                    html.P(
                        dict_control_info["title_dropdown3"],
                        className="control-card-title",
                    ),
                    html.Img(
                        src="assets\info-circle-svgrepo-com.svg",
                        style={"cursor": "pointer"},
                        id="info-icon",
                    ),
                ],
                style={
                    "display": "flex",
                    "justify-content": "start",
                    "align-items": "center",
                    "flex-direction": "row",
                    "justify-items": "center",
                    "align-items": "center",
                },
            ),
            dcc.Dropdown(
                id=f"{id}dropdown-select-3",
                options=[
                    {"label": i, "value": i}
                    for i in control_data["dropdown_3"]
                ],
                value=control_data["dropdown_3"][-1],
            ),
            html.Br(),
            html.P(
                dict_control_info["title_dropdown"],
                className="control-card-title",
            ),
            dcc.Dropdown(id=f"{id}dropdown-select"),
            html.Br(),
            html.P(
                dict_control_info["title_dropdown_2"],
                className="control-card-title",
            ),
            dcc.Dropdown(
                id=f"{id}dropdown-select-2",
                options=[
                    {"label": i, "value": i}
                    for i in control_data["dropdown_2"]
                ],
                value=control_data["dropdown_2"][-1],
            ),
            html.Br(),
            html.P(
                dict_control_info["title_checkbox"],
                className="control-card-title",
            ),
            dcc.Checklist(
                id=f"{id}checkbox-select",
                options=[
                    {'label': 'Sim', 'value': 'Sim'},
                ],
                value=["Sim"],
            ),
            html.Br(),
        ],
    )