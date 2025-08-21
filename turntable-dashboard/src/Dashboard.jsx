import React, { useState, useEffect } from "react";
import axios from "axios";
import AngleDial from "./AngleDial";
import "./Dashboard.css";
import CandelaLogo from "./candelalogo.png"; // ✅ import your PNG

const Dashboard = () => {
  const [rotateH, setRotateH] = useState(0);
  const [angleH, setAngleH] = useState(0);
  const [directionH, setDirectionH] = useState("cw");

  const [rotateV, setRotateV] = useState(0);
  const [angleV, setAngleV] = useState(0);
  const [directionV, setDirectionV] = useState("cw");

  const [currentAngles, setCurrentAngles] = useState({
    horizontal: 0,
    vertical: 0,
  });

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await axios.get("http://192.168.1.110:8000/status");
        setCurrentAngles(res.data);
      } catch (err) {
        console.error("Error fetching status:", err);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleSet = async () => {
    try {
      if (rotateH > 0) {
        await axios.get("http://192.168.1.110:8000/rotate", {
          params: { motor: "horizontal", angle: rotateH, direction: directionH },
        });
      } else if (angleH > 0) {
        await axios.get("http://192.168.1.110:8000/set_angle", {
          params: { motor: "horizontal", target_angle: angleH },
        });
      }

      if (rotateV > 0) {
        await axios.get("http://192.168.1.110:8000/rotate", {
          params: { motor: "vertical", angle: rotateV, direction: directionV },
        });
      } else if (angleV > 0) {
        await axios.get("http://192.168.1.110:8000/set_angle", {
          params: { motor: "vertical", target_angle: angleV },
        });
      }
    } catch (err) {
      console.error("Error setting motor:", err);
    }
  };

  return (
    <div
      style={{
        background: "black",
        color: "white",
        minHeight: "100vh",
        padding: "20px",
        position: "relative", // ✅ Needed for absolute positioning
      }}
    >
      {/* Logo in top-right */}
      <img
        src={CandelaLogo}
        alt="Candela Logo"
        style={{
          position: "absolute",
          top: "10px",
          right: "20px",
          width: "120px",
          height: "auto",
        }}
      />

      <h2
        style={{
          textAlign: "center",
          marginBottom: "10px",
          fontSize: "xxx-large",
          marginTop: "5px",
          fontFamily: "serif",
        }}
      >
        3D Turntable Dashboard
      </h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
        }}
      >
        {/* Horizontal Container */}
        <div
          style={{
            background: "#111",
            padding: "20px",
            borderRadius: "12px",
            boxShadow: "0 0 10px rgba(255,255,255,0.2)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "20px",
          }}
        >
          <h3>Horizontal Control</h3>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "15px",
              width: "100%",
            }}
          >
            <label>
              Rotate by (°):
              <input
                type="number"
                value={rotateH}
                onChange={(e) => setRotateH(Number(e.target.value))}
                style={{ marginLeft: "10px" }}
              />
            </label>
            <label>
              Set Angle (°):
              <input
                type="number"
                value={angleH}
                onChange={(e) => setAngleH(Number(e.target.value))}
                style={{ marginLeft: "10px" }}
              />
            </label>
            <label>
              Direction:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              <select
                value={directionH}
                onChange={(e) => setDirectionH(e.target.value)}
                style={{ marginLeft: "10px" }}
              >
                <option value="cw">Clockwise</option>
                <option value="ccw">Counter-Clockwise</option>
              </select>
            </label>
          </div>
          <AngleDial angle={currentAngles.horizontal} label="H" size={220} />
        </div>

        {/* Vertical Container */}
        <div
          style={{
            background: "#111",
            padding: "20px",
            borderRadius: "12px",
            boxShadow: "0 0 10px rgba(255,255,255,0.2)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "20px",
          }}
        >
          <h3>Vertical Control</h3>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "15px",
              width: "100%",
            }}
          >
            <label>
              Rotate by (°):
              <input
                type="number"
                value={rotateV}
                onChange={(e) => setRotateV(Number(e.target.value))}
                style={{ marginLeft: "10px" }}
              />
            </label>
            <label>
              Set Angle (°):
              <input
                type="number"
                value={angleV}
                onChange={(e) => setAngleV(Number(e.target.value))}
                style={{ marginLeft: "10px" }}
              />
            </label>
            <label>
              Direction:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              <select
                value={directionV}
                onChange={(e) => setDirectionV(e.target.value)}
                style={{ marginLeft: "10px" }}
              >
                <option value="cw">Clockwise</option>
                <option value="ccw">Counter-Clockwise</option>
              </select>
            </label>
          </div>
          <AngleDial angle={currentAngles.vertical} label="V" size={220} />
        </div>
      </div>

      <div style={{ textAlign: "center", marginTop: "30px" }}>
        <button
          onClick={handleSet}
          style={{
            padding: "12px 40px",
            fontSize: "16px",
            borderRadius: "8px",
            border: "none",
            cursor: "pointer",
          }}
        >
          Apply Movement
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
