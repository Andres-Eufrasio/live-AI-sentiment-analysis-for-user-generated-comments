function Settings({ theme, setTheme }) {
  const isMocha = theme === "mocha";

  function handleThemeChange(event) {
    setTheme(event.target.checked ? "mocha" : "cappuccino");
  }

  return (
    <div className="settings-page">
      <div className="settings-header">
        <div>
          <h2>Settings</h2>
          <p>Customize your moderator tools.</p>
        </div>
      </div>

      <section className="settings-section">
        <div className="settings-section-header">
          <h3>Appearance</h3>
          <p>Choose the color theme for the moderation dashboard.</p>
        </div>

        <div className="setting-row">
          <div className="setting-info">
            <div className="setting-icon">
              {isMocha ? "🍫" : "☕"}
            </div>

            <div>
              <strong>Mocha theme</strong>
              <span>
                {isMocha
                  ? "Using the darker mocha theme."
                  : "Using the light cappuccino theme."}
              </span>
            </div>
          </div>

          <label className="switch">
            <input
              type="checkbox"
              checked={isMocha}
              onChange={handleThemeChange}
            />

            <span className="slider" />
          </label>
        </div>
      </section>

    </div>
  );
}

export default Settings;

