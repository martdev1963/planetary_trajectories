# planetary_trajectories

This project creates a web application using Flask that visualizes the orbital trajectory of selected planets around the Sun. It leverages the Astropy and Poliastro libraries for astronomical calculations and Plotly for interactive 3D plotting.

@app.route('/', methods=['GET', 'POST'])
def index():
"""
Renders the main web page, processes user selections, and generates planet trajectory plots.

    This function handles both GET requests (initial page load) and POST requests
    (when a user selects a planet from the dropdown menu).

    For POST requests:
    1. Retrieves the selected planet's name from the form.
    2. Uses the `PLANET_IDS` dictionary to get the corresponding JPL HORIZONS ID.
    3. Sets the `epoch` (the reference time for the orbit calculation) to the current time.
    4. Fetches ephemeris data for the selected planet from NASA's HORIZONS system using `Ephem.from_horizons`.
       This is a critical step that obtains the precise orbital state vectors.
    5. Creates an `Orbit` object centered around the `Sun` using the fetched ephemeris data.
    6. Generates an array of time points spanning one full orbital period of the selected planet.
    7. Propagates the orbit for each time point to get a series of position vectors (x, y, z).
    8. Extracts the x, y, and z coordinates from the propagated positions and converts them to kilometers.
    9. Creates a 3D scatter plot using Plotly:
        - Adds the planet's trajectory as lines.
        - Adds a marker for the Sun at the origin (0,0,0).
    10. Configures the plot layout with titles and axis labels.
    11. Converts the Plotly figure into an HTML `div` that can be embedded directly into the web page.

    For GET requests or after processing a POST request:
    - Passes the generated plot HTML (or `None` if no planet was selected yet) and the list of
      available planet names to the `index.html` template.


            # Convert the Plotly figure to an HTML div string.
            # `full_html=False` ensures only the div containing the plot is returned,
            # not a complete HTML document, making it suitable for embedding.
            plot_div = fig.to_html(full_html=False)

    # Render the index.html template.
    # `plot_div`: Contains the generated Plotly graph HTML or None.
    # `planets`: A list of planet names (keys from PLANET_IDS) to populate the dropdown menu.
    return render_template('index.html', plot_div=plot_div, planets=PLANET_IDS.keys())
