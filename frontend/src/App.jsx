import { useState, useEffect } from 'react';
import { getConfigs, optimizeRoute } from './services/api';

function App() {
  const [config, setConfig] = useState(null);
  const [loadingConfig, setLoadingConfig] = useState(true);

  const [formData, setFormData] = useState({
    network: '',
    algorithm: '',
    startNode: '',
    endNode: ''
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch available networks and algorithms on load
    getConfigs()
      .then(data => {
        setConfig(data);
        // Set defaults if available
        if (data.networks.length > 0 && data.algorithms.length > 0) {
          setFormData(prev => ({
            ...prev,
            network: data.networks[0],
            algorithm: data.algorithms[0]
          }));
        }
      })
      .catch(err => {
        console.error("Failed to load config", err);
        setError("Failed to connect to backend server. Make sure server.py is running on port 5000.");
      })
      .finally(() => setLoadingConfig(false));
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Reset result on config change to avoid confusion
    if (e.target.name === 'network') {
      setResult(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await optimizeRoute(
        formData.network,
        formData.algorithm,
        formData.startNode,
        formData.endNode
      );

      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(typeof err === 'string' ? err : "An error occurred while communicating with the server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>🚦 Traffic Route Optimizer</h1>
        <p className="subtitle">Reinforcement Learning & Graph Search for Urban Traffic</p>
      </header>

      <div className="grid">
        {/* Configuration Panel */}
        <section>
          <div className="card">
            <h2>Configuration</h2>
            {loadingConfig ? (
              <p>Loading backend configuration...</p>
            ) : (
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="network">Network Map</label>
                  <select
                    id="network"
                    name="network"
                    value={formData.network}
                    onChange={handleChange}
                    required
                  >
                    {config?.networks.map(net => (
                      <option key={net} value={net}>{net}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="algorithm">Algorithm</label>
                  <select
                    id="algorithm"
                    name="algorithm"
                    value={formData.algorithm}
                    onChange={handleChange}
                    required
                  >
                    {config?.algorithms.map(algo => (
                      <option key={algo} value={algo}>{algo}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="startNode">Start Node ID</label>
                  <input
                    type="text"
                    id="startNode"
                    name="startNode"
                    value={formData.startNode}
                    onChange={handleChange}
                    placeholder="e.g. F or 107"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="endNode">Destination Node ID</label>
                  <input
                    type="text"
                    id="endNode"
                    name="endNode"
                    value={formData.endNode}
                    onChange={handleChange}
                    placeholder="e.g. M or 105"
                    required
                  />
                </div>

                <button type="submit" disabled={loading}>
                  {loading ? <><span className="spinner"></span> Optimization in Progress...</> : 'Find Best Route'}
                </button>
              </form>
            )}
          </div>
        </section>

        {/* Results Panel */}
        <section>
          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div className="card">
              <div className="result-header">
                <h2>Optimization Results</h2>
                <span className="badge badge-algo">{formData.algorithm}</span>
              </div>

              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Total Cost</span>
                  <span className="stat-value">{result.cost} {result.units}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Processing Time</span>
                  <span className="stat-value">{result.processing_time.toFixed(4)}s</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Total Hops</span>
                  <span className="stat-value">{result.path_nodes.length}</span>
                </div>
              </div>

              <h3>Route Path</h3>
              {result.path_nodes.length > 0 ? (
                <div className="route-list">
                  <p><strong>Path Sequence:</strong></p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {result.path_nodes.map((node, index) => (
                      <span key={index} style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{
                          background: index === 0 ? '#22c55e' : index === result.path_nodes.length - 1 ? '#ef4444' : '#e2e8f0',
                          color: index === 0 || index === result.path_nodes.length - 1 ? 'white' : 'black',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontWeight: 'bold'
                        }}>
                          {node}
                        </span>
                        {index < result.path_nodes.length - 1 && <span style={{ margin: '0 8px', color: '#94a3b8' }}>→</span>}
                      </span>
                    ))}
                  </div>
                </div>
              ) : (
                <p>No path found.</p>
              )}
            </div>
          )}

          {!result && !error && !loading && (
            <div className="card" style={{ textAlign: 'center', color: '#64748b', padding: '3rem' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🗺️</div>
              <p>Enter your trip details and click "Find Best Route" to see the results here.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;
