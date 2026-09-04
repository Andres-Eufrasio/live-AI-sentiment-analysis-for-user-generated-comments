import { useEffect, useState } from "react";
import { changeModel, getModel, getModelList } from "../api";
import "./ModelDashboard.css";


const MODELS = [
  "model-a",
  "model-b",
  "model-c",
];

function ModelDashboard() {
  const [currentModel, setCurrentModel] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [models, setModels] = useState([]);

useEffect(() => {
  async function loadModel() {
    try {
      const [modelResult, modelList] = await Promise.all([
        getModel(),
        getModelList(),
      ]);

      setCurrentModel(modelResult.model);
      setSelectedModel(modelResult.model);
      setModels(modelList);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  loadModel();
}, []);

  async function handleSwitchModel() {
    if (!selectedModel || selectedModel === currentModel) {
      return;
    }

    setSwitching(true);
    setMessage("");
    setError("");

    try {
      const result = await changeModel(selectedModel);

      setCurrentModel(result.model);
      setSelectedModel(result.model);

      setMessage(`Model successfully changed to ${result.model}.`);
    } catch (err) {
      setError(err.message);
      setSelectedModel(currentModel);
    } finally {
      setSwitching(false);
    }
  }

  if (loading) {
    return (
      <div className="model-dashboard">
        <h2>Model Dashboard</h2>
        <p>Loading model information...</p>
      </div>
    );
  }

  return (
    <div className="model-dashboard">
      {/* Header */}
      <div className="page-header">
        <h2>Model Dashboard</h2>
        <p>
          Manage and monitor the moderation models used by the system.
        </p>
      </div>

      {/* Current Model */}
      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Active Model</h3>
            <p>The model currently being used for moderation.</p>
          </div>

          <span className="model-status">
            Active
          </span>
        </div>

        <div className="active-model">
          <span className="model-name">
            {currentModel}
          </span>
        </div>
      </section>

      {/* Switch Model */}
      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Switch Model</h3>
            <p>
              Change the model used for new moderation predictions.
            </p>
          </div>
        </div>

        <div className="model-controls">
          <select
            value={selectedModel}
            onChange={(e) => {
              setSelectedModel(e.target.value);
              setMessage("");
              setError("");
            }}
            disabled={switching}
          >
            {models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>

          <button
            type="button"
            onClick={handleSwitchModel}
            disabled={
              switching ||
              !selectedModel ||
              selectedModel === currentModel
            }
          >
            {switching ? "Switching..." : "Switch Model"}
          </button>
        </div>

        {message && (
          <div className="success-message">
            {message}
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </section>

      {/* Future sections */}
      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Model Information</h3>
            <p>
              Additional model information and configuration will appear here.
            </p>
          </div>
        </div>

        <div className="model-info-grid">
          <div>
            <span className="info-label">Current model</span>
            <strong>{currentModel}</strong>
          </div>

          <div>
            <span className="info-label">Status</span>
            <strong>Active</strong>
          </div>
        </div>
      </section>
    </div>
  );
}

export default ModelDashboard;