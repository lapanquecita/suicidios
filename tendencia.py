import numpy as np
import pandas as pd
import plotly.graph_objects as go


# Estos serán los colores usados para todas las visualizaciones.
PAPER_COLOR = "#002222"
PLOT_COLOR = "#001414"


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


def tendencia_general():
    """
    Genera una gráfica tipo dumbbell con la evolución de las
    tasas de suicidio por sexo.
    """

    # Cargamos el dataset de población de hombres.
    hombres_pop = pd.read_csv("./assets/poblacion_entidad/hombres.csv", index_col=0)

    # Sumamos el total por año.
    hombres_pop = hombres_pop.sum(axis=0)

    # Convertimos el índice a int para poderlo emparejar.
    hombres_pop.index = hombres_pop.index.astype(int)

    # Cargamos el dataset de población de mujeres.
    mujeres_pop = pd.read_csv("./assets/poblacion_entidad/mujeres.csv", index_col=0)

    # Sumamos el total por año.
    mujeres_pop = mujeres_pop.sum(axis=0)

    # Sumamos el total por año.
    mujeres_pop.index = mujeres_pop.index.astype(int)

    # Cargamos el dataset de suicidios.
    df = pd.read_csv("./data.csv")

    # Contamos todos los registros por año de registro y sexo.
    df = df.pivot_table(
        index="ANIO_REGIS",
        columns="SEXO",
        values="EDAD",
        aggfunc="count",
        fill_value=0,
    )

    # Calculamos tasas por cada 100,000 habitantes.
    df["hombres_pop"] = hombres_pop
    df["hombres_tasa"] = df[1] / df["hombres_pop"] * 100000
    df["mujeres_pop"] = mujeres_pop
    df["mujeres_tasa"] = df[2] / df["mujeres_pop"] * 100000

    # Preparamos los textos.
    df["hombres_texto"] = df.apply(
        lambda x: f"<span style='color:#b3e5fc'><b>{x['hombres_tasa']:,.2f}</b></span><br>({x[1]:,.0f})",
        axis=1,
    )

    df["mujeres_texto"] = df.apply(
        lambda x: f"<span style='color:#ffe082'><b>{x['mujeres_tasa']:,.2f}</b></span><br>({x[2]:,.0f})",
        axis=1,
    )

    # Solo vamos a mostrar los últimos 20 aÑos.
    df = df.tail(20)

    # VAmos a calcular el cambio porcentual entre el primer y último año.
    hombres_cambio = (
        (df["hombres_tasa"].iloc[-1] - df["hombres_tasa"].iloc[0])
        / df["hombres_tasa"].iloc[0]
        * 100
    )

    mujeres_cambio = (
        (df["mujeres_tasa"].iloc[-1] - df["mujeres_tasa"].iloc[0])
        / df["mujeres_tasa"].iloc[0]
        * 100
    )

    fig = go.Figure()

    # Vamos a crear un tipo de gráfica especial.
    # Van a ser 20 gráficas de línea conectadas po raño.
    # Esto se le conoce como dumbbell o adn chart.
    for index, row in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[index, index],
                y=[row["hombres_tasa"], row["mujeres_tasa"]],
                text=[row["hombres_texto"], row["mujeres_texto"]],
                textposition=["top center", "bottom center"],
                mode="markers+lines+text",
                marker_size=30,
                marker_symbol=["circle", "diamond"],
                marker_color=["#b3e5fc", "#ffe082"],
                line_width=4,
                line_color="#FFFFFF",
                textfont_size=20,
                textfont_family="Oswald",
                showlegend=False,
            )
        )

    # Para nuestra leyenda usaremos gráficas con valores nulos.
    # Así tenemos más control sobre la leyenda.
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name=f"<b>Hombres</b><br>Total acumulado: <b>{df[1].sum():,.0f}</b><br>Crecimiento de la tasa: <b>{hombres_cambio:,.1f}%</b>",
            line_color="#b3e5fc",
            marker_symbol="circle",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name=f"<b>Mujeres</b><br>Total acumulado: <b>{df[2].sum():,.0f}</b><br>Crecimiento de la tasa: <b>{mujeres_cambio:,.1f}%</b>",
            line_color="#ffe082",
            marker_symbol="diamond",
        )
    )

    fig.update_xaxes(
        range=[df.index.min() - 0.7, df.index.max() + 0.7],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=len(df) + 1,
    )

    # Calculamos la escala vertical.
    tasas = df[["hombres_tasa", "mujeres_tasa"]].values.flatten()
    valor_min = np.min(tasas)
    valor_max = np.max(tasas)
    diferencia = (valor_max - valor_min) * 0.12

    fig.update_yaxes(
        title="Tasa por cada 100,000 hombres/mujeres",
        range=[valor_min - diferencia, valor_max + diferencia],
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        showlegend=True,
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        legend_font_size=20,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de las tasas de suicidio en México según sexo ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=130,
        margin_r=40,
        margin_b=120,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: INEGI (EDR)",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro de la defunción",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./tendencia_general.png")


def tendencia_causa(causa, xanchor="left"):
    """
    Genera una gráfica tipo dumbbell con la evolución de las
    tasas de suicidio por sexo según la causa especificada.

    Parameters
    ----------
    causa : str
        La causa de la defunción:
        'ahorcamiento'
        'armas de fuego'
        'envenenamiento'
        'otras causas'

    xanchor : str
        El lado donde se colocará la leyenda.

    """

    # Cargamos el dataset de población de hombres.
    hombres_pop = pd.read_csv("./assets/poblacion_entidad/hombres.csv", index_col=0)

    # Sumamos el total por año.
    hombres_pop = hombres_pop.sum(axis=0)

    # Convertimos el índice a int para poderlo emparejar.
    hombres_pop.index = hombres_pop.index.astype(int)

    # Cargamos el dataset de población de mujeres.
    mujeres_pop = pd.read_csv("./assets/poblacion_entidad/mujeres.csv", index_col=0)

    # Sumamos el total por año.
    mujeres_pop = mujeres_pop.sum(axis=0)

    # Sumamos el total por año.
    mujeres_pop.index = mujeres_pop.index.astype(int)

    # Cargamos el dataset de suicidios.
    df = pd.read_csv("./data.csv")

    # Acortamos los códigos de la CIE-10 para obtener la causa principal.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].str[:3]

    # Agregmos la categoría a cada causa de defunción.
    df["CAUSA_DEF"] = df["CAUSA_DEF"].map(CAUSAS)

    # Filtramos por la causa especificada.
    df = df[df["CAUSA_DEF"] == causa]

    # Contamos todos los registros por año de registro y sexo.
    df = df.pivot_table(
        index="ANIO_REGIS",
        columns="SEXO",
        values="EDAD",
        aggfunc="count",
        fill_value=0,
    )

    # Calculamos tasas por cada 100,000 habitantes.
    df["hombres_pop"] = hombres_pop
    df["hombres_tasa"] = df[1] / df["hombres_pop"] * 100000
    df["mujeres_pop"] = mujeres_pop
    df["mujeres_tasa"] = df[2] / df["mujeres_pop"] * 100000

    # Preparamos los textos.
    df["hombres_texto"] = df.apply(
        lambda x: f"<span style='color:#b3e5fc'><b>{x['hombres_tasa']:,.2f}</b></span><br>({x[1]:,.0f})",
        axis=1,
    )

    df["mujeres_texto"] = df.apply(
        lambda x: f"<span style='color:#ffe082'><b>{x['mujeres_tasa']:,.2f}</b></span><br>({x[2]:,.0f})",
        axis=1,
    )

    # Solo vamos a mostrar los últimos 20 aÑos.
    df = df.tail(20)

    # VAmos a calcular el cambio porcentual entre el primer y último año.
    hombres_cambio = (
        (df["hombres_tasa"].iloc[-1] - df["hombres_tasa"].iloc[0])
        / df["hombres_tasa"].iloc[0]
        * 100
    )

    mujeres_cambio = (
        (df["mujeres_tasa"].iloc[-1] - df["mujeres_tasa"].iloc[0])
        / df["mujeres_tasa"].iloc[0]
        * 100
    )

    fig = go.Figure()

    # Vamos a crear un tipo de gráfica especial.
    # Van a ser 20 gráficas de línea conectadas po raño.
    # Esto se le conoce como dumbbell o adn chart.
    for index, row in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[index, index],
                y=[row["hombres_tasa"], row["mujeres_tasa"]],
                text=[row["hombres_texto"], row["mujeres_texto"]],
                textposition=["top center", "bottom center"],
                mode="markers+lines+text",
                marker_size=30,
                marker_symbol=["circle", "diamond"],
                marker_color=["#b3e5fc", "#ffe082"],
                line_width=4,
                line_color="#FFFFFF",
                textfont_size=20,
                textfont_family="Oswald",
                showlegend=False,
            )
        )

    # Para nuestra leyenda usaremos gráficas con valores nulos.
    # Así tenemos más control sobre la leyenda.
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name=f"<b>Hombres</b><br>Total acumulado: <b>{df[1].sum():,.0f}</b><br>Crecimiento de la tasa: <b>{hombres_cambio:,.1f}%</b>",
            line_color="#b3e5fc",
            marker_symbol="circle",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name=f"<b>Mujeres</b><br>Total acumulado: <b>{df[2].sum():,.0f}</b><br>Crecimiento de la tasa: <b>{mujeres_cambio:,.1f}%</b>",
            line_color="#ffe082",
            marker_symbol="diamond",
        )
    )

    fig.update_xaxes(
        range=[df.index.min() - 0.7, df.index.max() + 0.7],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=len(df) + 1,
    )

    # Calculamos la escala vertical.
    tasas = df[["hombres_tasa", "mujeres_tasa"]].values.flatten()
    valor_min = np.min(tasas)
    valor_max = np.max(tasas)
    diferencia = (valor_max - valor_min) * 0.12

    fig.update_yaxes(
        title="Tasa por cada 100,000 hombres/mujeres",
        range=[valor_min - diferencia, valor_max + diferencia],
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        showlegend=True,
        legend_x=0.01 if xanchor == "left" else 0.99,
        legend_y=0.98,
        legend_xanchor=xanchor,
        legend_yanchor="top",
        legend_font_size=20,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de las tasas de suicidio por <b>{causa}</b> en México según sexo ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=130,
        margin_r=40,
        margin_b=120,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: INEGI (EDR)",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro de la defunción",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./tendencia_{causa}.png")


if __name__ == "__main__":
    tendencia_general()

    tendencia_causa("ahorcamiento")
    tendencia_causa("envenenamiento")
    tendencia_causa("armas de fuego", "right")
