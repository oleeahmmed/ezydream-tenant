import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles/sap-theme.css";
import "./styles/sap-document.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
