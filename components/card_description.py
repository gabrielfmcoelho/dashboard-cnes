import dash.html as html

def generate_description_card(dict_intro_info, id="description-card"):
    """

    :return: Uma DIV que contem um titulo para a dashboard e uma breve descrição.
    """
    return html.Div(
        id=id,
        children=[
            html.H5(dict_intro_info["subtitle"], className="card-subtitle"),
            html.H3(dict_intro_info["title"], className="card-title"),
            html.Div(
                id="intro",
                children=dict_intro_info["description"],
            ),
        ],
    )