
$(document).ready(function(){
        // Listen for category filter clicks
        $(".category-filter").click(function(e){
            e.preventDefault(); // Prevent default link behavior

            var category = $(this).data('category');  // Get the selected category from the clicked element

            // Call the function to filter products by category
            filterProducts(category);
        });

        // Function to filter products based on selected category
function filterProducts(category) {
            $.ajax({
                url: "{% url 'all-products' %}",  // URL to fetch the filtered products (Django URL tag)
                data: { 'category': category },  // Send category parameter to server
                dataType: 'json',  // Expect JSON response from the server
                success: function(response) {
                    $('#filtered-products').empty();  // Clear the existing product list

                    // Loop through each product in the response
                    response.products.forEach(function(product) {
                        // Create the HTML structure for each product
                        var productHTML = `
                            <div class="col-lg-4 col-md-6 col-sm-6">
                                <div class="product__item product-list" data-category="${product.category}">
                                    <div class="product__item__pic set-bg" data-setbg="${product.main_image}">
                                        <img src="${product.main_image}" alt="${product.name}">

                                        <ul class="product__hover">
                                            <li><a href="#"><img src="{% static 'img/icon/heart.png' %}" alt=""></a></li>
                                            <li><a href="#"><img src="{% static 'img/icon/compare.png' %}" alt=""> <span>Compare</span></a></li>
                                            <li><a href="#"><img src="{% static 'img/icon/search.png' %}" alt=""></a></li>
                                        </ul>
                                    </div>
                                    <div class="product__item__text">
                                        <h6>${product.name}</h6>
                                        <a href="#" class="add-cart">+ Add To Cart</a>
                                        <div class="rating">
                                            <i class="fa fa-star-o"></i>
                                            <i class="fa fa-star-o"></i>
                                            <i class="fa fa-star-o"></i>
                                            <i class="fa fa-star-o"></i>
                                            <i class="fa fa-star-o"></i>
                                            <script src="{% static 'js/stars-logic.js' %}"></script>
                                        </div>
                                        <h5>${product.price}</h5>
                                        <div class="product__color__select">
                                            <label for="pc-4"><input type="radio" id="pc-4"></label>
                                            <label class="active black" for="pc-5"><input type="radio" id="pc-5"></label>
                                            <label class="grey" for="pc-6"><input type="radio" id="pc-6"></label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;

                        // Append the generated HTML for this product to the #filtered-products container
                        $('#filtered-products').append(productHTML);
                    });
                },
                error: function(xhr, status, error) {
                    // Handle any errors that occur during the AJAX request
                    console.error("Error fetching products: " + error);
                }
            });
        }
    });
