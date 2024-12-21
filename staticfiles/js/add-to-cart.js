
document.addEventListener("DOMContentLoaded", function () {
    const addToCartButtons = document.querySelectorAll('.add-cart');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();  // Prevent the default link behavior

            const productId = button.getAttribute('data-product-id');
            addToCart(productId);
        });
    });

    function addToCart(productId) {
        fetch(`/product/add-to-cart/${productId}/`, {
            method: 'POST',  // Use POST method for adding items
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${yourTokenHere}`,  // Add token for auth if necessary
                'X-CSRFToken': getCsrfToken()  // Include CSRF token for security
            },
            body: JSON.stringify({
                quantity: 1  // You can modify this if you want to add a specific quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Item added to cart');
                // Optionally, update UI (cart count, etc.)
            } else {
                console.log('Error:', data.message || 'An error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Helper function to get CSRF token
    function getCsrfToken() {
        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfTokenElement ? csrfTokenElement.value : '';
    }
});
