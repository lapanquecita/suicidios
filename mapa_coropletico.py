import os
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots


# Estos serán los colores usados para todas las visualizaciones.
PAPER_COLOR = "#002222"
PLOT_COLOR = "#001414"


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


def main(año):
    """
    Genera un mapa coroplético con la distribución
    de las tasas de suicidio en México por entidad.

    Parameters
    ----------
    año : int
        El año que deseamos visualizar.

    """

    # Cargamos el dataset de población total por entidad.
    pop = pd.read_csv("./assets/poblacion_entidad/total.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    pop = pop[str(año)]

    # Cargamos el dataset de suicidios.
    df = pd.read_csv("./data.csv")

    # Seleccionamos el año de nuestro interés.`
    df = df[df["ANIO_REGIS"] == año]

    # Calculamos los totales nacionales para el subtítulo.
    total_nacional = len(df)
    poblacion_nacional = pop.sum()
    tasa_nacional = total_nacional / poblacion_nacional * 100000

    # Preparamos el subtítulo
    subtitulo = f"Tasa nacional: <b>{tasa_nacional:,.2f}</b> (con <b>{total_nacional:,.0f}</b> registros)"

    # Quitamos entidades no identificadas.
    df = df[df["ENT_RESID"].between(1, 32)]

    # Transformamos el DataFrame para darnos el total de registros
    # por entidad y sexo.
    df = df.pivot_table(
        index="ENT_RESID",
        columns="SEXO",
        values="EDAD",
        aggfunc="count",
        fill_value=0,
    )

    # Renombramos el índice con los nombres de las entidades.
    df.index = df.index.map(ENTIDADES)

    # Creamos una nueva columna con el total por entidad.
    df["total"] = df.sum(axis=1)

    # Agregamos la columna de población con los datos del DataFrame de población total.
    df["poblacion"] = pop

    # Calculamos la tasa por cada 100,000 habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Ordenamos el DataFrame por la tasa de mayor a menor.
    df.sort_values("tasa", ascending=False, inplace=True)

    # Determinamos los valores mínimos y máximos para nuestra escala.
    valor_min = df["tasa"].min()
    valor_max = df["tasa"].max()

    # Vamos a crear nuestra escala con 11 intervalos.
    marcas = np.linspace(valor_min, valor_max, 11)
    etiquetas = [f"{item:,.1f}" for item in marcas]

    # Cargamos el GeoJSON de México.
    geojson = json.loads(open("./assets/mexico.json", "r", encoding="utf-8").read())

    fig = go.Figure()

    # Para nuestro mapa vamos a enlazar los nombres de las entidades
    # con las tasas.
    # El GeoJSON ya se encuentra preconfigurado para esto.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=df.index,
            z=df["tasa"],
            featureidkey="properties.NOMGEO",
            colorscale="deep_r",
            marker_line_color="#FFFFFF",
            marker_line_width=1.5,
            zmin=valor_min,
            zmax=valor_max,
            colorbar=dict(
                x=0.03,
                y=0.5,
                ypad=50,
                ticks="outside",
                outlinewidth=2,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=3,
                tickcolor="#FFFFFF",
                ticklen=10,
            ),
        )
    )

    # Personalizamos la apariencia del mapa.
    fig.update_geos(
        fitbounds="geojson",
        showocean=True,
        oceancolor=PLOT_COLOR,
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=2,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    # Agregamos anotaciones.
    fig.update_layout(
        showlegend=False,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=80,
        margin_r=40,
        margin_b=60,
        margin_l=40,
        width=1920,
        height=1080,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.025,
                xanchor="center",
                yanchor="top",
                text=f"Tasas de suicidio en México durante {año} según entidad de residencia",
                font_size=42,
            ),
            dict(
                x=0.0275,
                y=0.46,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Tasa bruta por cada 100,000 habitantes",
            ),
            dict(
                x=0.01,
                y=-0.056,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: INEGI (EDR, {año})",
            ),
            dict(
                x=0.5,
                y=-0.056,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=-0.056,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./1.png")

    # Ahora creamos las tablas que irán debajo del mapa.
    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.03,
        specs=[[{"type": "table"}, {"type": "table"}]],
    )

    fig.add_trace(
        go.Table(
            columnwidth=[140, 70, 70, 70, 95],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Hombres</b>",
                    "<b>Mujeres</b>",
                    "<b>Total</b>",
                    "<b>Tasa ↓</b>",
                ],
                font_color="white",
                fill_color=["#00796b", "#00796b", "#00796b", "#00796b", "#C25B42"],
                align="center",
                height=45,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[:16],
                    df[1][:16],
                    df[2][:16],
                    df["total"][:16],
                    df["tasa"][:16],
                ],
                fill_color=PLOT_COLOR,
                height=45,
                format=["", ",", ",", ",", ",.2f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=1,
        row=1,
    )

    fig.add_trace(
        go.Table(
            columnwidth=[140, 70, 70, 70, 95],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Hombres</b>",
                    "<b>Mujeres</b>",
                    "<b>Total</b>",
                    "<b>Tasa ↓</b>",
                ],
                font_color="white",
                fill_color=["#00796b", "#00796b", "#00796b", "#00796b", "#C25B42"],
                align="center",
                height=45,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[16:],
                    df[1][16:],
                    df[2][16:],
                    df["total"][16:],
                    df["tasa"][16:],
                ],
                fill_color=PLOT_COLOR,
                height=45,
                format=["", ",", ",", ",", ",.2f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=2,
        row=1,
    )

    fig.update_layout(
        width=1920,
        height=840,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=25,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        paper_bgcolor=PAPER_COLOR,
    )

    fig.write_image("./2.png")

    # Con ambas imágenes generadas, es momento de unirlas en una sola.
    image1 = Image.open("./1.png")
    image2 = Image.open("./2.png")

    result_width = image1.width
    result_height = image1.height + image2.height

    result = Image.new("RGB", (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, image1.height))

    result.save(f"./mapa_{año}.png")

    os.remove("./1.png")
    os.remove("./2.png")


if __name__ == "__main__":
    main(2024)
