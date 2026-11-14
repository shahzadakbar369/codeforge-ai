
import { useRef, useState } from "react";
import "./App.css";

function App() {
  const fileInputRef = useRef(null);
  const [phpCode, setPhpCode] = useState("");
  const [pythonCode, setPythonCode] = useState("");
  const [fileStatus, setFileStatus] = useState("No file selected.");
  const [securityReport, setSecurityReport] = useState(
    "Security scan is not connected yet."
  );

  function showFile() {
    const file = fileInputRef.current?.files?.[0];

    if (!file) {
      setFileStatus("Please select a PHP file.");
      return;
    }

    setFileStatus(`Selected: ${file.name}`);

    const reader = new FileReader();

    reader.onload = (event) => {
      setPhpCode(String(event.target?.result ?? ""));
    };

    reader.onerror = () => {
      setFileStatus("Could not read this file.");
    };

    reader.readAsText(file);
  }

  function convertCode() {
    setPythonCode("");
    setSecurityReport(
      "Real conversion is not connected yet. No Python code was generated."
    );
  }

  function scanSecurity() {
    setSecurityReport(
      "Security scanning is not connected yet. No real scan has been performed."
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">⚡ CodeForge AI</div>

        <nav className="nav">
          <a href="#dashboard">Dashboard</a>
          <a href="#migration">Migration</a>
          <a href="#security">Security</a>
        </nav>
      </header>

      <main className="main" id="dashboard">
        <h1>Code Migration Workspace</h1>
        <p className="subtitle">
          Convert legacy PHP code into modern Python
        </p>

        <div className="steps">
          <span>1. Upload Code</span>
          <span>2. Convert</span>
          <span>3. Security Scan</span>
          <span>4. Compare Results</span>
        </div>

        <section className="upload-section">
          <label htmlFor="phpFile">
            Choose your legacy PHP file
          </label>

          <input
            ref={fileInputRef}
            id="phpFile"
            type="file"
            accept=".php"
            onChange={showFile}
          />

          <p className="file-status">{fileStatus}</p>
        </section>

        <section className="workspace" id="migration">
          <div className="panel">
            <h2>Legacy PHP</h2>
            <textarea
              value={phpCode}
              onChange={(event) => setPhpCode(event.target.value)}
              placeholder="Select a PHP file to view its code..."
              spellCheck={false}
            />
          </div>

          <div className="panel">
            <h2>Generated Python</h2>
            <textarea
              value={pythonCode}
              onChange={(event) => setPythonCode(event.target.value)}
              placeholder="Python output will appear here after backend integration..."
              spellCheck={false}
            />
          </div>
        </section>

        <div className="actions">
          <button onClick={convertCode}>Convert Code</button>
        </div>

        <section className="security-section" id="security">
          <h2>Security Report</h2>
          <p>{securityReport}</p>
          <button onClick={scanSecurity}>Scan Security</button>
        </section>
      </main>
    </div>
  );
}

export default App;
