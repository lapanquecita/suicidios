import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Estos serán los colores usados para todas las visualizaciones.
PAPER_COLOR = "#002222"
PLOT_COLOR = "#001414"


# Estas llaves y valores son utilizados para el eje vertical del calendario.
DIAS_SEMANA = {
    0: "Lun.",
    1: "Mar.",
    2: "Mié.",
    3: "Jue.",
    4: "Vie.",
    5: "Sáb.",
    6: "Dom.",
}


ABREVIACIONES_MESES = {
    1: "Ene.",
    2: "Feb.",
    3: "Mar.",
    4: "Abr.",
    5: "May.",
    6: "Jun.",
    7: "Jul.",
    8: "Ago.",
    9: "Sep.",
    10: "Oct.",
    11: "Nov.",
    12: "Dic.",
}


MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def crear_calendario(año):
    """
    Genera un calendario con la distribución de suicidios diarios.

    Parameters
    ----------
    año : int
        El año que se desea graficar.
        Puede ser entre 1998 y 2024.

    """

    # Cargamos el dataset de suicidios.
    df = pd.read_csv("./data.csv")

    # Filtramos por el año especificado.
    df = df[df["ANIO_OCUR"] == año]

    # Armamos las fechas.
    df.index = pd.to_datetime(
        {"year": año, "month": df["MES_OCURR"], "day": df["DIA_OCURR"]},
        errors="coerce",
    )

    # Calculamos el mes con más registros.
    mes_max = df["MES_OCURR"].value_counts().head(1)

    # Calculamos los totales de cada día.
    totales = df.index.value_counts()

    # Crearemos un DataFrame con fechas para todos los días del año.
    # Los valores los traemos de los totales antes calculados.
    df = pd.DataFrame(
        index=pd.date_range(f"{año}-01-01", f"{año}-12-31"), data={"total": totales}
    )

    # Crearemos una escala.
    valor_min = df["total"].min()
    valor_max = df["total"].quantile(0.975)

    marcas = np.linspace(valor_min, valor_max, 9)
    etiquetas = [f"{item:,.0f}" for item in marcas]

    etiquetas[-1] = f"≥{etiquetas[-1]}"

    #################################################
    # A partir de aquí las cosas se ponen complicadas.
    #################################################

    # Un año tiene por lo general de 52 a 53 semanas
    # pero cada 28 años tiene 54.

    # Parte del algoritmo es asignarle un número de semana a cada día.
    # No podemos usar la propiedad 'week' del objeto DateTime ya que nos
    # devuelve la del calendario Gregoriano (que puede ser del año anterior).

    # Vamos a crear una lista que nos da 7 veces el número de semana
    # para 54 semanas.
    numero_semana = list()

    for semana in range(54):
        numero_semana.extend([semana for _ in range(7)])

    # Creamos una columna con el día de la semana.
    # Donde 0 es lunes y 6 es domingo.
    df["dayofweek"] = df.index.dayofweek

    # Para determinar el número de semana de tada día
    # debemos ajustar desde el primer día del año (semana 0).
    # Pero no todos los años comienzan en lunes.
    # Lo que hacemos es recortar nuestra lista de numero de semana
    # exactamente donde comienza el año y donde termina y el
    # resultado se agrega a una nueva columna en el DataFrame.
    pad = df.index[0].dayofweek
    df["semana"] = numero_semana[pad : len(df) + pad]

    # En nuestro calendario, el primer día de cada mes tendrá un borde para distinguirlo.
    df["borde"] = df.index.map(lambda x: 1 if x.day == 1 else 0)

    # Calculamos algunas estadísticas que irán debajo del calendario.
    stats_max = f"{df['total'].max():,.0f} el {df['total'].idxmax():%d/%m/%Y}"
    stats_mes = f"{mes_max.values.max():,.0f} en {MESES[mes_max.idxmax()].lower()}"
    stats_total = f"{df['total'].sum():,.0f}"
    stats_promedio = f"{df['total'].sum() / len(df):,.0f}"

    # Vamos a crear un lienzo con tres elmentos:
    # (2) Heatmaps sobrepuestos y (1) Table
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[250, 150],
        vertical_spacing=0.08,
        specs=[[{"type": "scatter"}], [{"type": "table"}]],
    )

    # El primer Heatmap va a tener un solo proposito y es el
    # de mostrar el borde en el primer día de cada mes.
    # Es importante poner atención en los parámetros 'gap', ya que
    # el borde es un truco visual.
    fig.add_trace(
        go.Heatmap(
            x=df["semana"],
            y=df["dayofweek"],
            z=df["borde"],
            xgap=0,
            ygap=18,
            colorscale=["hsla(0, 100%, 100%, 0.0)", "hsla(0, 100%, 100%, 1.0)"],
            showscale=False,
        ),
        col=1,
        row=1,
    )

    # Este heatmap va a mostrar los valores de cada día.
    # Está configurado con la mayoría de variables que definimos anteriormente.
    fig.add_trace(
        go.Heatmap(
            x=df["semana"],
            y=df["dayofweek"],
            z=df["total"],
            xgap=7,
            ygap=25,
            zmin=valor_min,
            zmax=valor_max,
            colorscale="deep_r",
            colorbar=dict(
                title_text="<br>Número de registros diarios",
                title_side="right",
                y=0.6,
                ticks="outside",
                outlinewidth=1.5,
                thickness=20,
                outlinecolor="#FFFFFF",
                tickwidth=2,
                tickcolor="#FFFFFF",
                ticklen=10,
                tickvals=marcas,
                ticktext=etiquetas,
            ),
        ),
        col=1,
        row=1,
    )

    # Agregamos una sencilla tabla con las estadísticas que calculamos anteriormente.
    fig.add_trace(
        go.Table(
            header=dict(
                values=[
                    "<b>Día con más registros</b>",
                    "<b>Mes con más registros</b>",
                    "<b>Total anual</b>",
                    "<b>Promedio diario</b>",
                ],
                font_color="#FFFFFF",
                fill_color="#00796b",
                align="center",
                height=32,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    stats_max,
                    stats_mes,
                    stats_total,
                    stats_promedio,
                ],
                fill_color="#041C32",
                height=32,
                line_width=0.8,
                align="center",
            ),
        ),
        col=1,
        row=2,
    )

    # Es importante fijar el rango del eje horizontal para
    # evitar que se distorcione.
    fig.update_xaxes(
        range=[-1, df["semana"].max() + 1],
        side="top",
        ticktext=list(ABREVIACIONES_MESES.values()),
        tickvals=np.linspace(1.5, 49.5, 12),
        ticks="outside",
        ticklen=5,
        tickwidth=0,
        linecolor="#FFFFFF",
        tickcolor="#041C32",
        showline=True,
        zeroline=False,
        showgrid=False,
        mirror=True,
    )

    # Al igual que con el eje horizontal, fijamos el rango para darle
    # suficiente espacio a cada día de la semana.
    fig.update_yaxes(
        range=[6.75, -0.75],
        ticktext=list(DIAS_SEMANA.values()),
        tickvals=list(DIAS_SEMANA.keys()),
        ticks="outside",
        ticklen=10,
        title_standoff=0,
        tickcolor="#FFFFFF",
        linewidth=1.5,
        showline=True,
        zeroline=False,
        showgrid=False,
        mirror=True,
    )

    # Agregamos anotaciones.
    fig.update_layout(
        showlegend=False,
        width=1920,
        height=800,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Frecuencia diaria de suicidios en México durante {año}",
        title_x=0.5,
        title_y=0.93,
        margin_t=180,
        margin_r=180,
        margin_b=0,
        margin_l=90,
        title_font_size=40,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=0.04,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: INEGI (EDR, {año})",
            ),
            dict(
                x=0.5,
                y=0.04,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="El □ Indica el inicio de cada mes",
            ),
            dict(
                x=1.01,
                y=0.04,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./calendario_{año}.png")


def top_dias(sexo_id, sexo, marker_color):
    """
    Genera una gráfica de barras mostrando
    los días con mayor frecuencia de suicidios.

    Parameters
    ----------
    sexo_id : int
        El identificador del sexo.
        1 para hombres. 2 para mujeres.

    sexo : str
        La etiqueta del sexo.

    marker_color : str
        El color para las barras.

    """

    # Cargamos el dataset de suicidios.
    df = pd.read_csv("./data.csv")

    # Filtramos por sexo.
    df = df[df["SEXO"] == sexo_id]

    # Vamos a armar las fechas.
    # Solo nos interesa el día y mes, pero debemos especificar un año.
    # Nuestro año predeterminado será el 2000 ya que es bisiesto.
    df["fecha"] = pd.to_datetime(
        {"year": 2024, "month": df["MES_OCURR"], "day": df["DIA_OCURR"]},
        errors="coerce",
    )

    # Contamos los totales por fecha.
    df = df["fecha"].value_counts().to_frame("total")

    # Calculamos el total.
    total = df["total"].sum()

    # Solo mostraremos el top 20.
    df = df.head(20)

    # Calculmos los porcentajes.
    df["perc"] = df["total"] / total * 100

    # Preparamos el texto.
    df["texto"] = df.apply(
        lambda x: f"<b>{x['perc']:,.2f}%</b><br>({x['total']:,.0f})", axis=1
    )

    # Preparamos la fecha.
    df.index = df.index.map(lambda x: f"{x.day:02}<br>{ABREVIACIONES_MESES[x.month]}")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["perc"],
            text=df["texto"],
            textposition="outside",
            textfont_color="#FFFFFF",
            marker_color=marker_color,
            marker_line_width=0,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
    )

    fig.update_yaxes(
        range=[0, df["perc"].max() * 1.12],
        title="Proporción respecto al total de registros (absolutos)",
        ticksuffix="%",
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
        showlegend=False,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Los días con mayor frecuencia de suicidios de <b>{sexo}</b> en México",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=140,
        margin_r=40,
        margin_b=160,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.995,
                y=0.94,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                align="left",
                borderpad=7,
                bordercolor="#FFFFFF",
                borderwidth=1,
                bgcolor=PLOT_COLOR,
                text=f"<b>Nota:</b><br>Basado en {total:,.0f} registrps.",
            ),
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
                text="Día y mes de ocurrencia de la defunción",
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

    fig.write_image(f"./dias_{sexo}.png")


if __name__ == "__main__":
    crear_calendario(2024)

    top_dias(1, "hombres", "#00897b")
    top_dias(2, "mujeres", "#ef5350")
