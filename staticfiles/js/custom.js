document.addEventListener('DOMContentLoaded', function() {
    // Sticky navbar functionality
    let prevScrollPos = window.pageYOffset;
    const navbar = document.getElementById("sticky-nav");
    if (navbar) {
        const navbarHeight = navbar.offsetHeight;
        window.addEventListener('scroll', function() {
            const currentScrollPos = window.pageYOffset;
            if (prevScrollPos > currentScrollPos) {
                navbar.style.top = "0";
            } else {
                navbar.style.top = `-${navbarHeight}px`;
            }
            prevScrollPos = currentScrollPos;
        });
    }

    // Bootstrap dropdowns
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'))
    dropdownElementList.forEach(function (dropdownToggleEl) {
        new bootstrap.Dropdown(dropdownToggleEl)
    });

    // Custom submenu functionality
    var dropdownSubmenus = [].slice.call(document.querySelectorAll('.dropdown-submenu > a'));
    dropdownSubmenus.forEach(function(element){
        element.addEventListener('click', function(e){
            e.preventDefault();
            e.stopPropagation();
            var submenu = this.nextElementSibling;
            if(submenu && submenu.classList.contains('show')){
                submenu.classList.remove('show');
            } else {
                if(submenu) submenu.classList.add('show');
            }
        });
    });

    console.log('Custom JS loaded and executed');
});
