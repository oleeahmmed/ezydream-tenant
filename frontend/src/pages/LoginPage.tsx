import { Navigate } from "react-router-dom";
import { SapLoginScreen } from "../components/SapLoginScreen";
import { getAccessToken } from "../lib/auth";

export default function LoginPage() {
  if (getAccessToken()) return <Navigate to="/" replace />;
  return <SapLoginScreen />;
}
