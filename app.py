from flask import Flask, render_template
import database

app = Flask(__name__)

@app.route('/')
def index():
    """Main page to display the options data."""
    raw_data = database.get_latest_data()

    # Process data into a more usable format for the template
    # {strike: {'CE': volume, 'PE': volume}}
    pivoted_data = {}
    for strike, opt_type, volume in raw_data:
        if strike not in pivoted_data:
            pivoted_data[strike] = {}
        pivoted_data[strike][opt_type] = volume

    # Get a sorted list of strikes for table headers
    strikes = sorted(pivoted_data.keys())

    # The user requested "strikes in the column and volume on the rows"
    # I will create rows for CE and PE volumes, with strikes as columns.

    ce_volumes = [pivoted_data.get(s, {}).get('CE', 0) for s in strikes]
    pe_volumes = [pivoted_data.get(s, {}).get('PE', 0) for s in strikes]

    return render_template(
        'index.html',
        strikes=strikes,
        ce_volumes=ce_volumes,
        pe_volumes=pe_volumes
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
