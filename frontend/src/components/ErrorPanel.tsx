import type { ApiError } from "../api/client";

const GUIDANCE: Record<string, string> = {
  INSUFFICIENT_BASELINE:
    "The 1991–2020 reference data at this location is too incomplete to set a threshold. Try a nearby point.",
  INSUFFICIENT_DATA:
    "None of the selected years has enough valid daily data. Try a different period or location.",
  UNSUPPORTED_PERIOD: "Choose years that the enabled data source covers.",
  UNSUPPORTED_REGION: "Only single points can be analyzed at the moment.",
  VALIDATION_ERROR: "Check the highlighted settings and try again.",
  RATE_LIMITED: "Too many analyses were started in a short time.",
  CAPACITY_EXCEEDED: "The service is busy with other analyses.",
  PROVIDER_ERROR: "The weather data provider returned unusable data. Your settings are kept.",
  UPSTREAM_TIMEOUT: "The weather data provider did not respond in time. Your settings are kept.",
  ANALYSIS_TIMEOUT: "The analysis took too long. A shorter period may help.",
  STORAGE_UNAVAILABLE: "The results database is temporarily unavailable.",
  NETWORK_ERROR: "Check your connection; the analysis service could not be reached.",
};

export function ErrorPanel({ error, onRetry }: { error: ApiError; onRetry: () => void }) {
  return (
    <div className="error-panel">
      <h3>Analysis could not be completed</h3>
      <p>{error.message}</p>
      {GUIDANCE[error.code] && <p className="muted">{GUIDANCE[error.code]}</p>}
      {error.details.length > 0 && (
        <ul className="error-details">
          {error.details.map((detail) => (
            <li key={`${detail.field}-${detail.message}`}>
              <code>{detail.field}</code>: {detail.message}
            </li>
          ))}
        </ul>
      )}
      {error.retryable && (
        <p className="error-actions">
          <button type="button" className="secondary-action" onClick={onRetry}>
            Try again
          </button>
          {error.retryAfterSeconds !== null && (
            <span className="muted"> Wait about {error.retryAfterSeconds} seconds first.</span>
          )}
        </p>
      )}
      {error.requestId && <p className="request-id">Reference: {error.requestId}</p>}
    </div>
  );
}
