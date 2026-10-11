function SidePanel({ gameState }) {
  return (
    <div className="panel side-panel">
      <div className="panel-header">
        <h2>Status</h2>
      </div>

      <div className="status-block">
        <span className="status-label">Location</span>
        <p>{gameState.location}</p>
      </div>

      <div className="status-block">
        <span className="status-label">Threat Level</span>
        <p>{gameState.threatLevel} / 10</p>
      </div>

      <div className="status-block">
        <span className="status-label">Condition</span>
        <p>{gameState.condition}</p>
      </div>

      <div className="status-block">
        <span className="status-label">Inventory</span>
        <ul className="inventory-list">
          {gameState.inventory.length > 0 ? (
            gameState.inventory.map((item, index) => <li key={index}>{item}</li>)
          ) : (
            <li>Empty</li>
          )}
        </ul>
      </div>
    </div>
  );
}

export default SidePanel;