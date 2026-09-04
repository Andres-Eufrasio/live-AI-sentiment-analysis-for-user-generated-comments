import ModerationEventService from "./services/ModerationEventService";
import ModelDashboard from "./Components/ModelDashboard.jsx";

const API_URL = "http://host.docker.internal:8000";

export async function getFlags() {
  const response = await fetch(`${API_URL}/flags`);

  if (!response.ok) {
    const errorText = await response.text();

    console.error("GET /flags failed:", {
      status: response.status,
      statusText: response.statusText,
      body: errorText,
    });

    throw new Error(
      `Failed to retrieve flags (${response.status}): ${errorText}`
    );
  }

  return response.json();
}

export async function moderateComment({
  commentId,
  moderatorId,
  flagId,
  predictionId,
  decision,
}) {
  const response = await fetch(`${API_URL}/moderate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      comment_id: commentId,
      moderator_id: moderatorId,
      flag_id: flagId,
      prediction_id: predictionId ?? null,
      decision,
    }),
  });

  if (!response.ok) {
    const error = await response.json();

    console.error("POST /moderate failed:", error);

    if (Array.isArray(error.detail)) {
      const messages = error.detail
        .map((item) => {
          const location = item.loc?.join(".") ?? "unknown";
          return `${location}: ${item.msg}`;
        })
        .join("\n");

      throw new Error(messages);
    }

    throw new Error(
      error.detail || `Moderation failed (${response.status})`
    );
  }

  return response.json();
}

export async function fetchAuditLog() {
  const response = await fetch(`${API_URL}/audit-log`);

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Failed to retrieve audit log (${response.status}): ${errorText}`
    );
  }

  return response.json();
}




export async function changeModel(modelName) {
  const response = await fetch(`${API_URL}/model`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model_name: modelName,
    }),
  });

  if (!response.ok) {
    let error;

    try {
      error = await response.json();
    } catch {
      error = {};
    }

    console.error("POST /model failed:", error);

    throw new Error(
      error.detail ||
        error.error ||
        `Model change failed (${response.status})`
    );
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.error || "Model failed to load");
  }

  return result;
}



export async function getModel() {
  const response = await fetch(`${API_URL}/model`);

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Failed to retrieve model (${response.status}): ${errorText}`
    );
  }

  return response.json();
}

export async function getModelList() {
  const response = await fetch("/model/list");

  if (!response.ok) {
    throw new Error("Failed to fetch model list");
  }

  return response.json();
}