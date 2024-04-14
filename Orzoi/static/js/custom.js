let autocomplete;

function initAutoComplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('id_address'),
        {
            types: ['geocode', 'establishment'],
            componentRestrictions: { 'country': ['np'] },
        })
    // function to specify what should happen when the prediction is clicked
    autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged() {
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry) {
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else {
        //console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    //console.log(place)

    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    geocoder.geocode({ 'address': address }, function (results, status) {
        // console.log('results=>', results)
        // console.log('status=>', status)

    if(status == google.maps.GeocoderStatus.OK){
        var latitude = results[0].geometry.location.lat();
        var longitude = results[0].geometry.location.lng();

        console.log('lat=>', latitude);
        console.log('lng=>', longitude);
        $('#id_latitude2').val(latitude);
        $('#id_longitude2').val(longitude);
        $('#id_latitude').val(latitude);
        $('#id_longitude').val(longitude);
        $('#id_address').val(address);
    }
    });

    //loop through the address components and assign other address data
    console.log(place.address_components);
    for (var i = 0; i < place.address_components.length; i++) {
        for (var j = 0; j < place.address_components[i].types.length; j++) {
            //get country
            if (place.address_components[i].types[j] == 'country') {
                $('#id_country').val(place.address_components[i].long_name);
            }
            //get state
            if (place.address_components[i].types[j] == 'administrative_area_level_1') {
                $('#id_state').val(place.address_components[i].long_name);
            }
            //get city
            if (place.address_components[i].types[j] == 'locality') {
                $('#id_city').val(place.address_components[i].long_name);
            }
            //get pincode
            if (place.address_components[i].types[j] == 'postal_code') {
                $('#id_pin_code').val(place.address_components[i].long_name);
            }
            else {
                $('#id_pin_code').val("");
            }
        }
    }
}



$(document).ready(function () {
    // add to cart
    $('.add_to_cart').on('click', function (e) {
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        data = {
            food_id: food_id,
        }

        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function (response) {
                console.log(response)
                if (response.status == 'login_required') {
                    Swal.fire({
                        title: "Login Required!",
                        text: "Please login to continue",
                        icon: "warning",
                        showCancelButton: false,
                        confirmButtonColor: "#3085d6",
                        cancelButtonColor: "#d33",
                        confirmButtonText: "Login"
                    }).then(function () {
                        window.location = '/login'
                    });
                }

                if (response.status == 'Failed') {
                    Swal.fire({
                        icon: "error",
                        title: "Oops...",
                        text: "Something went wrong!",
                        footer: '<a href="#">Why do I have this issue?</a>'
                    });
                }
                else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + food_id).html(response.qty);


                    //subtotal, tax and grandtotal 
                    apply_Cart_Amt(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grandtotal'],
                    )

                }

            }
        })
    })


    // place the cart item quantity on load
    $('.item_qty').each(function () {
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        $('#' + the_id).html(qty)
    })


    //  decrease cart
    $('.decrease_cart').on('click', function (e) {
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');

        data = {
            food_id: food_id,
        }

        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function (response) {
                console.log(response)
                if (response.status == 'login_required') {
                    Swal.fire({
                        title: "Login Required!",
                        text: "Please login to continue",
                        icon: "warning",
                        showCancelButton: false,
                        confirmButtonColor: "#3085d6",
                        cancelButtonColor: "#d33",
                        confirmButtonText: "Login"
                    }).then(function () {
                        window.location = '/login'
                    });
                } else if (response.status == 'Failed') {
                    Swal.fire({
                        icon: "error",
                        title: "Oops...",
                        text: "You donot have this item in your cart",
                    });
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + food_id).html(response.qty);

                    //subtotal, tax and grandtotal 
                    apply_Cart_Amt(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grandtotal'],
                    )

                    if (window.location.pathname == '/cart/') {
                        removeCartItem(response.qty, cart_id);
                        checkEmptyCart();
                    }

                }


            }
        })
    })


    //Delete Cart items

    $('.delete_cart').on('click', function (e) {
        e.preventDefault();


        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        data = {
            cart_id: cart_id,
        }

        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function (response) {
                console.log(response)
                if (response.status == 'Failed') {
                    Swal.fire({
                        icon: "error",
                        title: "Oops...",
                        text: "You donot have this item in your cart",
                    });
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    Swal.fire({
                        position: "top-end",
                        icon: "success",
                        title: "Item removed successfully!",
                        showConfirmButton: false,
                        timer: 1500
                    });

                    //subtotal, tax and grandtotal 
                    apply_Cart_Amt(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grandtotal'],
                    )
                    removeCartItem(0, cart_id)
                    checkEmptyCart();

                }
            }
        })
    })


    //Remove cart element if qty is 0
    function removeCartItem(cartItemQty, cart_id) {
        if (cartItemQty <= 0) {
            //remove the cart item element
            document.getElementById("cart-item-" + cart_id).remove()
        }
    }


    // check if the cart is empty
    function checkEmptyCart() {
        var cart_count = document.getElementById('cart_counter').innerHTML
        if (cart_count == 0) {
            document.getElementById("empty-cart").style.display = "block";
        }
    }

    // apply cart amt
    function apply_Cart_Amt(subtotal, tax_dict, grandtotal) {
        if (window.location.pathname == '/cart/') {
            $('#subtotal').html(subtotal)
            $('#grandtotal').html(grandtotal)

            console.log(tax_dict)
            for (key1 in tax_dict) {
                //console.log(tax_dict[key1])
                for (key2 in tax_dict[key1]) {
                    //console.log(tax_dict[key1][key2])
                    $('#tax-' + key1).html(tax_dict[key1][key2])
                }
            }
        }
    }

    // add opening hour
    $('.add_hour').on('click', function (e) {
        e.preventDefault();
        //alert('test');
        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        var url = document.getElementById('add_hour_url').value

        console.log(day, from_hour, to_hour, is_closed, csrf_token)

        if (is_closed) {
            is_closed = 'True'
            condition = "day != '' "
        } else {
            is_closed = 'False'
            condition = " day != '' && from_hour != '' && to_hour != '' "
        }

        if (eval(condition)) {
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': csrf_token,
                },
                success: function (response) {
                    if (response.status == 'success') {
                        if (response.is_closed == 'closed') {
                            html = '<tr id="hour-' + response.id + '" ><td><b>' + response.day + '</b></td><td>closed</td><td><a href="#" class="remove_hour" data-url="/Restaurant/opening-hour/remove/' + response.id + '/" >Remove</a></td></tr>';
                        }
                        else {
                            html = '<tr id="hour-' + response.id + '" ><td><b>' + response.day + '</b></td><td>' + response.from_hour + ' - ' + response.to_hour + '</td><td><a href="#" class="remove_hour" data-url="/Restaurant/opening-hour/remove/' + response.id + '/"  >Remove</a></td></tr>';
                        }

                        $(".opening_hour").append(html)
                        document.getElementById("opening_hour").reset();
                    }
                    else {
                        Swal.fire(response.message, '', "error");
                    }

                    //console.log(response)
                }
            })
            //console.log('add the entry')
        } else {
            //console.log('please fill all fields')
            Swal.fire('Please fill all fields', '', 'info');
        }

    })

    //Remove opening hour
    $(document).on('click', '.remove_hour', function (e) {
        e.preventDefault();
        url = $(this).attr('data-url');
        //console.log(url);

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                //console.log(response)
                if (response.status == 'success') {
                    document.getElementById('hour-' + response.id).remove()
                }
            }
        })
    })
    //document ready close
});