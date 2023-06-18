import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import NavBar from "./NavBar/NavBar";
import PSQLComponent from "./Components/PSQL_Component/PSQL_Component";
import Python_Component from "./Components/Python_Component/Python_Component";

import styles from "./App.module.scss";
import Principal_Component from "./Components/Principal_Component/Principal_Component";

function App() {
  return (
    <Router>
      <div className={styles.principalStyle}>
        <NavBar className={styles.navBar} fixed />
        <div className={styles.routesContainer}>
          <Routes>
            <Route exact path="/" element={<Principal_Component />} />
            <Route exact path="/python" element={<Python_Component />} />
            <Route exact path="/psql" element={<PSQLComponent />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
