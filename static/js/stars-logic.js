  const stars = document.querySelectorAll('.rating i');

  // Add a click event listener to each star
  stars.forEach((star, index) => {
    star.addEventListener('click', () => {
      // Check if the clicked star is already filled (solid)
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
