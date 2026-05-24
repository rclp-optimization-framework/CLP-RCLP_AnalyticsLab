import { Navigate, Route, Routes } from "react-router-dom";
import { RootLayout } from "./components/layout/RootLayout";
import { HomePage } from "./pages/HomePage";
import { BatteriesPage } from "./pages/BatteriesPage";
import { TestsPage } from "./pages/TestsPage";
import { TestDetailPage } from "./pages/TestDetailPage";
import { ExecutionPageNew as ExecutionPage } from "./pages/ExecutionPageNew";
import { CachePage } from "./pages/CachePage";
import { CacheDetailPage } from "./pages/CacheDetailPage";
import { StatisticsPage } from "./pages/StatisticsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/batteries" element={<BatteriesPage />} />
        <Route path="/tests" element={<TestsPage />} />
        <Route path="/tests/:testId" element={<TestDetailPage />} />
        <Route path="/execution" element={<ExecutionPage />} />
        <Route path="/cache" element={<CachePage />} />
        <Route path="/cache/:cacheId" element={<CacheDetailPage />} />
        <Route path="/results" element={<Navigate to="/cache" replace />} />
        <Route path="/results/:resultId" element={<Navigate to="/cache" replace />} />
        <Route path="/statistics" element={<StatisticsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
