import React from "react";

const AngleDial = ({ angle, label, letter }) => {
  const size = 200;
  const radius = size / 2;
  const pointerLength = radius - 20;
  const angleRad = ((angle - 90) * Math.PI) / 180;

  const pointerX = radius + pointerLength * Math.cos(angleRad);
  const pointerY = radius + pointerLength * Math.sin(angleRad);

  // Tick marks every 30°
  const marks = [];
  for (let i = 0; i < 360; i += 30) {
    const rad = ((i - 90) * Math.PI) / 180;
    const x1 = radius + (radius - 10) * Math.cos(rad);
    const y1 = radius + (radius - 10) * Math.sin(rad);
    const x2 = radius + (radius - 20) * Math.cos(rad);
    const y2 = radius + (radius - 20) * Math.sin(rad);
    marks.push({ x1, y1, x2, y2, value: i, rad });
  }

  return (
    <div style={{ textAlign: "center" }}>
      <svg width={size} height={size}>
        {/* Outer border circle */}
        <circle
          cx={radius}
          cy={radius}
          r={radius - 2}
          stroke="white"
          strokeWidth="4"
          fill="none"
        />

        {/* Inner filled dial */}
        <circle
          cx={radius}
          cy={radius}
          r={radius - 5}
          stroke="black"
          strokeWidth="3"
          fill="black"
        />

        {/* Tick marks */}
        {marks.map((m, i) => (
          <g key={i}>
            <line
              x1={m.x1}
              y1={m.y1}
              x2={m.x2}
              y2={m.y2}
              stroke="white"
              strokeWidth="2"
            />
            <text
              x={radius + (radius - 35) * Math.cos(m.rad)}
              y={radius + (radius - 35) * Math.sin(m.rad)}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="12"
              fill="white"
            >
              {m.value}
            </text>
          </g>
        ))}

        {/* Pointer */}
        <line
          x1={radius}
          y1={radius}
          x2={pointerX}
          y2={pointerY}
          stroke="red"
          strokeWidth="3"
          style={{ transition: "all 0.5s ease-in-out" }}
        />

        {/* Center letter */}
        <text
          x={radius}
          y={radius}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="48"
          fontWeight="bold"
          fill="red"
        >
          {letter}
        </text>
      </svg>

      <div style={{ marginTop: "10px", fontWeight: "bold", color: "white" }}>
        {label}: {angle}°
      </div>
    </div>
  );
};

export default AngleDial;