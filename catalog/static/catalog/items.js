function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getProps(body) {
    let props = {
        method: 'POST',
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        mode: "same-origin",
    }
    if (body !== null && body !== undefined) {
        props.body = JSON.stringify(body);
    }
    return props;
}

function getFilters() {
    var count = 0;
    var filter="";
    if (search !== "") {
        filter = filter + "?search=" + search;
        count++;
    } 
    if (order !== "") {
        if (count > 0) {
            filter = filter + "&";
        }
        else {
            filter = filter + "?";
        }
        filter = filter + "ordering=" + order;
    }
    return filter;
}

function getEtsyFilters() {
    var filter="";
    if (search !== "") {
        filter = filter + "&keywords=" + search;
    }
    if (etsysort !== "") {
        filter = filter + "&sort_on=" + etsysort;
        filter = filter + "&sort_order=" + etsysortorder;
    }
    return filter;
}

var tab = "";

//get items
function getItems() {
    if (tab === "all") {
        getAllItems();
    }
    else if(tab === "manage") {
        getSponsorItems();
    }
    //etsy
    else if (tab === "etsy"){
        getEtsyItems();
    }
}

function getAllItems() {
    $('#item').empty();
    tab = "all";
    var filter = getFilters();
    var endpoint = "/catalog/items" + filter;
    $.ajax({
        url : endpoint,
    })
    .done(function(response) {
        getItemCards(response);
    });
}

function getEtsyItems() {
    $('#item').empty();
    tab = "etsy";
    var etsy_url = "https://openapi.etsy.com/v2"
    var etsy_key = "1a3ofydrsprc5cev28c3vb7l"
    var filter = getEtsyFilters();
    var endpoint = etsy_url + '/listings/active.js?' + 'limit=48&includes=Images:1' + filter + '&api_key=' + etsy_key;
    $.ajax({
        url: endpoint,
        dataType: 'jsonp',
    })
    .done(function(response) {
        var items = response.results;
        getItemCards(items);
    });
}

function getSponsorItems() {
    $('#item').empty();
    tab = "manage";
    var filter = getFilters();
    var endpoint = "/catalog/sponsor-items" + filter;
    $.ajax({
        url : endpoint,
    })
    .done(function(response) {
        getItemCards(response);
    });
}


function getItemCards(items) {
    items.forEach(function(items) {        
        if (tab === "all") {
            var ID = items.api_item_Id;
            var image = items.images[0].image_link;
            var name = items.item_name;
            var price = items.retail_price;
            var review = "";
        }
        else if(tab === "manage") {
            var ID = items.catalog_item.api_item_Id;
            var image = items.catalog_item.images[0].image_link;
            var name = items.catalog_item.item_name;
            var price = items.catalog_item.retail_price;
            var review = '<a href="/catalog/browse_pending_product_reviews/' + ID + ' " class="btn btn-primary mt-2">Pending reviews</a>';
        }
        //etsy
        else {
            var ID = items.listing_id;
            var image = items.Images[0].url_170x135;
            var name = items.title;
            var price = parseFloat(items.price);
            var review = "";
        }
        inSponsor(ID, price);
        $('#item').append(
            '<div class="card m-2 col-sm-4" id="' + ID + '" style="max-width: 20rem;"> ' +
            '<div class="card-body text-center">' +
            '<img class="m-2 mx-auto img-thumbnail" src="' + image + '" width="auto" height="auto" />' +
            '<h5 class="card-title font-weight-bold" data-toggle="tooltip" title="' + name + '">' + name.slice(0,30) + '...</h5>' +
            '<p class="card-text">price: $' + price.toFixed(2) + '</p>' +
            '<p class="card-text points" id="' + ID + '"></p>' + 
            '<input type="button" class="btn btn-primary change" name="change" id="' + ID + '" value="change" />' +
            review +
            '</div></div>'   
        );
    });
    

    function inSponsor(ID, price) {
        let body = {
            "ID": ID,
            "price": price
        };
        var props = getProps(body);
        fetch('/catalog/all_items', props)
        .then(function(response) {
            return response.json();
        })
        .then(function(response) { 
            
            if (Boolean(response.inSponsor)) {
                $('#'+ID+'.change').val("Add to Catalog");
                $('#'+ID+'.card').removeClass("active_card");
                
            }
            else {
                $('#'+ID+".change").val("Remove from Catalog");
                $('#'+ID+'.card').addClass("active_card");
                
            }
            if (response.points !== 0) {
                $('#'+ID+'.points').text("points: " + response.points);
            }
        })
    }

    $('.change').click(function(e) {
        e.preventDefault();
        var ID = this.id;
        let body = {
            "ID": ID
        };
        var props = getProps(body);
        fetch('/catalog/browse', props)
        .then(function(response) {
            return response;
        })
        .then(function() {
            inSponsor(ID, 0);
        })
    })
}


//get sidebars
//all and sponsor
function getAllSidebar() {
    $('#sidebar').empty();
    $('#sidebar').append(
    '<h5 class="font-weight-bold" style="text-align:center;">Sort By:</h5>' +
    '<button class="btn btn-primary btn-block side_group last_mod-">Most Recent</button>' +
    '<button class="btn btn-primary btn-block side_group last_mod">Least Recent</button> '+
    '<button class="btn btn-primary btn-block side_group price-">Most Expensive</button>'  +
    '<button class="btn btn-primary btn-block side_group price">Least Expensive</button>'
    );
    
    function buttonActiveSide(name) {
        $('.side_group').removeClass("btn-active");
        $('.'+name).addClass("btn-active");
    }

    $(".last_mod").click(function() { 
        buttonActiveSide("last_mod");
        if (tab === "manage") {
            order = "date_added";
        }
        else {
            order = "last_modified"
        }
        etsysort = "created";
        etsysortorder = "up";
        getItems();
    });

    $(".last_mod-").click(function() {
        buttonActiveSide("last_mod-");
        if (tab === "manage") {
            order = "-date_added";
        }
        else {
            order = "-last_modified"
        }
        etsysort = "created";
        etsysortorder = "down";
        getItems();
    });

    $(".price").click(function() { 
        buttonActiveSide("price");
        if (tab === "manage") {
            order = "point_value";
        }
        else {
            order = "retail_price";
        }
        etsysort = "price";
        etsysortorder = "up";
        getItems();
    });

    $(".price-").click(function() {
        buttonActiveSide("price-");
        if (tab === "manage") {
            order = "-point_value";
        }
        else {
            order = "-retail_price";
        }
        etsysort = "price";
        etsysortorder = "down";
        getItems();
    });

}


var search = "";
var order = "";
var etsysort = "";
var etsysortorder = "";


$(document).ready(function() {
    getAllItems(); 
    getAllSidebar();
    buttonActiveTop("all");
});

function buttonActiveTop(name) {
    $('.top_group').removeClass("btn-active");
    $('.'+name).addClass("btn-active");
}

$(".all").click(function() {
    buttonActiveTop("all");
    getAllItems();
    getAllSidebar();  
});

$(".etsy").click(function() {
    buttonActiveTop("etsy");
    getEtsyItems();
    getAllSidebar();
});

$(".manage").click(function() {
    buttonActiveTop("manage");
    getSponsorItems();
    getAllSidebar();
});

$("#search").click(function() {
    search = $("#searchbar").focus().val();
    getItems();
});

$("#clearsearch").click(function() {
    $("#searchbar").focus().val('');
    search = "";
    getItems();
});





