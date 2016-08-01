$(document).ready(function(){
	var idVal= $('.currentCategory').attr('id');
	$('.'+idVal).css( "background-color" , "#485563" );

	/* When Item creation is submitted this validation kicks in*/
    $("#itemCreateForm").validate({

        rules: {
            itemTitle: {
                required: true,
                lettersonly: true
            },
            itemDesc: {
                required: true,
                cannotbeempty: true
            },
            itemCategory:{
            	required:true,
            	cannotbeselect:true
            }
        },
        messages: {
            itemTitle: {
                required: "Please enter the item title.",
                lettersonly: "Letters only please.No spaces or Special Characters allowed."
            },
            itemDesc: {
                required: "Please provide the item description."
            },
            itemCategory:{
            	cannotbeselect: "Please select a category."
            }

        }

    });

    $('#itemCategory').change(function(){
    var itemCategoryId = $(this).find('option:selected').attr('id');
    $("#selectedCategoryId").val(itemCategoryId);
});


    $.validator.addMethod("lettersonly", function(value, element) {
    return this.optional(element) || (/^[a-zA-Z]+$/.test(value));
}, "Letters only please");

$.validator.addMethod("cannotbeempty", function(value, element) {
    if (value.trim() === "") {
        return false;
    } else {
        return true;
    }
}, "Comments cannot be empty.Please provide the item description.");

$.validator.addMethod("cannotbeselect", function(value, element) {

    if (value.trim() === "-- Select a Category --") {
        return false;
    } else {
        return true;
    }
}, "Please select a category.");


});