document.addEventListener('DOMContentLoaded', () => {
    // Select all product containers
    const products = document.querySelectorAll('.product__item');

    products.forEach(product => {
        // Inside each product container, select the stars for that product
        const stars = product.querySelectorAll('.star');

        stars.forEach((star, index) => {
            // Add click event listener to each star
            star.addEventListener('click', () => {
                if (star.classList.contains('fa-star')) {
                    // If the star is solid, empty it and all stars after it
                    for (let i = index; i < stars.length; i++) {
                        stars[i].classList.remove('fa-star');
                        stars[i].classList.add('fa-star-o');
                    }
                } else {
                    // If the star is empty, fill it and all previous stars
                    for (let i = 0; i <= index; i++) {
                        stars[i].classList.remove('fa-star-o');
                        stars[i].classList.add('fa-star');
                    }
                }
            });
        });
    });
});
