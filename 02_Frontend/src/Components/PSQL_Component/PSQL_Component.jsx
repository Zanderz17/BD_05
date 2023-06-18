import React, { useEffect, useState } from "react";
import styles from "./PSQL_Component.module.scss";

function PSQLComponent() {
  const [data, setData] = useState([]);
  const [consulta, setConsulta] = useState("");
  const [topK, setTopK] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [executionTime, setExecutionTime] = useState(0);

  const fetchData = () => {
    setIsLoading(true);
    fetch(`http://localhost:5000/api/news/${consulta}/${topK}`)
      .then((res) => res.json())
      .then((response) => {
        if (response.noticia) {
          setData(response.noticia);
          setExecutionTime(response.execution_time);
        } else {
          setData([]);
          setExecutionTime(0);
        }
        setIsLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setIsLoading(false);
      });
  };

  const handleConsultaChange = (event) => {
    setConsulta(event.target.value);
  };

  const handleTopKChange = (event) => {
    setTopK(event.target.value);
  };

  return (
    <div className={styles.principal}>
      <h3>Consulta en Postgres</h3>
      <div className={styles.inputs}>
        <input type="text" value={consulta} onChange={handleConsultaChange} />
        <input type="number" value={topK} onChange={handleTopKChange} />
        <button
          onClick={fetchData}
          disabled={isLoading}
          className="btn-secondary"
        >
          {isLoading ? "Cargando..." : "Consultar"}
        </button>
        <button
          onClick={() => {
            setConsulta("");
            setTopK(0);
          }}
          className="btn-danger"
        >
          Limpiar
        </button>

        <p>Tiempo de ejecución (s): {executionTime}</p>
      </div>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Rank</th>
          </tr>
        </thead>
        <tbody>
          {data.map((NewsItem) => (
            <tr key={NewsItem.id}>
              <td>{NewsItem.id}</td>
              <td>{NewsItem.title}</td>
              <td>{NewsItem.rank}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PSQLComponent;
