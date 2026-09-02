
import { useMemo, useState, useEffect } from "react";
import { useFlags } from "./useFlags.jsx";
import { moderateComment } from "../api.jsx";
import Stat from "./Stat.jsx";
import CommentCard from "./CommentCard.jsx";

function ModerationDashboard() {
  const {
    flags,
    loading,
    error,
    lastUpdated,
    refreshFlags,
  } = useFlags();

  const [filter, setFilter] = useState("all");
  const [moderating, setModerating] = useState(null);
  const [reviewedCount, setReviewedCount] = useState(0);

  
  useEffect(() => {
    const interval = setInterval(() => {
      refreshFlags();
    }, 1000);

    
    return () => clearInterval(interval);
  }, [refreshFlags]);

  const filteredFlags = useMemo(() => {
    if (filter === "all") {
      return flags;
    }

    return flags.filter((flag) => {
      if (filter === "flagged") {
        return true;
      }

      if (filter === "high") {
        return Number(flag.prediction_score ?? 0) >= 0.7;
      }

      return true;
    });
  }, [flags, filter]);

  async function handleModeration(flag, decision) {
    try {
      setModerating(flag.id);

      await moderateComment({
        commentId: flag.comment_id,
        moderatorId: "8410a16f-032d-4ebf-a128-c0bfbb4e7df4",
        flagId: flag.id,
        predictionId: flag.prediction_id,
        decision,
      });

      // No manual refresh needed.
      // The automatic 1-second refresh will update the list.
    } catch (err) {
      alert(err.message);
    } finally {
      setModerating(null);
      setReviewedCount((count) => count + 1);
    }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Moderation Dashboard</h1>
          <p>Live incoming comment monitoring</p>
        </div>

        <div className={`connection ${error ? "offline" : "online"}`}>
          <span className="status-dot" />
          {error ? "Offline" : "Live"}
        </div>
      </header>

      <section className="stats">
        <Stat
          title="Unreviewed"
          value={flags.length}
        />

        <Stat
          title="High Risk"
          value={
            flags.filter(
              (flag) =>
                Number(flag.prediction_score ?? 0) >= 0.7
            ).length
          }
        />

        <Stat
          title="Reviewed This Session"
          value={reviewedCount}
        />
      </section>

      <section className="toolbar">
        <div className="filters">
          <button
            className={filter === "all" ? "active" : ""}
            onClick={() => setFilter("all")}
          >
            All
          </button>

          <button
            className={filter === "flagged" ? "active" : ""}
            onClick={() => setFilter("flagged")}
          >
            Flagged
          </button>

          <button
            className={filter === "high" ? "active" : ""}
            onClick={() => setFilter("high")}
          >
            High Risk
          </button>
        </div>
      </section>

      {error && (
        <div className="error">
          Backend connection error: {error}
        </div>
      )}

      {loading ? (
        <div className="empty">
          Loading comments...
        </div>
      ) : filteredFlags.length === 0 ? (
        <div className="empty">
          No unreviewed flags
        </div>
      ) : (
        <main className="comments">
          {filteredFlags.map((flag) => (
            <CommentCard
              key={flag.id}
              flag={flag}
              moderating={moderating === flag.id}
              onModerate={handleModeration}
            />
          ))}
        </main>
      )}
    </div>
  );
}

export default ModerationDashboard;

