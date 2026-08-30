function CommentCard({
  flag,
  moderating,
  onModerate,
}) {
  const labels = flag.prediction_labels ?? [];
  const scores = flag.prediction_scores ?? [];

  const predictions = labels.map((label, index) => ({
    label,
    score: Number(scores[index] ?? 0),
  }));

  // Use the highest prediction to determine severity
  const highestScore = Math.max(
    ...predictions.map((prediction) => prediction.score),
    0
  );

  const severity =
    highestScore >= 0.7
      ? "high"
      : highestScore >= 0.4
        ? "medium"
        : "low";

  return (
    <article className={`comment-card ${severity}`}>
      <div className="comment-top">
        <div>
          <span className={`badge ${severity}`}>
            {severity.toUpperCase()}
          </span>

          <span className="flag-label">
            FLAGGED
          </span>
        </div>
      </div>

      <div className="comment-content">
        <p>
          {flag.content ||
            flag.comment ||
            "Comment content unavailable"}
        </p>
      </div>

      <div className="metadata">
        <span>
          Comment: {flag.comment_id}
        </span>

        {flag.author_username && (
          <span>
            Author: {flag.author_username}
          </span>
        )}

        {flag.model_name && (
          <span>
            Model: {flag.model_name}
          </span>
        )}
      </div>

      <div className="predictions">
        {predictions.map(({ label, score }) => (
          <div
            className="prediction"
            key={label}
          >
            <span>
              {label}
            </span>

            <span>
              {(score * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>

      <div className="actions">
        <button
          disabled={moderating}
          onClick={() => onModerate(flag, true)}
        >
          Approve
        </button>

        <button
          disabled={moderating}
          className="remove"
          onClick={() => onModerate(flag, false)}
        >
          Remove
        </button>
      </div>
    </article>
  );
}

export default CommentCard;