document.addEventListener("DOMContentLoaded", () => {
  const profileButton = document.getElementById("profile-button");
  const profileDropdown = document.getElementById("profile-dropdown");
  const mobileMenuButton = document.getElementById("mobile-menu-button");
  const mobileMenu = document.getElementById("mobile-menu");
  const menuIconOpen = document.getElementById("menu-icon-open");
  const menuIconClose = document.getElementById("menu-icon-close");

  // Toggle profile dropdown
  if (profileButton && profileDropdown) {
    profileButton.addEventListener("click", (e) => {
      e.stopPropagation();
      if (profileDropdown.classList.contains("hidden")) {
        profileDropdown.classList.remove("hidden");
        profileDropdown.classList.add("dropdown-enter");
        setTimeout(() => profileDropdown.classList.remove("dropdown-enter"), 300);
      } else {
        profileDropdown.classList.add("dropdown-exit");
        setTimeout(() => {
          profileDropdown.classList.add("hidden");
          profileDropdown.classList.remove("dropdown-exit");
        }, 250);
      }
    });

    document.addEventListener("click", (e) => {
      if (!profileDropdown.contains(e.target) && !profileButton.contains(e.target)) {
        profileDropdown.classList.add("hidden");
      }
    });
  }

  // Toggle mobile menu
  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener("click", () => {
      if (mobileMenu.classList.contains("hidden")) {
        mobileMenu.classList.remove("hidden");
        mobileMenu.classList.add("mobile-menu-enter");
        setTimeout(() => mobileMenu.classList.remove("mobile-menu-enter"), 400);
      } else {
        mobileMenu.classList.add("mobile-menu-exit");
        setTimeout(() => {
          mobileMenu.classList.add("hidden");
          mobileMenu.classList.remove("mobile-menu-exit");
        }, 300);
      }
      menuIconOpen.classList.toggle("hidden");
      menuIconClose.classList.toggle("hidden");
    });
  }
});
