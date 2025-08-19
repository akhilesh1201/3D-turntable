import React, { useEffect, useState } from "react";

const ProtractorGauge = ({ label, angle }) => {
  const radius = 80; // circle size
  const circumference = 2 * Math.PI * radius;

  // Convert angle (0–360) to stroke offset
  const offset = circumference - (angle / 360) * circumference;

  return (
    <div className="flex flex-col items-center m-4">
      <svg
        width={200}
        height={200}
        viewBox="0 0 200 200"
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          stroke="#e5e7eb"
          strokeWidth="12"
          fill="transparent"
        />

        {/* Progress (current angle) */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          stroke="#3b82f6"
          strokeWidth="12"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.5s ease" }}
        />

        {/* Needle/Marker */}
        <line
          x1="100"
          y1="100"
          x2={100 + radius * Math.cos((angle - 90) * (Math.PI / 180))}
          y2={100 + radius * Math.sin((angle - 90) * (Math.PI / 180))}
          stroke="#ef4444"
          strokeWidth="4"
        />
      </svg>

      {/* Label + Angle Value */}
      <p className="mt-2 text-lg font-semibold">{label}: {angle}°</p>
    </div>
  );
};

export default function TurntableUI() {
  const [horizontal, setHorizontal] = useState(0);
  const [vertical, setVertical] = useState(0);

  // Poll backend for angles
  useEffect(() => {
    const fetchAngles = async () => {
      try {
        const res = await fetch("http://<RASPBERRY-PI-IP>:8000/status");
        const data = await res.json();
        setHorizontal(data.horizontal_angle);
        setVertical(data.vertical_angle);
      } catch (err) {
        console.error("Error fetching angles:", err);
      }
    };

    fetchAngles();
    const interval = setInterval(fetchAngles, 1000); // refresh every second
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <div className="flex">
        <ProtractorGauge label="Horizontal" angle={horizontal} />
        <ProtractorGauge label="Vertical" angle={vertical} />
      </div>
    </div>
  );
}
