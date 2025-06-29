// document.addEventListener('DOMContentLoaded', function() {
//     const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
//     const sidebarCloseBtn = document.getElementById('sidebar-close-btn');
//     const sidebar = document.getElementById('sidebar');
//     const chatContent = document.getElementById('chat-content');

//     if (sidebarToggleBtn && sidebar && chatContent) {
//         sidebarToggleBtn.addEventListener('click', function() {
//             sidebar.classList.remove('-translate-x-full');
//             chatContent.classList.remove('ml-0');
//             chatContent.classList.add('ml-64');
//         });
//     }

//     if (sidebarCloseBtn && sidebar && chatContent) {
//         sidebarCloseBtn.addEventListener('click', function() {
//             sidebar.classList.add('-translate-x-full');
//             chatContent.classList.remove('ml-64');
//             chatContent.classList.add('ml-0');
//         });
//     }
// });

document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
    const sidebarCloseBtn = document.getElementById('sidebar-close-btn');
    const chatContent = document.getElementById('chat-content');

    // Initially hide sidebar
    sidebar.classList.add('-translate-x-full');
    sidebar.classList.add('transition-transform', 'duration-300');

    sidebarToggleBtn.addEventListener('click', () => {
        sidebar.classList.remove('-translate-x-full');
        sidebarToggleBtn.classList.add('hidden'); // Hide the open button
        chatContent.classList.add('ml-64'); // Push content to right
    });

    sidebarCloseBtn.addEventListener('click', () => {
        sidebar.classList.add('-translate-x-full');
        sidebarToggleBtn.classList.remove('hidden'); // Show the open button
        chatContent.classList.remove('ml-64'); // Remove margin
    });
});
