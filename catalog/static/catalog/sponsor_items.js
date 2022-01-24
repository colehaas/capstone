var order = "";
var search = "";

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

function getItems() {
    var filter = getFilters();
    var endpoint = "/catalog/sponsor-items" + filter;
    $.ajax({
        url : endpoint,
    })
    .done(function(response) {
        $('#item').empty();
        getSponsorItemCards(response);
    });
}   

function getSponsorItemCards(items) {
    items.forEach(function(items) {
        $('#item').append(
            '<div class="card m-2 col-sm-4" style="max-width: 20rem;"> ' +
            '<div class="card-body text-center">' +
            '<img class="m-2 mx-auto img-thumbnail" src="' + items.catalog_item.images[0].image_link + '" width="auto" height="auto" />' +
            '<h5 class="card-title font-weight-bold" data-toggle="tooltip" title="' + items.catalog_item.item_name + '">' + items.catalog_item.item_name.slice(0,30) + '...</h5>' +
            '<p class="card-text">points: ' + items.point_value + '</p>' +
            '<a href="/catalog/product-page/' + items.catalog_item.api_item_Id + ' " class="btn btn-primary px-auto">See full details</a>' +
            '</div></div>'
        ); 
    });
}

//sidebar

function getAllSidebar() {
    $('#sidebar').empty();
    $('#sidebar').append(
    '<h5 class="font-weight-bold" style="text-align:center;">Sort By:</h5>' +
    '<button class="btn btn-primary btn-block side_group date_added-">Most Recent</button>' +
    '<button class="btn btn-primary btn-block side_group date_added">Least Recent</button> '+
    '<button class="btn btn-primary btn-block side_group point_value-">Most Expensive</button>'  +
    '<button class="btn btn-primary btn-block side_group point_value">Least Expensive</button>'
    );
    
    function buttonActiveSide(name) {
        $('.side_group').removeClass("btn-active");
        $('.'+name).addClass("btn-active");
    }

    $(".date_added").click(function() { 
        buttonActiveSide("date_added");
        order = "date_added";
        getItems();
    });

    $(".date_added-").click(function() {
        buttonActiveSide("date_added-");
        order = "-date_added";
        getItems();
    });

    $(".point_value").click(function() { 
        buttonActiveSide("point_value");
        order = "point_value";
        getItems();
    });

    $(".point_value-").click(function() {
        buttonActiveSide("point_value-");
        order = "-point_value";
        getItems();
    });

}



$(document).ready(function() {
    getItems("");  
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

