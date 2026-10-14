import { useState, type FormEvent } from "react";

const EARLIEST_YEAR = 1940;
// Guidance only: the backend applies the authoritative last-complete-year rule.
const LATEST_YEAR_HINT = new Date().getUTCFullYear() - 1;

export function DashboardPage() {
  const [notice, setNotice] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice("Analysis requests are not connected in this build yet. Nothing was calculated.");
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Climate Hazard Analyzer</h1>
        <p className="subtitle">
          Historical heatwave trends for a chosen location, calculated from reanalysis data.
        </p>
      </header>

      <main className="dashboard">
        <section className="panel" aria-labelledby="settings-heading">
          <h2 id="settings-heading">Analysis settings</h2>
          <form className="controls" onSubmit={handleSubmit} noValidate>
            <div className="field-groups">
              <fieldset>
                <legend>Location</legend>
                <div className="field">
                  <label htmlFor="label">Location name</label>
                  <input id="label" name="label" type="text" maxLength={120} autoComplete="off" required />
                </div>
                <div className="field-row">
                  <div className="field">
                    <label htmlFor="latitude">Latitude</label>
                    <input id="latitude" name="latitude" type="number" inputMode="decimal"
                      min={-90} max={90} step="any" aria-describedby="latitude-hint" required />
                    <span id="latitude-hint" className="hint">−90 to 90</span>
                  </div>
                  <div className="field">
                    <label htmlFor="longitude">Longitude</label>
                    <input id="longitude" name="longitude" type="number" inputMode="decimal"
                      min={-180} max={180} step="any" aria-describedby="longitude-hint" required />
                    <span id="longitude-hint" className="hint">−180 to 180</span>
                  </div>
                </div>
              </fieldset>

              <fieldset>
                <legend>Hazard and period</legend>
                <div className="field">
                  <label htmlFor="hazard">Hazard</label>
                  <select id="hazard" name="hazard" defaultValue="heatwave">
                    <option value="heatwave">Heatwave</option>
                  </select>
                </div>
                <div className="field-row">
                  <div className="field">
                    <label htmlFor="start_year">Start year</label>
                    <input id="start_year" name="start_year" type="number" inputMode="numeric"
                      min={EARLIEST_YEAR} max={LATEST_YEAR_HINT} step={1} aria-describedby="period-hint" required />
                  </div>
                  <div className="field">
                    <label htmlFor="end_year">End year</label>
                    <input id="end_year" name="end_year" type="number" inputMode="numeric"
                      min={EARLIEST_YEAR} max={LATEST_YEAR_HINT} step={1} aria-describedby="period-hint" required />
                  </div>
                </div>
                <span id="period-hint" className="hint">
                  Full calendar years from {EARLIEST_YEAR}, up to 50 years.
                </span>
              </fieldset>
            </div>

            <div className="actions">
              <button className="primary-action" type="submit">Analyze trends</button>
              <p className="form-notice" role="status">{notice}</p>
            </div>
          </form>
        </section>

        <section className="panel" aria-labelledby="results-heading">
          <h2 id="results-heading">Results</h2>
          <div className="empty-state">
            <p className="empty-title">No analysis yet</p>
            <p>
              Choose a location and period, then select Analyze trends. A heatwave is three or more
              consecutive days with a daily maximum temperature above that location's 1991–2020
              95th percentile.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
