import { Routes, Route } from "react-router-dom";

import { FullScreenPage } from "@pages/FullScreenPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<FullScreenPage />}></Route>
    </Routes>
  );
}
