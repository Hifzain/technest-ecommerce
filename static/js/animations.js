document.addEventListener("DOMContentLoaded", function () {
    if (typeof AOS !== "undefined") {
        AOS.init({
            duration: 700,
            easing: "ease-out-cubic",
            once: true,
            offset: 60
        });
    } else {
        console.warn("AOS library failed to load - showing content without scroll animations.");
        document.querySelectorAll("[data-aos]").forEach(function (el) {
            el.removeAttribute("data-aos");
        });
    }
});
