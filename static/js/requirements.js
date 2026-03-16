
$("#more_tags").click(function(){
    var len = parseInt($('#inputs').children('input').length)+1;
    var newTag = $( "<input />", {type: "text", 'name': 'term_'+len, 'id': 'term_'+len, "placeholder": "Insira um termo"});
    $('#inputs').append(newTag);
});