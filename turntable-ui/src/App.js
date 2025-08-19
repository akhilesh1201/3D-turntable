import React, { useState, useEffect } from "react";
import AngleDial from "./AngleDial";

function App() {
  const [angles, setAngles] = useState({ horizontal: 0, vertical: 0 });

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://127.0.0.1:8000/status")
        .then((res) => res.json())
        .then((data) =>
          setAngles({ horizontal: data.horizontal, vertical: data.vertical })
        )
        .catch((err) => console.error(err));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        background: "black",
        gap: "50px",
      }}
    >
      <AngleDial angle={angles.horizontal} label="Horizontal" letter="H" />
      <AngleDial angle={angles.vertical} label="Vertical" letter="V" />
    </div>
  );
}

export default App;
