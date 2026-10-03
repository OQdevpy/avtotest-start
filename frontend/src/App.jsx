import { Navigate, Route, Routes } from "react-router-dom";
import { AppProvider, useApp } from "./AppContext";
import Background from "./components/Background";
import Login from "./pages/Login";
import Home from "./pages/Home";
import StageList from "./pages/StageList";
import CategoryGrid from "./pages/CategoryGrid";
import CategoryStudy from "./pages/CategoryStudy";
import VariantList from "./pages/VariantList";
import StageVariants from "./pages/StageVariants";
import TestPlayer from "./pages/TestPlayer";

function Private({ children }) {
  const { user } = useApp();
  if (user === undefined) return null;
  return user ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  const { user } = useApp();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/" element={<Private><Home /></Private>} />
      <Route path="/talim" element={<Private><StageList mode="talim" /></Private>} />
      <Route path="/talim/:stageId" element={<Private><CategoryGrid /></Private>} />
      <Route path="/bolim/:categoryId" element={<Private><CategoryStudy /></Private>} />
      <Route path="/bosqichli" element={<Private><StageList mode="test" /></Private>} />
      <Route path="/variantlar" element={<Private><VariantList /></Private>} />
      <Route path="/bolim-variantlar" element={<Private><StageVariants /></Private>} />
      <Route path="/test/:attemptId" element={<Private><TestPlayer /></Private>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AppProvider>
      <Background />
      <AppRoutes />
    </AppProvider>
  );
}
