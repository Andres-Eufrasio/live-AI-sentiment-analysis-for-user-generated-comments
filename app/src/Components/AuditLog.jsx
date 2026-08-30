import { useEffect, useState } from "react";

function AuditLog() {
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function fetchAuditLog() {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("http://localhost:8000/audit-log");

      if (!response.ok) {
        throw new Error("Failed to retrieve audit log");
      }

      const data = await response.json();

      setAuditLog(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAuditLog();
  }, []);

  function formatTimestamp(timestamp) {
    if (!timestamp) {
      return "—";
    }

    return new Date(timestamp).toLocaleString();
  }

  function getPrimaryScore(scores, labels) {
    if (!scores || scores.length === 0) {
      return null;
    }

    if (labels?.length) {
      const toxicIndex = labels.indexOf("toxic");

      if (toxicIndex !== -1) {
        return scores[toxicIndex];
      }
    }

    return Math.max(...scores);
  }

  function formatScore(score) {
    if (score === null || score === undefined) {
      return "—";
    }

    return `${(Number(score) * 100).toFixed(1)}%`;
  }

  function getDecisionLabel(decision) {
    if (decision === null || decision === undefined) {
      return "Pending";
    }

    return decision ? "Approved" : "Removed";
  }

  if (loading) {
    return (
      <div className="audit-page">
        <div className="audit-header">
          <div>
            <h1>Audit Log</h1>
            <p>Complete history of flagged comments and moderation actions.</p>
          </div>
        </div>

        <div className="audit-empty">
          Loading audit log...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="audit-page">
        <div className="audit-header">
          <div>
            <h1>Audit Log</h1>
            <p>Complete history of flagged comments and moderation actions.</p>
          </div>
        </div>

        <div className="audit-error">
          {error}

          <button onClick={fetchAuditLog}>
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="audit-page">
      <div className="audit-header">
        <div>
          <h1>Audit Log</h1>
          <p>
            Complete history of flagged comments and moderation actions.
          </p>
        </div>

        <button
          className="audit-refresh"
          onClick={fetchAuditLog}
        >
          Refresh
        </button>
      </div>

      {auditLog.length === 0 ? (
        <div className="audit-empty">
          No flagged comments have been recorded yet.
        </div>
      ) : (
        <div className="audit-table-container">
          <table className="audit-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Comment</th>
                <th>Author</th>
                <th>Score</th>
                <th>Model</th>
                <th>Moderator</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {auditLog.map((entry) => {
                const score = getPrimaryScore(
                  entry.prediction_scores
                );

                return (
                  <tr key={entry.flag_id}>
                    <td>
                      <span className="audit-time">
                        {formatTimestamp(
                          entry.moderation_timestamp ||
                          entry.comment_timestamp
                        )}
                      </span>
                    </td>

                    <td>
                      <div className="audit-comment">
                        {entry.comment_content}
                      </div>
                    </td>

                    <td>
                      {entry.author_username || "Unknown"}
                    </td>

                    <td>
                      <span className="audit-score">
                        {formatScore(score)}
                      </span>
                    </td>

                    <td>
                      <span className="audit-model">
                        {entry.model_name || "—"}
                      </span>
                    </td>

                    <td>
                      {entry.moderator_username || "—"}
                    </td>

                    <td>
                      <span
                        className={`audit-action ${
                          entry.decision === true
                            ? "approved"
                            : entry.decision === false
                              ? "removed"
                              : "pending"
                        }`}
                      >
                        {getDecisionLabel(entry.decision)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AuditLog;

