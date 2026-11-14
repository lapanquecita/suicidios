import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Este diccionario seá usado para asignarle un nombre a cada clave de entidad.
ENTIDADES = {
    1: "Aguascalientes",
    2: "Baja California",
    3: "Baja California Sur",
    4: "Campeche",
    5: "Coahuila",
    6: "Colima",
    7: "Chiapas",
    8: "Chihuahua",
    9: "Ciudad de México",
    10: "Durango",
    11: "Guanajuato",
    12: "Guerrero",
    13: "Hidalgo",
    14: "Jalisco",
    15: "Estado de México",
    16: "Michoacán",
    17: "Morelos",
    18: "Nayarit",
    19: "Nuevo León",
    20: "Oaxaca",
    21: "Puebla",
    22: "Querétaro",
    23: "Quintana Roo",
    24: "San Luis Potosí",
    25: "Sinaloa",
    26: "Sonora",
    27: "Tabasco",
    28: "Tamaulipas",
    29: "Tlaxcala",
    30: "Veracruz",
    31: "Yucatán",
    32: "Zacatecas",
}


# Clasificaremos las defunciones en 4 categorías.
CAUSAS = {
    "X70": "ahorcamiento",
    "X72": "armas de fuego",
    "X73": "armas de fuego",
    "X74": "armas de fuego",
    "X60": "envenenamiento",
    "X61": "envenenamiento",
    "X62": "envenenamiento",
    "X63": "envenenamiento",
    "X64": "envenenamiento",
    "X65": "envenenamiento",
    "X66": "envenenamiento",
    "X67": "envenenamiento",
    "X68": "envenenamiento",
    "X69": "envenenamiento",
    "X71": "otras causas",
    "X75": "otras causas",
    "X76": "otras causas",
    "X77": "otras causas",
    "X78": "otras causas",
    "X79": "otras causas",
    "X80": "otras causas",
    "X81": "otras causas",
    "X82": "otras causas",
    "X83": "otras causas",
    "X84": "otras causas",
}

# Nuestras categorías tendrán un color específico.
COLORES_CAUSAS = {
    "ahorcamiento": "#ab47bc",
    "armas de fuego": "#e64a19",
    "envenenamiento": "#558b2f",
    "otras causas": "#1976d2",
}


# Estos bins serán usados para agrupar las edades.
BINS = [0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79, 84, 120]

LABELS = [
    "0-4",
    "5-9",
    "10-14",
    "15-19",
    "20-24",
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "55-59",
    "60-64",
    "65-69",
    "70-74",
    "75-79",
    "80-84",
    "≥85",
]


