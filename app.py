from flask import Flask, render_template, request

# Import Astropy Time object and units
from astropy.time import Time
from astropy import units as u

# Import Numpy for creating the time points
import numpy as np

# Import Poliastro libraries
from poliastro.bodies import Sun
from poliastro.twobody import Orbit
from poliastro.ephem import Ephem

# Import Plotly
import plotly.graph_objects as go

app = Flask(__name__)

# ---- FINAL FIX: Use specific JPL HORIZONS IDs instead of names ----
# This dictionary maps the user-friendly name to the official ID required by the NASA API.
# This completely removes the "Ambiguous target name" error.
PLANET_IDS = {
    "Mercury": "199",
    "Venus": "299",
    "Earth": "399",
    "Mars": "499",
    "Jupiter": "599",  # Use the specific ID for the planet
    "Saturn": "699",   # Use the specific ID for the planet
    "Uranus": "799",
    "Neptune": "899",
}
# ---- END FINAL FIX ----

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Renders the main page and handles the planet selection form.
    """
    plot_div = None
    if request.method == 'POST':
        planet_name = request.form.get('planet')
        if planet_name in PLANET_IDS:
            # Get the specific ID for the selected planet
            planet_id = PLANET_IDS[planet_name]

            # Set the epoch (time of observation) to the current time
            epoch = Time.now()

            # ---- FINAL, VERIFIED ORBIT CREATION ----
            # 1. Fetch the ephemeris data from NASA using the specific, unambiguous ID.
            ephem = Ephem.from_horizons(planet_id, epochs=epoch)

            # 2. Create the Orbit object using this special Ephem object.
            orbit = Orbit.from_ephem(Sun, ephem, epoch=epoch)
            # ---- END FINAL, VERIFIED ORBIT CREATION ----

            # Create an array of time durations spanning one full orbital period.
            time_deltas = np.linspace(0 * u.s, orbit.period, 200)

            # Loop through each time duration and propagate the orbit.
            positions = []
            for dt in time_deltas:
                propagated_orbit = orbit.propagate(dt)
                positions.append(propagated_orbit.r)

            # Unpack the position vectors into separate x, y, z lists for plotting.
            x_coords = [pos[0].to(u.km).value for pos in positions]
            y_coords = [pos[1].to(u.km).value for pos in positions]
            z_coords = [pos[2].to(u.km).value for pos in positions]

            # Create a 3D plot using Plotly
            fig = go.Figure()

            # Add the trajectory of the planet
            fig.add_trace(go.Scatter3d(
                x=x_coords,
                y=y_coords,
                z=z_coords,
                mode='lines',
                name=planet_name,
                line=dict(width=4)
            ))

            # Add the Sun at the center
            fig.add_trace(go.Scatter3d(
                x=[0], y=[0], z=[0],
                mode='markers',
                marker=dict(size=10, color='yellow'),
                name='Sun'
            ))

            # Update the layout of the plot
            fig.update_layout(
                title=f"Trajectory of {planet_name} (around the current date)",
                scene=dict(
                    xaxis_title="X (km)",
                    yaxis_title="Y (km)",
                    zaxis_title="Z (km)",
                    aspectmode='data'
                ),
                margin=dict(l=0, r=0, b=0, t=40)
            )

            plot_div = fig.to_html(full_html=False)

    # Pass the keys of the ID dictionary to the template for the dropdown menu
    return render_template('index.html', plot_div=plot_div, planets=PLANET_IDS.keys())

if __name__ == '__main__':
    app.run(debug=True)