from flask import Flask, render_template, request

# Import Astropy Time object and units
from astropy.time import Time
from astropy import units as u

# Import Numpy for creating the time points
import numpy as np

# Import Poliastro libraries
from poliastro.bodies import Sun, Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune
from poliastro.twobody import Orbit

# Import Plotly
import plotly.graph_objects as go

app = Flask(__name__)

PLANETS = {
    "Mercury": Mercury,
    "Venus": Venus,
    "Earth": Earth,
    "Mars": Mars,
    "Jupiter": Jupiter,
    "Saturn": Saturn,
    "Uranus": Uranus,
    "Neptune": Neptune,
}

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Renders the main page and handles the planet selection form.
    """
    plot_div = None
    if request.method == 'POST':
        planet_name = request.form.get('planet')
        if planet_name in PLANETS:
            # Get the planet object from poliastro
            planet = PLANETS[planet_name]

            # Set the epoch (time of observation) to the current time
            epoch = Time.now()

            # Create an Orbit object for the planet from its ephemeris data
            orbit = Orbit.from_body_ephem(planet, epoch)

            # ---- FINAL CORRECTED SECTION ----
            # The 'propagate' method takes a time DURATION (a Quantity).
            # To get a full trajectory, we must propagate the orbit over many small time steps.

            # 1. Create an array of time durations spanning one full orbital period.
            #    We use numpy's linspace to create 200 points for a smooth curve.
            time_deltas = np.linspace(0 * u.s, orbit.period, 200)

            # 2. Loop through each time duration, call propagate() for that duration,
            #    and store the resulting position vector (.r) of the new orbit.
            positions = []
            for dt in time_deltas:
                propagated_orbit = orbit.propagate(dt)
                positions.append(propagated_orbit.r)  # .r is the position vector [x, y, z]

            # 3. Unpack the list of position vectors into separate x, y, z lists for plotting.
            #    The .value strips the units (e.g., km) to get raw numbers for Plotly.
            x_coords = [pos[0].to(u.km).value for pos in positions]
            y_coords = [pos[1].to(u.km).value for pos in positions]
            z_coords = [pos[2].to(u.km).value for pos in positions]
            # ---- END FINAL CORRECTED SECTION ----

            # Create a 3D plot using Plotly
            fig = go.Figure()

            # Add the trajectory of the planet
            fig.add_trace(go.Scatter3d(
                x=x_coords,
                y=y_coords,
                z=z_coords,
                mode='lines',
                name=planet.name,
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
                title=f"Trajectory of {planet.name} (around the current date)",
                scene=dict(
                    xaxis_title="X (km)",
                    yaxis_title="Y (km)",
                    zaxis_title="Z (km)",
                    aspectmode='data'
                ),
                margin=dict(l=0, r=0, b=0, t=40)
            )

            plot_div = fig.to_html(full_html=False)

    return render_template('index.html', plot_div=plot_div, planets=PLANETS.keys())

if __name__ == '__main__':
    app.run(debug=True)