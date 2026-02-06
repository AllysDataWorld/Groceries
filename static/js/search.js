


    <!-- The script targets:
    #myCategory → calls /get_categories/
    #myItem → calls /get_items/
    #storeCategory → calls /get_store_categories/ (optional)
    #storeItem → calls /get_store_items/ (optional) -->

    $(document).ready(function(){
        // Autocomplete for My Category
        $("#myCategory").autocomplete({
            source: "/get_categories/",
            minLength: 2
        });

        // Autocomplete for My Item
        $("#myItem").autocomplete({
            source: "/get_items/",
            minLength: 2
        });

        // Optional: Autocomplete for Store Category
        $("#storeCategory").autocomplete({
            source: "/get_store_categories/",
            minLength: 2
        });

        // Optional: Autocomplete for Store Item
        $("#storeItem").autocomplete({
            source: "/get_store_items/",
            minLength: 2
        });
    });
