// vacancy script
jQuery(document).ready(function(e){
  var i=1;
  var xcount=true;
  var counter;
  $.ajax({
    async: false,
    type: "GET",
    url: "/labster/fetch_career_data/",
    dataType: "json",
    success : function(data) {
      counter = data;
    },
    error: function(obj, msg, status) {
    }
  });
  jQuery('body').on('DOMNodeInserted', ".rbox-opening-list", function(e){
    var element=e.target;
    if (!xcount)
      return;
    i+=1;
    if (i!=counter)
      return;
    xcount=false;
    var mylist = jQuery('.rbox-opening-list');
    var listitems = mylist.children('.rbox-opening-li').get();
    var student=[];
    var k=0;
    listitems.sort(function(a, b) {
     var compA = jQuery(a).find("a").text().toUpperCase();
     var compB = jQuery(b).find("a").text().toUpperCase();
     return (compA < compB) ? -1 : (compA > compB) ? 1 : 0;
   })
    jQuery.each(listitems, function(idx, itm) { mylist.append(itm); });
    jQuery.each(mylist.children('.rbox-opening-li').get(),function(index){
      var desc=jQuery(this).find(".rbox-job-shortdesc");
      // console.log(desc.text());
      if (desc.text().indexOf("Labster") == -1){
        jQuery(this).hide();
      }
    });
  });
});
