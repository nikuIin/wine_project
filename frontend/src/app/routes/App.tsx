import { Routes, Route } from "react-router-dom";

import { FullScreenPage } from "@pages/FullScreenPage";
import { PageLinks } from "@shared/pagesLinks";
import { LoginPage } from "@pages/LoginPage";
import { RegisterPage } from "@pages/RegisterPage";
import { BlogPage } from "@pages/BlogPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<FullScreenPage />} />
      <Route path={PageLinks.LOGIN_PAGE} element={<LoginPage />} />
      <Route path={PageLinks.REGISTER} element={<RegisterPage />} />
      <Route path={PageLinks.BLOG_PAGE} element={<BlogPage />} />
      <Route path="*" element={<div>404 Not Found</div>} />
    </Routes>
  );
}
