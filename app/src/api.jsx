
import { useEffect, useState } from "react";

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
    throw new Error(error.detail || "Moderation failed");
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