def causas(año):
    """
    Genera una gráfica de pastel con la distribución
    de suicidios por causa de defunción.

    Parameters
    ----------
    año : int
        El año que se desea graficar.
        Puede ser entre 1998 y 2024.

    """

    # Cargamos el dataset de suicidios.
    df = pd.read_csv("./data.csv")

    # Filtramos por el año especificado.
    df = df[df["ANIO_REGIS"] == año]

    # Acortamos los códigos de la CIE-10 para obtener la causa principal.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].str[:3]

    # Agregmos la categoría a cada causa de defunción.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].map(CAUSAS)

    # Contamos el total de registros por causa de defunción y año de registro.
    df = df.pivot_table(
        index="CAUSA_DEF",
        columns="SEXO",
        values="EDAD",
        aggfunc="count",
        fill_value=0,
    )

    # Agregamos una columna con el total para cada grupo de edad.
    df["total"] = df.sum(axis=1)

    # Vamos a crear un DataFrame para cada sexo.
    # Cada uno tendrá sus porcentajes y textos calculados.
    hombres = df[1].to_frame("total").sort_index()
    hombres["color"] = hombres.index.map(COLORES_CAUSAS)
    hombres["perc"] = hombres["total"] / hombres["total"].sum() * 100
    hombres.index = hombres.index.str.capitalize()
    hombres["texto"] = hombres.apply(
        lambda x: f"<b>{x['perc']:,.2f}%</b><br>({x['total']:,.0f})", axis=1
    )

    mujeres = df[2].to_frame("total").sort_index()
    mujeres["perc"] = mujeres["total"] / mujeres["total"].sum() * 100
    mujeres["color"] = mujeres.index.map(COLORES_CAUSAS)
    mujeres.index = mujeres.index.str.capitalize()
    mujeres["texto"] = mujeres.apply(
        lambda x: f"<b>{x['perc']:,.2f}%</b><br>({x['total']:,.0f})", axis=1
    )

    # Definimos los títulos para cada gráfica de dona.
    titulos = [
        f"<b>{hombres['total'].sum():,.0f}</b><br>Hombres",
        f"<b>{mujeres['total'].sum():,.0f}</b><br>Mujeres",
    ]

    # Crearemos dos gráficas de dona, una para cada sexo.
    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.12,
        subplot_titles=titulos,
        specs=[[{"type": "pie"}, {"type": "pie"}]],
    )

    fig.add_trace(
        go.Pie(
            labels=hombres.index,
            values=hombres["total"],
            text=hombres["texto"],
            texttemplate="%{text}",
            hole=0.75,
            textposition="outside",
            marker_line_color="#001414",
            marker_colors=hombres["color"],
            marker_line_width=5,
            sort=False,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Pie(
            labels=mujeres.index,
            values=mujeres["total"],
            text=mujeres["texto"],
            texttemplate="%{text}",
            hole=0.75,
            textposition="outside",
            marker_line_color="#001414",
            marker_colors=mujeres["color"],
            marker_line_width=5,
            sort=False,
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        legend_orientation="h",
        legend_itemsizing="constant",
        legend_x=0.5,
        legend_y=-0.1,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Suicidios registrados en México durante {año} según sexo y causa de defunción",
        title_x=0.5,
        title_y=0.95,
        margin_t=200,
        margin_b=160,
        title_font_size=36,
        paper_bgcolor="#001414",
    )

    # Ajustamos la posición y el tamaño de los títulos de cada gráfica.
    for annotation in fig["layout"]["annotations"]:
        annotation["y"] = 0.5
        annotation["yanchor"] = "middle"
        annotation["font"]["size"] = 100

    fig.add_annotation(
        x=0.01,
        xanchor="left",
        xref="paper",
        y=-0.2,
        yanchor="bottom",
        yref="paper",
        text=f"Fuente: INEGI (EDR, {año})",
    )

    fig.add_annotation(
        x=1.01,
        xanchor="right",
        xref="paper",
        y=-0.2,
        yanchor="bottom",
        yref="paper",
        text="🧁 @lapanquecita",
    )

    fig.write_image(f"./causas_{año}.png")


def causas_tendencia(sexo_id, sexo, plot_color, paper_color):
    """
    Genera una gráfica de barras normalizada mostrando las
    proporciones de suicidios por año de registro y causa de defunción.

    Parameters
    ----------
    sexo_id : int
        El identificador del sexo.
        1 para hombres. 2 para mujeres.

    sexo : str
        La etiqueta del sexo.

    plot_color : str
        El color para el fondo del gráfico.

    paper_color : str
        El color para el lienzo.

    """

    # Cargamos el dataset de suicidios.
    df = pd.read_csv("./data.csv")

    # Filtramos por sexo.
    df = df[df["SEXO"] == sexo_id]

    # Solo tomamos registros de 1998 en adelante.
    # Ya que a partir de ese año se usa la CIE-10.
    df = df[df["ANIO_REGIS"] >= 1998]

    # Acortamos los códigos de la CIE-10 para obtener la causa principal.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].str[:3]

    # Agregmos la categoría a cada causa de defunción.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].map(CAUSAS)

    # Contamos el total de registros por causa de defunción y año de registro.
    df = df.pivot_table(
        index="ANIO_REGIS",
        columns="CAUSA_DEF",
        values="SEXO",
        aggfunc="count",
        fill_value=0,
    )

    # Agregamos una columna con el total.
    df["total"] = df.sum(axis=1)

    # Modificamos el índice para que muestre el total.
    df.index = df.apply(lambda x: f"<b>{x.name}</b><br>({x['total']:,.0f})", axis=1)

    # Solo mostraremos los últimos 20 años.
    df = df.tail(20)

    fig = go.Figure()

    # Vamos a iterar sobre las 4 categorías
    # y crear una gráfica de barras normalizada.
    for columna in df.columns[:-1]:
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df[columna] / df["total"] * 100,
                text=df[columna] / df["total"] * 100,
                texttemplate=" %{text:,.0f}% ",
                textfont_family="Oswald",
                textfont_color="#FFFFFF",
                textfont_size=32,
                name=columna.capitalize(),
                marker_color=COLORES_CAUSAS[columna],
                marker_line_width=0,
                textposition="inside",
                insidetextanchor="middle",
                textangle=0,
            )
        )

    fig.update_xaxes(
        tickfont_size=20,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=len(df) + 1,
    )

    fig.update_yaxes(
        range=[0, 100],
        title="Proporción respecto al total anual",
        ticksuffix="%",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showgrid=False,
        showline=True,
        nticks=11,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        uniformtext_minsize=22,
        uniformtext_mode="show",
        barmode="stack",
        legend_itemsizing="constant",
        legend_traceorder="normal",
        showlegend=True,
        legend_orientation="h",
        legend_x=0.5,
        legend_y=1.06,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="white",
        font_size=24,
        title_text=f"Suicidios de <b>{sexo}</b> en México según causa de defunción y año de registor (2005-2024)",
        title_x=0.5,
        title_y=0.965,
        margin_t=120,
        margin_l=140,
        margin_r=40,
        margin_b=160,
        title_font_size=36,
        plot_bgcolor=plot_color,
        paper_bgcolor=paper_color,
        annotations=[
            dict(
                x=0.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: INEGI (EDR)",
            ),
            dict(
                x=0.5,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro de la defunción",
            ),
            dict(
                x=1.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./causas_anual_{sexo_id}.png")


def causas_entidad(sexo_id, sexo, plot_color, paper_color):
    """
    Genera una gráfica de barras normalizada mostrando las
    proporciones de suicidios por entidad de residencia y causa de defunción.

    Parameters
    ----------
    sexo_id : int
        El identificador del sexo.
        1 para hombres. 2 para mujeres.

    sexo : str
        La etiqueta del sexo.

    plot_color : str
        El color para el fondo del gráfico.

    paper_color : str
        El color para el lienzo.

    """

    # Cargamos el dataset de suicidios.
    df = pd.read_csv("./data.csv")

    # Filtramos por sexo.
    df = df[df["SEXO"] == sexo_id]

    # Solo tomamos registros de 1998 en adelante.
    # Ya que a partir de ese año se usa la CIE-10.
    df = df[df["ANIO_REGIS"] >= 1998]

    # Escogemos solo a residentes de México.
    df = df[df["ENT_RESID"].between(1, 32)]

    # Asiganmos el nombre a cada clave de entidad.
    df["ENT_RESID"] = df["ENT_RESID"].map(ENTIDADES)

    # Acortamos los códigos de la CIE-10 para obtener la causa principal.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].str[:3]

    # Agregmos la categoría a cada causa de defunción.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].map(CAUSAS)

    # Contamos el total de registros por causa de defunción y entidad de residencia.
    df = df.pivot_table(
        index="ENT_RESID",
        columns="CAUSA_DEF",
        values="SEXO",
        aggfunc="count",
        fill_value=0,
    )

    # Agregamos una fila con el total nacional.
    df.loc["Nacional"] = df.sum(axis=0)

    # Agregamos una columna con el total por entidad.
    df["total"] = df.sum(axis=1)

    # Modificamos el índice para que muestre el total.
    df.index = df.apply(lambda x: f"<b>{x.name}</b><br>({x['total']:,.0f})", axis=1)

    # Para esta gráfica vamos a calcular las proporciones antes
    # de graficarlas, ya que las ordenaremos.
    for columna in df.columns[:-1]:
        df[columna] = df[columna] / df["total"] * 100

    # Ordenamos por ahorcamiento.
    df = df.sort_values("ahorcamiento", ascending=True)

    fig = go.Figure()

    # Vamos a iterar sobre las 4 categorías
    # y crear una gráfica de barras normalizada.
    for columna in df.columns[:-1]:
        fig.add_trace(
            go.Bar(
                y=df.index,
                x=df[columna],
                text=df[columna],
                texttemplate=" %{text:,.0f}% ",
                textfont_family="Oswald",
                textfont_color="#FFFFFF",
                textfont_size=32,
                name=columna.capitalize(),
                orientation="h",
                marker_color=COLORES_CAUSAS[columna],
                marker_line_width=0,
                textposition="inside",
                insidetextanchor="end",
            )
        )
    fig.update_xaxes(
        range=[0, 100],
        ticks="outside",
        ticksuffix="%",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=11,
    )

    fig.update_yaxes(
        tickfont_size=20,
        ticks="outside",
        ticklen=10,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showgrid=False,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        barmode="stack",
        legend_orientation="h",
        legend_traceorder="normal",
        showlegend=True,
        legend_x=0.5,
        legend_y=1.025,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1920,
        height=2400,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Suicidios de <b>{sexo}</b> en México según causa de defunción y entidad de residencia (1998-2024)",
        title_x=0.5,
        title_y=0.98,
        margin_t=140,
        margin_l=240,
        margin_r=40,
        margin_b=120,
        title_font_size=36,
        plot_bgcolor=plot_color,
        paper_bgcolor=paper_color,
        annotations=[
            dict(
                x=0.01,
                y=-0.045,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: INEGI (EDR)",
            ),
            dict(
                x=0.55,
                y=-0.045,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Proporción dentro de cada entidad",
            ),
            dict(
                x=1.01,
                y=-0.045,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./causas_entidad_{sexo_id}.png")


def causas_edad(sexo_id, sexo, plot_color, paper_color):
    """
    Genera una gráfica de barras normalizada mostrando las
    proporciones de suicidios por grupo de edad y causa de defunción.

    Parameters
    ----------
    sexo_id : int
        El identificador del sexo.
        1 para hombres. 2 para mujeres.

    sexo : str
        La etiqueta del sexo.

    plot_color : str
        El color para el fondo del gráfico.

    paper_color : str
        El color para el lienzo.

    """

    # Cargamos el dataset de suicidios.
    df = pd.read_csv("./data.csv")

    # Filtramos por sexo.
    df = df[df["SEXO"] == sexo_id]

    # Solo tomamos registros de 1998 en adelante.
    # Ya que a partir de ese año se usa la CIE-10.
    df = df[df["ANIO_REGIS"] >= 1998]

    # Acortamos los códigos de la CIE-10 para obtener la causa principal.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].str[:3]

    # Agregmos la categoría a cada causa de defunción.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].map(CAUSAS)

    # Categorizamos la edad.
    df["EDAD"] = pd.cut(df["EDAD"], bins=BINS, labels=LABELS, include_lowest=True)

    # Contamos el total de registros por causa de defunción y grupo de edad.
    df = df.pivot_table(
        index="EDAD",
        columns="CAUSA_DEF",
        values="SEXO",
        aggfunc="count",
        fill_value=0,
        observed=True,
    )

    # Agregamos una fila con el total de todos los grupos.
    df.loc["Todos"] = df.sum(axis=0)

    # Agregamos una columna con el total para cada grupo de edad.
    df["total"] = df.sum(axis=1)

    # Modificamos el índice para que muestre el total.
    df.index = df.apply(lambda x: f"<b>{x.name}</b><br>({x['total']:,.0f})", axis=1)

    fig = go.Figure()

    # Vamos a iterar sobre las 4 categorías
    # y crear una gráfica de barras normalizada.
    for columna in df.columns[:-1]:
        fig.add_trace(
            go.Bar(
                y=df.index,
                x=df[columna] / df["total"] * 100,
                text=df[columna] / df["total"] * 100,
                texttemplate=" %{text:,.0f}% ",
                textfont_family="Oswald",
                textfont_color="#FFFFFF",
                textfont_size=32,
                name=columna.capitalize(),
                orientation="h",
                marker_color=COLORES_CAUSAS[columna],
                marker_line_width=0,
                textposition="inside",
                insidetextanchor="end",
            )
        )

    fig.update_xaxes(
        range=[0, 100],
        ticks="outside",
        ticksuffix="%",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=11,
    )

    fig.update_yaxes(
        title_text="Grupo de edad al momento de la defunción (número de registros)",
        ticks="outside",
        ticklen=10,
        title_standoff=20,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showgrid=False,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        barmode="stack",
        legend_orientation="h",
        legend_traceorder="normal",
        showlegend=True,
        legend_x=0.5,
        legend_y=1.03,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1920,
        height=1920,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Suicidios de <b>{sexo}</b> en México según causa de defunción y grupo de edad (1998-2024)",
        title_x=0.5,
        title_y=0.975,
        margin_t=140,
        margin_l=200,
        margin_r=40,
        margin_b=120,
        title_font_size=36,
        plot_bgcolor=plot_color,
        paper_bgcolor=paper_color,
        annotations=[
            dict(
                x=0.01,
                y=-0.055,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: INEGI (EDR)",
            ),
            dict(
                x=0.55,
                y=-0.055,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Proporción dentro de cada grupo de edad",
            ),
            dict(
                x=1.01,
                y=-0.055,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./causas_edad_{sexo_id}.png")


if __name__ == "__main__":
    causas(2025)

    causas_tendencia(1, "hombres", "#0A1410", "#13261D")
    causas_tendencia(2, "mujeres", "#18122B", "#393053")

    causas_entidad(1, "hombres", "#0A1410", "#13261D")
    causas_entidad(2, "mujeres", "#18122B", "#393053")

    causas_edad(1, "hombres", "#0A1410", "#13261D")
    causas_edad(2, "mujeres", "#18122B", "#393053")
