export const PageLinks = {
  MAIN_PAGE: "/",
  PROFILE_PAGE: "/profile",
  LOGIN_PAGE: "/login",
  REGISTER: "/sign-up",
  BLOG_PAGE: "/blog",
};

export type PageLink = (typeof PageLinks)[keyof typeof PageLinks];
