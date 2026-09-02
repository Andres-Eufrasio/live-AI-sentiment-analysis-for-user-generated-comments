import { useEffect, useState } from "react";

import { fetchAuditLog } from "../api.jsx";

function AuditLog() {
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all");

async function loadAuditLog() {
  try {
    setError(null);

    const data = await fetchAuditLog();

    // check for previous data
    setAuditLog((previous) => {
      if (JSON.stringify(previous) === JSON.stringify(data)) {
        return previous;
      }

      return data;
    });
  } catch (err) {
    setError(err.message || "Failed to retrieve audit log");
  } finally {
    setLoading(false);
  }
}

useEffect(() => {
  loadAuditLog();

  const interval = setInterval(() => {
    loadAuditLog();
  }, 5000);

  return () => clearInterval(interval);
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

    return `${Number(score * 100).toFixed(1)}%`;
  }

  function getDecisionLabel(decision) {
    if (decision === null || decision === undefined) {
      return "Pending";
    }

    return decision ? "Approved" : "Removed";
  }

  function getEventLabel(type) {
    switch (type) {
      case "comment":
        return "Comment";
      case "moderation":
        return "Moderator Decision";
      default:
        return "Other";
    }
  }

  const filteredAuditLog = auditLog.filter((entry) => {
    if (filter === "all") {
      return true;
    }

    if (filter === "other") {
      return (
        entry.type !== "comment" &&
        entry.type !== "moderation"
      );
    }

    return entry.type === filter;
  });

  // Only show the loading screen when we have no data yet.
  if (loading && auditLog.length === 0) {
    return (
      <div className="audit-page">
        <div className="audit-header">
          <div>
            <h1>Audit Log</h1>
            <p>
              Complete history of system activity and moderation actions.
            </p>
          </div>
        </div>

        <div className="audit-empty">
          Loading audit log...
        </div>
      </div>
    );
  }

  // Only show the full error screen if we have no existing data.
  if (error && auditLog.length === 0) {
    return (
      <div className="audit-page">
        <div className="audit-header">
          <div>
            <h1>Audit Log</h1>
            <p>
              Complete history of system activity and moderation actions.
            </p>
          </div>
        </div>

        <div className="audit-error">
          <span>{error}</span>
          <button onClick={loadAuditLog}>
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
            Complete history of system activity and moderation actions.
          </p>
        </div>

        {/* Optional: show refresh status without replacing the table */}
        {loading && (
          <span className="audit-refreshing">
            Refreshing...
          </span>
        )}

        {error && auditLog.length > 0 && (
          <span className="audit-refresh-error">
            Refresh failed
          </span>
        )}
      </div>

      <div className="audit-filters">
        <button
          className={filter === "all" ? "active" : ""}
          onClick={() => setFilter("all")}
        >
          All
        </button>

        <button
          className={filter === "comment" ? "active" : ""}
          onClick={() => setFilter("comment")}
        >
          Comments
        </button>

        <button
          className={filter === "moderation" ? "active" : ""}
          onClick={() => setFilter("moderation")}
        >
          Moderator Decisions
        </button>

        <button
          className={filter === "other" ? "active" : ""}
          onClick={() => setFilter("other")}
        >
          Other
        </button>
      </div>

      {filteredAuditLog.length === 0 ? (
        <div className="audit-empty">
          No audit events found.
        </div>
      ) : (
        <div className="audit-table-container">
          <table className="audit-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event</th>
                <th>Comment</th>
                <th>Author</th>
                <th>Score</th>
                <th>Model</th>
                <th>Moderator</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {filteredAuditLog.map((entry, index) => {
                const score = getPrimaryScore(
                  entry.prediction_scores,
                  entry.prediction_labels
                );

                const timestamp =
                  entry.type === "moderation"
                    ? entry.moderation_timestamp
                    : entry.comment_timestamp;

                const rowKey =
                  entry.type === "moderation"
                    ? `moderation-${entry.moderation_decision_id}`
                    : entry.type === "comment"
                      ? `comment-${entry.flag_id}`
                      : `other-${entry.id || index}`;

                return (
                  <tr key={rowKey}>
                    <td>
                      <span className="audit-time">
                        {formatTimestamp(timestamp)}
                      </span>
                    </td>

                    <td>
                      <span
                        className={`audit-event audit-event-${entry.type}`}
                      >
                        {getEventLabel(entry.type)}
                      </span>
                    </td>

                    <td>
                      <div className="audit-comment">
                        {entry.comment_content || "—"}
                      </div>
                    </td>

                    <td>
                      {entry.author_username || "Unknown"}
                    </td>

                    <td>
                      {entry.type === "comment" ? (
                        <span className="audit-score">
                          {formatScore(score)}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>

                    <td>
                      {entry.type === "comment" ? (
                        <span className="audit-model">
                          {entry.model_name || "—"}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>

                    <td>
                      {entry.type === "moderation"
                        ? entry.moderator_username || "Unknown"
                        : "—"}
                    </td>

                    <td>
                      {entry.type === "moderation" ? (
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
                      ) : (
                        "—"
                      )}
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

