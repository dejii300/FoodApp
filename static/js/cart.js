document.addEventListener('DOMContentLoaded', function () {
    // Update Cart
    var updateBtns = document.getElementsByClassName('update-cart');
    var cartTotal = document.getElementById('cart-total');
    var cartItems = document.getElementById('cart-items');
    var totalCart = document.getElementById('total-cart');

    for (var i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener('click', function (event) {
            event.preventDefault(); // Prevent default behavior of the button click
            var productId = this.dataset.product;
            var action = this.dataset.action;
            var quantityInput = document.getElementById('quantityInput_' + productId);  // Adjust this based on your actual HTML structure
            var quantity = quantityInput ? quantityInput.value : 1;

            console.log('Before Fetch - productId:', productId);
            console.log('Before Fetch - action:', action);
            console.log('Before Fetch - quantity:', quantity);

            fetch('/update_item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    'productId': productId,
                    'action': action,
                    'quantity': quantity,
                }),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                // Update cart total
                cartTotal.textContent = data.cartItems;
                cartItems.textContent = data.items;
                totalCart.textContent = data.cartTotal;

                if (action === 'add') {
                    var itemTotal = document.getElementById('item-total_' + productId);
                    itemTotal.textContent = data.itemTotal;
                }

                if (action === 'delete') {
                    var itemRow = this.closest('.rows');
                    itemRow.remove();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Product Quantity
    $('.quantity button').on('click', function () {
        var button = $(this);
        var inputField = button.closest('.quantity').find('input');
        var oldValue = parseFloat(inputField.val());

        if (button.hasClass('btn-plus')) {
            var newVal = oldValue + 1;
        } else {
            newVal = Math.max(0, oldValue - 1);
        }

        inputField.val(newVal);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var dropdown = document.getElementById('categoryDropdown');
    var dropdownMenu = dropdown.querySelector('.dropdown-c');

    dropdown.addEventListener('click', function() {
        dropdownMenu.style.display = (dropdownMenu.style.display === 'block') ? 'none' : 'block';
    });

    // Close the dropdown if the user clicks outside of it
    window.addEventListener('click', function(event) {
        if (!event.target.matches('.rd-nav-link')) {
            dropdownMenu.style.display = 'none';
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var dropdown = document.getElementById('settingDropdown');
    var dropdownMenu = dropdown.querySelector('.dropdown-c');

    dropdown.addEventListener('click', function() {
        dropdownMenu.style.display = (dropdownMenu.style.display === 'block') ? 'none' : 'block';
    });

    // Close the dropdown if the user clicks outside of it
    window.addEventListener('click', function(event) {
        if (!event.target.matches('.rd-nav-link')) {
            dropdownMenu.style.display = 'none';
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var ratesBtn = document.getElementById('ratesBtn');
    var ratesContainer = document.getElementById('ratesContainer');

    if (ratesBtn) {
        ratesBtn.addEventListener('click', function (event) {
            event.preventDefault();
            var displayStyle = (ratesContainer.style.display === 'none') ? 'block' : 'none';
            ratesContainer.style.display = displayStyle;

            // Update button text based on visibility
            ratesBtn.textContent = (displayStyle === 'none') ? 'Click to see rates' : 'Click to hide rates';
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    var showSmallchopsBtn = document.getElementById('showSmallchopsBtn');
    var smallchopsContainer = document.getElementById('smallchopsContainer');

    if (showSmallchopsBtn) {
        showSmallchopsBtn.addEventListener('click', function (event) {
            event.preventDefault();
            var displayStyle = (smallchopsContainer.style.display === 'none') ? 'block' : 'none';
            smallchopsContainer.style.display = displayStyle;

            // Update button text based on visibility
            showSmallchopsBtn.textContent = (displayStyle === 'none') ? 'Click to show  smallchops' : 'Click to hide smallchops';
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    var showSmallchopsBtn = document.getElementById('eventBtn');
    var smallchopsContainer = document.getElementById('eventContainer');

    if (showSmallchopsBtn) {
        showSmallchopsBtn.addEventListener('click', function (event) {
            event.preventDefault();
            var displayStyle = (smallchopsContainer.style.display === 'none') ? 'block' : 'none';
            smallchopsContainer.style.display = displayStyle;

            // Update button text based on visibility
            showSmallchopsBtn.textContent = (displayStyle === 'none') ? 'Click to show event orders' : 'Click to hide eventOrders';
        });
    }
});

$(document).ready(function() {
    $('#search-input').on('input', function() {
        var query = $(this).val();
        if (query.length >= 2) {
            $.ajax({
                url: '/search/suggestions/',
                method: 'GET',
                data: { query: query },
                success: function(response) {
                    var suggestions = response.product_suggestions.concat(response.video_suggestions, response.delivery_suggestions, response.evtproduct_suggestions);
                    var suggestionsHtml = '';
                    suggestions.forEach(function(suggestion) {
                        suggestionsHtml += '<div>' + suggestion + '</div>';
                    });
                    $('#search-suggestions').html(suggestionsHtml);
                    suggestionsContainer.show();
                }
            });
        } else {
            $('#search-suggestions').empty();
            suggestionsContainer.hide();
        }
    });
});

$(document).ready(function() {
    $('#submitBtn').click(function() {
        $.ajax({
            type: 'POST',
            url:  '/submit_comment/',
            data: $('#feedbackForm').serialize(),
            success: function(response) {
                if (response.success) {
                    // Show success message
                    $('#successText').text(response.message);
                    $('#successMessage').show();
                    // You may hide the form or perform other actions here
                } else {
                    // Handle errors
                    alert('Failed to submit comment: ' + response.errors);
                }
            },
            error: function(xhr, status, error) {
                // Handle AJAX errors
                console.error('AJAX Error: ' + status + ' - ' + error);
            }
        });
    });
});
