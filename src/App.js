import React, { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const FIREBASE_URL = "https://smart-resources-kelompok20-default-rtdb.asia-southeast1.firebasedatabase.app";

function detectAnomaly(data, key) {
  if (data.length < 5) return [];
  const values = data.map(d => d[key]);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const std = Math.sqrt(values.map(v => Math.pow(v - mean, 2)).reduce((a, b) => a + b, 0) / values.length);
  return data.filter(d => Math.abs(d[key] - mean) > 2 * std);
}

function predictNext7(data, key) {
  if (data.length < 5) return [];
  const n = data.length;
  const xMean = (n - 1) / 2;
  const yMean = data.reduce((a, b) => a + b[key], 0) / n;
  let num = 0, den = 0;
  data.forEach((d, i) => { num += (i - xMean) * (d[key] - yMean); den += Math.pow(i - xMean, 2); });
  const slope = den !== 0 ? num / den : 0;
  const intercept = yMean - slope * xMean;
  return Array.from({ length: 7 }, (_, i) => ({
    hari: `Hari ke-${i + 1}`,
    nilai: Math.round((slope * (n + i) + intercept) * 1000) / 1000
  }));
}

function App() {
  const [dataListrik, setDataListrik] = useState([]);
  const [dataAir, setDataAir] = useState([]);
  const [anomaliListrik, setAnomaliListrik] = useState([]);
  const [anomaliAir, setAnomaliAir] = useState([]);
  const [prediksiListrik, setPrediksiListrik] = useState([]);
  const [prediksiAir, setPrediksiAir] = useState([]);

  const fetchData = async () => {
    try {
      const resListrik = await fetch(`${FIREBASE_URL}/listrik.json`);
      const resAir = await fetch(`${FIREBASE_URL}/air.json`);
      const listrik = await resListrik.json();
      const air = await resAir.json();

      if (listrik) {
        const arr = Object.values(listrik).slice(-20).map(d => ({ time: d.timestamp.slice(11, 19), kwh: d.kwh }));
        setDataListrik(arr);
        setAnomaliListrik(detectAnomaly(arr, "kwh"));
        setPrediksiListrik(predictNext7(arr, "kwh"));
      }
      if (air) {
        const arr = Object.values(air).slice(-20).map(d => ({ time: d.timestamp.slice(11, 19), liter: d.liter }));
        setDataAir(arr);
        setAnomaliAir(detectAnomaly(arr, "liter"));
        setPrediksiAir(predictNext7(arr, "liter"));
      }
    } catch (err) { console.error(err); }
  };

  useEffect(() => { fetchData(); const i = setInterval(fetchData, 5000); return () => clearInterval(i); }, []);

  const cardStyle = { background: "#1a1a1a", border: "1px solid #333", borderRadius: "12px", padding: "1.5rem", marginBottom: "1.5rem" };

  return (
    <div style={{ background: "#111", minHeight: "100vh", color: "#fff", padding: "2rem", fontFamily: "sans-serif" }}>
      <h1 style={{ color: "#FFD700", textAlign: "center", marginBottom: "0.5rem" }}>Smart Resources Usage Analysis</h1>
      <p style={{ textAlign: "center", color: "#aaa", marginBottom: "2rem" }}>Kelompok 20 — Monitoring Listrik & Air Real-Time</p>

      {/* Stats */}
      <div style={{ display: "flex", gap: "1rem", justifyContent: "center", marginBottom: "2rem", flexWrap: "wrap" }}>
        <div style={{ ...cardStyle, textAlign: "center", padding: "1rem 2rem" }}>
          <div style={{ color: "#aaa", fontSize: "13px" }}>Listrik Terakhir</div>
          <div style={{ color: "#FFD700", fontSize: "28px", fontWeight: "bold" }}>{dataListrik.length > 0 ? dataListrik[dataListrik.length - 1].kwh : "-"} kWh</div>
        </div>
        <div style={{ ...cardStyle, textAlign: "center", padding: "1rem 2rem" }}>
          <div style={{ color: "#aaa", fontSize: "13px" }}>Air Terakhir</div>
          <div style={{ color: "#00BFFF", fontSize: "28px", fontWeight: "bold" }}>{dataAir.length > 0 ? dataAir[dataAir.length - 1].liter : "-"} L/min</div>
        </div>
        <div style={{ ...cardStyle, textAlign: "center", padding: "1rem 2rem" }}>
          <div style={{ color: "#aaa", fontSize: "13px" }}>Anomali Listrik</div>
          <div style={{ color: anomaliListrik.length > 0 ? "#FF4444" : "#00FF88", fontSize: "28px", fontWeight: "bold" }}>{anomaliListrik.length > 0 ? `${anomaliListrik.length} ⚠️` : "Normal ✅"}</div>
        </div>
        <div style={{ ...cardStyle, textAlign: "center", padding: "1rem 2rem" }}>
          <div style={{ color: "#aaa", fontSize: "13px" }}>Anomali Air</div>
          <div style={{ color: anomaliAir.length > 0 ? "#FF4444" : "#00FF88", fontSize: "28px", fontWeight: "bold" }}>{anomaliAir.length > 0 ? `${anomaliAir.length} ⚠️` : "Normal ✅"}</div>
        </div>
      </div>

      {/* Grafik Listrik */}
      <div style={cardStyle}>
        <h2 style={{ color: "#FFD700", marginBottom: "1rem" }}>Pemakaian Listrik (kWh)</h2>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={dataListrik}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="time" stroke="#aaa" tick={{ fontSize: 11 }} />
            <YAxis stroke="#aaa" tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#222", border: "1px solid #444", color: "#fff" }} />
            <Legend />
            <Line type="monotone" dataKey="kwh" stroke="#FFD700" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Grafik Air */}
      <div style={cardStyle}>
        <h2 style={{ color: "#00BFFF", marginBottom: "1rem" }}>Pemakaian Air (L/min)</h2>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={dataAir}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="time" stroke="#aaa" tick={{ fontSize: 11 }} />
            <YAxis stroke="#aaa" tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#222", border: "1px solid #444", color: "#fff" }} />
            <Legend />
            <Line type="monotone" dataKey="liter" stroke="#00BFFF" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Prediksi */}
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <div style={{ ...cardStyle, flex: 1, minWidth: "300px" }}>
          <h2 style={{ color: "#FFD700", marginBottom: "1rem" }}>Prediksi Listrik 7 Hari</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={prediksiListrik}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="hari" stroke="#aaa" tick={{ fontSize: 10 }} />
              <YAxis stroke="#aaa" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#222", border: "1px solid #444", color: "#fff" }} />
              <Line type="monotone" dataKey="nilai" stroke="#FFD700" strokeWidth={2} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div style={{ ...cardStyle, flex: 1, minWidth: "300px" }}>
          <h2 style={{ color: "#00BFFF", marginBottom: "1rem" }}>Prediksi Air 7 Hari</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={prediksiAir}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="hari" stroke="#aaa" tick={{ fontSize: 10 }} />
              <YAxis stroke="#aaa" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#222", border: "1px solid #444", color: "#fff" }} />
              <Line type="monotone" dataKey="nilai" stroke="#00BFFF" strokeWidth={2} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default App;