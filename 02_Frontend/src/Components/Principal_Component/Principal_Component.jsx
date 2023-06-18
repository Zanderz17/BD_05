import React, { useEffect, useState } from "react";
import styles from "./Principal_Component.module.scss";

function Principal_Component() {
  const [size, setSize] = useState("");
  const [executionTimePython, setExecutionTimePython] = useState(0);
  const [executionTimePSQL, setExecutionTimePSQL] = useState(0);
  const [isLoadingPSQL, setIsLoadingPSQL] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const uploadDataPython = () => {
    setIsLoading(true);
    fetch(`http://localhost:5000/uploadDataPython/${size}`)
      .then((res) => res.json())
      .then((response) => {
        if (response.mensaje) {
          setExecutionTimePython(response.execution_time);
        }
        setIsLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setIsLoading(false);
      });
  };

  const uploadDataPSQL = () => {
    setIsLoadingPSQL(true);
    fetch(`http://localhost:5000/uploadDataPSQL/${size}`)
      .then((res) => res.json())
      .then((response) => {
        if (response.mensaje) {
          setExecutionTimePSQL(response.execution_time);
        }
        setIsLoadingPSQL(false);
      })
      .catch((error) => {
        console.error(error);
        setIsLoadingPSQL(false);
      });
  };

  const handleSizeChange = (event) => {
    setSize(event.target.value);
  };

  return (
    <div className={styles.mainContainer}>
      <div className={styles.psqlMainInput}>
        <p>Ingrese la cantidad de documentos a cargar </p>
        <input
          type="text"
          className={styles.psqlInput}
          value={size}
          onChange={handleSizeChange}
        />
      </div>
      <div className={styles.principalButtons}>
        <div className="Python">
          <h1>Python</h1>
          <button
            onClick={uploadDataPython}
            disabled={isLoading}
            className="btn-secondary"
          >
            {isLoading ? "Cargando..." : "Cargar índice en python"}
          </button>
          <p>Tiempo de ejecución (s): {executionTimePython}</p>
        </div>

        <div className="Postgres">
          <h1>Postgres</h1>
          <button
            onClick={uploadDataPSQL}
            disabled={isLoadingPSQL}
            className="btn-secondary"
          >
            {isLoadingPSQL ? "Cargando..." : "Cargar índice en Postgres"}
          </button>
          <p>Tiempo de ejecución (s): {executionTimePSQL}</p>
        </div>
      </div>
    </div>
  );
}

export default Principal_Component;
