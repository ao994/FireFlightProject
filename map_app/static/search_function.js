
function liveSearch() 
{
    // Declare variables
    var input, filter, list, item, bird, i, txtValue;
    
    //get input
    input = document.getElementById('searchInput');
    filter = input.value.toUpperCase();
    list = document.getElementById("birdList");
    item = list.getElementsByClassName('list-group-item');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < item.length; i++) {
        bird = item[i];

        txtValue = bird.textContent || bird.innerText;

        if (txtValue.toUpperCase().indexOf(filter) > -1) 
        {
            item[i].style.display = "";
        } 
        else 
        {
            item[i].style.display = "none";
        }
    }
}

function selectAllBirds() 
{
    // Declare variables
    var list, item, bird, i;
        
    //get input
    list = document.getElementById("birdList");
    item = list.getElementsByClassName('list-group-item');

    // Loop through all list items and select them all
    for (i = 0; i < item.length; i++) 
    {
        bird = item[i].querySelector("input");

        console.log(bird);

        bird.checked = true;
    }
}

function deselectAllBirds() 
{
    // Declare variables
    var list, item, bird, i;
        
    //get input
    list = document.getElementById("birdList");
    item = list.getElementsByClassName('list-group-item');

    // Loop through all list items and select them all
    for (i = 0; i < item.length; i++) 
    {
        bird = item[i].querySelector("input");

        console.log(bird);

        bird.checked = false;
    }

}
