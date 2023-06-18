import { Link } from "react-router-dom";
import styles from "./NavBar.module.scss";

function NavBar() {
  return (
    <nav className={`border fixed split-nav`}>
      <div className="nav-brand">
        <h3>
          <Link to="/">Proyecto 2</Link>
        </h3>
      </div>
      <div className="collapsible">
        <input id="collapsible1" type="checkbox" name="collapsible1" />
        <label htmlFor="collapsible1">
          <div className="bar1"></div>
          <div className="bar2"></div>
          <div className="bar3"></div>
        </label>
        <div className="collapsible-body">
          <ul className="inline">
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/python">Python</Link>
            </li>
            <li>
              <Link to="/psql">PostgreSQL</Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default NavBar;
