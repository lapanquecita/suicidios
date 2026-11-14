import numpy as np
import pandas as pd
import plotly.graph_objects as go


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


def main(sexo_id, sexo, plot_color, paper_color):
    """
    Genera un mapa de calor mostrando la evolución
    de las tasas de suicidio por grupo quinquenal de edad.

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

    # Categorizamos la edad.
    df["EDAD"] = pd.cut(df["EDAD"], bins=BINS, labels=LABELS, include_lowest=True)

    # Contamos el total de registros por año y grupo de edad.
    df = df.pivot_table(
        index="EDAD",
        columns="ANIO_REGIS",
        values="SEXO",
        aggfunc="count",
        observed=False,
    )

    # Los valores en cero los hacemos nulos.
    df = df.replace(0, None)

    # Convertimos los nombres de columna a categorías.
    # Esto es para que queden centrados enl a cuadrícula.
    df.columns = df.columns.astype(str)

    # Seleccionamos los últimos 20 años.
    df = df.iloc[:, -20:]

    # Cargamos el dataset de población quinquenal del sexo especificado.
    pop = pd.read_csv(
        f"./assets/poblacion_quinquenal/{sexo}.csv",
        index_col=0,
    )

    # Los valores en cero los hacemos nulos.
    df = df.replace(0, None)

    # Ajustamos la forma del DataFrame de población para que sea igual al de suicidois.
    pop = pop.loc[df.index, df.columns]

    # Hacemos una copia del DataFrame para nuestras anotaciones.
    absolutos_df = df.copy()

    # Calculamos las tasas para cada grupo de edad y año de registro.
    df = df / pop * 100000

    # Para calcular la escala usaremos la tasa más baja y la más alta.
    tasas = df.values.flatten()

    valor_min = np.nanmin(tasas)
    valor_max = np.nanmax(tasas)

    # La escala será de 11 intervalos.
    marcas = np.linspace(valor_min, valor_max, 15)
    etiquetas = [f"{item:,.1f}" for item in marcas]

    # Si la primera etiqueta es 0.0 la convertimos a 0.
    etiquetas[0] = "0" if etiquetas[0] == "0.0" else etiquetas[0]

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(
            x=df.columns,
            y=df.index,
            z=df,
            colorscale=["#0647C8", "#C62828"],
            zmax=valor_max,
            zmin=valor_min,
            colorbar=dict(
                title=f"Tasa por cada 100,000 {sexo} (cifras absolutas en paréntesis)",
                title_side="right",
                ticks="outside",
                outlinewidth=2,
                outlinecolor="#EEEEEE",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=3,
                tickcolor="#EEEEEE",
                ticklen=10,
            ),
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
    )

    fig.update_yaxes(
        title="Grupo de edad al momento de la defunción",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showgrid=False,
        showline=True,
        mirror=True,
    )

    # Agregamos las anotaciones.
    for x in range(len(df.columns)):
        for y in range(len(df.index)):
            tasa = df.iloc[y, x]

            # Nos saltamos taasas nulas.
            if pd.isna(tasa):
                continue

            absoluto = absolutos_df.iloc[y, x]

            if tasa >= 100:
                tasa = f"{tasa:,.0f}<br>({absoluto:,.0f})"
            else:
                tasa = f"{tasa:,.2f}<br>({absoluto:,.0f})"

            fig.add_annotation(
                x=x + 0.15,
                y=y + 0.1,
                xref="x1",
                yref="y1",
                align="center",
                xanchor="center",
                yanchor="top",
                font_family="Oswald",
                font_size=26,
                text=tasa,
                font_color="#FFFFFF",
            )

    # Vamos a dibujar nuestra propia cuadrícula.
    # Necesitamos desfazarla para que coincida con los límites de cada celda.
    for x in range(len(df.columns)):
        fig.add_vline(x + 0.5, line_color="#EEEEEE")

    for y in range(len(df.index)):
        fig.add_hline(y + 0.5, line_color="#EEEEEE")

    fig.update_layout(
        showlegend=False,
        width=2000,
        height=2000,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de las tasas de suicidio de <b>{sexo}</b> en México ({df.columns[0]}-{df.columns[-1]})<br>(tasas calculadas con la población estimada de cada grupo de edad del año correspondiente)",
        title_x=0.5,
        title_y=0.965,
        margin_t=140,
        margin_l=180,
        margin_r=40,
        margin_b=120,
        title_font_size=34,
        plot_bgcolor=plot_color,
        paper_bgcolor=paper_color,
    )

    fig.add_annotation(
        x=0.01,
        y=-0.055,
        xref="paper",
        yref="paper",
        xanchor="left",
        yanchor="top",
        text="Fuente: INEGI (EDR)",
    )

    fig.add_annotation(
        x=0.5,
        y=-0.055,
        xref="paper",
        yref="paper",
        xanchor="center",
        yanchor="top",
        text="Año de registro de la defunción",
    )

    fig.add_annotation(
        x=1.01,
        y=-0.055,
        xref="paper",
        yref="paper",
        xanchor="right",
        yanchor="top",
        text="🧁 @lapanquecita",
    )

    fig.write_image(f"./heat_{sexo_id}.png")


if __name__ == "__main__":
    main(1, "hombres", "#0A1410", "#13261D")
    main(2, "mujeres", "#18122B", "#393053")
