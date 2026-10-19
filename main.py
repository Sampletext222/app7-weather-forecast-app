import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from backend import get_data

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Atmospheric & Weather Intelligence",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🌤️ Forecast Controls")
    st.markdown(
        "Configure parameters below to analyse regional weather trends.")

    place = st.text_input(
        "Location Search",
        value="Adelaide",
        placeholder="e.g., Adelaide, Melbourne, London..."
    )

    days = st.slider(
        "Forecast Horizon (Days)",
        min_value=1,
        max_value=5,
        value=3,
        help="OpenWeatherMap provides 3-hourly intervals up to 5 days ahead."
    )

    st.divider()
    st.caption(
        "**Portfolio Demo**\n\n"
        "Built with Python, Streamlit & Plotly.\n"
        "Live meteorological data via OpenWeatherMap API.\n"
        "Created By Julian Soriano"
    )

# --- MAIN DASHBOARD ---
if not place:
    st.info(
        "👈 Please enter a city name in the sidebar to generate the forecast.")
    st.stop()

try:
    with st.spinner(
            f"Retrieving atmospheric telemetry for {place.title()}..."):
        filtered_data, city_info = get_data(place, days)

    # Parse JSON into a structured Pandas DataFrame for clean analysis
    records = []
    for item in filtered_data:
        dt = datetime.fromtimestamp(item["dt"])
        records.append({
            "Datetime": pd.to_datetime(item["dt_txt"]),
            "Day": dt.strftime("%a %d %b"),
            "Time": dt.strftime("%H:%M"),
            "Temp (°C)": round(item["main"]["temp"], 1),
            "Feels Like (°C)": round(item["main"]["feels_like"], 1),
            "Min Temp (°C)": round(item["main"]["temp_min"], 1),
            "Max Temp (°C)": round(item["main"]["temp_max"], 1),
            "Humidity (%)": item["main"]["humidity"],
            "Pressure (hPa)": item["main"]["pressure"],
            "Wind Speed (km/h)": round(item["wind"]["speed"] * 3.6, 1),
            # m/s to km/h
            "Pop (%)": int(item.get("pop", 0) * 100),
            # Probability of precipitation
            "Condition": item["weather"][0]["main"],
            "Description": item["weather"][0]["description"].title(),
            "Icon": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png"
        })
    df = pd.DataFrame(records)

    # --- HEADER SECTION ---
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.title(f"📍 {city_info['name']}, {city_info['country']}")
        st.caption(
            f"Coordinates: {city_info['coord']['lat']:.2f}°, {city_info['coord']['lon']:.2f}° | "
            f"Showing {len(df)} intervals across {days} {'day' if days == 1 else 'days'}"
        )
    with head_col2:
        # Display current condition badge at top right
        current = df.iloc[0]
        st.image(current["Icon"], width=70)
        st.markdown(
            f"**Now:** {current['Temp (°C)']}°C ({current['Description']})")

    # --- TOP-LEVEL KPI METRICS ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        with st.container(border=True):
            temp_delta = round(
                df["Temp (°C)"].iloc[-1] - df["Temp (°C)"].iloc[0], 1)
            st.metric(
                label="Current Temperature",
                value=f"{current['Temp (°C)']} °C",
                delta=f"{temp_delta} °C over {days}d",
            )

    with kpi2:
        with st.container(border=True):
            st.metric(
                label=f"{days}-Day Peak / Low",
                value=f"{df['Temp (°C)'].max()}° / {df['Temp (°C)'].min()}°",
                delta=f"Avg: {df['Temp (°C)'].mean():.1f} °C",
                delta_color="off"
            )

    with kpi3:
        with st.container(border=True):
            st.metric(
                label="Max Humidity",
                value=f"{df['Humidity (%)'].max()}%",
                delta=f"Avg: {df['Humidity (%)'].mean():.0f}% | Now: {current['Humidity (%)']}%",
                delta_color="off"
            )

    with kpi4:
        with st.container(border=True):
            st.metric(
                label="Peak Wind Speed",
                value=f"{df['Wind Speed (km/h)'].max()} km/h",
                delta=f"Current: {current['Wind Speed (km/h)']} km/h",
                delta_color="off"
            )

    st.write("")  # Spacing

    # --- INTERACTIVE TABS ---
    tab_temp, tab_sky, tab_wind, tab_data = st.tabs([
        "🌡️ Temperature & Rain",
        "☁️ Sky Conditions Timeline",
        "💨 Wind & Humidity",
        "🗺️ Map & Raw Data"
    ])

    # TAB 1: Temperature & Precipitation Dual Chart
    with tab_temp:
        st.subheader("Temperature Trajectory & Rain Probability")

        fig = go.Figure()

        # Actual Temperature Line
        fig.add_trace(go.Scatter(
            x=df["Datetime"],
            y=df["Temp (°C)"],
            mode="lines+markers",
            name="Actual Temp (°C)",
            line=dict(color="#FF6B6B", width=3),
            hovertemplate="%{y}°C<extra>Actual</extra>"
        ))

        # Feels Like Dashed Line
        fig.add_trace(go.Scatter(
            x=df["Datetime"],
            y=df["Feels Like (°C)"],
            mode="lines",
            name="Feels Like (°C)",
            line=dict(color="#FFA8A8", width=2, dash="dot"),
            hovertemplate="%{y}°C<extra>Feels Like</extra>"
        ))

        # Rain Probability Bar Overlay on Secondary Y-Axis
        fig.add_trace(go.Bar(
            x=df["Datetime"],
            y=df["Pop (%)"],
            name="Rain Probability (%)",
            marker_color="rgba(77, 171, 247, 0.25)",
            yaxis="y2",
            hovertemplate="%{y}%<extra>Rain Prob</extra>"
        ))

        fig.update_layout(
            hovermode="x unified",
            height=420,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(title="Date & Time (3-Hour Intervals)", showgrid=False),
            yaxis=dict(title="Temperature (°C)", side="left"),
            yaxis2=dict(
                title="Precipitation Probability (%)",
                side="right",
                overlaying="y",
                range=[0, 100],
                showgrid=False
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    # TAB 2: Sky Conditions Visual Cards
    with tab_sky:
        st.subheader("3-Hourly Sky Condition Breakdown")

        # Group by Day so it reads cleanly like a real weather app
        for day_label, group in df.groupby("Day", sort=False):
            st.markdown(f"#### 📅 {day_label}")
            cols = st.columns(len(group))
            for idx, (_, row) in enumerate(group.iterrows()):
                with cols[idx]:
                    with st.container(border=True):
                        st.markdown(f"**{row['Time']}**")
                        st.image(row["Icon"], width=55)
                        st.markdown(f"**{row['Temp (°C)']}°C**")
                        st.caption(
                            f"{row['Description']}\n\n💧 {row['Pop (%)']}%")

    # TAB 3: Wind & Humidity Analysis
    with tab_wind:
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            st.subheader("Wind Speed (km/h)")
            fig_wind = px.area(
                df, x="Datetime", y="Wind Speed (km/h)",
                color_discrete_sequence=["#20C997"]
            )
            fig_wind.update_layout(height=350,
                                   margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_wind, use_container_width=True)

        with col_w2:
            st.subheader("Relative Humidity (%)")
            fig_hum = px.line(
                df, x="Datetime", y="Humidity (%)",
                markers=True,
                color_discrete_sequence=["#339AF0"]
            )
            fig_hum.update_layout(height=350,
                                  margin=dict(l=10, r=10, t=20, b=10),
                                  yaxis_range=[0, 100])
            st.plotly_chart(fig_hum, use_container_width=True)

    # TAB 4: Geospatial Map & Styled Dataframe
    with tab_data:
        map_col, table_col = st.columns([1, 2])

        with map_col:
            st.subheader("Station Location")
            map_df = pd.DataFrame({
                "lat": [city_info["coord"]["lat"]],
                "lon": [city_info["coord"]["lon"]]
            })
            st.map(map_df, zoom=9, use_container_width=True)

        with table_col:
            st.subheader("Forecast Telemetry Dataset")
            st.dataframe(
                df[["Datetime", "Condition", "Description", "Temp (°C)",
                    "Feels Like (°C)", "Pop (%)", "Humidity (%)",
                    "Wind Speed (km/h)", "Icon"]],
                column_config={
                    "Datetime": st.column_config.DatetimeColumn("Date & Time",
                                                                format="DD/MM/YY HH:mm"),
                    "Icon": st.column_config.ImageColumn("Sky", width="small"),
                    "Temp (°C)": st.column_config.NumberColumn("Temp",
                                                               format="%.1f °C"),
                    "Feels Like (°C)": st.column_config.NumberColumn(
                        "Feels Like", format="%.1f °C"),
                    "Pop (%)": st.column_config.ProgressColumn("Rain Prob",
                                                               format="%d%%",
                                                               min_value=0,
                                                               max_value=100),
                    "Humidity (%)": st.column_config.ProgressColumn("Humidity",
                                                                    format="%d%%",
                                                                    min_value=0,
                                                                    max_value=100),
                },
                hide_index=True,
                use_container_width=True,
                height=340
            )

            csv = df.drop(columns=["Icon"]).to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Forecast CSV",
                data=csv,
                file_name=f"{city_info['name'].lower()}_forecast_{days}d.csv",
                mime="text/csv"
            )

except ValueError:
    st.error(
        f"Could not locate weather data for **'{place}'**. Please check the spelling and try again.")
except Exception as e:
    st.error(
        f"An unexpected error occurred while communicating with the weather service: {e}")